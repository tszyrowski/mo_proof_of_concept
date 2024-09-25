# SQLite to Oracle DB Synchronization

S mechanism between a local SQLite database (`inspection_data.db`)  
and an Oracle database as centralised DB. 

Tracks synchronization history using the `sync_metadata` table in Oracle  
to ensure only new or modified records are transferred.

## Key Points:
1. **Sync Metadata**: The last sync time is stored in Oracle to ensure efficient and accurate syncing.
2. **Extensibility**: Easily add more tables to the synchronization process.
3. **Idempotent Design**: The `MERGE` query ensures that records are only updated or inserted as necessary, preventing duplicate entries.

Provides a foundation for syncing between SQLite and Oracle,  
Changes in SQLite are reflected in Oracle by `sync_layer/sync_db.py` script invocation.
