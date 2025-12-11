"""database.py using Cosmos DB"""
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey

load_dotenv()

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE", "db-servicedesk")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "repairs")

if not COSMOS_ENDPOINT or not COSMOS_KEY:
    raise RuntimeError("Missing COSMOS_ENDPOINT or COSMOS_KEY env vars")

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

# Ensure DB & container exist (safe if already created)
database = client.create_database_if_not_exists(id=COSMOS_DATABASE)
container = database.create_container_if_not_exists(
    id=COSMOS_CONTAINER,
    partition_key=PartitionKey(path="/id"),
)

def create_repair_in_db(
    item: str,
    description: str,
    status: str = "New",
    assigned_to: Optional[str] = None,
    created_by: Optional[str] = None,
) -> Dict[str, Any]:
    repair_id = str(uuid4())
    created_at = datetime.utcnow().isoformat() + "Z"

    doc = {
        "id": repair_id,
        "item": item,
        "description": description,
        "status": status,
        "assigned_to": assigned_to,
        "created_at": created_at,
        "created_by": created_by
    }

    container.create_item(body=doc)
    return doc

def list_repairs_from_db(
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    query = "SELECT * FROM c"
    params = []

    if status and assigned_to:
        query += " WHERE c.status = @status AND CONTAINS(c.assigned_to, @assigned_to)"
        params = [
            {"name": "@status", "value": status},
            {"name": "@assigned_to", "value": assigned_to},
        ]
    elif status:
        query += " WHERE c.status = @status"
        params = [{"name": "@status", "value": status}]
    elif assigned_to:
        query += " WHERE CONTAINS(c.assigned_to, @assigned_to)"
        params = [{"name": "@assigned_to", "value": assigned_to}]

    items = container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True,
    )
    return list(items)

if __name__ == "__main__":
    print("Testing Cosmos connection & insert...")
    r = create_repair_in_db(
        item="Laptop",
        description="Screen is flickering",
        assigned_to="Jane Doe",
    )
    print("Inserted:", r)
    print("All repairs:", list_repairs_from_db())
