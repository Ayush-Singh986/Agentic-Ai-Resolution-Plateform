from datetime import datetime, timedelta, timezone
import logging
from typing import Any
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from app.core.config import settings


REQUEST_TTL_SECONDS = 24 * 60 * 60
logger = logging.getLogger(__name__)


def _configured() -> None:
    if not all(
        (
            settings.ECS_CLUSTER_NAME,
            settings.ECS_SERVICE_NAME,
            settings.REMEDIATION_TABLE_NAME,
        )
    ):
        raise HTTPException(
            status_code=503,
            detail="AWS ECS remediation is not configured.",
        )


def _clients():
    _configured()
    try:
        return (
            boto3.client("ecs", region_name=settings.AWS_REGION),
            boto3.resource("dynamodb", region_name=settings.AWS_REGION).Table(
                settings.REMEDIATION_TABLE_NAME
            ),
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not initialize AWS remediation clients.",
        ) from exc


def _service(ecs) -> dict[str, Any]:
    response = ecs.describe_services(
        cluster=settings.ECS_CLUSTER_NAME,
        services=[settings.ECS_SERVICE_NAME],
    )
    services = response.get("services", [])
    if len(services) != 1 or services[0].get("status") != "ACTIVE":
        raise HTTPException(
            status_code=404,
            detail="The configured ECS service was not found or is not active.",
        )
    return services[0]


def _previous_task_definition(ecs, current_arn: str) -> str:
    family, separator, revision_text = current_arn.rpartition(":")
    if not separator or not revision_text.isdigit():
        raise HTTPException(
            status_code=409,
            detail="The ECS service task definition has an unexpected ARN.",
        )

    current_revision = int(revision_text)
    next_token = None
    previous_arn = None
    while True:
        arguments = {
            "familyPrefix": family.rsplit("/", 1)[-1],
            "status": "ACTIVE",
            "sort": "DESC",
            "maxResults": 100,
        }
        if next_token:
            arguments["nextToken"] = next_token
        response = ecs.list_task_definitions(**arguments)
        candidates = response.get("taskDefinitionArns", [])
        previous_arn = next(
            (
                arn
                for arn in candidates
                if arn.rpartition(":")[0] == family
                and arn.rpartition(":")[2].isdigit()
                and int(arn.rpartition(":")[2]) < current_revision
            ),
            None,
        )
        if previous_arn:
            break
        next_token = response.get("nextToken")
        if not next_token:
            break

    if previous_arn is None:
        raise HTTPException(
            status_code=409,
            detail="No earlier active task definition exists for rollback.",
        )
    return previous_arn


def create_remediation_request(
    incident_id: str,
    action: str,
    created_by: str,
) -> dict[str, Any]:
    ecs, table = _clients()
    try:
        service = _service(ecs)
        current_task_definition = service["taskDefinition"]
        target_task_definition = current_task_definition
        if action == "rollback":
            target_task_definition = _previous_task_definition(
                ecs,
                current_task_definition,
            )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not inspect the configured ECS service.",
        ) from exc

    now = datetime.now(timezone.utc)
    item = {
        "request_id": str(uuid4()),
        "incident_id": incident_id,
        "action": action,
        "status": "pending",
        "cluster": settings.ECS_CLUSTER_NAME,
        "service": settings.ECS_SERVICE_NAME,
        "current_task_definition": current_task_definition,
        "target_task_definition": target_task_definition,
        "current_deployment_id": next(
            (
                deployment.get("id")
                for deployment in service.get("deployments", [])
                if deployment.get("status") == "PRIMARY"
            ),
            "",
        ),
        "service_updated_at": service["updatedAt"].isoformat(),
        "created_at": now.isoformat(),
        "expires_at": int((now + timedelta(seconds=REQUEST_TTL_SECONDS)).timestamp()),
        "created_by": created_by,
    }
    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(request_id)",
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not save the pending remediation request.",
        ) from exc
    return item


def get_remediation_request(request_id: str) -> dict[str, Any]:
    _, table = _clients()
    try:
        response = table.get_item(
            Key={"request_id": request_id},
            ConsistentRead=True,
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not load the remediation request.",
        ) from exc
    item = response.get("Item")
    if item is None:
        raise HTTPException(status_code=404, detail="Remediation request not found.")
    if item["expires_at"] <= int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=410, detail="Remediation request expired.")
    return item


def list_pending_remediation_requests() -> list[dict[str, Any]]:
    _, table = _clients()
    requests = []
    arguments: dict[str, Any] = {
        "FilterExpression": Attr("status").eq("pending"),
    }
    try:
        while True:
            response = table.scan(**arguments)
            requests.extend(
                item
                for item in response.get("Items", [])
                if item["expires_at"] > int(datetime.now(timezone.utc).timestamp())
            )
            last_key = response.get("LastEvaluatedKey")
            if not last_key:
                break
            arguments["ExclusiveStartKey"] = last_key
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not load pending remediation requests.",
        ) from exc
    return sorted(requests, key=lambda item: item["created_at"])


def get_remediation_status(request_id: str) -> dict[str, Any]:
    item = get_remediation_request(request_id)
    if item["status"] != "submitted":
        return item

    ecs, table = _clients()
    try:
        service_response = ecs.describe_services(
            cluster=item["cluster"],
            services=[item["service"]],
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Could not read ECS deployment status.",
        ) from exc

    services = service_response.get("services", [])
    if len(services) != 1:
        raise HTTPException(
            status_code=404,
            detail="The configured ECS service is no longer available.",
        )

    deployment = next(
        (
            candidate
            for candidate in services[0].get("deployments", [])
            if candidate.get("id") == item.get("deployment_id")
        ),
        None,
    )
    if deployment is None:
        deployment = next(
            (
                candidate
                for candidate in services[0].get("deployments", [])
                if candidate.get("status") == "PRIMARY"
                and candidate.get("taskDefinition")
                == item["target_task_definition"]
            ),
            None,
        )

    rollout_state = deployment.get("rolloutState") if deployment else None
    rollout_reason = deployment.get("rolloutStateReason") if deployment else None
    status = item["status"]
    if rollout_state == "COMPLETED":
        status = "healthy"
    elif rollout_state == "FAILED":
        status = "rollout_failed"

    if status != item["status"] or rollout_state:
        update_expression = "SET rollout_state = :rollout, rollout_reason = :reason"
        values = {
            ":rollout": rollout_state or "UNKNOWN",
            ":reason": rollout_reason or "No rollout reason provided.",
        }
        attribute_names = {}
        if status != item["status"]:
            update_expression += ", #status = :status"
            attribute_names["#status"] = "status"
            values[":status"] = status
        update_arguments = {
            "Key": {"request_id": request_id},
            "UpdateExpression": update_expression,
            "ExpressionAttributeValues": values,
            "ReturnValues": "ALL_NEW",
        }
        if attribute_names:
            update_arguments["ExpressionAttributeNames"] = attribute_names
        try:
            response = table.update_item(**update_arguments)
            item = response["Attributes"]
        except (BotoCoreError, ClientError) as exc:
            raise HTTPException(
                status_code=502,
                detail="Could not save the latest ECS deployment status.",
            ) from exc
    return item


def reject_remediation_request(
    request_id: str,
    rejected_by: str,
) -> dict[str, Any]:
    _, table = _clients()
    now = datetime.now(timezone.utc).isoformat()
    try:
        response = table.update_item(
            Key={"request_id": request_id},
            UpdateExpression="SET #status = :rejected, rejected_by = :user, rejected_at = :now",
            ConditionExpression="#status = :pending AND expires_at > :timestamp",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":rejected": "rejected",
                ":user": rejected_by,
                ":now": now,
                ":pending": "pending",
                ":timestamp": int(datetime.now(timezone.utc).timestamp()),
            },
            ReturnValues="ALL_NEW",
        )
        return response["Attributes"]
    except (BotoCoreError, ClientError) as exc:
        if (
            isinstance(exc, ClientError)
            and exc.response.get("Error", {}).get("Code")
            == "ConditionalCheckFailedException"
        ):
            raise HTTPException(
                status_code=409,
                detail="Request is no longer pending or has expired.",
            ) from exc
        raise HTTPException(
            status_code=502,
            detail="Could not reject the remediation request.",
        ) from exc


def approve_remediation_request(
    request_id: str,
    approved_by: str,
) -> dict[str, Any]:
    ecs, table = _clients()
    now = datetime.now(timezone.utc)
    try:
        lock_response = table.update_item(
            Key={"request_id": request_id},
            UpdateExpression="SET #status = :executing, approved_by = :user, approved_at = :now",
            ConditionExpression="#status = :pending AND expires_at > :timestamp",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={
                ":executing": "executing",
                ":user": approved_by,
                ":now": now.isoformat(),
                ":pending": "pending",
                ":timestamp": int(now.timestamp()),
            },
            ReturnValues="ALL_NEW",
        )
        item = lock_response["Attributes"]
    except (BotoCoreError, ClientError) as exc:
        if (
            isinstance(exc, ClientError)
            and exc.response.get("Error", {}).get("Code")
            == "ConditionalCheckFailedException"
        ):
            raise HTTPException(
                status_code=409,
                detail="Request is no longer pending or has expired.",
            ) from exc
        raise HTTPException(
            status_code=502,
            detail="Could not lock the remediation request for approval.",
        ) from exc

    try:
        current_service = _service(ecs)
        current_deployment_id = next(
            (
                deployment.get("id")
                for deployment in current_service.get("deployments", [])
                if deployment.get("status") == "PRIMARY"
            ),
            "",
        )
        if (
            current_service["taskDefinition"] != item["current_task_definition"]
            or current_deployment_id != item["current_deployment_id"]
            or current_service["updatedAt"].isoformat()
            != item["service_updated_at"]
        ):
            table.update_item(
                Key={"request_id": request_id},
                UpdateExpression="SET #status = :stale",
                ConditionExpression="#status = :executing",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":stale": "stale",
                    ":executing": "executing",
                },
            )
            raise HTTPException(
                status_code=409,
                detail=(
                    "The ECS service changed after this request was prepared. "
                    "Prepare a fresh remediation request."
                ),
            )
        update_arguments = {
            "cluster": item["cluster"],
            "service": item["service"],
        }
        if item["action"] == "restart":
            update_arguments["forceNewDeployment"] = True
        elif item["action"] == "rollback":
            update_arguments["taskDefinition"] = item["target_task_definition"]
        else:
            raise ValueError("Stored remediation action is not allowlisted.")

        response = ecs.update_service(**update_arguments)
        deployments = response.get("service", {}).get("deployments", [])
        primary = next(
            (
                deployment
                for deployment in deployments
                if deployment.get("status") == "PRIMARY"
            ),
            deployments[0] if deployments else {},
        )
        deployment_id = primary.get("id")
    except (BotoCoreError, ClientError, ValueError) as exc:
        try:
            table.update_item(
                Key={"request_id": request_id},
                UpdateExpression="SET #status = :failed, failure_code = :code",
                ConditionExpression="#status = :executing",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":failed": "failed",
                    ":code": (
                        exc.response.get("Error", {}).get("Code", "InvalidAction")
                        if isinstance(exc, ClientError)
                        else type(exc).__name__
                    ),
                    ":executing": "executing",
                },
            )
        except (BotoCoreError, ClientError):
            logger.exception(
                "Could not record failed remediation request %s",
                request_id,
            )
        raise HTTPException(
            status_code=502,
            detail="AWS did not accept the approved remediation action.",
        ) from exc

    try:
        expression_values = {
            ":submitted": "submitted",
            ":executing": "executing",
        }
        expression = "SET #status = :submitted"
        if deployment_id:
            expression += ", deployment_id = :deployment"
            expression_values[":deployment"] = deployment_id
        response = table.update_item(
            Key={"request_id": request_id},
            UpdateExpression=expression,
            ConditionExpression="#status = :executing",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues=expression_values,
            ReturnValues="ALL_NEW",
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "AWS accepted the action, but its audit status could not be saved. "
                "Check ECS service deployments before retrying."
            ),
        ) from exc
    return response["Attributes"]
