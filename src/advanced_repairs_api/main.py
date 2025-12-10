"""Repair Service API (con Cosmos DB)"""
from typing import List, Optional

from datetime import datetime
from fastapi import FastAPI, Query
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

@app.get(
    "/repairs",
    response_model=List[Repair],
    operation_id="listRepairs",
    summary="List all repairs",
    description=(
        "Returns a list of repair tickets with their details. "
        "You can optionally filter by status or by who the repair is assigned to."
    ),
)
def list_repairs(
    status: Optional[str] = Query(
        None,
        description="Optional status to filter repairs by. Example: 'New' or 'Completed'.",
    ),
    assigned_to: Optional[str] = Query(
        None,
        description="Optional name or ID of the person or team the repair is assigned to.",
    ),
) -> List[Repair]:
    """List all repairs, optionally filtered by status or assigned_to."""
    # Ahora leemos directamente desde Cosmos DB
    repairs = list_repairs_from_db(status=status, assigned_to=assigned_to)
    # FastAPI usará el response_model=List[Repair] para validar/parsear los dicts
    return repairs


@app.post(
    "/repairs",
    response_model=Repair,
    status_code=201,
    operation_id="createRepair",
    summary="Create a new repair",
    description="Create a new repair ticket for a device that needs to be fixed.",
)
def create_repair(payload: RepairCreate) -> Repair:
    """Create a new repair ticket."""
    # Ahora delegamos en Cosmos DB
    repair = create_repair_in_db(
        item=payload.item,
        description=payload.description,
        status=payload.status,
        assigned_to=payload.assigned_to,
    )
    return repair