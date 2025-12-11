# Agent debug info:

* X-Microsoft-AI-ConversationId

* X-Microsoft-TenantID

* X-Microsoft-AI-UserLocale

* X-Microsoft-AI-UserTimeZone

### Models

```python
class RepairBase(BaseModel):
    item: str
    description: str
    status: str = "New"
    assigned_to: Optional[str] = None

class Repair(RepairBase):
    id: str
    created_at: datetime

class RepairCreate(RepairBase):
    """Payload for creating a new repair ticket."""
```

### Endpoints

```python

from fastapi import FastAPI, Query
# ...

@app.post(
    "/repairs",
    response_model=Repair,
    status_code=201,
    operation_id="createRepair",
)
def create_repair(payload: RepairCreate) -> Repair:
    repair = Repair(
        id=str(uuid4()),
        created_at=datetime.utcnow(),
        **payload.model_dump(),
    )
    repairs_db.append(repair)
    return repair
```

### Database 

```python
def create_repair_in_db(
    item: str,
    description: str,
    status: str = "New",
    assigned_to: Optional[str] = None,
) -> Dict[str, Any]:
    repair_id = str(uuid4())
    created_at = datetime.utcnow().isoformat()

    doc = {
        "id": repair_id,
        "item": item,
        "description": description,
        "status": status,
        "assigned_to": assigned_to,
        "created_at": created_at,
    }

    container.create_item(doc)
    return doc
```