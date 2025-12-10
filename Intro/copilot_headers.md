# Agent debug info:

* X-Microsoft-AI-ConversationId

* X-Microsoft-TenantID

* X-Microsoft-AI-UserLocale

* X-Microsoft-AI-UserTimeZone

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