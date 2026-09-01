# Stream Processing

## Overview

Services that continuously transform, aggregate, or analyze data as it arrives from a [streaming/messaging](../7.streaming-messaging/README.md) source, rather than processing it in scheduled batches — windowed aggregations, real-time joins, anomaly detection, and similar continuous-query workloads.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | Kinesis Data Analytics | Dataflow (streaming mode) | Stream Analytics |
| Underlying engine | Apache Flink (or legacy SQL-based) | Apache Beam | Proprietary SQL-like query engine |
| Authoring style | Flink API (Java/Python/SQL) | Beam SDK (Java/Python/Go) | Declarative SQL-like query language |
| Shares engine with batch processing on same cloud | No (separate from EMR's Spark/Hadoop) | Yes — same Beam pipeline can run batch or streaming | No |

---

## What it's for

- **Real-time aggregation and windowing** — rolling counts, sums, and averages over sliding/tumbling time windows as events arrive.
- **Real-time joins and enrichment** — combining a live stream with reference data or another stream.
- **Anomaly/pattern detection and alerting** — flagging events or sequences of events as they happen, rather than after a batch job runs.

---

## Key differences

**Dataflow is architecturally unique here, same as in the [serverless ETL](../5.serverless-etl/README.md) comparison** — because it's built on Apache Beam, the exact same pipeline code can run in either batch or streaming mode. Kinesis Data Analytics and Stream Analytics are both purpose-built streaming engines with no equivalent batch counterpart sharing the same programming model — Kinesis Data Analytics runs on Apache Flink specifically for streaming (EMR, AWS's batch engine, is a completely separate Spark/Hadoop-based product), and Stream Analytics has no batch analog at all within Azure.

**Stream Analytics is deliberately the simplest and least flexible.** It's built around a declarative, SQL-like query language purpose-made for streaming windowing/aggregation logic — genuinely the easiest of the three to get started with for straightforward windowed queries, but it hits a ceiling fast for complex custom logic (arbitrary stateful processing, custom deduplication logic, complex event patterns), at which point Azure teams typically pair it with Azure Functions for the parts SQL can't express, or move to Databricks Structured Streaming instead.

**Kinesis Data Analytics gives full Flink programming model access** (via its Studio notebooks or application code), meaning arbitrary custom logic, complex event processing, and fine-grained state management are all available — closer in power to what Dataflow offers, but scoped specifically to streaming rather than Dataflow's unified batch+streaming model.

**Latency and processing guarantees** are broadly comparable across all three (all support exactly-once processing semantics with appropriate configuration), so the differentiator between them in practice is programming model flexibility and how much the team wants to write custom code versus declare SQL-like queries, not raw processing capability.

---

## When to reach for it vs. alternatives

- Reach for Stream Analytics for straightforward windowed aggregation/alerting where a SQL-like query fully expresses the logic — fastest to build and lowest operational overhead for that use case.
- Reach for Dataflow when the same transformation logic needs to serve both batch and streaming use cases, or when Beam's unified model simplifies maintaining one codebase instead of two.
- Reach for Kinesis Data Analytics (Flink) when you need full programming-model flexibility for complex stateful stream processing while staying AWS-native.

---

## Resources

- [AWS Kinesis Data Analytics documentation](https://docs.aws.amazon.com/kinesisanalytics/)
- [GCP Dataflow documentation](https://cloud.google.com/dataflow/docs)
- [Azure Stream Analytics documentation](https://learn.microsoft.com/en-us/azure/stream-analytics/)
