import requests
import sys
import json
from datetime import datetime
import uuid

class ITAssetManagementReviewTester:
    def __init__(self, base_url="https://assetmaster-13.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data storage
        self.created_org_id = None
        self.created_group_id = None
        self.created_type_id = None
        self.created_asset_id = None
        self.created_custom_template_id = None

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "response_data": response_data
        })

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            response_data = None
            
            try:
                response_data = response.json()
            except:
                response_data = response.text

            return success, response_data, response.status_code

        except Exception as e:
            return False, str(e), 0

    def setup_test_environment(self):
        """Setup test environment with user, organization, and basic data"""
        print("🔧 Setting up test environment...")
        
        # Register user
        test_email = f"review_test_{datetime.now().strftime('%H%M%S')}@example.com"
        user_data = {
            "name": "Review Test User",
            "email": test_email,
            "password": "ReviewTest123!",
            "role": "admin"
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/register', user_data, 200)
        if not success:
            print(f"❌ Failed to register user: {status_code} - {response_data}")
            return False
        
        self.user_data = user_data
        
        # Login
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/login', login_data, 200)
        if not success or 'access_token' not in response_data:
            print(f"❌ Failed to login: {status_code} - {response_data}")
            return False
        
        self.token = response_data['access_token']
        
        # Create organization
        org_data = {
            "name": f"Review Test Org {datetime.now().strftime('%H%M%S')}",
            "description": "Organization for review testing"
        }
        
        success, response_data, status_code = self.make_request('POST', 'organizations', org_data, 200)
        if not success or 'id' not in response_data:
            print(f"❌ Failed to create organization: {status_code} - {response_data}")
            return False
        
        self.created_org_id = response_data['id']
        print(f"✅ Test environment setup complete - Org ID: {self.created_org_id}")
        return True

    def test_1_basic_backend_health(self):
        """Test 1: Basic Backend Health - Verify all core endpoints are working"""
        print("\n🏥 Test 1: Basic Backend Health")
        
        # Test authentication endpoint
        success, response_data, status_code = self.make_request('GET', 'auth/me', expected_status=200)
        if success:
            self.log_test("Authentication Endpoint Health", True, f"User: {response_data.get('name', 'Unknown')}")
        else:
            self.log_test("Authentication Endpoint Health", False, f"Status: {status_code}")
            return False
        
        # Test organizations endpoint
        success, response_data, status_code = self.make_request('GET', 'organizations', expected_status=200)
        if success and isinstance(response_data, list):
            self.log_test("Organizations Endpoint Health", True, f"Found {len(response_data)} organizations")
        else:
            self.log_test("Organizations Endpoint Health", False, f"Status: {status_code}")
            return False
        
        # Test asset groups endpoint
        success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}/asset-groups', expected_status=200)
        if success and isinstance(response_data, list):
            self.log_test("Asset Groups Endpoint Health", True, f"Endpoint accessible")
        else:
            self.log_test("Asset Groups Endpoint Health", False, f"Status: {status_code}")
            return False
        
        # Test assets endpoint
        success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}/assets', expected_status=200)
        if success and isinstance(response_data, list):
            self.log_test("Assets Endpoint Health", True, f"Endpoint accessible")
        else:
            self.log_test("Assets Endpoint Health", False, f"Status: {status_code}")
            return False
        
        return True

    def test_2_asset_crud_operations(self):
        """Test 2: Asset CRUD Operations - Test creating, reading, updating, and deleting assets with custom fields"""
        print("\n💻 Test 2: Asset CRUD Operations with Custom Fields")
        
        # Create asset group with custom fields
        group_data = {
            "name": "IT Hardware Assets",
            "description": "Hardware devices with custom tracking fields",
            "organization_id": self.created_org_id,
            "custom_fields": [
                {
                    "name": "serial_number",
                    "label": "Serial Number",
                    "type": "text",
                    "required": True
                },
                {
                    "name": "purchase_date",
                    "label": "Purchase Date",
                    "type": "date",
                    "required": True
                },
                {
                    "name": "warranty_years",
                    "label": "Warranty Years",
                    "type": "number",
                    "default_value": 3
                },
                {
                    "name": "is_critical",
                    "label": "Critical Asset",
                    "type": "boolean",
                    "default_value": False
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        if not success or 'id' not in response_data:
            self.log_test("Create Asset Group with Custom Fields", False, f"Status: {status_code}")
            return False
        
        self.created_group_id = response_data['id']
        self.log_test("Create Asset Group with Custom Fields", True, f"Group ID: {self.created_group_id}")
        
        # Create asset type
        type_data = {
            "name": "Laptops",
            "description": "Portable computers",
            "asset_group_id": self.created_group_id,
            "custom_fields": [
                {
                    "name": "cpu_model",
                    "label": "CPU Model",
                    "type": "text",
                    "required": True
                },
                {
                    "name": "ram_gb",
                    "label": "RAM (GB)",
                    "type": "number",
                    "default_value": 8
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-types', type_data, 200)
        if not success or 'id' not in response_data:
            self.log_test("Create Asset Type with Custom Fields", False, f"Status: {status_code}")
            return False
        
        self.created_type_id = response_data['id']
        self.log_test("Create Asset Type with Custom Fields", True, f"Type ID: {self.created_type_id}")
        
        # CREATE: Create asset with custom fields
        asset_data = {
            "name": "MacBook Pro 16-inch M3",
            "description": "Development laptop for senior engineer",
            "asset_type_id": self.created_type_id,
            "custom_data": {
                "serial_number": "MBP2024001",
                "purchase_date": "2024-01-15",
                "warranty_years": 3,
                "is_critical": True,
                "cpu_model": "Apple M3 Pro",
                "ram_gb": 32
            },
            "tags": ["development", "high-performance"],
            "relationships": []
        }
        
        success, response_data, status_code = self.make_request('POST', 'assets', asset_data, 200)
        if not success or 'id' not in response_data:
            self.log_test("CREATE Asset with Custom Fields", False, f"Status: {status_code}")
            return False
        
        self.created_asset_id = response_data['id']
        self.log_test("CREATE Asset with Custom Fields", True, f"Asset ID: {self.created_asset_id}")
        
        # READ: Get asset and verify custom fields
        success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}/assets', expected_status=200)
        if success and isinstance(response_data, list) and len(response_data) > 0:
            asset = next((a for a in response_data if a['id'] == self.created_asset_id), None)
            if asset and 'custom_data' in asset:
                custom_data = asset['custom_data']
                required_fields = ['serial_number', 'purchase_date', 'cpu_model']
                missing_fields = [field for field in required_fields if field not in custom_data]
                
                if not missing_fields:
                    self.log_test("READ Asset with Custom Fields", True, f"All custom fields present")
                else:
                    self.log_test("READ Asset with Custom Fields", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("READ Asset with Custom Fields", False, "Asset not found or missing custom_data")
                return False
        else:
            self.log_test("READ Asset with Custom Fields", False, f"Status: {status_code}")
            return False
        
        # UPDATE: Update asset with new custom field values
        update_data = {
            "name": "MacBook Pro 16-inch M3 (Updated)",
            "description": "Updated development laptop",
            "custom_data": {
                "serial_number": "MBP2024001-UPD",
                "purchase_date": "2024-01-15",
                "warranty_years": 4,
                "is_critical": True,
                "cpu_model": "Apple M3 Pro (Updated)",
                "ram_gb": 64,
                "updated_field": "new_value"
            },
            "tags": ["development", "high-performance", "updated"]
        }
        
        success, response_data, status_code = self.make_request('PUT', f'assets/{self.created_asset_id}', update_data, 200)
        if success and 'id' in response_data:
            # Verify update worked
            if (response_data.get('name') == update_data['name'] and 
                'custom_data' in response_data and 
                response_data['custom_data'].get('serial_number') == 'MBP2024001-UPD'):
                self.log_test("UPDATE Asset with Custom Fields", True, "Asset updated successfully")
            else:
                self.log_test("UPDATE Asset with Custom Fields", False, "Update verification failed")
                return False
        else:
            self.log_test("UPDATE Asset with Custom Fields", False, f"Status: {status_code}")
            return False
        
        # DELETE: Delete asset
        success, response_data, status_code = self.make_request('DELETE', f'assets/{self.created_asset_id}', expected_status=200)
        if success:
            self.log_test("DELETE Asset", True, "Asset deleted successfully")
        else:
            self.log_test("DELETE Asset", False, f"Status: {status_code}")
            return False
        
        # Verify deletion
        success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}/assets', expected_status=200)
        if success and isinstance(response_data, list):
            asset_exists = any(a['id'] == self.created_asset_id for a in response_data)
            if not asset_exists:
                self.log_test("Verify Asset Deletion", True, "Asset successfully removed")
            else:
                self.log_test("Verify Asset Deletion", False, "Asset still exists after deletion")
                return False
        else:
            self.log_test("Verify Asset Deletion", False, f"Status: {status_code}")
            return False
        
        return True

    def test_3_custom_template_endpoints(self):
        """Test 3: Custom Template Endpoints - Verify the custom template CRUD operations work correctly"""
        print("\n📋 Test 3: Custom Template CRUD Operations")
        
        # CREATE: Create custom template
        template_data = {
            "name": "Custom Server Template",
            "description": "Custom template for server assets",
            "icon": "Server",
            "template_type": "asset_group",
            "custom_fields": [
                {
                    "name": "server_type",
                    "label": "Server Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["web", "database", "application", "file"],
                    "default_value": "web"
                },
                {
                    "name": "cpu_cores",
                    "label": "CPU Cores",
                    "type": "number",
                    "required": True,
                    "default_value": 4
                },
                {
                    "name": "memory_gb",
                    "label": "Memory (GB)",
                    "type": "number",
                    "required": True,
                    "default_value": 16
                },
                {
                    "name": "storage_type",
                    "label": "Storage Type",
                    "type": "dataset",
                    "dataset_values": ["SSD", "HDD", "NVMe"],
                    "default_value": "SSD"
                },
                {
                    "name": "backup_enabled",
                    "label": "Backup Enabled",
                    "type": "boolean",
                    "default_value": True
                }
            ],
            "organization_id": self.created_org_id,
            "is_public": False
        }
        
        success, response_data, status_code = self.make_request('POST', 'templates/custom', template_data, 200)
        if not success or 'id' not in response_data:
            self.log_test("CREATE Custom Template", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        self.created_custom_template_id = response_data['id']
        self.log_test("CREATE Custom Template", True, f"Template ID: {self.created_custom_template_id}")
        
        # READ: Get custom templates
        success, response_data, status_code = self.make_request('GET', 'templates/custom', expected_status=200)
        if success and isinstance(response_data, list):
            template = next((t for t in response_data if t['id'] == self.created_custom_template_id), None)
            if template:
                if (template['name'] == template_data['name'] and 
                    len(template.get('custom_fields', [])) == 5):
                    self.log_test("READ Custom Templates", True, f"Found template with {len(template['custom_fields'])} fields")
                else:
                    self.log_test("READ Custom Templates", False, "Template data mismatch")
                    return False
            else:
                self.log_test("READ Custom Templates", False, "Created template not found")
                return False
        else:
            self.log_test("READ Custom Templates", False, f"Status: {status_code}")
            return False
        
        # UPDATE: Update custom template
        update_data = {
            "name": "Updated Custom Server Template",
            "description": "Updated custom template for server assets",
            "icon": "Database",
            "template_type": "asset_group",
            "custom_fields": [
                {
                    "name": "server_type",
                    "label": "Server Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["web", "database", "application", "file", "cache"],
                    "default_value": "web"
                },
                {
                    "name": "cpu_cores",
                    "label": "CPU Cores",
                    "type": "number",
                    "required": True,
                    "default_value": 8
                },
                {
                    "name": "memory_gb",
                    "label": "Memory (GB)",
                    "type": "number",
                    "required": True,
                    "default_value": 32
                },
                {
                    "name": "storage_type",
                    "label": "Storage Type",
                    "type": "dataset",
                    "dataset_values": ["SSD", "HDD", "NVMe"],
                    "default_value": "NVMe"
                },
                {
                    "name": "backup_enabled",
                    "label": "Backup Enabled",
                    "type": "boolean",
                    "default_value": True
                },
                {
                    "name": "monitoring_enabled",
                    "label": "Monitoring Enabled",
                    "type": "boolean",
                    "default_value": True
                }
            ],
            "organization_id": self.created_org_id,
            "is_public": True
        }
        
        success, response_data, status_code = self.make_request('PUT', f'templates/custom/{self.created_custom_template_id}', update_data, 200)
        if success and 'id' in response_data:
            if (response_data.get('name') == update_data['name'] and 
                len(response_data.get('custom_fields', [])) == 6 and
                response_data.get('is_public') == True):
                self.log_test("UPDATE Custom Template", True, "Template updated successfully")
            else:
                self.log_test("UPDATE Custom Template", False, "Update verification failed")
                return False
        else:
            self.log_test("UPDATE Custom Template", False, f"Status: {status_code}")
            return False
        
        # DELETE: Delete custom template
        success, response_data, status_code = self.make_request('DELETE', f'templates/custom/{self.created_custom_template_id}', expected_status=200)
        if success:
            self.log_test("DELETE Custom Template", True, "Template deleted successfully")
        else:
            self.log_test("DELETE Custom Template", False, f"Status: {status_code}")
            return False
        
        # Verify deletion
        success, response_data, status_code = self.make_request('GET', 'templates/custom', expected_status=200)
        if success and isinstance(response_data, list):
            template_exists = any(t['id'] == self.created_custom_template_id for t in response_data)
            if not template_exists:
                self.log_test("Verify Custom Template Deletion", True, "Template successfully removed")
            else:
                self.log_test("Verify Custom Template Deletion", False, "Template still exists after deletion")
                return False
        else:
            self.log_test("Verify Custom Template Deletion", False, f"Status: {status_code}")
            return False
        
        return True

    def test_4_default_template_endpoints(self):
        """Test 4: Default Template Endpoints - Verify these are still working"""
        print("\n🏗️ Test 4: Default Template Endpoints")
        
        # Test default asset groups templates
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        if success and isinstance(response_data, list):
            if len(response_data) > 0:
                # Verify template structure
                first_template = response_data[0]
                required_fields = ['name', 'description', 'icon', 'custom_fields']
                missing_fields = [field for field in required_fields if field not in first_template]
                
                if not missing_fields:
                    self.log_test("GET Default Asset Groups Templates", True, f"Found {len(response_data)} templates with proper structure")
                else:
                    self.log_test("GET Default Asset Groups Templates", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("GET Default Asset Groups Templates", False, "No templates found")
                return False
        else:
            self.log_test("GET Default Asset Groups Templates", False, f"Status: {status_code}")
            return False
        
        # Test default asset types templates
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-types', expected_status=200)
        if success and isinstance(response_data, list):
            if len(response_data) > 0:
                # Verify template structure
                first_template = response_data[0]
                required_fields = ['name', 'description', 'icon', 'custom_fields']
                missing_fields = [field for field in required_fields if field not in first_template]
                
                if not missing_fields:
                    self.log_test("GET Default Asset Types Templates", True, f"Found {len(response_data)} templates with proper structure")
                else:
                    self.log_test("GET Default Asset Types Templates", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("GET Default Asset Types Templates", False, "No templates found")
                return False
        else:
            self.log_test("GET Default Asset Types Templates", False, f"Status: {status_code}")
            return False
        
        # Test default assets templates
        success, response_data, status_code = self.make_request('GET', 'templates/default-assets', expected_status=200)
        if success and isinstance(response_data, list):
            if len(response_data) > 0:
                self.log_test("GET Default Assets Templates", True, f"Found {len(response_data)} asset templates")
            else:
                self.log_test("GET Default Assets Templates", True, "No asset templates found (acceptable)")
        else:
            self.log_test("GET Default Assets Templates", False, f"Status: {status_code}")
            return False
        
        return True

    def test_5_detailed_assets_endpoint(self):
        """Test 5: Detailed Assets Endpoint - Test GET /api/organizations/{org_id}/assets/detailed for drag-and-drop functionality"""
        print("\n📊 Test 5: Detailed Assets Endpoint for Drag-and-Drop")
        
        # First, create some test assets for the detailed endpoint
        # Create asset group
        group_data = {
            "name": "Test Hardware Group",
            "description": "Test group for detailed assets",
            "organization_id": self.created_org_id
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        if not success:
            self.log_test("Setup Asset Group for Detailed Test", False, f"Status: {status_code}")
            return False
        
        group_id = response_data['id']
        
        # Create asset type
        type_data = {
            "name": "Test Computers",
            "description": "Test computer type",
            "asset_group_id": group_id
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-types', type_data, 200)
        if not success:
            self.log_test("Setup Asset Type for Detailed Test", False, f"Status: {status_code}")
            return False
        
        type_id = response_data['id']
        
        # Create multiple test assets
        test_assets = []
        for i in range(3):
            asset_data = {
                "name": f"Test Asset {i+1}",
                "description": f"Test asset number {i+1}",
                "asset_type_id": type_id,
                "custom_data": {
                    "test_field": f"value_{i+1}"
                },
                "tags": [f"test_{i+1}"]
            }
            
            success, response_data, status_code = self.make_request('POST', 'assets', asset_data, 200)
            if success:
                test_assets.append(response_data['id'])
        
        if len(test_assets) != 3:
            self.log_test("Setup Test Assets for Detailed Test", False, f"Only created {len(test_assets)} assets")
            return False
        
        # Test the detailed assets endpoint
        success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}/assets/detailed', expected_status=200)
        
        if success and isinstance(response_data, list):
            if len(response_data) >= 3:
                # Verify detailed information is included
                first_asset = response_data[0]
                required_detailed_fields = ['asset_type_name', 'asset_group_name']
                missing_fields = [field for field in required_detailed_fields if field not in first_asset]
                
                if not missing_fields:
                    # Verify all standard asset fields are present
                    standard_fields = ['id', 'name', 'description', 'asset_type_id', 'asset_group_id', 'organization_id']
                    missing_standard = [field for field in standard_fields if field not in first_asset]
                    
                    if not missing_standard:
                        self.log_test("GET Detailed Assets Endpoint", True, f"Found {len(response_data)} detailed assets with proper structure")
                        
                        # Verify the detailed fields have actual values
                        asset_type_name = first_asset.get('asset_type_name')
                        asset_group_name = first_asset.get('asset_group_name')
                        
                        if asset_type_name and asset_group_name and asset_type_name != "Unknown" and asset_group_name != "Unknown":
                            self.log_test("Verify Detailed Asset Information", True, f"Asset type: {asset_type_name}, Asset group: {asset_group_name}")
                        else:
                            self.log_test("Verify Detailed Asset Information", False, f"Invalid detailed info - Type: {asset_type_name}, Group: {asset_group_name}")
                            return False
                    else:
                        self.log_test("GET Detailed Assets Endpoint", False, f"Missing standard fields: {missing_standard}")
                        return False
                else:
                    self.log_test("GET Detailed Assets Endpoint", False, f"Missing detailed fields: {missing_fields}")
                    return False
            else:
                self.log_test("GET Detailed Assets Endpoint", False, f"Expected at least 3 assets, found {len(response_data)}")
                return False
        else:
            self.log_test("GET Detailed Assets Endpoint", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return True

    def run_review_tests(self):
        """Run all review-focused tests"""
        print(f"🚀 Starting IT Asset Management Review-Focused Backend Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Setup test environment
        if not self.setup_test_environment():
            print("❌ Test environment setup failed - stopping tests")
            return self.generate_report()
        
        # Run the 5 main test categories from the review request
        test_results = []
        
        test_results.append(self.test_1_basic_backend_health())
        test_results.append(self.test_2_asset_crud_operations())
        test_results.append(self.test_3_custom_template_endpoints())
        test_results.append(self.test_4_default_template_endpoints())
        test_results.append(self.test_5_detailed_assets_endpoint())
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 70)
        print(f"📊 IT Asset Management Review Test Results")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Show failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All review tests passed!")
            return 0
        else:
            print("⚠️ Some tests failed. Check the details above.")
            return 1

def main():
    tester = ITAssetManagementReviewTester()
    return tester.run_review_tests()

if __name__ == "__main__":
    sys.exit(main())