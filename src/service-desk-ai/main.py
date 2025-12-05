"""Repair Service API"""
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="Repair Service",
    description=(
        "A simple service to manage repair tickets for devices on behalf of users."
    ),
    version="1.0.0",
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
# In-memory "database" for demo purposes
repairs_db: List[Repair] = []

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
    results = repairs_db
    if status:
        results = [r for r in results if r.status.lower() == status.lower()]
    if assigned_to:
        results = [
            r for r in results
            if r.assigned_to and assigned_to.lower() in r.assigned_to.lower()
        ]
    return results

@app.get(
    "/repairs/{repair_id}",
    response_model=Repair, 
    operation_id="getRepairById",
    summary="Get a single repair",
    description="Get the full details of a repair ticket by its unique identifier.",
)
def get_repair_by_id(repair_id: str) -> Repair:
    """Get a single repair by its ID."""
    for repair in repairs_db:
        if repair.id == repair_id:
            return repair
    raise HTTPException(status_code=404, detail="Repair not found")

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
    repair = Repair(
        id=str(uuid4()),
        created_at=datetime.utcnow(),
        **payload.model_dump(),
    )
    repairs_db.append(repair)
    return repair
