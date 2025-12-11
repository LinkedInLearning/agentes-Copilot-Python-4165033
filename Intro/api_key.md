## Marcar el API como protegido en OpenAPI

Para marcar el API como protegido en la especificación OpenAPI, debes agregar una sección de seguridad en el archivo OpenAPI (generalmente un archivo YAML o JSON). Aquí tienes un ejemplo de cómo hacerlo en YAML:

```yaml
components:
  securitySchemes:
    apiKey:
      type: http
      scheme: bearer
```
