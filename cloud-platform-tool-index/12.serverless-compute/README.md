# Serverless Compute (Functions)

## Overview

Function-as-a-service platforms that run small units of code in response to triggers without any server or container management — commonly used in data pipelines for lightweight glue logic: reacting to a new file landing in storage, transforming a single event, or triggering a downstream job.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | Lambda | Cloud Functions (2nd gen) | Azure Functions |
| Underlying execution model | One request per instance (traditional FaaS) | Built on Cloud Run — supports concurrent requests per instance | One request per instance (traditional), varies by plan |
| Stateful/long-running orchestration | Step Functions (separate service) | Workflows (separate service) | Durable Functions (built into the same programming model) |
| Hosting flexibility | Fixed (Lambda's own execution model) | Fixed (inherits Cloud Run model) | Multiple plans: Consumption, Premium, Dedicated |

---

## What it's for

- **Event-driven pipeline glue** — react to a file landing in object storage, a message arriving on a queue, or a database change, and trigger the next pipeline step.
- **Lightweight, short-lived transformations** — small stateless processing that doesn't warrant a full ETL job.
- **API endpoints and webhooks** — receiving external data pushes into a pipeline.

---

## Key differences

**Cloud Functions 2nd gen has a genuinely different execution architecture from Lambda.** It's built directly on top of Cloud Run, which means it inherits Cloud Run's concurrency model — a single function instance can handle multiple concurrent requests, rather than the traditional FaaS model (used by Lambda, and by Azure Functions in its default Consumption plan) where each instance handles exactly one request at a time. This affects both cost (fewer instances needed under concurrent load) and cold-start behavior, and is a real architectural distinction, not just a marketing difference.

**Azure Functions uniquely bakes stateful orchestration into the function programming model itself**, via the **Durable Functions** extension — letting you write long-running, stateful workflows (with waits, fan-out/fan-in, human interaction patterns) as ordinary-looking function code, with the orchestration state managed automatically. AWS and GCP's equivalents (Step Functions, Workflows) are separate services with their own definition languages (state machine JSON/YAML for Step Functions, YAML for GCP Workflows) rather than an extension of the function code itself.

**Azure Functions offers the most hosting flexibility** — Consumption (true serverless, pay-per-execution), Premium (pre-warmed instances, VNet integration, no cold starts), and Dedicated/App Service plans (fixed capacity, functions run alongside regular App Service apps) — letting you dial how "serverless" the deployment actually is. Lambda and Cloud Functions are more architecturally fixed to their respective serverless execution models, with less of a built-in dial toward "always-warm, dedicated capacity" short of using a different compute service entirely.

---

## When to reach for it vs. alternatives

- Reach for functions generally for event-driven, short-duration glue logic — not for long-running batch transformations, which belong in the ETL/batch-processing tiers of this index.
- Reach for Azure Durable Functions when the workflow needs to be stateful and long-running but you want to keep it in function code rather than standing up a separate orchestration service.
- Consider Cloud Functions 2nd gen (or Cloud Run directly) when concurrent-request efficiency matters for cost — high-concurrency, short-execution workloads benefit from the shared-instance model.
- Use Azure Functions Premium plan (or provisioned concurrency on Lambda) when cold-start latency is unacceptable for the use case.

---

## Resources

- [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/)
- [GCP Cloud Functions documentation](https://cloud.google.com/functions/docs)
- [Azure Functions documentation](https://learn.microsoft.com/en-us/azure/azure-functions/) · [Durable Functions overview](https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-functions-overview)
