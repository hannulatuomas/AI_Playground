import requests
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

class EmergentNexusAPITester:
    def __init__(self, base_url="https://emergent-nexus.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.created_nodes = []
        self.created_relations = []

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, data: Dict = None, headers: Dict = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_base}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json() if response.text else {}
                except:
                    response_data = {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                response_data = {}

            return success, response_data

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_create_markdown_node(self):
        """Test creating a markdown note"""
        node_data = {
            "node_type": "markdown",
            "title": "Test Markdown Note",
            "content": {
                "markdown": "# Test Note\n\nThis is a test note with [[Test Link]] syntax."
            },
            "tags": ["test", "markdown"]
        }
        
        success, response = self.run_test(
            "Create Markdown Node",
            "POST",
            "nodes",
            200,
            data=node_data
        )
        
        if success and 'id' in response:
            self.created_nodes.append(response['id'])
            return response['id']
        return None

    def test_create_kanban_card(self):
        """Test creating a kanban card"""
        card_data = {
            "node_type": "kanban-card",
            "title": "Test Kanban Card",
            "content": {
                "description": "This is a test kanban card",
                "status": "todo",
                "assignee": "Test User",
                "dueDate": "2024-12-31"
            },
            "tags": ["test", "kanban"]
        }
        
        success, response = self.run_test(
            "Create Kanban Card",
            "POST",
            "nodes",
            200,
            data=card_data
        )
        
        if success and 'id' in response:
            self.created_nodes.append(response['id'])
            return response['id']
        return None

    def test_create_evidence_item(self):
        """Test creating an evidence board item"""
        evidence_data = {
            "node_type": "evidence-item",
            "title": "Test Evidence Item",
            "content": {
                "description": "This is a test evidence item",
                "type": "evidence",
                "x": 100,
                "y": 150
            },
            "tags": ["test", "evidence"]
        }
        
        success, response = self.run_test(
            "Create Evidence Item",
            "POST",
            "nodes",
            200,
            data=evidence_data
        )
        
        if success and 'id' in response:
            self.created_nodes.append(response['id'])
            return response['id']
        return None

    def test_get_all_nodes(self):
        """Test fetching all nodes"""
        success, response = self.run_test(
            "Get All Nodes",
            "GET",
            "nodes",
            200
        )
        
        if success:
            print(f"   Found {len(response)} nodes")
            return response
        return []

    def test_get_node_by_id(self, node_id: str):
        """Test fetching a specific node"""
        if not node_id:
            print("❌ No node ID provided for get test")
            return False
            
        success, response = self.run_test(
            f"Get Node by ID ({node_id[:8]}...)",
            "GET",
            f"nodes/{node_id}",
            200
        )
        return success

    def test_update_node(self, node_id: str):
        """Test updating a node"""
        if not node_id:
            print("❌ No node ID provided for update test")
            return False
            
        update_data = {
            "node_type": "markdown",
            "title": "Updated Test Note",
            "content": {
                "markdown": "# Updated Note\n\nThis note has been updated."
            },
            "tags": ["test", "updated"]
        }
        
        success, response = self.run_test(
            f"Update Node ({node_id[:8]}...)",
            "PUT",
            f"nodes/{node_id}",
            200,
            data=update_data
        )
        return success

    def test_get_nodes_by_type(self, node_type: str):
        """Test fetching nodes by type"""
        success, response = self.run_test(
            f"Get Nodes by Type ({node_type})",
            "GET",
            f"nodes/type/{node_type}",
            200
        )
        
        if success:
            print(f"   Found {len(response)} {node_type} nodes")
        return success

    def test_create_relation(self, from_id: str, to_id: str):
        """Test creating a relation between nodes"""
        if not from_id or not to_id:
            print("❌ Missing node IDs for relation test")
            return False
            
        relation_data = {
            "from_id": from_id,
            "to_id": to_id,
            "relation_type": "links-to",
            "color": "#3b82f6",
            "label": "test connection"
        }
        
        success, response = self.run_test(
            f"Create Relation ({from_id[:8]}... -> {to_id[:8]}...)",
            "POST",
            "relations",
            200,
            data=relation_data
        )
        
        if success:
            self.created_relations.append((from_id, to_id))
        return success

    def test_get_all_relations(self):
        """Test fetching all relations"""
        success, response = self.run_test(
            "Get All Relations",
            "GET",
            "relations",
            200
        )
        
        if success:
            print(f"   Found {len(response)} relations")
        return success

    def test_get_node_relations(self, node_id: str):
        """Test fetching relations for a specific node"""
        if not node_id:
            print("❌ No node ID provided for relations test")
            return False
            
        success, response = self.run_test(
            f"Get Node Relations ({node_id[:8]}...)",
            "GET",
            f"relations/node/{node_id}",
            200
        )
        
        if success:
            print(f"   Found {len(response)} relations for node")
        return success

    def test_delete_relation(self, from_id: str, to_id: str):
        """Test deleting a relation"""
        if not from_id or not to_id:
            print("❌ Missing node IDs for delete relation test")
            return False
            
        success, response = self.run_test(
            f"Delete Relation ({from_id[:8]}... -> {to_id[:8]}...)",
            "DELETE",
            f"relations/{from_id}/{to_id}",
            200
        )
        return success

    def test_delete_node(self, node_id: str):
        """Test deleting a node"""
        if not node_id:
            print("❌ No node ID provided for delete test")
            return False
            
        success, response = self.run_test(
            f"Delete Node ({node_id[:8]}...)",
            "DELETE",
            f"nodes/{node_id}",
            200
        )
        return success

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete relations first
        for from_id, to_id in self.created_relations:
            self.test_delete_relation(from_id, to_id)
        
        # Delete nodes
        for node_id in self.created_nodes:
            self.test_delete_node(node_id)

    def run_comprehensive_test(self):
        """Run all API tests"""
        print("🚀 Starting Emergent Nexus API Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)

        # Basic connectivity tests
        self.test_health_check()
        self.test_root_endpoint()

        # Node CRUD tests
        markdown_id = self.test_create_markdown_node()
        kanban_id = self.test_create_kanban_card()
        evidence_id = self.test_create_evidence_item()

        # Test fetching nodes
        self.test_get_all_nodes()
        
        if markdown_id:
            self.test_get_node_by_id(markdown_id)
            self.test_update_node(markdown_id)

        # Test nodes by type
        self.test_get_nodes_by_type("markdown")
        self.test_get_nodes_by_type("kanban-card")
        self.test_get_nodes_by_type("evidence-item")

        # Relation tests
        if markdown_id and kanban_id:
            self.test_create_relation(markdown_id, kanban_id)
            self.test_get_node_relations(markdown_id)
        
        if markdown_id and evidence_id:
            self.test_create_relation(markdown_id, evidence_id)

        self.test_get_all_relations()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            success_rate = 100
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            success_rate = (self.tests_passed / self.tests_run) * 100

        # Cleanup
        self.cleanup_test_data()
        
        return success_rate >= 80  # Consider 80%+ as success

def main():
    tester = EmergentNexusAPITester()
    success = tester.run_comprehensive_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())