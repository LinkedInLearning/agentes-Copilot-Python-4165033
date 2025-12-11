"""Repair Service API (FastAPI + Cosmos DB)."""
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Optional

from fastapi import FastAPI, Query, Request, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from database import create_repair_in_db, list_repairs_from_db

app = FastAPI(
    title="Repair Service",
    description="A simple service to manage repair tickets for devices on behalf of users.",
    version="1.0.0",
    openapi_url="/openapi.json",
)

# --- API Key auth (para el API plugin de Copilot) ---
load_dotenv()

API_KEY = os.getenv("SECRET_API_KEY")

print(f"DEBUG: Loaded SECRET_API_KEY = {API_KEY}")

if API_KEY is None:
    # En un entorno real podrías usar logging, aquí hacemos un fallo explícito
    raise RuntimeError("SECRET_API_KEY no está configurada en las variables de entorno.")

def verify_api_key(authorization: str = Header(None)):
    """
    Verifica que la petición incluye un header:
      Authorization: Bearer <API_KEY_CORRECTA>
    """
    print (f"DEBUG: Verifying API key from Authorization header: {authorization}")
    
    if not authorization:
        # Falta la cabecera Authorization
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        # El formato no es Bearer ...
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[len(prefix):].strip()

    if token != API_KEY:
        # Token incorrecto
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Si todo va bien, no devolvemos nada, simplemente dejamos pasar la request
    return True


# ---------- Models ----------


class RepairBase(BaseModel):
    """Base model for a repair ticket."""
    item: str = Field(
        ...,
        description="Name or type of the item that needs repair, for example 'Laptop' or 'Printer'.",
    )
    description: str = Field(
        ...,
        description="Short description of the issue reported by the customer.",
    )
    status: str = Field(
        "New",
        description="Current status of the repair, such as 'New', 'In Progress', or 'Completed'.",
    )
    assigned_to: Optional[str] = Field(
        None,
        description="Name of the person or team that this repair is assigned to.",
    )


class Repair(RepairBase):
    """Model representing a repair ticket with all details."""
    id: str = Field(
        ...,
        description="Unique identifier of the repair ticket.",
    )
    created_at: datetime = Field(
        ...,
        description="Date and time when the repair ticket was created (UTC).",
    )
    created_by: Optional[str] = Field(
        None,
        description="Identifier of who created this ticket (tenant ID and/or conversation ID).",
    )


class RepairCreate(RepairBase):
    """Payload for creating a new repair ticket from Copilot."""
    # deliberately no created_by here; we compute it on the server side


# ---------- Endpoints ----------


@app.get(
    "/repairs",
    response_model=List[Repair],
    operation_id="listRepairs",
    summary="List all repairs",
    description=(
        "Returns a list of repair tickets with their details. "
        "You can optionally filter by status, assigned_to, or created_by."
    ),
    dependencies=[Depends(verify_api_key)],
)
async def list_repairs(
    status: Optional[str] = Query(
        None,
        description="Optional status to filter repairs by. Example: 'New' or 'Completed'.",
    ),
    assigned_to: Optional[str] = Query(
        None,
        description="Optional name or ID of the person or team the repair is assigned to.",
    ),
    created_by: Optional[str] = Query(
        None,
        description=(
            "Optional identifier of who created the ticket "
            "(for example the tenant ID or tenant|conversation)."
        ),
    ),
) -> List[Repair]:
    """
    List all repairs, optionally filtered by status, assigned_to and created_by.
    Data is retrieved from Azure Cosmos DB.
    """
    rows = list_repairs_from_db(
        status=status,
        assigned_to=assigned_to,
        created_by=created_by,
    )

    # Pydantic se encarga de convertir created_at (string ISO) a datetime
    return [Repair(**row) for row in rows]


@app.post(
    "/repairs",
    response_model=Repair,
    status_code=201,
    operation_id="createRepair",
    summary="Create a new repair",
    description="Create a new repair ticket for a device that needs to be fixed.",
    dependencies=[Depends(verify_api_key)],
)
async def create_repair(payload: RepairCreate, request: Request) -> Repair:
    """
    Create a new repair ticket.

    Enriches the ticket with 'created_by' using Microsoft 365 Copilot context headers:
    - x-microsoft-tenantid
    - x-microsoft-ai-conversationid
    """
    headers = request.headers

    tenant_id = headers.get("x-microsoft-tenantid")
    conversation_id = headers.get("x-microsoft-ai-conversationid")

    # Construimos un identificador simple de quién creó el ticket
    if tenant_id and conversation_id:
        created_by = f"{tenant_id}|{conversation_id}"
    elif tenant_id:
        created_by = tenant_id
    else:
        created_by = "unknown"  # útil en pruebas locales o llamadas directas sin Copilot

    # Guardar en Cosmos DB
    data = create_repair_in_db(
        item=payload.item,
        description=payload.description,
        status=payload.status,
        assigned_to=payload.assigned_to,
        created_by=created_by,
    )

    # Devolver el modelo completo a Copilot
    return Repair(**data)
