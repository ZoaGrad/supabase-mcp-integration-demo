# Supabase MCP Connector API Reference

This document provides comprehensive documentation for all available tools in the Supabase MCP connector, organized by functional category.

## Table of Contents

- [Authentication](#authentication)
- [Documentation & Search](#documentation--search)
- [Organization Management](#organization-management)
- [Project Management](#project-management)
- [Database Operations](#database-operations)
- [Development Workflow](#development-workflow)
- [Edge Functions](#edge-functions)
- [Monitoring & Security](#monitoring--security)
- [Cost Management](#cost-management)

## Authentication

The Supabase MCP connector requires authentication via a platform access token. Set the `SUPABASE_ACCESS_TOKEN` environment variable before using any authenticated endpoints.

```bash
export SUPABASE_ACCESS_TOKEN="your_access_token_here"
```

## Documentation & Search

### search_docs

Search the Supabase documentation using GraphQL queries.

**Input Parameters:**
- `graphql_query` (string, required): Valid GraphQL query string

**Example Usage:**
```python
result = client._run_command("search_docs", {
    "graphql_query": """
    {
        searchDocs(query: "database tables", limit: 5) {
            nodes {
                title
                href
                content
            }
        }
    }
    """
})
```

**Response Format:**
```json
{
    "searchDocs": {
        "nodes": [
            {
                "title": "Tables and Data",
                "href": "https://supabase.com/docs/guides/database/tables",
                "content": "Tables are where you store your data..."
            }
        ]
    }
}
```

## Organization Management

### list_organizations

Lists all organizations that the user is a member of.

**Input Parameters:** None

**Example Usage:**
```python
result = client._run_command("list_organizations", {})
```

**Response Format:**
```json
{
    "organizations": [
        {
            "id": "org_123",
            "name": "My Organization",
            "slug": "my-org",
            "plan": "pro",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
}
```

### get_organization

Gets detailed information for a specific organization.

**Input Parameters:**
- `id` (string, required): The organization ID

**Example Usage:**
```python
result = client._run_command("get_organization", {
    "id": "org_123"
})
```

## Project Management

### list_projects

Lists all Supabase projects for the user.

**Input Parameters:** None

**Example Usage:**
```python
result = client._run_command("list_projects", {})
```

**Response Format:**
```json
{
    "projects": [
        {
            "id": "proj_456",
            "name": "My Project",
            "organization_id": "org_123",
            "region": "us-east-1",
            "status": "ACTIVE_HEALTHY",
            "created_at": "2024-01-15T00:00:00Z",
            "database": {
                "host": "db.proj456.supabase.co",
                "port": 5432
            }
        }
    ]
}
```

### get_project

Gets detailed information for a specific project.

**Input Parameters:**
- `id` (string, required): The project ID

**Example Usage:**
```python
result = client._run_command("get_project", {
    "id": "proj_456"
})
```

### create_project

Creates a new Supabase project.

**Input Parameters:**
- `organization_id` (string, required): Organization to create project in
- `confirm_cost_id` (string, required): Cost confirmation ID from `confirm_cost`
- `name` (string, required): Project name
- `region` (string, required): AWS region for the project

**Example Usage:**
```python
# First, get cost estimate
cost = client._run_command("get_cost", {
    "type": "project",
    "organization_id": "org_123"
})

# Confirm cost
confirmation = client._run_command("confirm_cost", {
    "type": "project",
    "recurrence": "monthly",
    "amount": cost["amount"]
})

# Create project
result = client._run_command("create_project", {
    "organization_id": "org_123",
    "confirm_cost_id": confirmation["id"],
    "name": "My New Project",
    "region": "us-east-1"
})
```

### pause_project

Pauses a Supabase project to save costs.

**Input Parameters:**
- `project_id` (string, required): The project ID to pause

### restore_project

Restores a paused Supabase project.

**Input Parameters:**
- `project_id` (string, required): The project ID to restore

### get_project_url

Gets the API URL for a project.

**Input Parameters:**
- `project_id` (string, required): The project ID

### get_anon_key

Gets the anonymous API key for a project.

**Input Parameters:**
- `project_id` (string, required): The project ID

## Database Operations

### list_tables

Lists all tables in one or more schemas.

**Input Parameters:**
- `project_id` (string, required): The project ID
- `schemas` (array, optional): List of schemas to include (defaults to all)

**Example Usage:**
```python
result = client._run_command("list_tables", {
    "project_id": "proj_456",
    "schemas": ["public", "auth"]
})
```

**Response Format:**
```json
{
    "tables": [
        {
            "schema": "public",
            "name": "users",
            "columns": [
                {
                    "name": "id",
                    "type": "uuid",
                    "is_primary_key": true,
                    "is_nullable": false
                }
            ]
        }
    ]
}
```

### list_extensions

Lists all PostgreSQL extensions in the database.

**Input Parameters:**
- `project_id` (string, required): The project ID

### execute_sql

Executes raw SQL queries in the PostgreSQL database.

**Input Parameters:**
- `project_id` (string, required): The project ID
- `query` (string, required): SQL query to execute

**Example Usage:**
```python
result = client._run_command("execute_sql", {
    "project_id": "proj_456",
    "query": "SELECT * FROM users LIMIT 10"
})
```

**Response Format:**
```json
{
    "data": [
        {
            "id": "user_123",
            "email": "user@example.com",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "count": 1
}
```

### apply_migration

Applies a database migration (DDL operations).

**Input Parameters:**
- `project_id` (string, required): The project ID
- `name` (string, required): Migration name in snake_case
- `query` (string, required): SQL DDL query to apply

**Example Usage:**
```python
result = client._run_command("apply_migration", {
    "project_id": "proj_456",
    "name": "add_user_profiles_table",
    "query": """
        CREATE TABLE profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES auth.users(id),
            display_name TEXT,
            avatar_url TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
    """
})
```

### list_migrations

Lists all applied migrations in the database.

**Input Parameters:**
- `project_id` (string, required): The project ID

### generate_typescript_types

Generates TypeScript types from the database schema.

**Input Parameters:**
- `project_id` (string, required): The project ID

**Example Usage:**
```python
result = client._run_command("generate_typescript_types", {
    "project_id": "proj_456"
})

# Save types to file
if "types" in result:
    with open("types/database.ts", "w") as f:
        f.write(result["types"])
```

## Development Workflow

### create_branch

Creates a development branch with an isolated database.

**Input Parameters:**
- `project_id` (string, required): The main project ID
- `name` (string, required): Branch name
- `confirm_cost_id` (string, required): Cost confirmation ID

### list_branches

Lists all development branches for a project.

**Input Parameters:**
- `project_id` (string, required): The project ID

**Response Format:**
```json
{
    "branches": [
        {
            "id": "branch_789",
            "name": "feature-auth",
            "status": "ACTIVE_HEALTHY",
            "created_at": "2024-01-20T00:00:00Z",
            "project_ref": "branch789"
        }
    ]
}
```

### merge_branch

Merges migrations and edge functions from a development branch to production.

**Input Parameters:**
- `project_id` (string, required): The main project ID
- `branch_id` (string, required): The branch ID to merge

### reset_branch

Resets a development branch to a clean state.

**Input Parameters:**
- `project_id` (string, required): The main project ID
- `branch_id` (string, required): The branch ID to reset

### rebase_branch

Rebases a development branch on the latest production changes.

**Input Parameters:**
- `project_id` (string, required): The main project ID
- `branch_id` (string, required): The branch ID to rebase

### delete_branch

Deletes a development branch.

**Input Parameters:**
- `project_id` (string, required): The main project ID
- `branch_id` (string, required): The branch ID to delete

## Edge Functions

### list_edge_functions

Lists all Edge Functions in a Supabase project.

**Input Parameters:**
- `project_id` (string, required): The project ID

**Response Format:**
```json
{
    "functions": [
        {
            "slug": "hello-world",
            "name": "hello-world",
            "status": "ACTIVE",
            "version": 1,
            "created_at": "2024-01-20T00:00:00Z"
        }
    ]
}
```

### get_edge_function

Retrieves the source code for an Edge Function.

**Input Parameters:**
- `project_id` (string, required): The project ID
- `function_slug` (string, required): The function slug/name

### deploy_edge_function

Deploys an Edge Function to a Supabase project.

**Input Parameters:**
- `project_id` (string, required): The project ID
- `name` (string, required): Function name
- `files` (array, required): Array of file objects with `name` and `content`
- `entrypoint_path` (string, optional): Main function file path
- `import_map_path` (string, optional): Import map file path

**Example Usage:**
```python
result = client._run_command("deploy_edge_function", {
    "project_id": "proj_456",
    "name": "hello-world",
    "files": [
        {
            "name": "index.ts",
            "content": '''
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req: Request) => {
    return new Response(JSON.stringify({
        message: "Hello World!",
        timestamp: new Date().toISOString()
    }), {
        headers: { "Content-Type": "application/json" }
    })
})
            '''
        }
    ]
})
```

## Monitoring & Security

### get_logs

Gets service logs for debugging purposes.

**Input Parameters:**
- `project_id` (string, required): The project ID
- `service` (string, required): Service type ("database", "auth", "realtime", etc.)

**Note:** Only returns logs from the last minute.

### get_advisors

Gets security and performance recommendations.

**Input Parameters:**
- `project_id` (string, required): The project ID
- `type` (string, required): Advisor type ("security", "performance", or "all")

**Example Usage:**
```python
result = client._run_command("get_advisors", {
    "project_id": "proj_456",
    "type": "security"
})
```

**Response Format:**
```json
{
    "advisors": [
        {
            "type": "security",
            "level": "warning",
            "message": "Row Level Security (RLS) is not enabled on table 'posts'",
            "remediation_url": "https://supabase.com/docs/guides/auth/row-level-security"
        }
    ]
}
```

## Cost Management

### get_cost

Gets the cost estimate for creating a new project or branch.

**Input Parameters:**
- `type` (string, required): "project" or "branch"
- `organization_id` (string, required): The organization ID

### confirm_cost

Confirms understanding of costs before creation.

**Input Parameters:**
- `type` (string, required): "project" or "branch"
- `recurrence` (string, required): Billing frequency
- `amount` (number, required): Cost amount from `get_cost`

**Returns:** A confirmation ID to use with `create_project` or `create_branch`

## Error Handling

All MCP commands return a consistent error format when operations fail:

```json
{
    "error": "Error message describing what went wrong",
    "returncode": 1
}
```

Common error scenarios:

- **Authentication errors**: Invalid or missing access token
- **Permission errors**: Insufficient permissions for the operation
- **Not found errors**: Project, organization, or resource doesn't exist
- **Validation errors**: Invalid input parameters
- **Rate limiting**: Too many requests in a short time period

## Rate Limits

The Supabase Management API has rate limits to ensure fair usage:

- **General operations**: 100 requests per minute
- **Database operations**: 50 requests per minute
- **Project creation**: 5 requests per hour

When rate limits are exceeded, the API returns a 429 status code with retry information.

## Best Practices

1. **Cache results** when possible to reduce API calls
2. **Handle errors gracefully** with proper retry logic
3. **Use batch operations** for multiple related changes
4. **Monitor rate limits** and implement backoff strategies
5. **Validate inputs** before making API calls
6. **Use development branches** for testing schema changes
7. **Regular security scans** with `get_advisors`
8. **Keep access tokens secure** and rotate regularly

## Examples

For complete working examples, see:
- [Basic Usage Examples](../examples/basic_usage.py)
- [Advanced Workflows](../examples/advanced_workflows.py)
- [Integration Patterns](../examples/integration_patterns.py)

---

**Need help?** Check our [Setup Guide](SETUP.md) or [Troubleshooting Guide](TROUBLESHOOTING.md).
