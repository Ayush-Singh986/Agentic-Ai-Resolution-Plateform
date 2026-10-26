import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.services import aws_remediation


def make_pending_request(now):
    return {
        "request_id": "request-1",
        "incident_id": "INC-1005",
        "action": "restart",
        "status": "pending",
        "cluster": "incident-resolution",
        "service": "incident-resolution",
        "current_task_definition": "arn:aws:ecs:region:account:task-definition/app:2",
        "target_task_definition": "arn:aws:ecs:region:account:task-definition/app:2",
        "current_deployment_id": "deployment-1",
        "service_updated_at": now.isoformat(),
        "created_at": now.isoformat(),
        "expires_at": int((now + timedelta(hours=1)).timestamp()),
        "created_by": "requester",
    }


class PendingRemediationTests(unittest.TestCase):
    def test_lists_unexpired_pending_requests_across_scan_pages(self):
        now = datetime.now(timezone.utc)
        first_page_key = {"request_id": "page-1"}
        table = Mock()
        table.scan.side_effect = [
            {
                "Items": [
                    {
                        "request_id": "pending-new",
                        "status": "pending",
                        "created_at": now.isoformat(),
                        "expires_at": int((now + timedelta(hours=1)).timestamp()),
                    },
                    {
                        "request_id": "pending-expired",
                        "status": "pending",
                        "created_at": (now - timedelta(hours=1)).isoformat(),
                        "expires_at": int((now - timedelta(seconds=1)).timestamp()),
                    },
                ],
                "LastEvaluatedKey": first_page_key,
            },
            {
                "Items": [
                    {
                        "request_id": "pending-old",
                        "status": "pending",
                        "created_at": (now - timedelta(minutes=1)).isoformat(),
                        "expires_at": int((now + timedelta(hours=1)).timestamp()),
                    },
                ]
            },
        ]

        with patch.object(aws_remediation, "_clients", return_value=(Mock(), table)):
            requests = aws_remediation.list_pending_remediation_requests()

        self.assertEqual(
            [request["request_id"] for request in requests],
            ["pending-old", "pending-new"],
        )
        self.assertEqual(table.scan.call_count, 2)
        self.assertEqual(
            table.scan.call_args_list[1].kwargs["ExclusiveStartKey"],
            first_page_key,
        )

    def test_approval_submits_only_the_predefined_restart_action(self):
        now = datetime.now(timezone.utc)
        item = make_pending_request(now)
        service = {
            "taskDefinition": item["current_task_definition"],
            "updatedAt": now,
            "deployments": [{"id": "deployment-1", "status": "PRIMARY"}],
        }
        ecs = Mock()
        ecs.update_service.return_value = {
            "service": {
                "deployments": [{"id": "deployment-2", "status": "PRIMARY"}],
            }
        }
        table = Mock()
        table.update_item.side_effect = [
            {"Attributes": item},
            {"Attributes": {**item, "status": "submitted", "deployment_id": "deployment-2"}},
        ]

        with (
            patch.object(aws_remediation, "_clients", return_value=(ecs, table)),
            patch.object(aws_remediation, "_service", return_value=service),
        ):
            result = aws_remediation.approve_remediation_request(
                "request-1",
                "approver",
            )

        ecs.update_service.assert_called_once_with(
            cluster=item["cluster"],
            service=item["service"],
            forceNewDeployment=True,
        )
        self.assertEqual(result["status"], "submitted")
        self.assertEqual(result["deployment_id"], "deployment-2")

    def test_stale_request_is_marked_without_calling_ecs_update(self):
        now = datetime.now(timezone.utc)
        item = make_pending_request(now)
        service = {
            "taskDefinition": "arn:aws:ecs:region:account:task-definition/app:3",
            "updatedAt": now + timedelta(seconds=1),
            "deployments": [{"id": "deployment-2", "status": "PRIMARY"}],
        }
        ecs = Mock()
        table = Mock()
        table.update_item.side_effect = [
            {"Attributes": item},
            {"Attributes": item},
        ]

        with (
            patch.object(aws_remediation, "_clients", return_value=(ecs, table)),
            patch.object(aws_remediation, "_service", return_value=service),
        ):
            with self.assertRaises(HTTPException) as raised:
                aws_remediation.approve_remediation_request(
                    "request-1",
                    "approver",
                )

        self.assertEqual(raised.exception.status_code, 409)
        ecs.update_service.assert_not_called()


if __name__ == "__main__":
    unittest.main()
