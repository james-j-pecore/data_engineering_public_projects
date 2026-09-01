# Relational Database (OLTP)

## Overview

Managed relational databases handle transactional (OLTP) workloads — the operational data stores behind applications, where data engineers usually show up as the *source system* to extract from (via CDC or batch pulls) rather than the primary user. Understanding what's underneath matters for designing extraction pipelines, especially around replication and CDC support.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Standard managed DB | RDS (Postgres, MySQL, MariaDB, Oracle, SQL Server) | Cloud SQL (Postgres, MySQL, SQL Server) | Azure Database for PostgreSQL / MySQL |
| Cloud-native high-performance variant | Aurora (Postgres/MySQL-compatible) | AlloyDB (Postgres-compatible) | Azure SQL Database (PaaS, SQL Server-based) |
| Serverless option | Aurora Serverless v2 | — (AlloyDB has some elasticity, not true serverless) | Azure SQL Database Serverless tier |

---

## What it's for

- **Application backends** — the OLTP store behind a product, where rows are inserted/updated/deleted continuously.
- **CDC source for pipelines** — most warehouse-ingestion pipelines extract from here via change data capture (Debezium, DMS, Datastream) rather than direct batch queries, to avoid load on the production database.
- **Reference/dimension data** — smaller, relationally-modeled datasets (customers, products, config) that get joined into larger pipelines.

---

## Key differences

**Two-tier product lineup on AWS and GCP, but not on Azure.** Both AWS and GCP offer a "vanilla" managed database (RDS, Cloud SQL) alongside a proprietary, higher-performance variant (Aurora, AlloyDB) that rearchitects the storage layer for better throughput and HA while staying wire-compatible with Postgres/MySQL. Azure's structure is different: **Azure SQL Database** is a PaaS product built specifically around the SQL Server engine (not a generic "better Postgres"), while Postgres and MySQL live in their own separate, less deeply-integrated "Azure Database for X" services. If your workload is SQL Server, Azure's PaaS offering is arguably the most mature of the three; if it's Postgres/MySQL, AWS and GCP's cloud-native variants (Aurora, AlloyDB) currently outpace Azure's equivalents on performance engineering.

**Storage architecture.** Aurora and AlloyDB both decouple compute from a distributed, log-structured storage layer (Aurora replicates 6 ways across 3 AZs; AlloyDB separates transactional and analytical storage internally for fast analytical queries on operational data). Standard RDS/Cloud SQL/Azure Database use a more conventional attached-storage model, which is simpler but has lower ceiling throughput and failover speed.

**CDC support varies.** AWS RDS/Aurora has first-class integration with AWS DMS (Database Migration Service) for CDC. GCP's equivalent is Datastream, which supports Cloud SQL, AlloyDB, and also on-prem/other-cloud sources. Azure's native CDC tooling is comparatively thinner — many Azure-based pipelines lean on Debezium (open source, cloud-agnostic) rather than a first-party Azure CDC service, or use Azure Data Factory's change tracking features which are less general-purpose than DMS/Datastream.

---

## When to reach for it vs. alternatives

- Use the cloud-native variant (Aurora/AlloyDB) over the standard managed offering when you need higher write throughput, faster failover, or (for AlloyDB specifically) fast analytical queries directly against operational data without a separate warehouse hop.
- Use CDC (DMS/Datastream/Debezium) rather than repeated batch `SELECT` extraction when the source database is a live production system — batch polling adds load and misses deletes/updates between polls.
- Don't use an OLTP database as a substitute for a warehouse — row-oriented storage and transaction-optimized indexes make large analytical scans slow and expensive compared to a columnar warehouse.

---

## Resources

- [AWS RDS documentation](https://docs.aws.amazon.com/rds/) · [Aurora documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/)
- [GCP Cloud SQL documentation](https://cloud.google.com/sql/docs) · [AlloyDB documentation](https://cloud.google.com/alloydb/docs)
- [Azure SQL Database documentation](https://learn.microsoft.com/en-us/azure/azure-sql/database/) · [Azure Database for PostgreSQL](https://learn.microsoft.com/en-us/azure/postgresql/)
