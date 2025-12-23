# Security Guidelines

<!--
  Note: This rule has no `paths` frontmatter because security applies globally.
  Add path scoping if you want security rules for specific areas only.
-->

## Sensitive Data
- Never commit: [.env, credentials.json, *.pem, *.key]
- Use environment variables for: [API keys, database credentials, secrets]

## Authentication
- [Auth patterns used in project, e.g., "JWT tokens with short expiry"]
- [Session management approach]

## Input Validation
- [Validation approach, e.g., "Validate all inputs at API boundaries using Zod"]
- [Sanitization requirements for user content]

## Dependencies
- [How to handle security updates, e.g., "Run `npm audit` weekly"]
- [Approved dependency sources]
