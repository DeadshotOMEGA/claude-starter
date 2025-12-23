---
name: configuring-mcp-servers
description: MCP server configuration templates, patterns, and integration examples for Claude Code. Use when creating MCP configurations, setting up MCP servers, or integrating external services via Model Context Protocol.
---

# Configuring MCP Servers

MCP (Model Context Protocol) configuration templates and patterns for Claude Code integrations.

## Standard MCP Configuration Format

```json
{
  "mcpServers": {
    "ServiceName MCP": {
      "command": "npx",
      "args": [
        "-y",
        "package-name@latest",
        "additional-args"
      ],
      "env": {
        "API_KEY": "required-env-var",
        "BASE_URL": "optional-base-url"
      }
    }
  }
}
```

## MCP Server Types

### 1. API Integration MCPs
- REST API connectors (GitHub, Stripe, Slack, etc.)
- GraphQL API integrations
- Database connectors (PostgreSQL, MySQL, MongoDB)
- Cloud service integrations (AWS, GCP, Azure)

### 2. Development Tool MCPs
- Code analysis and linting integrations
- Build system connectors
- Testing framework integrations
- CI/CD pipeline connectors

### 3. Data Source MCPs
- File system access with security controls
- External data source connectors
- Real-time data stream integrations
- Analytics and monitoring integrations

## Common MCP Patterns

### Database MCP Template

```json
{
  "mcpServers": {
    "PostgreSQL MCP": {
      "command": "npx",
      "args": [
        "-y",
        "postgresql-mcp@latest"
      ],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
        "MAX_CONNECTIONS": "10",
        "CONNECTION_TIMEOUT": "30000",
        "ENABLE_SSL": "true"
      }
    }
  }
}
```

### API Integration MCP Template

```json
{
  "mcpServers": {
    "GitHub Integration MCP": {
      "command": "npx",
      "args": [
        "-y",
        "github-mcp@latest"
      ],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here",
        "GITHUB_API_URL": "https://api.github.com",
        "RATE_LIMIT_REQUESTS": "5000",
        "RATE_LIMIT_WINDOW": "3600"
      }
    }
  }
}
```

### File System MCP Template

```json
{
  "mcpServers": {
    "Secure File Access MCP": {
      "command": "npx",
      "args": [
        "-y",
        "filesystem-mcp@latest"
      ],
      "env": {
        "ALLOWED_PATHS": "/home/user/projects,/tmp",
        "MAX_FILE_SIZE": "10485760",
        "ALLOWED_EXTENSIONS": ".js,.ts,.json,.md,.txt",
        "ENABLE_WRITE": "false"
      }
    }
  }
}
```

## MCP Naming Conventions

### File Naming
- Use lowercase with hyphens: `service-name-integration.json`
- Include service and integration type: `postgresql-database.json`
- Be descriptive and consistent: `github-repo-management.json`

### MCP Server Names
- Use clear, descriptive names: "GitHub Repository MCP"
- Include service and purpose: "PostgreSQL Database MCP"
- Maintain consistency: "[Service] [Purpose] MCP"

## Testing and Validation

### MCP Configuration Testing
1. Validate JSON syntax and structure
2. Test environment variable requirements
3. Verify authentication and connection
4. Test error handling and edge cases
5. Validate performance under load

### Integration Testing
1. Test with Claude Code CLI
2. Verify component installation process
3. Test environment variable handling
4. Validate security constraints
5. Test cross-platform compatibility

## MCP Creation Workflow

### 1. Create the MCP File

**Location**: Always create new MCPs in `cli-tool/components/mcps/`
**Naming**: Use kebab-case: `service-integration.json`
**Format**: Follow exact JSON structure with `mcpServers` key

Example:
```bash
/cli-tool/components/mcps/stripe-integration.json
```

### 2. Content Structure

```json
{
  "mcpServers": {
    "Stripe Integration MCP": {
      "command": "npx",
      "args": [
        "-y",
        "stripe-mcp@latest"
      ],
      "env": {
        "STRIPE_SECRET_KEY": "sk_test_your_key_here",
        "STRIPE_WEBHOOK_SECRET": "whsec_your_webhook_secret",
        "STRIPE_API_VERSION": "2023-10-16"
      }
    }
  }
}
```

### 3. Installation Command

After creating the MCP, users can install it with:
```bash
npx claude-code-templates@latest --mcp="stripe-integration" --yes
```

This will:
- Read from `cli-tool/components/mcps/stripe-integration.json`
- Merge the configuration into the user's `.mcp.json` file
- Enable the MCP server for Claude Code

### 4. Testing Workflow

1. Create the MCP file in correct location
2. Test the installation command
3. Verify the MCP server configuration works
4. Document any required environment variables
5. Test error handling and edge cases

## Security Best Practices

- Use environment variables for sensitive data
- Implement proper token rotation where applicable
- Add rate limiting and request throttling
- Validate all inputs and responses
- Log security events appropriately

## Performance Optimization

- Implement connection pooling for database MCPs
- Add caching layers where appropriate
- Optimize batch operations
- Handle large datasets efficiently
- Monitor resource usage

## Complete Example: Stripe Integration

```json
{
  "mcpServers": {
    "Stripe Integration MCP": {
      "command": "npx",
      "args": [
        "-y",
        "stripe-mcp@latest"
      ],
      "env": {
        "STRIPE_SECRET_KEY": "sk_test_your_key_here",
        "STRIPE_WEBHOOK_SECRET": "whsec_your_webhook_secret",
        "STRIPE_API_VERSION": "2023-10-16",
        "STRIPE_MAX_RETRIES": "3",
        "STRIPE_TIMEOUT": "30000"
      }
    }
  }
}
```

**Environment Variables:**
- `STRIPE_SECRET_KEY`: Your Stripe secret API key (required)
- `STRIPE_WEBHOOK_SECRET`: Webhook signing secret for event verification
- `STRIPE_API_VERSION`: Stripe API version to use
- `STRIPE_MAX_RETRIES`: Maximum retry attempts for failed requests
- `STRIPE_TIMEOUT`: Request timeout in milliseconds
