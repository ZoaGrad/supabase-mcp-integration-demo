# Supabase MCP Integration Demo

A comprehensive demonstration of the Supabase Model Context Protocol (MCP) connector, showcasing full GitHub integration and complete scaffolding for modern development workflows.

## Overview

This repository demonstrates how to leverage the Supabase MCP connector for automated project management, database operations, and seamless integration with GitHub workflows. The connector provides access to 29 different tools covering the entire Supabase platform lifecycle.

## Features Demonstrated

### Core Supabase MCP Capabilities

**Documentation & Search**
- Real-time documentation search using GraphQL queries
- Access to guides, API references, and troubleshooting resources

**Organization & Project Management**
- List and manage organizations with subscription details
- Create, pause, and restore projects with cost management
- Retrieve project URLs and API keys programmatically

**Database Operations**
- Schema inspection and table management
- SQL execution and migration management
- TypeScript type generation from database schema

**Development Workflow**
- Branch-based development with isolated databases
- Merge, reset, and rebase operations
- Edge Function deployment and management

**Security & Monitoring**
- Security vulnerability detection
- Performance optimization recommendations
- Service log analysis and debugging

### GitHub Integration Features

**Repository Management**
- Automated repository creation and configuration
- Branch protection rules and workflow setup
- Issue and pull request templates

**CI/CD Pipeline**
- GitHub Actions for Supabase deployments
- Automated testing and migration workflows
- Environment-specific configurations

**Documentation & Collaboration**
- Comprehensive README and documentation
- Code review templates and guidelines
- Contributor onboarding automation

## Quick Start

### Prerequisites

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **Access Token**: Generate from [Account Settings](https://supabase.com/dashboard/account/tokens)
3. **GitHub Account**: Required for repository integration
4. **MCP CLI**: Pre-installed in Manus environment

### Setup Instructions

1. **Clone this repository**
   ```bash
   git clone https://github.com/ZoaGrad/supabase-mcp-integration-demo.git
   cd supabase-mcp-integration-demo
   ```

2. **Configure authentication**
   ```bash
   export SUPABASE_ACCESS_TOKEN="your_access_token_here"
   ```

3. **Test the connector**
   ```bash
   python3 scripts/test_connector.py
   ```

4. **Run the full demo**
   ```bash
   python3 scripts/full_demo.py
   ```

## Project Structure

```
supabase-mcp-integration-demo/
├── README.md                          # This file
├── .github/
│   ├── workflows/
│   │   ├── supabase-deploy.yml       # Deployment workflow
│   │   ├── test-connector.yml        # Connector testing
│   │   └── security-scan.yml         # Security scanning
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md             # Bug report template
│   │   └── feature_request.md        # Feature request template
│   └── pull_request_template.md      # PR template
├── scripts/
│   ├── test_connector.py             # Connector testing script
│   ├── full_demo.py                  # Complete demonstration
│   ├── setup_project.py              # Project setup automation
│   └── deploy_functions.py           # Edge function deployment
├── supabase/
│   ├── config.toml                   # Supabase configuration
│   ├── migrations/                   # Database migrations
│   ├── functions/                    # Edge functions
│   └── seed.sql                      # Sample data
├── docs/
│   ├── SETUP.md                      # Detailed setup guide
│   ├── API.md                        # API documentation
│   └── TROUBLESHOOTING.md            # Common issues
└── examples/
    ├── basic_usage.py                # Basic connector usage
    ├── advanced_workflows.py         # Complex workflows
    └── integration_patterns.py       # Integration examples
```

## Usage Examples

### Basic Connector Usage

```python
from supabase_mcp import SupabaseConnector

# Initialize connector
connector = SupabaseConnector()

# List organizations
orgs = connector.list_organizations()
print(f"Found {len(orgs)} organizations")

# Create a new project
project = connector.create_project(
    name="My New Project",
    organization_id="org_123",
    region="us-east-1"
)
```

### Database Operations

```python
# List tables
tables = connector.list_tables(project_id="proj_456")

# Execute SQL
results = connector.execute_sql(
    project_id="proj_456",
    query="SELECT * FROM users LIMIT 10"
)

# Apply migration
connector.apply_migration(
    project_id="proj_456",
    name="add_user_profiles",
    query="CREATE TABLE profiles (id UUID PRIMARY KEY, user_id UUID REFERENCES users(id));"
)
```

### Edge Function Deployment

```python
# Deploy edge function
connector.deploy_edge_function(
    project_id="proj_456",
    name="hello-world",
    files=[{
        "name": "index.ts",
        "content": "export default { fetch: () => new Response('Hello World!') }"
    }]
)
```

## GitHub Integration Workflows

### Automated Deployment

The repository includes GitHub Actions workflows that automatically:

- Deploy Supabase migrations on push to main
- Run connector tests on pull requests
- Perform security scans on dependencies
- Generate TypeScript types from schema changes

### Branch-based Development

Each feature branch can have its own Supabase branch for isolated development:

```yaml
# .github/workflows/branch-deploy.yml
name: Branch Deploy
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Create Supabase branch
        run: |
          python3 scripts/create_branch.py --pr-number ${{ github.event.number }}
```

## Security Considerations

The connector includes built-in security features:

- **Row Level Security (RLS) Detection**: Automatically identifies tables without RLS policies
- **Performance Monitoring**: Suggests database optimizations
- **Access Control**: Manages API keys and permissions
- **Audit Logging**: Tracks all operations for compliance

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Testing

Run the test suite:

```bash
python3 -m pytest tests/
```

Test the MCP connector:

```bash
python3 scripts/test_connector.py --verbose
```

## Troubleshooting

### Common Issues

**Authentication Errors**
- Ensure your access token is valid and has proper permissions
- Check that the token is set in the environment variable

**Connection Timeouts**
- Verify your network connection
- Check Supabase service status

**Permission Denied**
- Confirm your organization membership
- Verify project access permissions

For more detailed troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

## Resources

- [Supabase Documentation](https://supabase.com/docs)
- [MCP Specification](https://modelcontextprotocol.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Supabase Management API](https://supabase.com/docs/reference/api)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support:

- 📧 Email: support@example.com
- 💬 Discord: [Join our community](https://discord.gg/example)
- 🐛 Issues: [GitHub Issues](https://github.com/ZoaGrad/supabase-mcp-integration-demo/issues)

---

**Built with ❤️ using Supabase MCP Connector**
