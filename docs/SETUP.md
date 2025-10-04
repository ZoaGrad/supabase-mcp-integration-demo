# Supabase MCP Connector Setup Guide

This comprehensive guide walks you through setting up and configuring the Supabase MCP connector for your development workflow.

## Prerequisites

Before you begin, ensure you have the following:

### Required Accounts and Access
- **Supabase Account**: Sign up at [supabase.com](https://supabase.com) if you haven't already
- **GitHub Account**: Required for repository integration and CI/CD workflows
- **Manus Environment**: This connector is designed to work within the Manus platform

### System Requirements
- Python 3.9 or higher
- Git version control
- Internet connection for API access

## Step 1: Supabase Access Token

The MCP connector requires a Supabase platform access token to authenticate with the management API.

### Generating an Access Token

1. **Navigate to Account Settings**
   - Go to [https://supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens)
   - Sign in to your Supabase account if prompted

2. **Create New Token**
   - Click "Create new token" or similar button
   - Provide a descriptive name (e.g., "MCP Connector Token")
   - Select appropriate permissions:
     - ✅ Read organizations
     - ✅ Read projects
     - ✅ Manage projects
     - ✅ Read database schema
     - ✅ Execute SQL queries
     - ✅ Manage Edge Functions
     - ✅ Manage branches

3. **Copy and Store Token**
   - Copy the generated token immediately
   - Store it securely (you won't be able to see it again)

### Setting the Environment Variable

Set the access token as an environment variable:

```bash
# For current session
export SUPABASE_ACCESS_TOKEN="your_token_here"

# For persistent setup (add to ~/.bashrc or ~/.zshrc)
echo 'export SUPABASE_ACCESS_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

## Step 2: Project Setup

### Clone the Repository

```bash
git clone https://github.com/ZoaGrad/supabase-mcp-integration-demo.git
cd supabase-mcp-integration-demo
```

### Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify MCP CLI is available (should be pre-installed in Manus)
manus-mcp-cli --version
```

### Verify Connector Setup

Test the connector to ensure everything is working:

```bash
# Run the test suite
python3 scripts/test_connector.py --verbose

# Run basic usage examples
python3 examples/basic_usage.py
```

## Step 3: GitHub Integration

### Repository Configuration

1. **Fork or Clone Repository**
   ```bash
   # If forking, clone your fork
   git clone https://github.com/YOUR_USERNAME/supabase-mcp-integration-demo.git
   ```

2. **Set Repository Secrets**
   - Go to your repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Add the following secrets:
     - `SUPABASE_ACCESS_TOKEN`: Your Supabase access token
     - `SUPABASE_PROJECT_ID`: Your default project ID (optional)

### GitHub Actions Setup

The repository includes pre-configured workflows for:

- **Automated Testing**: Runs connector tests on pull requests
- **Deployment**: Deploys migrations and functions on merge to main
- **Security Scanning**: Checks for security issues and performance problems
- **Branch Management**: Creates isolated Supabase branches for feature development

To enable workflows:

1. Ensure you have the necessary repository permissions
2. The workflows will automatically trigger on push/pull request events
3. Check the "Actions" tab in your repository to monitor workflow runs

## Step 4: Supabase Project Configuration

### Create a Test Project

If you don't have a Supabase project yet:

```python
# Use the MCP connector to create a project
python3 -c "
from examples.basic_usage import SupabaseMCPClient
client = SupabaseMCPClient()

# List organizations first
orgs = client.list_organizations()
if orgs:
    org_id = orgs[0]['id']
    print(f'Organization ID: {org_id}')
    print('Use this ID to create a project via the Supabase dashboard')
else:
    print('No organizations found. Please create one in the Supabase dashboard.')
"
```

### Configure Project Settings

1. **Enable Required Extensions**
   ```sql
   -- Common extensions for MCP integration
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   CREATE EXTENSION IF NOT EXISTS "pgcrypto";
   ```

2. **Set Up Row Level Security**
   ```sql
   -- Enable RLS on your tables
   ALTER TABLE your_table_name ENABLE ROW LEVEL SECURITY;
   
   -- Create appropriate policies
   CREATE POLICY "Users can view own data" ON your_table_name
     FOR SELECT USING (auth.uid() = user_id);
   ```

## Step 5: Development Workflow

### Branch-Based Development

The connector supports branch-based development with isolated databases:

```python
# Create a development branch
from examples.basic_usage import SupabaseMCPClient
client = SupabaseMCPClient()

# This would create a new branch (requires authentication)
# result = client._run_command("create_branch", {
#     "project_id": "your_project_id",
#     "name": "feature-branch"
# })
```

### Local Development Setup

1. **Environment Configuration**
   ```bash
   # Create .env file
   cat > .env << EOF
   SUPABASE_ACCESS_TOKEN=your_token_here
   SUPABASE_PROJECT_ID=your_project_id
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   EOF
   ```

2. **Database Migrations**
   ```bash
   # Apply migrations using the connector
   python3 scripts/deploy_migrations.py --project-id your_project_id
   ```

3. **Type Generation**
   ```bash
   # Generate TypeScript types
   python3 scripts/generate_types.py --project-id your_project_id
   ```

## Step 6: Monitoring and Maintenance

### Security Monitoring

Regularly check for security issues:

```python
from examples.basic_usage import SupabaseMCPClient
client = SupabaseMCPClient()

# Get security advisors
advisors = client.get_security_advisors("your_project_id", "security")
for advisor in advisors:
    print(f"⚠️  {advisor['message']}")
```

### Performance Optimization

Monitor performance recommendations:

```python
# Get performance advisors
advisors = client.get_security_advisors("your_project_id", "performance")
for advisor in advisors:
    print(f"💡 {advisor['message']}")
```

### Log Monitoring

Check service logs for issues:

```python
# Get recent logs (requires project access)
logs = client._run_command("get_logs", {
    "project_id": "your_project_id",
    "service": "database"
})
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```
   Error: Unauthorized. Please provide a valid access token
   ```
   - Verify your access token is set correctly
   - Check token permissions in Supabase dashboard
   - Ensure token hasn't expired

2. **Connection Timeouts**
   ```
   Error: Command timed out after 30 seconds
   ```
   - Check your internet connection
   - Verify Supabase service status
   - Try again after a few minutes

3. **Permission Denied**
   ```
   Error: Permission denied for project
   ```
   - Confirm you're a member of the project's organization
   - Check your role permissions
   - Contact organization admin if needed

### Getting Help

- **Documentation**: Check the [Supabase docs](https://supabase.com/docs)
- **Community**: Join the [Supabase Discord](https://discord.supabase.com)
- **Issues**: Report bugs in this repository's [Issues](https://github.com/ZoaGrad/supabase-mcp-integration-demo/issues)

## Next Steps

Once setup is complete:

1. **Explore Examples**: Run the example scripts to understand capabilities
2. **Customize Workflows**: Adapt the GitHub Actions to your needs
3. **Build Applications**: Use the connector in your own projects
4. **Contribute**: Share improvements and feedback with the community

## Security Best Practices

- **Never commit access tokens** to version control
- **Use environment variables** for sensitive configuration
- **Regularly rotate access tokens** (recommended: every 90 days)
- **Monitor access logs** in your Supabase dashboard
- **Enable Row Level Security** on all user-facing tables
- **Review security advisors** regularly

---

**Need help?** Check our [Troubleshooting Guide](TROUBLESHOOTING.md) or open an issue in the repository.
