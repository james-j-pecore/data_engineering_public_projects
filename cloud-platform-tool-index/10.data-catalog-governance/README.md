# Data Catalog & Governance

## Overview

Services for discovering, cataloging, classifying, and governing access to data assets spread across storage, warehouses, and databases — answering "what data do we have, what's in it, who can access it, and where did it come from" at an organizational level.

---

## Comparison table

| | AWS | GCP | Azure |
|---|---|---|---|
| Metastore/catalog | Glue Data Catalog | Dataplex (incorporates Data Catalog) | Microsoft Purview |
| Fine-grained access governance | Lake Formation (separate service) | Dataplex (integrated) | Purview (integrated) |
| Scope | Primarily AWS-internal metastore for analytics services | Data lake/mesh management: discovery, quality, lineage | Enterprise-wide: Azure + on-prem + multi-cloud sources |
| Primary positioning | Technical metastore first, governance as an add-on | Data management platform | Governance-first platform |

---

## What it's for

- **Schema/metadata discovery** — knowing what tables, columns, and file formats exist across storage and warehouses without manually inspecting each source.
- **Fine-grained access control on data** — restricting which users/roles can see which tables, columns, or rows, layered on top of general IAM.
- **Data lineage and classification** — tracking where data came from, how it's transformed, and flagging sensitive data (PII, financial data) automatically.

---

## Key differences

**AWS splits metastore and governance into two separate services**, where GCP and Azure each consolidate into one. Glue Data Catalog is primarily a technical metastore (Hive-metastore-compatible) that Athena, Redshift Spectrum, and EMR all read from directly for schema information — it's not primarily a governance tool. Fine-grained permissions (table/column/row-level access control on top of the catalog) live in a separate service, **Lake Formation**, which you set up in addition to Glue if you need governance beyond basic IAM. This two-service split is a meaningful setup difference versus GCP and Azure's more unified products.

**GCP consolidated its offering into Dataplex**, which absorbed what used to be a separate Data Catalog product and now spans discovery, metadata management, data quality checks, and lineage as one integrated "data mesh/lake management" platform — positioned less as a passive metastore and more as an active data management layer with quality and organizational (domain/zone) concepts built in.

**Purview is the most governance-first and broadest in scope of the three.** Rather than being scoped primarily to the cloud provider's own analytics services, Purview is built to scan and classify data across Azure, on-premises systems, and even other clouds (AWS S3, for instance) — positioning it as an enterprise data governance platform rather than a metastore for Azure-native tools specifically. Its classification engine (automatic PII/sensitive-data detection) and lineage tracking are generally considered the most mature of the three out of the box.

---

## When to reach for it vs. alternatives

- On AWS, set up Lake Formation alongside Glue Data Catalog from the start if you anticipate needing fine-grained (column/row-level) access control — retrofitting it later means reworking access patterns already built around plain IAM.
- Reach for Dataplex on GCP when you want data quality and lineage tracking bundled with cataloging, not just schema discovery.
- Reach for Purview specifically when governance needs to span beyond one cloud provider — its multi-cloud/on-prem scanning is a genuine differentiator if your data estate isn't Azure-only.

---

## Resources

- [AWS Glue Data Catalog documentation](https://docs.aws.amazon.com/glue/latest/dg/catalog-and-crawler.html) · [Lake Formation documentation](https://docs.aws.amazon.com/lake-formation/)
- [GCP Dataplex documentation](https://cloud.google.com/dataplex/docs)
- [Microsoft Purview documentation](https://learn.microsoft.com/en-us/purview/)
