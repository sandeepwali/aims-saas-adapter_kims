# AIMS SaaS Adapater for kims in Python

Features

- CSV Processing: Reads CSVs from data/input, validates rows, hashes content, updates SQLite DB.
- 
- Syncing with AIMS SaaS: Sends pending articles from DB to the AIMS platform. Handles retries and logs failures.
- 
- Error Handling: Invalid CSVs or failed syncs are moved to data/failed for review.
- 
- Maintenance: Optional automated cleanup of old ZIPs and daily tasks.

Workflow

- CSV arrives in data/input.
- 
- CSV processed → DB updated → article data sent to AIMS SaaS.
- 
- Failures logged and CSV moved to failed.
- 
- Maintenance tasks run daily for zipping.
