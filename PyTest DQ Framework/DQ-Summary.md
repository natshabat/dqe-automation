Issues Identified
- Row count mismatch:
 - Source: 34,894 rows
 - Target: 43,622 rows
- Duplicate records in target dataset:
 - 8,728 duplicates detected
- Aggregation mismatch:
 - Source grouped by `facility_id`, `facility_name`, `visit_date`
 - Target dataset had inconsistent grouping, causing duplicates
---
 Actions Taken
- Aligned aggregation logic with source query
- Ensured correct grouping fields are used
- Revalidated target dataset
---
 Final Result
- Row counts match
- No duplicates
- Data transformation is consistent