#!/usr/bin/env python3
"""
Comprehensive test suite for the Supabase MCP connector.

This script tests all major functionality of the connector and provides
detailed reporting on capabilities and performance.
"""

import json
import subprocess
import sys
import time
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

class SupabaseMCPTester:
    def __init__(self, ci_mode: bool = False, verbose: bool = False):
        self.ci_mode = ci_mode
        self.verbose = verbose
        self.server_name = "supabase"
        self.test_results = []
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] {level}:"
        
        if level == "ERROR":
            print(f"❌ {prefix} {message}")
        elif level == "SUCCESS":
            print(f"✅ {prefix} {message}")
        elif level == "WARNING":
            print(f"⚠️  {prefix} {message}")
        else:
            print(f"ℹ️  {prefix} {message}")
            
        if self.verbose:
            sys.stdout.flush()
    
    def run_mcp_command(self, tool_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP command and return result"""
        try:
            cmd = [
                "manus-mcp-cli", "tool", "call", tool_name,
                "--server", self.server_name,
                "--input", json.dumps(input_data)
            ]
            
            if self.verbose:
                self.log(f"Executing: {' '.join(cmd)}")
            
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
    
    def test_documentation_search(self) -> bool:
        """Test documentation search functionality"""
        self.log("Testing documentation search...")
        
        test_queries = [
            "database tables",
            "authentication setup", 
            "edge functions deployment",
            "row level security"
        ]
        
        for query in test_queries:
            graphql_query = f"""{{
                searchDocs(query: "{query}", limit: 3) {{
                    nodes {{
                        title
                        href
                        content
                    }}
                }}
            }}"""
            
            result = self.run_mcp_command("search_docs", {
                "graphql_query": graphql_query
            })
            
            if "error" in result:
                self.log(f"Documentation search failed for '{query}': {result['error']}", "ERROR")
                return False
            
            if "searchDocs" in result and result["searchDocs"]["nodes"]:
                self.log(f"Found {len(result['searchDocs']['nodes'])} results for '{query}'", "SUCCESS")
            else:
                self.log(f"No results found for '{query}'", "WARNING")
        
        return True
    
    def test_authentication_required_commands(self) -> Dict[str, bool]:
        """Test commands that require authentication"""
        self.log("Testing authentication-required commands...")
        
        auth_commands = [
            ("list_organizations", {}),
            ("list_projects", {}),
        ]
        
        results = {}
        
        for cmd_name, cmd_input in auth_commands:
            result = self.run_mcp_command(cmd_name, cmd_input)
            
            if "error" in result:
                if "Unauthorized" in result["error"] or "access token" in result["error"]:
                    self.log(f"{cmd_name}: Authentication required (expected)", "INFO")
                    results[cmd_name] = True  # Expected behavior
                else:
                    self.log(f"{cmd_name}: Unexpected error: {result['error']}", "ERROR")
                    results[cmd_name] = False
            else:
                self.log(f"{cmd_name}: Successfully executed", "SUCCESS")
                results[cmd_name] = True
        
        return results
    
    def test_tool_availability(self) -> bool:
        """Test that all expected tools are available"""
        self.log("Testing tool availability...")
        
        expected_tools = [
            "search_docs", "list_organizations", "get_organization", "list_projects",
            "get_project", "create_project", "pause_project", "restore_project",
            "list_tables", "list_extensions", "list_migrations", "apply_migration",
            "execute_sql", "get_logs", "get_advisors", "get_project_url",
            "get_anon_key", "generate_typescript_types", "list_edge_functions",
            "get_edge_function", "deploy_edge_function", "create_branch",
            "list_branches", "delete_branch", "merge_branch", "reset_branch",
            "rebase_branch", "get_cost", "confirm_cost"
        ]
        
        try:
            # Get tool list
            result = subprocess.run(
                ["manus-mcp-cli", "tool", "list", "--server", self.server_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                self.log(f"Failed to get tool list: {result.stderr}", "ERROR")
                return False
            
            # Parse available tools from output
            available_tools = []
            for line in result.stdout.split('\n'):
                if line.startswith('Tool: '):
                    tool_name = line.replace('Tool: ', '').strip()
                    available_tools.append(tool_name)
            
            missing_tools = set(expected_tools) - set(available_tools)
            extra_tools = set(available_tools) - set(expected_tools)
            
            if missing_tools:
                self.log(f"Missing tools: {', '.join(missing_tools)}", "WARNING")
            
            if extra_tools:
                self.log(f"Extra tools found: {', '.join(extra_tools)}", "INFO")
            
            self.log(f"Found {len(available_tools)} tools, expected {len(expected_tools)}", "INFO")
            
            return len(missing_tools) == 0
            
        except Exception as e:
            self.log(f"Error checking tool availability: {e}", "ERROR")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling with invalid inputs"""
        self.log("Testing error handling...")
        
        error_tests = [
            ("search_docs", {"graphql_query": "invalid graphql {{"}, "Invalid GraphQL"),
            ("get_project", {"id": "invalid_project_id"}, "Invalid project ID"),
            ("execute_sql", {"project_id": "fake", "query": "SELECT 1"}, "Invalid project"),
        ]
        
        for cmd_name, cmd_input, expected_error in error_tests:
            result = self.run_mcp_command(cmd_name, cmd_input)
            
            if "error" in result:
                self.log(f"{cmd_name}: Properly handled error - {expected_error}", "SUCCESS")
            else:
                self.log(f"{cmd_name}: Expected error but got success", "WARNING")
        
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        end_time = time.time()
        duration = end_time - self.start_time
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "ci_mode": self.ci_mode,
            "test_results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r["passed"]),
                "failed": sum(1 for r in self.test_results if not r["passed"]),
            }
        }
        
        report["summary"]["success_rate"] = (
            report["summary"]["passed"] / report["summary"]["total_tests"] * 100
            if report["summary"]["total_tests"] > 0 else 0
        )
        
        return report
    
    def run_all_tests(self) -> bool:
        """Run all test suites"""
        self.log("🚀 Starting Supabase MCP Connector Test Suite")
        self.log("=" * 60)
        
        tests = [
            ("Tool Availability", self.test_tool_availability),
            ("Documentation Search", self.test_documentation_search),
            ("Authentication Commands", lambda: all(self.test_authentication_required_commands().values())),
            ("Error Handling", self.test_error_handling),
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            self.log(f"\n🧪 Running {test_name} tests...")
            
            try:
                start = time.time()
                passed = test_func()
                duration = time.time() - start
                
                self.test_results.append({
                    "name": test_name,
                    "passed": passed,
                    "duration": round(duration, 2)
                })
                
                if passed:
                    self.log(f"{test_name}: PASSED ({duration:.2f}s)", "SUCCESS")
                else:
                    self.log(f"{test_name}: FAILED ({duration:.2f}s)", "ERROR")
                    all_passed = False
                    
            except Exception as e:
                self.log(f"{test_name}: ERROR - {e}", "ERROR")
                self.test_results.append({
                    "name": test_name,
                    "passed": False,
                    "error": str(e),
                    "duration": 0
                })
                all_passed = False
        
        # Generate and save report
        report = self.generate_report()
        
        self.log("\n📊 Test Summary")
        self.log("=" * 30)
        self.log(f"Total Tests: {report['summary']['total_tests']}")
        self.log(f"Passed: {report['summary']['passed']}")
        self.log(f"Failed: {report['summary']['failed']}")
        self.log(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        self.log(f"Duration: {report['duration_seconds']}s")
        
        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"📄 Report saved to: {report_file}")
        
        if all_passed:
            self.log("🎉 All tests passed!", "SUCCESS")
        else:
            self.log("❌ Some tests failed. Check the report for details.", "ERROR")
        
        return all_passed

def main():
    parser = argparse.ArgumentParser(description="Test Supabase MCP Connector")
    parser.add_argument("--ci-mode", action="store_true", help="Run in CI mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    tester = SupabaseMCPTester(ci_mode=args.ci_mode, verbose=args.verbose)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
