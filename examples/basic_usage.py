#!/usr/bin/env python3
"""
Basic usage examples for the Supabase MCP connector.

This module demonstrates fundamental operations and common patterns
for interacting with Supabase through the MCP connector.
"""

import json
import subprocess
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class SupabaseProject:
    """Data class representing a Supabase project."""
    id: str
    name: str
    organization_id: str
    region: str
    status: str
    created_at: str


class SupabaseMCPClient:
    """
    Simple client wrapper for Supabase MCP connector operations.
    
    This class provides a clean interface for common Supabase operations
    through the MCP connector, with proper error handling and type hints.
    """
    
    def __init__(self, server_name: str = "supabase"):
        """
        Initialize the MCP client.
        
        Args:
            server_name: Name of the MCP server (default: "supabase")
        """
        self.server_name = server_name
        self._check_authentication()
    
    def _check_authentication(self) -> None:
        """Check if authentication is properly configured."""
        if not os.getenv("SUPABASE_ACCESS_TOKEN"):
            print("⚠️  Warning: SUPABASE_ACCESS_TOKEN not set. Some operations may fail.")
    
    def _run_command(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an MCP command and return the result.
        
        Args:
            tool_name: Name of the MCP tool to execute
            input_data: Input parameters for the tool
            
        Returns:
            Dictionary containing the command result or error information
        """
        try:
            cmd = [
                "manus-mcp-cli", "tool", "call", tool_name,
                "--server", self.server_name,
                "--input", json.dumps(input_data)
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"raw_output": result.stdout}
            else:
                return {"error": result.stderr, "returncode": result.returncode}
                
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out after 30 seconds"}
        except Exception as e:
            return {"error": str(e)}
    
    def search_documentation(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Search Supabase documentation.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of documentation results with title, href, and content
        """
        graphql_query = f"""{{
            searchDocs(query: "{query}", limit: {limit}) {{
                nodes {{
                    title
                    href
                    content
                }}
            }}
        }}"""
        
        result = self._run_command("search_docs", {"graphql_query": graphql_query})
        
        if "error" in result:
            print(f"❌ Documentation search failed: {result['error']}")
            return []
        
        if "searchDocs" in result and result["searchDocs"]["nodes"]:
            return result["searchDocs"]["nodes"]
        
        return []
    
    def list_organizations(self) -> List[Dict[str, Any]]:
        """
        List all organizations the user has access to.
        
        Returns:
            List of organization dictionaries
        """
        result = self._run_command("list_organizations", {})
        
        if "error" in result:
            print(f"❌ Failed to list organizations: {result['error']}")
            return []
        
        return result.get("organizations", [])
    
    def list_projects(self) -> List[SupabaseProject]:
        """
        List all Supabase projects.
        
        Returns:
            List of SupabaseProject objects
        """
        result = self._run_command("list_projects", {})
        
        if "error" in result:
            print(f"❌ Failed to list projects: {result['error']}")
            return []
        
        projects = []
        for project_data in result.get("projects", []):
            try:
                project = SupabaseProject(
                    id=project_data["id"],
                    name=project_data["name"],
                    organization_id=project_data["organization_id"],
                    region=project_data["region"],
                    status=project_data["status"],
                    created_at=project_data["created_at"]
                )
                projects.append(project)
            except KeyError as e:
                print(f"⚠️  Skipping project with missing field: {e}")
        
        return projects
    
    def get_project_details(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific project.
        
        Args:
            project_id: The project ID to query
            
        Returns:
            Project details dictionary or None if not found
        """
        result = self._run_command("get_project", {"id": project_id})
        
        if "error" in result:
            print(f"❌ Failed to get project details: {result['error']}")
            return None
        
        return result
    
    def list_tables(self, project_id: str, schemas: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List database tables for a project.
        
        Args:
            project_id: The project ID
            schemas: Optional list of schemas to include (default: all)
            
        Returns:
            List of table information dictionaries
        """
        input_data = {"project_id": project_id}
        if schemas:
            input_data["schemas"] = schemas
        
        result = self._run_command("list_tables", input_data)
        
        if "error" in result:
            print(f"❌ Failed to list tables: {result['error']}")
            return []
        
        return result.get("tables", [])
    
    def execute_sql(self, project_id: str, query: str) -> Optional[Dict[str, Any]]:
        """
        Execute a SQL query against the project database.
        
        Args:
            project_id: The project ID
            query: SQL query to execute
            
        Returns:
            Query results or None if failed
        """
        result = self._run_command("execute_sql", {
            "project_id": project_id,
            "query": query
        })
        
        if "error" in result:
            print(f"❌ SQL execution failed: {result['error']}")
            return None
        
        return result
    
    def get_security_advisors(self, project_id: str, advisor_type: str = "all") -> List[Dict[str, Any]]:
        """
        Get security and performance advisors for a project.
        
        Args:
            project_id: The project ID
            advisor_type: Type of advisors to fetch ("security", "performance", or "all")
            
        Returns:
            List of advisor recommendations
        """
        result = self._run_command("get_advisors", {
            "project_id": project_id,
            "type": advisor_type
        })
        
        if "error" in result:
            print(f"❌ Failed to get advisors: {result['error']}")
            return []
        
        return result.get("advisors", [])
    
    def generate_typescript_types(self, project_id: str) -> Optional[str]:
        """
        Generate TypeScript types from the database schema.
        
        Args:
            project_id: The project ID
            
        Returns:
            TypeScript type definitions as string or None if failed
        """
        result = self._run_command("generate_typescript_types", {"project_id": project_id})
        
        if "error" in result:
            print(f"❌ Failed to generate types: {result['error']}")
            return None
        
        return result.get("types")


def example_basic_operations():
    """Demonstrate basic operations with the Supabase MCP connector."""
    print("🚀 Basic Supabase MCP Operations Example")
    print("=" * 50)
    
    # Initialize client
    client = SupabaseMCPClient()
    
    # 1. Search documentation
    print("\n📚 Searching documentation...")
    docs = client.search_documentation("database tables", limit=3)
    for doc in docs[:2]:  # Show first 2 results
        print(f"  • {doc['title']}")
        print(f"    URL: {doc['href']}")
    
    # 2. List organizations
    print("\n🏢 Listing organizations...")
    orgs = client.list_organizations()
    for org in orgs:
        print(f"  • {org.get('name', 'Unknown')} (ID: {org.get('id', 'N/A')})")
    
    # 3. List projects
    print("\n📋 Listing projects...")
    projects = client.list_projects()
    for project in projects:
        print(f"  • {project.name} ({project.status})")
        print(f"    Region: {project.region}")
    
    # 4. If we have projects, demonstrate database operations
    if projects:
        project = projects[0]
        print(f"\n🗄️  Database operations for '{project.name}'...")
        
        # List tables
        tables = client.list_tables(project.id)
        print(f"  Found {len(tables)} tables:")
        for table in tables[:3]:  # Show first 3
            schema = table.get("schema", "public")
            name = table.get("name", "unknown")
            print(f"    • {schema}.{name}")
        
        # Get security advisors
        advisors = client.get_security_advisors(project.id)
        if advisors:
            print(f"  Security recommendations: {len(advisors)}")
            for advisor in advisors[:2]:  # Show first 2
                level = advisor.get("level", "info")
                message = advisor.get("message", "No message")
                icon = "🚨" if level == "critical" else "⚠️" if level == "warning" else "💡"
                print(f"    {icon} {message}")
        
        # Generate TypeScript types
        print("  Generating TypeScript types...")
        types = client.generate_typescript_types(project.id)
        if types:
            print("    ✅ Types generated successfully")
            # Save to file
            with open("generated_types.ts", "w") as f:
                f.write(types)
            print("    📄 Saved to generated_types.ts")
        else:
            print("    ❌ Type generation failed")
    
    print("\n✅ Basic operations example completed!")


def example_error_handling():
    """Demonstrate proper error handling patterns."""
    print("\n🛡️  Error Handling Example")
    print("=" * 30)
    
    client = SupabaseMCPClient()
    
    # Try to get details for a non-existent project
    print("Testing error handling with invalid project ID...")
    result = client.get_project_details("invalid_project_id")
    if result is None:
        print("  ✅ Error properly handled")
    else:
        print("  ⚠️  Unexpected success")
    
    # Try to execute invalid SQL
    print("Testing SQL error handling...")
    if client.list_projects():  # Only if we have projects
        project_id = client.list_projects()[0].id
        result = client.execute_sql(project_id, "INVALID SQL QUERY")
        if result is None:
            print("  ✅ SQL error properly handled")
        else:
            print("  ⚠️  Unexpected success")


def example_advanced_patterns():
    """Demonstrate advanced usage patterns."""
    print("\n🔧 Advanced Usage Patterns")
    print("=" * 30)
    
    client = SupabaseMCPClient()
    
    # Pattern 1: Project health check
    print("1. Project health check pattern...")
    projects = client.list_projects()
    
    for project in projects:
        print(f"  Checking {project.name}...")
        
        # Check project status
        if project.status != "ACTIVE_HEALTHY":
            print(f"    ⚠️  Status: {project.status}")
        else:
            print("    ✅ Status: Healthy")
        
        # Check for security issues
        advisors = client.get_security_advisors(project.id, "security")
        security_issues = [a for a in advisors if a.get("level") in ["critical", "warning"]]
        
        if security_issues:
            print(f"    🚨 {len(security_issues)} security issues found")
        else:
            print("    🔒 No security issues")
    
    # Pattern 2: Documentation-driven development
    print("\n2. Documentation-driven development...")
    topics = ["authentication", "row level security", "edge functions"]
    
    for topic in topics:
        docs = client.search_documentation(topic, limit=1)
        if docs:
            print(f"  📖 {topic.title()}: {docs[0]['title']}")
        else:
            print(f"  ❌ No docs found for {topic}")


if __name__ == "__main__":
    """Run all examples when script is executed directly."""
    try:
        example_basic_operations()
        example_error_handling()
        example_advanced_patterns()
        
        print("\n🎉 All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed with error: {e}")
