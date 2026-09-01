# NoSQL Key-Value / Document Database

## Overview

Non-relational databases optimized for high-throughput, low-latency access at massive scale, trading relational query flexibility for horizontal scalability and predictable performance — common as the operational store behind high-traffic applications and as a sink for semi-structured event or session data.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Primary service | DynamoDB | Firestore | Cosmos DB |
| Model | Key-value / document | Document (real-time sync focus) | Multi-model (document, key-value, graph, column-family) |
| Wide-column/high-throughput analog | (DynamoDB itself scales to this use case) | Bigtable | Cosmos DB Cassandra API |
| API/wire-protocol compatibility with other databases | No | No | Yes — MongoDB, Cassandra, Gremlin, Table APIs |
| Global distribution with tunable consistency | Global Tables (eventual/strong per-region) | Multi-region (fixed consistency modes) | Native, with 5 selectable consistency levels |

---

## What it's for

- **High-throughput operational stores** — session state, user profiles, shopping carts, leaderboards — anything needing predictable single-digit-millisecond reads/writes at scale.
- **Semi-structured event/document storage** — data that doesn't fit cleanly into a relational schema, or where schema evolves frequently.
- **Real-time application backends** — Firestore in particular is heavily used for mobile/web apps needing live data sync to clients.

---

## Key differences

**Cosmos DB is genuinely unique in offering wire-protocol compatibility with other databases.** Rather than just being "a document database," Cosmos DB exposes multiple API surfaces on the same underlying engine — a native SQL/Core API, plus MongoDB, Cassandra, Gremlin (graph), and Table API-compatible endpoints. This means existing MongoDB or Cassandra client code can often point at Cosmos DB with minimal changes, similar in spirit to Event Hubs' Kafka-compatible endpoint (see [Streaming/Messaging](../7.streaming-messaging/README.md)). Neither DynamoDB nor Firestore offers an equivalent multi-protocol story.

**GCP splits this category into two distinct products depending on use case**, where AWS and Azure each try to cover the range with one primary service. Firestore targets document-model, real-time-sync application backends (its standout feature is live client synchronization, popular for mobile/web apps). For DynamoDB-style massive-scale key-value/wide-column workloads, GCP's actual analog is **Bigtable** — a separate, wide-column store built for very high-throughput analytical and operational workloads (originally built for Google's own internal use, predating Bigtable-as-a-service by years). Picking the wrong one of the two on GCP (Firestore for a massive-scale wide-column workload, or Bigtable for a real-time-sync mobile app) is a common miscategorization.

**Consistency models differ in flexibility.** Cosmos DB's headline differentiator is five selectable consistency levels (from strong to eventual, with several intermediate options like "session" and "bounded staleness") tunable per request — the most granular control of the three. DynamoDB offers a simpler binary choice (eventually consistent or strongly consistent reads) plus Global Tables for multi-region with configurable conflict resolution. Firestore's consistency behavior is comparatively fixed by its mode (Native vs. Datastore mode) rather than exposed as a per-request tuning knob.

---

## When to reach for it vs. alternatives

- Reach for Cosmos DB specifically when you have existing MongoDB/Cassandra/Gremlin-based application code and want to avoid a rewrite while moving to a managed service.
- On GCP, choose Firestore for application-facing document storage with real-time sync needs, and Bigtable for high-throughput analytical/time-series workloads at DynamoDB-comparable scale — don't default to Firestore for everything just because it's the more commonly reached-for GCP NoSQL service.
- Reach for DynamoDB when staying AWS-native and needing predictable, scalable key-value/document access with straightforward operational simplicity.

---

## Resources

- [AWS DynamoDB documentation](https://docs.aws.amazon.com/dynamodb/)
- [GCP Firestore documentation](https://cloud.google.com/firestore/docs) · [Bigtable documentation](https://cloud.google.com/bigtable/docs)
- [Azure Cosmos DB documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/)
