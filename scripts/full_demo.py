#!/usr/bin/env python3
"""
Complete demonstration of Supabase MCP connector capabilities.

This script showcases the full workflow from project creation to deployment,
including GitHub integration and best practices.
"""

import json
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class SupabaseFullDemo:
    def __init__(self, project_id: Optional[str] = None):
        self.project_id = project_id
        self.server_name = "supabase"
        self.demo_data = {}
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with emojis"""
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅", 
            "ERROR": "❌",
            "WARNING": "⚠️",
            "STEP": "🔄"
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = icons.get(level, "📝")
        print(f"{icon} [{timestamp}] {message}")
        
    def run_mcp_command(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP command with error handling"""
        try:
            cmd = [
                "manus-mcp-cli", "tool", "call", tool_name,
                "--server", self.server_name,
                "--input", json.dumps(input_data)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"raw_output": result.stdout}
            else:
                return {"error": result.stderr, "returncode": result.returncode}
                
        except Exception as e:
            return {"error": str(e)}
    
    def demonstrate_organization_management(self):
        """Demonstrate organization and project management"""
        self.log("🏢 Organization & Project Management", "STEP")
        
        # List organizations
        self.log("Fetching organizations...")
        orgs = self.run_mcp_command("list_organizations", {})
        
        if "error" not in orgs and orgs.get("organizations"):
            self.log(f"Found {len(orgs['organizations'])} organizations", "SUCCESS")
            for org in orgs["organizations"][:3]:  # Show first 3
                self.log(f"  • {org['name']} ({org.get('plan', 'unknown')} plan)")
            self.demo_data["organizations"] = orgs["organizations"]
        else:
            self.log("Using mock organization data for demo", "WARNING")
            self.demo_data["organizations"] = [{
                "id": "org_demo",
                "name": "Demo Organization", 
                "plan": "pro"
            }]
        
        # List projects
        self.log("Fetching projects...")
        projects = self.run_mcp_command("list_projects", {})
        
        if "error" not in projects and projects.get("projects"):
            self.log(f"Found {len(projects['projects'])} projects", "SUCCESS")
            for project in projects["projects"][:3]:
                self.log(f"  • {project['name']} ({project.get('status', 'unknown')})")
            self.demo_data["projects"] = projects["projects"]
            
            # Use first project for further demos
            if not self.project_id and projects["projects"]:
                self.project_id = projects["projects"][0]["id"]
                self.log(f"Using project: {projects['projects'][0]['name']}")
        else:
            self.log("Using mock project data for demo", "WARNING")
            self.demo_data["projects"] = [{
                "id": "proj_demo",
                "name": "Demo Project",
                "status": "ACTIVE_HEALTHY"
            }]
            if not self.project_id:
                self.project_id = "proj_demo"
    
    def demonstrate_database_operations(self):
        """Demonstrate database schema and operations"""
        if not self.project_id:
            self.log("No project ID available for database operations", "WARNING")
            return
            
        self.log("🗄️ Database Operations", "STEP")
        
        # List tables
        self.log("Analyzing database schema...")
        tables = self.run_mcp_command("list_tables", {"project_id": self.project_id})
        
        if "error" not in tables and tables.get("tables"):
            self.log(f"Found {len(tables['tables'])} tables", "SUCCESS")
            for table in tables["tables"][:5]:
                schema = table.get("schema", "public")
                name = table.get("name", "unknown")
                self.log(f"  • {schema}.{name}")
            self.demo_data["tables"] = tables["tables"]
        else:
            self.log("Using mock table data for demo", "WARNING")
            self.demo_data["tables"] = [
                {"schema": "public", "name": "users"},
                {"schema": "public", "name": "posts"},
                {"schema": "public", "name": "comments"}
            ]
        
        # List extensions
        self.log("Checking database extensions...")
        extensions = self.run_mcp_command("list_extensions", {"project_id": self.project_id})
        
        if "error" not in extensions and extensions.get("extensions"):
            self.log(f"Found {len(extensions['extensions'])} extensions", "SUCCESS")
            for ext in extensions["extensions"][:3]:
                name = ext.get("name", "unknown")
                version = ext.get("version", "unknown")
                self.log(f"  • {name} (v{version})")
        
        # Generate TypeScript types
        self.log("Generating TypeScript types...")
        types = self.run_mcp_command("generate_typescript_types", {"project_id": self.project_id})
        
        if "error" not in types:
            self.log("TypeScript types generated successfully", "SUCCESS")
            # Save types to file
            if types.get("types"):
                with open("types/database.ts", "w") as f:
                    f.write(types["types"])
                self.log("Types saved to types/database.ts")
        else:
            self.log("Could not generate types (expected in demo mode)", "WARNING")
    
    def demonstrate_security_analysis(self):
        """Demonstrate security and performance analysis"""
        if not self.project_id:
            self.log("No project ID available for security analysis", "WARNING")
            return
            
        self.log("🔒 Security & Performance Analysis", "STEP")
        
        # Get security advisors
        self.log("Running security analysis...")
        advisors = self.run_mcp_command("get_advisors", {
            "project_id": self.project_id,
            "type": "all"
        })
        
        if "error" not in advisors and advisors.get("advisors"):
            self.log(f"Found {len(advisors['advisors'])} recommendations", "SUCCESS")
            
            security_count = sum(1 for a in advisors["advisors"] if a.get("type") == "security")
            performance_count = sum(1 for a in advisors["advisors"] if a.get("type") == "performance")
            
            self.log(f"  • Security issues: {security_count}")
            self.log(f"  • Performance recommendations: {performance_count}")
            
            # Show critical issues
            for advisor in advisors["advisors"][:3]:
                level = advisor.get("level", "info")
                message = advisor.get("message", "No message")
                icon = "🚨" if level == "critical" else "⚠️" if level == "warning" else "💡"
                self.log(f"  {icon} {message}")
                
        else:
            self.log("Using mock security analysis for demo", "WARNING")
            mock_advisors = [
                {"type": "security", "level": "warning", "message": "RLS not enabled on 'posts' table"},
                {"type": "performance", "level": "info", "message": "Consider adding index on user_id column"}
            ]
            for advisor in mock_advisors:
                level = advisor["level"]
                message = advisor["message"]
                icon = "⚠️" if level == "warning" else "💡"
                self.log(f"  {icon} {message}")
    
    def demonstrate_edge_functions(self):
        """Demonstrate Edge Functions management"""
        if not self.project_id:
            self.log("No project ID available for Edge Functions", "WARNING")
            return
            
        self.log("⚡ Edge Functions Management", "STEP")
        
        # List existing functions
        self.log("Listing Edge Functions...")
        functions = self.run_mcp_command("list_edge_functions", {"project_id": self.project_id})
        
        if "error" not in functions and functions.get("functions"):
            self.log(f"Found {len(functions['functions'])} functions", "SUCCESS")
            for func in functions["functions"]:
                name = func.get("name", "unknown")
                status = func.get("status", "unknown")
                version = func.get("version", "unknown")
                self.log(f"  • {name} (v{version}, {status})")
        else:
            self.log("No existing functions found (or demo mode)", "INFO")
        
        # Demonstrate function deployment (mock)
        self.log("Demonstrating function deployment...")
        sample_function = {
            "name": "hello-world",
            "files": [{
                "name": "index.ts",
                "content": '''
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req: Request) => {
  const data = {
    message: "Hello from Supabase Edge Function!",
    timestamp: new Date().toISOString(),
    method: req.method,
    url: req.url
  }
  
  return new Response(JSON.stringify(data), {
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*"
    }
  })
})
'''
            }]
        }
        
        self.log("Sample function code prepared:")
        self.log("  • TypeScript with Deno runtime")
        self.log("  • CORS enabled")
        self.log("  • JSON response format")
        
        # In real scenario, would deploy with:
        # deploy_result = self.run_mcp_command("deploy_edge_function", {
        #     "project_id": self.project_id,
        #     **sample_function
        # })
    
    def demonstrate_branch_workflow(self):
        """Demonstrate branch-based development workflow"""
        if not self.project_id:
            self.log("No project ID available for branch workflow", "WARNING")
            return
            
        self.log("🌿 Branch-based Development Workflow", "STEP")
        
        # List existing branches
        self.log("Checking existing branches...")
        branches = self.run_mcp_command("list_branches", {"project_id": self.project_id})
        
        if "error" not in branches and branches.get("branches"):
            self.log(f"Found {len(branches['branches'])} development branches", "SUCCESS")
            for branch in branches["branches"]:
                name = branch.get("name", "unknown")
                status = branch.get("status", "unknown")
                self.log(f"  • {name} ({status})")
        else:
            self.log("No development branches found", "INFO")
        
        # Demonstrate branch creation workflow
        self.log("Branch workflow capabilities:")
        self.log("  • create_branch: Create isolated development environment")
        self.log("  • merge_branch: Merge changes to production")
        self.log("  • reset_branch: Reset branch to clean state")
        self.log("  • rebase_branch: Sync with latest production changes")
        self.log("  • delete_branch: Clean up completed branches")
        
        # Show cost estimation
        self.log("Checking branch creation costs...")
        if self.demo_data.get("organizations"):
            org_id = self.demo_data["organizations"][0]["id"]
            cost = self.run_mcp_command("get_cost", {
                "type": "branch",
                "organization_id": org_id
            })
            
            if "error" not in cost:
                self.log("Cost estimation retrieved successfully", "SUCCESS")
            else:
                self.log("Using mock cost data for demo", "WARNING")
                self.log("  • Branch creation: $0.00/hour (first 2 branches free)")
                self.log("  • Additional branches: $0.01/hour")
    
    def demonstrate_github_integration(self):
        """Demonstrate GitHub integration capabilities"""
        self.log("🐙 GitHub Integration", "STEP")
        
        # Check if we're in a git repository
        try:
            result = subprocess.run(["git", "status"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("Git repository detected", "SUCCESS")
                
                # Get current branch
                branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                             capture_output=True, text=True)
                if branch_result.returncode == 0:
                    current_branch = branch_result.stdout.strip()
                    self.log(f"Current branch: {current_branch}")
                
                # Show GitHub integration features
                self.log("GitHub integration features:")
                self.log("  • Automated deployments via GitHub Actions")
                self.log("  • Branch-based Supabase environments")
                self.log("  • Security scanning and advisors")
                self.log("  • TypeScript type generation")
                self.log("  • Pull request previews")
                
            else:
                self.log("Not in a git repository", "WARNING")
                
        except FileNotFoundError:
            self.log("Git not available", "WARNING")
        
        # Show workflow files
        workflow_files = [
            ".github/workflows/supabase-deploy.yml",
            ".github/workflows/test-connector.yml",
            ".github/ISSUE_TEMPLATE/bug_report.md"
        ]
        
        self.log("Checking GitHub workflow files...")
        for file_path in workflow_files:
            if os.path.exists(file_path):
                self.log(f"  ✅ {file_path}")
            else:
                self.log(f"  ❌ {file_path} (missing)")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        self.log("📊 Generating Summary Report", "STEP")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "demo_data": self.demo_data,
            "project_id": self.project_id,
            "capabilities_demonstrated": [
                "Organization and project management",
                "Database schema inspection",
                "Security and performance analysis", 
                "Edge Functions management",
                "Branch-based development workflow",
                "GitHub integration patterns"
            ],
            "tools_used": [
                "list_organizations", "list_projects", "list_tables",
                "list_extensions", "generate_typescript_types",
                "get_advisors", "list_edge_functions", "list_branches",
                "get_cost"
            ],
            "next_steps": [
                "Set up SUPABASE_ACCESS_TOKEN environment variable",
                "Create a new Supabase project for testing",
                "Configure GitHub repository secrets",
                "Deploy sample Edge Functions",
                "Set up branch-based development workflow"
            ]
        }
        
        # Save report
        report_file = f"demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"Report saved to: {report_file}", "SUCCESS")
        
        # Display summary
        self.log("\n🎯 Demo Summary:")
        self.log(f"  • Demonstrated {len(report['capabilities_demonstrated'])} major capabilities")
        self.log(f"  • Used {len(report['tools_used'])} MCP tools")
        self.log(f"  • Generated {len(report['next_steps'])} next steps")
        
        return report
    
    def run_full_demo(self):
        """Execute the complete demonstration"""
        self.log("🚀 Starting Supabase MCP Full Demonstration")
        self.log("=" * 60)
        
        try:
            # Run all demonstration modules
            self.demonstrate_organization_management()
            print()
            
            self.demonstrate_database_operations()
            print()
            
            self.demonstrate_security_analysis()
            print()
            
            self.demonstrate_edge_functions()
            print()
            
            self.demonstrate_branch_workflow()
            print()
            
            self.demonstrate_github_integration()
            print()
            
            # Generate final report
            report = self.generate_summary_report()
            
            self.log("\n🎉 Demo completed successfully!", "SUCCESS")
            self.log("Check the generated report for detailed information.")
            
            return True
            
        except Exception as e:
            self.log(f"Demo failed with error: {e}", "ERROR")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Supabase MCP Full Demo")
    parser.add_argument("--project-id", help="Specific project ID to use")
    
    args = parser.parse_args()
    
    demo = SupabaseFullDemo(project_id=args.project_id)
    success = demo.run_full_demo()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
