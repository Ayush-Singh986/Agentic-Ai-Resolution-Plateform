# Deployed-server measurement guide

Use this procedure after deploying the application to AWS (or another HTTPS
server). The runner makes HTTP requests from your workstation to the deployed
server; all measured behavior and timing comes from that deployment. It refuses
localhost and requires HTTPS by default. It does not run the detector or PII
masker locally.

## Before measuring

1. Deploy the latest application image. It includes `GET /measurement-info`,
   which returns only the loaded FAISS document count required to qualify the
   retrieval result. Confirm `GET /health` returns `{"status":"healthy"}`.
2. Ingest the intended knowledge base in the image before deployment. Check the
   reported deployed document count in the output; this is the index actually
   loaded by the server, not a count read from your checkout.
3. Check in an independently labelled set of at least 30 unique incident
   scenarios in `evaluation/golden_dataset.json` for retrieval/root-cause
   measurements. Each expected passage and root-cause phrase list must be
   reviewed by a person. Do not count paraphrases, repeat requests, or duplicate
   incidents as independent labels. The repository's starter set has only four
   cases, so its percentages are exploratory and the runner will mark them
   ineligible as resume metrics.
4. Use at least 10 distinct cases for the timed manual-vs-tool study. Add
   representative cases; repeated or paraphrased examples do not strengthen the
   evidence.
5. Ensure the measurement client is allowed by your ALB/network access rules and
   that the deployed service has a working model-provider connection. Each
   quality, latency, benign-control, PII, and timed tool request runs the full
   incident workflow and may incur provider charges. Injection attempts should
   be rejected before inference.

The measurement-info endpoint reveals only an integer document count. It does
not return incident text or index contents.

## Run the full deployed measurement

From the repository root in PowerShell, substitute your deployed HTTPS API URL:

```powershell
python evaluation\server_measure.py `
  --base-url "https://incidents.example.com" `
  --suite all `
  --count 50 `
  --output "server-measurements.json"
```

The full suite:

- Calls `POST /incident` for each labelled case. Top-3 retrieval is a hit when
  the labelled expected passage appears among the returned evidence. Root-cause
  agreement requires every case-specific labelled phrase in the response.
- Sends 30 prompt-injection attempts and 10 benign controls to the deployed
  endpoint. It records the block rate, missed attempts, and false positives.
- Sends 30 synthetic PII entities (10 email, 10 phone, 10 IPv4) through one
  deployed incident request. It verifies that masking markers are returned and
  the original synthetic values are absent from the API response. The report
  stores counts and sample IDs, not the synthetic PII values.
- Makes 50 incident requests and calculates client-observed median and nearest
  rank p95 latency. This includes client-to-server network time and model time;
  it is not a production MTTR measurement. Optionally supply a Prometheus scrape
  URL to record the deployed histogram count before and after the run.
- Prompts you to time manual investigation/plan writing and tool-assisted
  investigation for each case. It randomizes the order per case and records
  paired results. This is a self-timed, single-operator study, not a controlled
  user study.
- Reports cost per incident as **not measurable** until the deployed service
  exposes provider-reported token usage or billing. The current fixed-price cost
  helper is not sufficient evidence; the runner will not convert it into a
  fabricated cost number.

`--suite all` includes the interactive time study, so run it in an interactive
terminal. You can run suites separately; each command first verifies the remote
health and measurement-info endpoints:

```powershell
python evaluation\server_measure.py --base-url "https://incidents.example.com" --suite quality
python evaluation\server_measure.py --base-url "https://incidents.example.com" --suite security
python evaluation\server_measure.py --base-url "https://incidents.example.com" --suite latency --count 50
python evaluation\server_measure.py --base-url "https://incidents.example.com" --suite cost
python evaluation\server_measure.py --base-url "https://incidents.example.com" --suite time-study
```

If your Prometheus `/metrics` endpoint is separately reachable, include its
deployed URL (otherwise client-side samples still provide the latency
percentiles):

```powershell
python evaluation\server_measure.py `
  --base-url "https://incidents.example.com" `
  --suite latency `
  --count 50 `
  --metrics-url "https://metrics.example.com/metrics"
```

The script appends runs to `server-measurements.json`; the file is git-ignored
and should remain an evidence artifact, not be committed with source. It stores
the deployment URL, timestamp, raw per-request outcomes, aggregate metrics,
misses, and an automatically generated `claude_resume_inputs` array. Do not
publish the JSON if the deployment URL or your environment is sensitive.

An HTTP-only trusted private deployment can be used only with explicit
`--allow-http`; do not use this for a public service:

```powershell
python evaluation\server_measure.py `
  --base-url "http://10.0.0.12:8000" `
  --allow-http `
  --suite quality
```

## Interpreting results honestly

- Retrieval and root-cause rates are resume-eligible only with at least 30
  independently labelled cases, at least 30 documents reported by the deployed
  index, and successful responses for every case.
- The timed-study result is included in resume inputs only with at least 10
  paired, distinct scenarios. State that this was a single-operator test; do not
  describe it as an MTTR reduction.
- Security scores apply only to the supplied synthetic cases and current
  deployed behavior. Report misses and benign false positives; a score is not a
  general security guarantee.
- Latency is measured from the runner to the deployed endpoint, not by replaying
  a local function or by relying on a pre-existing local metrics file.
- Cost is explicitly left blank until real provider usage/billing is instrumented.

## Push the measurement changes

After reviewing the staged file list and verifying that no result JSON or secrets
are staged:

```powershell
git status --short
git add .gitignore README.md SERVER_MEASUREMENTS.md `
  app\api\routes.py app\retrieval\vector_store.py `
  evaluation\evaluator.py evaluation\golden_dataset.json `
  evaluation\measure.py evaluation\server_measure.py `
  tests\test_incident_api.py tests\test_measurement.py
git diff --cached --check
git diff --cached --stat
git commit -m "Add deployed server measurement runner"
git push -u origin HEAD
```

The commands intentionally stage only measurement-related source and docs, not
the generated report, `.env`, credentials, or unrelated workspace files.
