# Streaming / Pub-Sub Messaging

## Overview

Messaging services that decouple producers from consumers of event data — the ingestion layer for real-time pipelines, application events, IoT telemetry, and change data capture streams, sitting upstream of [stream processing](../8.stream-processing/README.md).

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | Kinesis Data Streams | Pub/Sub | Event Hubs |
| Model | Partition/shard-based ordered log | Topic/subscription, no exposed partitions | Partition-based ordered log |
| Ordering guarantee | Within a shard | Only with ordering keys opted in | Within a partition |
| Capacity model | Provisioned shards, or on-demand | Fully automatic, no capacity planning | Throughput units, or auto-inflate |
| Kafka-compatible endpoint | No (MSK is the separate managed-Kafka product) | No (separate Confluent/managed-Kafka offerings) | Yes — Kafka protocol endpoint built in |

---

## What it's for

- **Real-time event ingestion** — application events, clickstreams, IoT telemetry, log data arriving continuously rather than in batches.
- **Decoupling producers and consumers** — multiple downstream consumers (stream processors, storage sinks, alerting) can read the same stream independently.
- **Buffering ahead of stream processing** — acts as the durable, replayable input to Dataflow/Kinesis Data Analytics/Stream Analytics jobs.

---

## Key differences

**Kinesis and Event Hubs share a conceptual model that Pub/Sub doesn't.** Both Kinesis Data Streams and Event Hubs are partition-based (shards, in Kinesis's terminology) ordered logs, conceptually close to Kafka — you provision capacity (shards / throughput units, though both now support on-demand/auto-inflate modes), and ordering is guaranteed within a partition but not across the whole stream. Pub/Sub is architecturally different: it's a topic/subscription model where partitions aren't exposed to the user at all, ordering isn't guaranteed by default (you opt into it per-message via an ordering key), and capacity scales automatically without any provisioning step. This makes Pub/Sub simpler to operate but means workloads that depend on strict, easy-to-reason-about ordering may fit the Kinesis/Event Hubs model more naturally.

**Event Hubs uniquely speaks the Kafka wire protocol.** This means existing Kafka producer/consumer clients can often point at Event Hubs with just a connection-string change, no code rewrite — a genuinely distinctive feature neither Kinesis nor Pub/Sub offers directly (AWS's answer is a separate product, Amazon MSK, a fully managed Kafka service rather than a Kafka-compatible facade on Kinesis).

**Capacity planning burden differs.** Pub/Sub requires the least upfront capacity planning — no shard/partition count decisions, it scales transparently. Kinesis and Event Hubs both traditionally required choosing a shard/throughput-unit count based on expected throughput (each shard capped at a fixed MB/s and records/s), though both have since added on-demand modes (Kinesis On-Demand, Event Hubs Auto-inflate) that narrow this gap.

---

## When to reach for it vs. alternatives

- Reach for Event Hubs when you need Kafka protocol compatibility without running Kafka yourself, or already have Kafka-based tooling to migrate.
- Reach for Pub/Sub when operational simplicity matters more than fine-grained ordering control, and your consumers don't need strict cross-message ordering.
- Reach for Kinesis when staying AWS-native and needing shard-level control, or pair with MSK specifically when full Kafka API/ecosystem compatibility (not just protocol compatibility) is required.

---

## Resources

- [AWS Kinesis Data Streams documentation](https://docs.aws.amazon.com/streams/)
- [GCP Pub/Sub documentation](https://cloud.google.com/pubsub/docs)
- [Azure Event Hubs documentation](https://learn.microsoft.com/en-us/azure/event-hubs/)
