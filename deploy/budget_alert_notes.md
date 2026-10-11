# Budget Alerts and Deployment Notes

The example Azure and AWS configurations use a **$1,000 monthly USD budget**.
That is a proposed cap for this capstone: the model estimates $537.90/month at
baseline and $979.01/month at the stated sustained 10x volume. It is not a
cloud quote, subscription, or deployed alert. Replace the cost-owner email and
confirm the budget scope before applying either configuration.

- Azure: deploy the ARM template at the intended subscription or resource
  group scope. It configures actual-spend alerts at 80% and 100%, plus a
  forecast alert at 100%. Verify the target scope and notification recipients
  in Azure Cost Management after deployment.
- AWS: use the object as the `CreateBudget` request body, then create budget
  notifications/subscribers in the same account. The cost filter expects the
  `CostCenter=afyaplus-ai-platform` resource tag; apply it consistently or the
  filtered budget will omit untagged spend.
- Alert-only: neither budget automatically stops resources or API calls. Add
  an explicit operator runbook and service-side spend limits before treating
  alerts as a hard cap.
- Serverless/autoscaling: compare scale-to-zero cold starts against the
  interactive p95 SLO, and use maximum concurrency/replica settings plus
  provider quotas to bound a traffic spike. Autoscaling is not enabled by the
  local Compose fallback.
- Observability: tag spend by cost center, environment, and workload; emit
  request-level token counts, retries, queue wait, latency, cache outcome, and
  status without logging patient text or secrets.
- Security: do not put provider API keys, cloud credentials, JWT secrets, or
  personal data in these JSON files. Use the cloud secret manager and IAM roles
  with least privilege. The local Compose service uses a runtime JWT secret.
- No paid cloud account is assumed. These are reviewable example payloads for
  free-tier consoles or a mentor account; no cloud deployment is claimed.

The local Compose file builds the unchanged Week 6 API, binds only to loopback,
and declares CPU, memory, and cost-identification labels. It does not include
Redis, a GPU, autoscaling, or a production OpenRouter call. A container limit
protects local resource use; it is not an autoscaling policy.

## Local Run Evidence

Validated locally on 2026-10-11; no paid cloud resource or model-provider call
was used.

```bash
export JWT_SECRET='replace-with-a-local-development-secret'
docker compose -p afya-cost -f deploy/docker-compose.cost.yml up --detach --build
python3 -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"
docker compose -p afya-cost -f deploy/docker-compose.cost.yml ps
docker compose -p afya-cost -f deploy/docker-compose.cost.yml down
```

Observed: image build succeeded; Compose reported the API container `healthy`
on `127.0.0.1:8000`; the health endpoint returned
`{"service":"AfyaPlus E-commerce Fulfilment API","version":"1.0.0","status":"ok"}`.
An authenticated Python request to `POST /agent/ask` returned HTTP 200 with a
grounded clinic-catalog answer and the two MCP tools in its trace. This is a
deterministic local agent fixture, not a live OpenRouter LLM integration.

Docker inspection confirmed a 1 CPU quota, 536,870,912-byte memory limit, and
the labels `com.afyaplus.cost-center=afyaplus-ai-platform`,
`com.afyaplus.environment=capstone`, and
`com.afyaplus.workload=triage-api`. These match the budget tag/filter values.
The Azure/AWS alerts are config-as-submitted only: $1,000/month with alerts at
$800 actual, $1,000 actual, and a forecast above $1,000. No cloud alert was
deployed or triggered.