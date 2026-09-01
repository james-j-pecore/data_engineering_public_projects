# Monitoring & Observability

## Overview

Services for collecting metrics, logs, and traces from pipelines and infrastructure, and alerting when something breaks — the layer that turns "the pipeline failed silently at 3am" into "we got paged at 3am with the exact failing step."

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | CloudWatch | Cloud Monitoring + Cloud Logging | Azure Monitor |
| Origin | Built natively for AWS | Originally Stackdriver (acquired third-party product) | Built natively for Azure |
| Log query language | CloudWatch Logs Insights | Logging query language (similar to Cloud Monitoring's) | Kusto Query Language (KQL), via Log Analytics |
| Metrics granularity | Per-service namespaces, very granular | Unified across GCP services | Unified across Azure services |
| Cross-service correlation tooling | ServiceLens, Contributor Insights, X-Ray (tracing) | Native, since Stackdriver was built as a unified product | Application Insights (APM/tracing) |

---

## What it's for

- **Pipeline failure alerting** — knowing immediately when a scheduled job fails, a queue backs up, or a service errors out.
- **Performance monitoring** — tracking latency, throughput, and resource utilization across pipeline stages.
- **Debugging via logs and traces** — correlating a failure across multiple services (e.g., a warehouse load failure traced back to a malformed record from an upstream ETL job).

---

## Key differences

**GCP's offering has the most unified origin story.** Cloud Monitoring and Cloud Logging began life as Stackdriver, a third-party product Google acquired and built to work across multiple clouds and services from day one as a single coherent logs+metrics+traces product. This history shows up as a generally cleaner, more consistent cross-service correlation experience out of the box, since the product wasn't retrofitted service-by-service the way CloudWatch's per-service metric namespaces grew organically over AWS's history.

**Azure Monitor's standout feature is Kusto Query Language (KQL)**, used to query logs via Log Analytics — a genuinely distinct and fairly powerful query language (closer to a specialized analytical query language than SQL) that represents a real learning curve for teams coming from CloudWatch Logs Insights or GCP's logging query syntax. Once learned, KQL is considered by many to be more expressive for log analytics than the other two clouds' query languages, but it is a dedicated skill to pick up rather than something transferable from SQL knowledge alone.

**CloudWatch is the most granular at the individual-service level** — nearly every AWS service emits detailed metrics into its own CloudWatch namespace — but this granularity historically came at the cost of a clunkier experience correlating an issue *across* services (tracing a failure from, say, a Lambda function through SQS to a downstream RDS write). AWS has closed much of this gap with newer additions (CloudWatch ServiceLens, Contributor Insights, embedded metric format, and X-Ray for distributed tracing), but the underlying architecture is still more "per-service metrics you correlate yourself" than GCP's or Azure's more unified starting points.

**Distributed tracing is a separate add-on product on all three** — AWS X-Ray, Google Cloud Trace, and Azure Application Insights (technically part of Azure Monitor but distinct in setup) — rather than bundled seamlessly into the base metrics/logging product, though Azure's Application Insights is generally considered the most tightly integrated of the three tracing add-ons with its parent monitoring product.

---

## When to reach for it vs. alternatives

- Budget real ramp-up time for KQL if adopting Azure Monitor/Log Analytics — it pays off in query power but isn't a transferable SQL skill.
- On AWS, set up ServiceLens/X-Ray deliberately for any pipeline spanning more than one or two services — CloudWatch's default per-service view alone won't give you an easy cross-service failure trace.
- Regardless of provider, alert on pipeline-level SLAs (job completion time, data freshness) in addition to raw infrastructure metrics — infrastructure health alone doesn't catch "the job succeeded but processed zero rows."

---

## Resources

- [AWS CloudWatch documentation](https://docs.aws.amazon.com/cloudwatch/)
- [GCP Cloud Monitoring documentation](https://cloud.google.com/monitoring/docs) · [Cloud Logging documentation](https://cloud.google.com/logging/docs)
- [Azure Monitor documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/) · [Kusto Query Language documentation](https://learn.microsoft.com/en-us/kusto/query/)
