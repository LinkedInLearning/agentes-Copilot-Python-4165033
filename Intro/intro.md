## Arquitectura de Copilot Agents

### Vista general

| User interface                    | Agent Store                                           | Tool and knowledge                                                                 |
| --------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------------- |
| - M365 Copilot App               | - Pre-build Agent                                     | - SharePoint                                                                       |
| - Microsoft Teams                | - Declarative Agent                                   | - Microsoft Search / Indexadores                                                   |
|                                   | - Custom Engine Agent                                 | - Bases de datos (SQL, etc.)                                                       |
|                                   |                                                       | - Azure Functions / APIs internos                                                  |
|                                   |                                                       | - Otros orígenes de datos empresariales                                            |

---

### Flujos principales

- **Interfaz de usuario → Agentes**
  - M365 Copilot App → *Declarative Agent*  
  - Microsoft Teams → *Declarative Agent*

- **Agentes → Herramientas y datos**
  - *Declarative Agent* → **Connector** →  
    → SharePoint, buscadores, bases de datos, APIs, etc.
  - *Custom Engine Agent* → **Bot Service / AI Agent** → **Models**

---

### Developer tools

| Developer tools |
| --------------- |
| Copilot Studio · Microsoft 365 Agents SDK · Visual Studio Code|


---

## Declarative agent

- Instructions
- Knowledge (M365 + Connectors)
- Actions (plugins / APIs)
- Orchestrator & models de Copilot
- App package: app manifest, agent manifest




App Manifest:

```json
"copilotAgents": {
  "declarativeAgents": [            
    {
      "id": "declarativeAgent",
      "file": "declarativeAgent.json"
    }
  ]
},
```

Declarative agent manifest:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/copilot/declarative-agent/v1.3/schema.json",
  "version": "v1.3",
  "name": "ddb-test-declarative-agent",
  "description": "Test Declarative agent",
  "instructions": "You are a declarative agent and were. You should start every response and answer to the user with \"Thanks for using the test declarative agent!\\n\\n\" and then answer the questions and help the user."
}
```

---

### Flujo:
1. Usuario elige el agente declarativo
2. Usuario lanza petición para el agente
3. Copilot elige acción (OpenAPI)
4. Llama a tu API
5. Devuelve respuesta (texto / Adaptive Card)

---

### OpenAPI para Copilot:
- Operaciones pequeñas y claras
- Parámetros bien tipados y descritos
- Ejemplos realistas
- Respuestas con datos + texto / tarjetas
- No hay orquestación compleja en el agente
