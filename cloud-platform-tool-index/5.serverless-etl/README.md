# Serverless ETL

## Overview

Fully or largely managed ETL services that abstract away cluster management entirely (or almost entirely) — you write or configure a transformation job, and the provider handles provisioning and scaling. This sits above the distributed-batch-processing tier in abstraction: less control, but far less operational overhead.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | Glue | Dataflow | Data Factory (Mapping Data Flows) |
| Underlying engine | Apache Spark | Apache Beam | Apache Spark (compiled from a visual designer) |
| Batch + streaming | Primarily batch (Glue Streaming exists, less central) | Unified — same programming model for both | Primarily batch |
| Authoring style | Code-first (PySpark/Scala) | Code-first (Beam SDKs: Java, Python, Go) | Visual/low-code |
| Metadata integration | Native — built around Glue Data Catalog | External (BigQuery, GCS, etc.) | Native — built around Data Factory pipelines |

---

## What it's for

- **Transformation jobs without cluster management** — read from a source, transform (clean, join, reshape), write to a destination, without provisioning or tuning a cluster yourself.
- **Schema discovery and cataloging** — Glue's crawlers in particular are used to infer schema from raw files and populate a metastore automatically.
- **Visual, less-code-heavy pipeline authoring** — Data Factory's Mapping Data Flows target teams who want ETL logic expressed visually rather than in Spark code directly.

---

## Key differences

**Dataflow is a fundamentally different kind of product from the other two.** Glue and Data Factory's Mapping Data Flows are both essentially "managed Spark, batch-oriented." Dataflow is built on Apache Beam, which unifies batch and streaming under one programming model — you write a single pipeline definition, and the same code can run against a bounded (batch) or unbounded (streaming) data source with minimal changes. Glue and ADF both treat streaming as a secondary mode bolted onto a fundamentally batch-shaped product; Dataflow treats batch as a special case of streaming from the start.

**Authoring philosophy diverges sharply.** Glue and Dataflow are code-first — you write PySpark/Scala (Glue) or Beam SDK code in Java/Python/Go (Dataflow). Data Factory's Mapping Data Flows are visual-first: you build the transformation as a drag-and-drop graph inside the ADF UI, which then compiles to Spark execution behind the scenes. This makes ADF more approachable for teams without heavy Spark expertise, but less flexible for arbitrary custom logic — complex transformations that would be a few lines of PySpark can require more workarounds in a visual designer.

**Metastore coupling.** Glue is tightly coupled to the Glue Data Catalog — crawlers populate it automatically, and most other AWS analytics services (Athena, Redshift Spectrum, EMR) read from it directly, making Glue as much a cataloging/discovery tool as a transformation engine. Dataflow has no equivalent built-in catalog; it's purely a processing engine that reads/writes to whatever GCP storage/warehouse service you point it at. Data Factory similarly has no built-in catalog of its own (though it integrates with Purview for governance).

---

## When to reach for it vs. alternatives

- Reach for Dataflow specifically when you need one pipeline definition to serve both batch and streaming — this saves real engineering effort versus maintaining separate batch and streaming codepaths.
- Reach for Glue when you're already AWS-native and want automatic schema discovery (crawlers) plus tight integration with Athena/Redshift Spectrum via the shared Glue Data Catalog.
- Reach for ADF Mapping Data Flows when the team prefers visual pipeline authoring over Spark code, or when the transformation logic is straightforward enough that a visual designer doesn't become a constraint.
- Drop down to the distributed-batch-processing tier (EMR/Dataproc/HDInsight or Databricks) when you need Spark tuning control these fully-managed services intentionally abstract away.

---

## Resources

- [AWS Glue documentation](https://docs.aws.amazon.com/glue/)
- [GCP Dataflow documentation](https://cloud.google.com/dataflow/docs) · [Apache Beam programming guide](https://beam.apache.org/documentation/programming-guide/)
- [Azure Data Factory Mapping Data Flows documentation](https://learn.microsoft.com/en-us/azure/data-factory/concepts-data-flow-overview)
