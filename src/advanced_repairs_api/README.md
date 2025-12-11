# Módulo: Service Desk Copilot – Parte avanzada

Este módulo contiene el código y los ejemplos de los dos vídeos avanzados:

1. **Añadir `created_by` a los tickets usando el contexto del Copilot**  
2. **Proteger la API con una API Key e integrarla con un API plugin de Copilot**

---

## Vídeo 1 – Añadimos `created_by` usando el contexto de Copilot

En este vídeo partimos de la API de reparaciones que ya guardaba tickets en **Azure Cosmos DB** y la extendemos para que cada ticket tenga un campo `created_by`, de forma que:

- Podamos saber **qué usuario (o conversación)** creó cada ticket.
- Podamos filtrar reparaciones por usuario desde Copilot.
- El comportamiento sea más realista: cada persona ve “sus” tickets.

### Objetivos de aprendizaje

Al final del vídeo, el alumno será capaz de:

- Entender cómo aprovechar los **metadatos** que envía Copilot en las cabeceras HTTP (tenant, user, conversation…).
- Capturar un identificador de usuario/conversación en la API (`created_by`).
- Persistir este `created_by` en Cosmos DB junto con el resto de campos del ticket.
- Extender el endpoint de listado para filtrar por `created_by`.

### Archivos relevantes

- `src/repairs_api/main.py`
- `src/repairs_api/database.py`
- `src/repairs_api/openapi.yaml` (o `openapi.yml`, según el proyecto)

### Cambios principales

#### 1. Nuevo campo `created_by` en la capa de datos

En `database.py`:

- Añadimos el campo `created_by` al documento que guardamos en Cosmos.
- Permitimos filtrar por `created_by` en `list_repairs_from_db`.

Ejemplo conceptual:

```python
def create_repair_in_db(
    item: str,
    description: str,
    status: str = "New",
    assigned_to: Optional[str] = None,
    created_by: Optional[str] = None,
) -> Dict[str, Any]:
    doc = {
        "id": str(uuid4()),
        "item": item,
        "description": description,
        "status": status,
        "assigned_to": assigned_to,
        "created_at": datetime.utcnow().isoformat(),
        "created_by": created_by,
    }
    container.create_item(doc)
    return doc


def list_repairs_from_db(
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    created_by: Optional[str] = None,
) -> List[Dict[str, Any]]:
    # Construimos una query Cosmos sencilla con filtros opcionales
    # (la implementación concreta está en el código del vídeo)
    ...
