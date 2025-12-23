---
paths: src/api/**/*.ts, src/routes/**/*.ts
---

# API Standards

## Endpoint Naming
- [RESTful conventions, e.g., "Use nouns for resources: /users, /orders"]
- [URL patterns, e.g., "Use kebab-case for multi-word paths"]

## Request/Response
- [Format: JSON, etc.]
- [Error response structure, e.g., "{ error: string, code: string, details?: object }"]

## Authentication
- [How endpoints should handle auth, e.g., "All routes require Bearer token except /auth/*"]

## Documentation
- [OpenAPI/Swagger requirements, e.g., "All public endpoints must have JSDoc annotations"]
