"""database.py - Acceso a datos para la Repair API usando Azure Cosmos DB."""
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from azure.cosmos import CosmosClient, exceptions

# Cargar variables de entorno en local (.env)
load_dotenv()

COSMOS_URL = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB_NAME = os.getenv("COSMOS_DATABASE")
COSMOS_CONTAINER_NAME = os.getenv("COSMOS_CONTAINER", "Repairs")

if not all([COSMOS_URL, COSMOS_KEY, COSMOS_DB_NAME]):
    raise RuntimeError(
        "Missing one or more Cosmos env variables. "
        "Make sure COSMOS_URL, COSMOS_KEY and COSMOS_DB_NAME are set."
    )

# Crear cliente de Cosmos y obtener referencias a DB y contenedor
try:
    client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
    database = client.get_database_client(COSMOS_DB_NAME)
    container = database.get_container_client(COSMOS_CONTAINER_NAME)
except exceptions.CosmosHttpResponseError as e:
    raise RuntimeError(f"Error connecting to Cosmos DB: {e}") from e


def create_repair_in_db(
    item: str,
    description: str,
    status: str = "New",
    assigned_to: Optional[str] = None,
    created_by: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Inserta un ticket de reparación en Cosmos DB y devuelve el documento como dict.

    Campos:
    - id: GUID generado por la API
    - item, description, status, assigned_to: datos funcionales
    - created_at: timestamp UTC ISO-8601
    - created_by: identificador de quién crea el ticket (tenant|conversation, etc.)
    """
    from uuid import uuid4

    repair_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    doc: Dict[str, Any] = {
        "id": repair_id,
        "item": item,
        "description": description,
        "status": status,
        "assigned_to": assigned_to,
        "created_at": created_at,
        "created_by": created_by,
    }

    container.create_item(doc)
    return doc


def list_repairs_from_db(
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    created_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Devuelve una lista de tickets desde Cosmos DB, con filtros opcionales:

    - status: filtra por estado exacto (New, In Progress, Completed, etc.)
    - assigned_to: hace un CONTAINS sobre el campo assigned_to (case-insensitive).
    - created_by: filtra por el identificador guardado (tenant o tenant|conversation).
    """
    query = """
        SELECT c.id, c.item, c.description, c.status,
               c.assigned_to, c.created_at, c.created_by
        FROM c
        WHERE 1 = 1
    """
    parameters: List[Dict[str, Any]] = []

    if status:
        query += " AND c.status = @status"
        parameters.append({"name": "@status", "value": status})

    if assigned_to:
        # CONTAINS, case-insensitive (tercer parámetro = true)
        query += " AND IS_DEFINED(c.assigned_to) " \
                 "AND CONTAINS(c.assigned_to, @assigned_to, true)"
        parameters.append({"name": "@assigned_to", "value": assigned_to})

    if created_by:
        query += " AND c.created_by = @created_by"
        parameters.append({"name": "@created_by", "value": created_by})

    items = list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )

    # items ya es una lista de dicts
    return items


if __name__ == "__main__":
    # Pequeño test manual para validar conexión
    print("Testing DB connection and insert...")
    sample = create_repair_in_db(
        item="Test device",
        description="Just a test ticket from database.py __main__",
        status="New",
        assigned_to="Demo User",
        created_by="local-test",
    )
    print("Inserted document:")
    print(sample)

    repairs = list_repairs_from_db()
    print(f"Total repairs in DB: {len(repairs)}")
