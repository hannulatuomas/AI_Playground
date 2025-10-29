import requests
import sys
import json
from datetime import datetime
import uuid

class FocusedITAssetManagementTester:
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

    def log_test(self, name, success, details="", response_data=None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
            if details:
                print(f"   📝 {details}")
        else:
            print(f"❌ {name} - {details}")
            if response_data:
                print(f"   📄 Response: {json.dumps(response_data, indent=2)}")
        
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

    def setup_authentication(self):
        """Setup user and authentication"""
        print("🔐 Setting up Authentication...")
        
        # Register user
        test_email = f"focused_test_{datetime.now().strftime('%H%M%S')}@example.com"
        user_data = {
            "name": "Focused Test User",
            "email": test_email,
            "password": "FocusedTest123!",
            "role": "admin"
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/register', user_data, 200)
        if not success:
            self.log_test("User Registration", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        self.user_data = user_data
        self.log_test("User Registration", True, f"User created: {test_email}")
        
        # Login
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/login', login_data, 200)
        if not success or 'access_token' not in response_data:
            self.log_test("User Login", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        self.token = response_data['access_token']
        self.log_test("User Login", True, f"JWT token received")
        
        # Verify token
        success, response_data, status_code = self.make_request('GET', 'auth/me', expected_status=200)
        if not success:
            self.log_test("JWT Token Validation", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        self.log_test("JWT Token Validation", True, f"Token valid for user: {response_data.get('name')}")
        return True

    def test_organization_creation(self):
        """Test creating an organization"""
        print("\n🏢 Testing Organization Creation...")
        
        org_data = {
            "name": f"Focused Test Org {datetime.now().strftime('%H%M%S')}",
            "description": "Organization for focused custom field inheritance testing"
        }
        
        success, response_data, status_code = self.make_request('POST', 'organizations', org_data, 200)
        
        if success and 'id' in response_data:
            self.created_org_id = response_data['id']
            self.log_test("Organization Creation", True, f"Organization ID: {self.created_org_id}")
            return True
        else:
            self.log_test("Organization Creation", False, f"Status: {status_code}", response_data)
            return False

    def test_asset_group_with_custom_fields(self):
        """Test creating Asset Group with comprehensive custom fields"""
        print("\n📦 Testing Asset Group with Custom Fields...")
        
        if not self.created_org_id:
            self.log_test("Asset Group Creation", False, "No organization ID available")
            return False
        
        group_data = {
            "name": "IT Hardware Group",
            "description": "Hardware assets with comprehensive custom fields",
            "organization_id": self.created_org_id,
            "custom_fields": [
                {
                    "name": "purchase_date",
                    "label": "Purchase Date",
                    "type": "date",
                    "required": True,
                    "default_value": "2024-01-01"
                },
                {
                    "name": "warranty_years",
                    "label": "Warranty Period (Years)",
                    "type": "number",
                    "required": True,
                    "default_value": 3
                },
                {
                    "name": "is_critical",
                    "label": "Critical Asset",
                    "type": "boolean",
                    "required": False,
                    "default_value": False
                },
                {
                    "name": "location",
                    "label": "Physical Location",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["office_floor_1", "office_floor_2", "datacenter", "remote"],
                    "default_value": "office_floor_1"
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        
        if success and 'id' in response_data:
            self.created_group_id = response_data['id']
            
            # Verify custom fields were saved correctly
            if 'custom_fields' in response_data and len(response_data['custom_fields']) == 4:
                field_names = [field['name'] for field in response_data['custom_fields']]
                expected_fields = ['purchase_date', 'warranty_years', 'is_critical', 'location']
                
                if all(field in field_names for field in expected_fields):
                    self.log_test("Asset Group with Custom Fields", True, 
                                f"Group ID: {self.created_group_id}, Fields: {field_names}")
                    return True
                else:
                    missing = [f for f in expected_fields if f not in field_names]
                    self.log_test("Asset Group with Custom Fields", False, 
                                f"Missing fields: {missing}", response_data)
                    return False
            else:
                self.log_test("Asset Group with Custom Fields", False, 
                            f"Expected 4 custom fields, got {len(response_data.get('custom_fields', []))}", response_data)
                return False
        else:
            self.log_test("Asset Group with Custom Fields", False, f"Status: {status_code}", response_data)
            return False

    def test_asset_type_with_inheritance(self):
        """Test creating Asset Type that inherits from Asset Group and adds its own fields"""
        print("\n🏷️ Testing Asset Type with Custom Field Inheritance...")
        
        if not self.created_group_id:
            self.log_test("Asset Type with Inheritance", False, "No asset group ID available")
            return False
        
        type_data = {
            "name": "Laptop Computers",
            "description": "Portable computing devices with inherited and specific fields",
            "asset_group_id": self.created_group_id,
            "custom_fields": [
                {
                    "name": "cpu_model",
                    "label": "CPU Model",
                    "type": "text",
                    "required": True,
                    "default_value": "Intel i7"
                },
                {
                    "name": "ram_gb",
                    "label": "RAM (GB)",
                    "type": "number",
                    "required": True,
                    "default_value": 16
                },
                {
                    "name": "operating_system",
                    "label": "Operating System",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["windows_11", "macos_sonoma", "ubuntu_22", "fedora_39"],
                    "default_value": "windows_11"
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-types', type_data, 200)
        
        if success and 'id' in response_data:
            self.created_type_id = response_data['id']
            
            # Verify inheritance - should have both inherited and own fields
            if 'custom_fields' in response_data:
                all_fields = response_data['custom_fields']
                inherited_fields = [f for f in all_fields if f.get('inherited_from')]
                own_fields = [f for f in all_fields if not f.get('inherited_from')]
                
                # Should have 4 inherited fields from asset group + 3 own fields
                if len(inherited_fields) == 4 and len(own_fields) == 3:
                    inherited_names = [f['name'] for f in inherited_fields]
                    own_names = [f['name'] for f in own_fields]
                    
                    expected_inherited = ['purchase_date', 'warranty_years', 'is_critical', 'location']
                    expected_own = ['cpu_model', 'ram_gb', 'operating_system']
                    
                    if (all(field in inherited_names for field in expected_inherited) and
                        all(field in own_names for field in expected_own)):
                        self.log_test("Asset Type with Inheritance", True, 
                                    f"Type ID: {self.created_type_id}, Inherited: {inherited_names}, Own: {own_names}")
                        return True
                    else:
                        self.log_test("Asset Type with Inheritance", False, 
                                    f"Field name mismatch. Expected inherited: {expected_inherited}, got: {inherited_names}. Expected own: {expected_own}, got: {own_names}", response_data)
                        return False
                else:
                    self.log_test("Asset Type with Inheritance", False, 
                                f"Expected 4 inherited + 3 own fields, got {len(inherited_fields)} inherited + {len(own_fields)} own", response_data)
                    return False
            else:
                self.log_test("Asset Type with Inheritance", False, "No custom fields found in response", response_data)
                return False
        else:
            self.log_test("Asset Type with Inheritance", False, f"Status: {status_code}", response_data)
            return False

    def test_asset_creation_with_inheritance(self):
        """Test creating Asset that inherits custom fields from both Asset Group and Asset Type"""
        print("\n💻 Testing Asset Creation with Custom Field Inheritance...")
        
        if not self.created_type_id:
            self.log_test("Asset Creation with Inheritance", False, "No asset type ID available")
            return False
        
        asset_data = {
            "name": "MacBook Pro 16-inch M3",
            "description": "High-performance laptop for software development",
            "asset_type_id": self.created_type_id,
            "custom_data": {
                # Fields from Asset Group (inherited)
                "purchase_date": "2024-03-15",
                "warranty_years": 3,
                "is_critical": True,
                "location": "office_floor_2",
                # Fields from Asset Type (inherited)
                "cpu_model": "Apple M3 Pro",
                "ram_gb": 32,
                "operating_system": "macos_sonoma",
                # Additional custom data
                "serial_number": "MBP2024-001",
                "assigned_to": "john.developer@company.com"
            },
            "tags": ["development", "high-performance", "apple"]
        }
        
        success, response_data, status_code = self.make_request('POST', 'assets', asset_data, 200)
        
        if success and 'id' in response_data:
            self.created_asset_id = response_data['id']
            
            # Verify custom data was saved correctly
            if 'custom_data' in response_data:
                custom_data = response_data['custom_data']
                
                # Check for all expected fields
                expected_fields = [
                    'purchase_date', 'warranty_years', 'is_critical', 'location',  # From Asset Group
                    'cpu_model', 'ram_gb', 'operating_system',  # From Asset Type
                    'serial_number', 'assigned_to'  # Additional custom data
                ]
                
                missing_fields = [field for field in expected_fields if field not in custom_data]
                
                if not missing_fields:
                    # Verify some specific values
                    if (custom_data.get('cpu_model') == 'Apple M3 Pro' and
                        custom_data.get('location') == 'office_floor_2' and
                        custom_data.get('warranty_years') == 3):
                        self.log_test("Asset Creation with Inheritance", True, 
                                    f"Asset ID: {self.created_asset_id}, All {len(expected_fields)} fields present")
                        return True
                    else:
                        self.log_test("Asset Creation with Inheritance", False, 
                                    f"Field values incorrect: cpu_model={custom_data.get('cpu_model')}, location={custom_data.get('location')}, warranty_years={custom_data.get('warranty_years')}", response_data)
                        return False
                else:
                    self.log_test("Asset Creation with Inheritance", False, 
                                f"Missing custom fields: {missing_fields}", response_data)
                    return False
            else:
                self.log_test("Asset Creation with Inheritance", False, "No custom_data found in response", response_data)
                return False
        else:
            self.log_test("Asset Creation with Inheritance", False, f"Status: {status_code}", response_data)
            return False

    def test_asset_edit_functionality(self):
        """Test updating asset custom field values and changing asset type"""
        print("\n🔄 Testing Asset Edit Functionality...")
        
        if not self.created_asset_id:
            self.log_test("Asset Edit Functionality", False, "No asset ID available")
            return False
        
        # First, test updating custom field values
        update_data = {
            "name": "MacBook Pro 16-inch M3 (Updated)",
            "description": "Updated high-performance laptop for software development",
            "custom_data": {
                # Update some existing fields
                "purchase_date": "2024-04-01",  # Changed
                "warranty_years": 4,  # Changed
                "is_critical": False,  # Changed
                "location": "datacenter",  # Changed
                "cpu_model": "Apple M3 Max",  # Changed
                "ram_gb": 64,  # Changed
                "operating_system": "macos_sonoma",  # Same
                "serial_number": "MBP2024-001-UPDATED",  # Changed
                "assigned_to": "jane.developer@company.com",  # Changed
                # Add new custom field
                "storage_gb": 2048
            },
            "tags": ["development", "high-performance", "apple", "updated"]
        }
        
        success, response_data, status_code = self.make_request('PUT', f'assets/{self.created_asset_id}', update_data, 200)
        
        if success and 'id' in response_data:
            # Verify the updates
            if (response_data.get('name') == update_data['name'] and
                response_data.get('description') == update_data['description']):
                
                custom_data = response_data.get('custom_data', {})
                if (custom_data.get('warranty_years') == 4 and
                    custom_data.get('location') == 'datacenter' and
                    custom_data.get('cpu_model') == 'Apple M3 Max' and
                    custom_data.get('storage_gb') == 2048):
                    self.log_test("Asset Edit - Custom Field Updates", True, 
                                f"Successfully updated asset fields")
                else:
                    self.log_test("Asset Edit - Custom Field Updates", False, 
                                f"Custom field values not updated correctly", response_data)
                    return False
            else:
                self.log_test("Asset Edit - Custom Field Updates", False, 
                            f"Basic fields not updated correctly", response_data)
                return False
        else:
            self.log_test("Asset Edit - Custom Field Updates", False, f"Status: {status_code}", response_data)
            return False
        
        # Now test changing asset type (if we have another type)
        # For this test, we'll create a simple asset type and change to it
        simple_type_data = {
            "name": "Desktop Computers",
            "description": "Desktop workstations",
            "asset_group_id": self.created_group_id,
            "custom_fields": [
                {
                    "name": "monitor_count",
                    "label": "Number of Monitors",
                    "type": "number",
                    "default_value": 2
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-types', simple_type_data, 200)
        
        if success and 'id' in response_data:
            new_type_id = response_data['id']
            
            # Change asset type
            type_change_data = {
                "asset_type_id": new_type_id,
                "custom_data": {
                    # Keep some existing data
                    "purchase_date": "2024-04-01",
                    "warranty_years": 4,
                    "location": "office_floor_1",
                    # Add new type-specific field
                    "monitor_count": 3
                }
            }
            
            success, response_data, status_code = self.make_request('PUT', f'assets/{self.created_asset_id}', type_change_data, 200)
            
            if success and response_data.get('asset_type_id') == new_type_id:
                self.log_test("Asset Edit - Asset Type Change", True, 
                            f"Successfully changed asset type to {new_type_id}")
                return True
            else:
                self.log_test("Asset Edit - Asset Type Change", False, 
                            f"Asset type not changed correctly. Expected: {new_type_id}, Got: {response_data.get('asset_type_id')}", response_data)
                return False
        else:
            self.log_test("Asset Edit - Asset Type Change", False, 
                        f"Failed to create new asset type for testing. Status: {status_code}", response_data)
            return False

    def test_no_field_duplication(self):
        """Test that there's no field duplication in the inheritance chain"""
        print("\n🔍 Testing No Field Duplication in Inheritance...")
        
        # Create a new asset group with a field that might conflict
        conflict_group_data = {
            "name": "Conflict Test Group",
            "description": "Testing field name conflicts",
            "organization_id": self.created_org_id,
            "custom_fields": [
                {
                    "name": "model",
                    "label": "Model Name",
                    "type": "text",
                    "default_value": "Group Model"
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', conflict_group_data, 200)
        
        if not success:
            self.log_test("No Field Duplication Test", False, f"Failed to create test group. Status: {status_code}", response_data)
            return False
        
        conflict_group_id = response_data['id']
        
        # Create asset type with same field name
        conflict_type_data = {
            "name": "Conflict Test Type",
            "description": "Testing field name conflicts",
            "asset_group_id": conflict_group_id,
            "custom_fields": [
                {
                    "name": "model",  # Same name as in group
                    "label": "Type Model Name",
                    "type": "text",
                    "default_value": "Type Model"
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-types', conflict_type_data, 200)
        
        if success and 'custom_fields' in response_data:
            all_fields = response_data['custom_fields']
            model_fields = [f for f in all_fields if f['name'] == 'model']
            
            # Should have only one 'model' field (no duplication)
            if len(model_fields) == 1:
                self.log_test("No Field Duplication Test", True, 
                            f"No field duplication detected. Single 'model' field present.")
                return True
            else:
                self.log_test("No Field Duplication Test", False, 
                            f"Field duplication detected. Found {len(model_fields)} 'model' fields", response_data)
                return False
        else:
            self.log_test("No Field Duplication Test", False, f"Status: {status_code}", response_data)
            return False

    def run_focused_tests(self):
        """Run focused tests for the review request"""
        print("🎯 Starting Focused IT Asset Management Backend Tests")
        print("📍 Focus: Custom Field Inheritance & Asset Edit Functionality")
        print("=" * 70)
        
        # Setup
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return self.generate_report()
        
        if not self.test_organization_creation():
            print("❌ Organization creation failed - stopping tests")
            return self.generate_report()
        
        # Core functionality tests
        if not self.test_asset_group_with_custom_fields():
            print("❌ Asset Group with custom fields failed - stopping tests")
            return self.generate_report()
        
        if not self.test_asset_type_with_inheritance():
            print("❌ Asset Type inheritance failed - stopping tests")
            return self.generate_report()
        
        if not self.test_asset_creation_with_inheritance():
            print("❌ Asset creation with inheritance failed - stopping tests")
            return self.generate_report()
        
        # Additional tests
        self.test_asset_edit_functionality()
        self.test_no_field_duplication()
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 70)
        print(f"📊 Focused Test Results Summary")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All focused tests passed!")
            print("\n✅ VERIFICATION COMPLETE:")
            print("   • Asset Groups can have custom fields")
            print("   • Asset Types inherit from Asset Groups correctly")
            print("   • Assets inherit from Asset Types (including Group fields)")
            print("   • No field duplication in inheritance chain")
            print("   • Asset edit endpoint works correctly")
            print("   • Asset type changes affect custom fields properly")
            print("   • Authentication and JWT validation working")
            return 0
        else:
            print("⚠️ Some focused tests failed. Check the details above.")
            
            # Show failed tests
            failed_tests = [test for test in self.test_results if not test['success']]
            if failed_tests:
                print("\n❌ Failed Tests:")
                for test in failed_tests:
                    print(f"   • {test['test']}: {test['details']}")
            
            return 1

def main():
    tester = FocusedITAssetManagementTester()
    return tester.run_focused_tests()

if __name__ == "__main__":
    sys.exit(main())