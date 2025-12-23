---
name: writing-api-endpoints
description: Write documentation for individual API endpoints. Use when documenting REST API endpoints or server actions.
---

# API Endpoint Documentation Writing

Create documentation for individual API endpoints.

## Purpose

Endpoint docs provide:
- Request/response specifications
- Authentication requirements
- Error handling
- Usage examples

## Template

Use `template.md` in this Skill directory.

## Required Sections

1. **Overview** — What the endpoint does
2. **Endpoint Details** — Path, method, auth, rate limiting
3. **Request** — Headers, parameters, body schema, example
4. **Response** — Success and error responses
5. **Implementation Files** — Handler, service, repository
6. **Usage Examples** — Client-side and server action alternatives

## Request Documentation Format

```markdown
### Headers
```http
Content-Type: application/json
Authorization: Bearer [token]
```

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | string | Yes | Resource identifier |

### Body Schema
```typescript
interface RequestBody {
  field: string;
  optionalField?: number;
}
```
```

## Response Documentation Format

```markdown
### Success (200 OK)
```typescript
interface Response {
  id: string;
  data: object;
}
```

### Errors
| Status | Description | Response |
|--------|-------------|----------|
| 400 | Bad Request | `{ error: "Invalid input" }` |
| 401 | Unauthorized | `{ error: "Auth required" }` |
```

## Best Practices

- Include working curl examples
- Document all error cases
- Show TypeScript types for schemas
- Link to implementation files
- Include rate limiting if applicable
