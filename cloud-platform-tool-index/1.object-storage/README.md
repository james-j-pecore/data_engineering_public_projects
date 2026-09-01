# Object Storage

## Overview

Object storage holds unstructured or semi-structured data — files, blobs, logs, backups, raw data lake files — as immutable objects addressed by key, rather than as blocks on a filesystem or rows in a database. It's the foundation almost every other data engineering service in this index sits on top of: data lakes, ETL staging areas, data warehouse external tables, and ML training data all typically live here first.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | S3 (Simple Storage Service) | Cloud Storage (GCS) | Blob Storage |
| Unit of organization | Bucket → key | Bucket → object name | Storage account → container → blob |
| Default consistency | Strong (since Dec 2020) | Strong | Strong |
| Hot-tier equivalent | S3 Standard | Standard | Hot |
| Infrequent-access tier | S3 Standard-IA | Nearline | Cool |
| Archive tier | S3 Glacier / Glacier Deep Archive | Coldline / Archive | Archive |
| Auto-tiering | S3 Intelligent-Tiering | Autoclass | Lifecycle management (policy-based, not automatic) |

---

## What it's for

- **Data lake landing zone** — raw ingested data before it's cleaned, transformed, or loaded into a warehouse.
- **ETL/ELT staging** — intermediate files between pipeline stages (e.g., a Glue job writing Parquet to S3 for Redshift Spectrum or Athena to query).
- **Data warehouse backing store** — BigQuery and Redshift Spectrum/external tables, and Synapse serverless SQL pools, all query object storage directly without loading data in.
- **Backups, logs, and archives** — durable, cheap, long-term retention.
- **Static assets and ML artifacts** — model weights, training datasets, website assets.

---

## Key differences

**Namespace structure.** S3 and GCS both use a flat bucket → key namespace (with a "folder" illusion via `/` delimiters in key names). Azure adds an explicit extra layer — a *storage account* holds multiple *containers*, and blobs live inside containers — which changes how you think about resource limits and access scoping, since IAM and networking policy in Azure are often set at the storage-account level, not just per-container.

**Bucket/account naming and global uniqueness.** S3 bucket names are globally unique across *all* AWS customers; GCS bucket names are also globally unique. Azure storage account names are globally unique, but container names only need to be unique within an account — so naming collisions bite you at a different layer in Azure than in AWS/GCP.

**Tiering model.** AWS and GCP both offer a fully automatic tiering product (Intelligent-Tiering, Autoclass) that moves objects between tiers based on access patterns with no lifecycle rules to write. Azure's Lifecycle Management is policy-based (age- or last-accessed-based rules you define) rather than automatic — functionally similar in outcome but requires you to author the rules rather than opting into a black-box feature.

**Strong consistency is now universal**, but it wasn't always — S3 was eventually consistent for overwrite/delete until December 2020. This matters mainly for understanding older pipeline designs that added retry/reconciliation logic to work around it; new pipelines don't need to.

**Query-in-place ecosystem.** All three clouds support querying object storage directly (Athena/Redshift Spectrum on S3, BigQuery external tables/BigLake on GCS, Synapse serverless SQL on Blob Storage/ADLS Gen2), but GCP's BigQuery has the tightest, most transparent integration — a BigQuery external table over GCS behaves close to a native table. Azure typically pairs object storage with **ADLS Gen2** (Azure Data Lake Storage Gen2) rather than plain Blob Storage for analytics workloads — ADLS Gen2 is Blob Storage with a hierarchical namespace enabled, giving true directory semantics and better performance for big-data engines (Spark, Synapse) that expect POSIX-like paths.

---

## When to reach for it vs. alternatives

- Reach for object storage as the default landing/staging layer for any data lake or ETL pipeline — it's cheaper and more scalable than a database for raw files, and every processing engine in each cloud reads from it natively.
- Prefer querying data in place (Athena, BigQuery external tables, Synapse serverless) over loading into a warehouse when query volume is low/ad hoc — avoids both the load step and warehouse compute costs.
- Move to a warehouse (Redshift/BigQuery/Synapse dedicated pools) when you need fast, frequent, complex analytical queries with strong performance guarantees — object storage query-in-place is slower and less predictable than a warehouse's native storage format.
- On Azure specifically, use ADLS Gen2 rather than flat Blob Storage for analytics/data-lake use cases — enabling the hierarchical namespace is essentially free and unlocks the performance/semantics big-data tools expect.

---

## Resources

- [AWS S3 documentation](https://docs.aws.amazon.com/s3/)
- [GCP Cloud Storage documentation](https://cloud.google.com/storage/docs)
- [Azure Blob Storage documentation](https://learn.microsoft.com/en-us/azure/storage/blobs/)
- [Azure Data Lake Storage Gen2 overview](https://learn.microsoft.com/en-us/azure/storage/blobs/data-lake-storage-introduction)
