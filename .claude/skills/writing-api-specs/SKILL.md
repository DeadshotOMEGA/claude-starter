---
name: writing-api-specs
description: Write OpenAPI/Swagger specifications and API documentation. Use when creating API specs, SDK docs, or interactive API documentation.
---

# Writing API Specifications

Create OpenAPI specifications and comprehensive API documentation.

## Purpose

API docs provide:
- Machine-readable API specifications
- Interactive documentation
- SDK generation source
- Contract definitions

## When to Use

- Creating new API endpoints
- Documenting existing APIs
- Generating client SDKs
- Setting up Swagger/OpenAPI UI

## OpenAPI 3.0 Structure

```yaml
openapi: 3.0.0
info:
  title: API Name
  version: 1.0.0
  description: API description

servers:
  - url: https://api.example.com/v1

paths:
  /resource:
    get:
      summary: Get resources
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Resource'

components:
  schemas:
    Resource:
      type: object
      properties:
        id:
          type: string
```

## Best Practices

### Complete Schemas
Define all request/response schemas in `components/schemas`.

### Include Examples
```yaml
examples:
  success:
    value:
      id: "123"
      name: "Example"
```

### Document Errors
```yaml
responses:
  '400':
    description: Bad Request
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
```

### Use Tags for Organization
```yaml
tags:
  - name: Users
    description: User management
  - name: Products
    description: Product operations
```

### Version Everything
Include version in URL path or header specification.

## Output Files

- `openapi.yaml` or `openapi.json` — Main specification
- `docs/api/` — Markdown documentation
- `postman/` — Postman collection (optional)

## Tools

- **Swagger UI**: Interactive docs from spec
- **Redoc**: Alternative documentation renderer
- **openapi-generator**: SDK generation
