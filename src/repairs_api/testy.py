"""Repair Service API (con Cosmos DB)"""
from typing import List, Optional

from datetime import datetime
from fastapi import FastAPI, Query, Request
from pydantic import BaseModel, Field

from database import create_repair_in_db, list_repairs_from_db

app = FastAPI(
    title="Repair Service",
    description=(
        "A simple service to manage repair tickets for devices on behalf of users."
    ),
    version="1.0.0",
    openapi_url="/openapi.json",
)

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


class RepairCreate(RepairBase):
    """Payload for creating a new repair ticket."""

# ---------- Endpoints ----------
@app.post(
    "/repairs",
    response_model=Repair,
    status_code=201,
    operation_id="createRepair",
    summary="Create a new repair",
    description="Create a new repair ticket for a device that needs to be fixed.",
)
async def create_repair(payload: RepairCreate, request: Request) -> Repair:
    """
    Create a new repair ticket. Enriches the ticket with 'created_by'
    using Microsoft 365 Copilot context headers.
    """

    # 1. Leer cabeceras que envía Copilot al plugin
    headers = request.headers

    tenant_id = headers.get("x-microsoft-tenantid")
    conversation_id = headers.get("x-microsoft-ai-conversationid")
    print ("Headers received:", headers)
    print("Tenant ID:", tenant_id)
    print("Conversation ID:", conversation_id)

    created_by = f"{tenant_id}|{conversation_id}"

    # 3. Llamar a nuestra capa de datos (Cosmos DB) pasando created_by
    data = create_repair_in_db(
        item=payload.item,
        description=payload.description,
        status=payload.status,
        assigned_to=payload.assigned_to,
        created_by=created_by,
    )

    # 4. Devolver el modelo Pydantic completo a Copilot
    return Repair(**data)