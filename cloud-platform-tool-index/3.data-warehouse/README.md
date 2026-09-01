# Data Warehouse (OLAP)

## Overview

Data warehouses store and query large, structured/semi-structured datasets optimized for analytical (OLAP) workloads — columnar storage, heavy aggregation, and joins across billions of rows, rather than high-frequency single-row transactions. This is typically the end destination of a data engineering pipeline: the layer BI tools and analysts query directly.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Service | Redshift | BigQuery | Synapse Analytics (dedicated SQL pools) |
| Architecture | Provisioned clusters (leader + compute nodes), or Serverless | Fully serverless, no cluster management | Provisioned DWUs, or Synapse serverless SQL |
| Pricing model | Node-hours (RA3) or RPU-hours (Serverless) | Per-TB-scanned (on-demand) or slot capacity (flat-rate) | DWU-hours (dedicated) or per-TB (serverless) |
| Query-in-place on object storage | Redshift Spectrum (on S3) | Native — BigQuery is built on separated storage/compute | Synapse serverless SQL (on ADLS Gen2) |

---

## What it's for

- **BI and dashboarding backend** — the layer Looker, Tableau, Power BI, and similar tools query.
- **Large-scale aggregation and joins** — the kind of "scan billions of rows, group by five dimensions" query that would be slow or expensive against an OLTP database or raw object storage.
- **Curated, modeled data** — the destination of dbt/ELT transformation layers (staging → intermediate → marts).

---

## Key differences

**Serverless-first vs. cluster-first.** This is the biggest architectural divide. BigQuery has been fully serverless from the start — no clusters to size, pause, or resume; you just query, and Google handles the compute allocation behind the scenes. Redshift and Synapse both originated as provisioned-cluster products (you choose node types and counts, pay whether or not you're querying) and have since added serverless modes (Redshift Serverless, Synapse serverless SQL) to catch up — but the "default," most fully-featured experience on both is still the provisioned one, with serverless treated as an alternative deployment option rather than the native architecture.

**Storage/compute separation.** BigQuery separates storage and compute natively and always has — you're never paying for idle compute tied to stored data. Redshift's RA3 node type and Synapse's dedicated pools both separate storage from compute at the architecture level too, but the compute side is still something you provision and pay for continuously (or pause manually), unlike BigQuery's true pay-per-query model.

**Pricing shape changes the cost-optimization playbook.** BigQuery's on-demand pricing (per TB scanned) means query *design* — partitioning, clustering, avoiding `SELECT *` — directly drives cost per query, which is a different discipline than Redshift/Synapse's provisioned pricing, where cost is mostly about right-sizing and pausing clusters rather than individual query efficiency (though inefficient queries still cost you in slower response and contention). Teams on BigQuery often switch to flat-rate/capacity pricing once volume is high enough that per-query billing becomes unpredictable — this is analogous to switching from serverless to provisioned in the other direction.

**Query-in-place maturity.** Querying object storage directly without loading is native and seamless in BigQuery (external tables, or BigLake for governed access). Redshift Spectrum and Synapse serverless SQL both offer the same capability but as a distinctly separate mode bolted onto the warehouse, with some feature/performance gaps versus querying native warehouse tables.

---

## When to reach for it vs. alternatives

- Choose BigQuery-style serverless when workload is spiky/unpredictable and you don't want to manage cluster sizing — you pay only for what you scan/compute.
- Choose provisioned clusters (Redshift, Synapse dedicated) when workload is steady and high-volume enough that flat-rate/reserved pricing beats per-query billing, and you want predictable performance under concurrent load.
- Reach for query-in-place (Spectrum/BigQuery external tables/Synapse serverless) over loading into the warehouse when data is queried infrequently — skip the ETL load step entirely for low-frequency analytical access.

---

## Resources

- [AWS Redshift documentation](https://docs.aws.amazon.com/redshift/)
- [GCP BigQuery documentation](https://cloud.google.com/bigquery/docs)
- [Azure Synapse Analytics documentation](https://learn.microsoft.com/en-us/azure/synapse-analytics/)
