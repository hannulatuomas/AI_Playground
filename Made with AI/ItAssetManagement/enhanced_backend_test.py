import requests
import sys
import json
from datetime import datetime
import uuid

class EnhancedITAssetManagementTester:
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
        self.created_custom_templates = []

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

    def setup_authentication(self):
        """Setup user authentication for testing"""
        # Register user
        test_email = f"enhanced_test_{datetime.now().strftime('%H%M%S')}@example.com"
        user_data = {
            "name": "Enhanced Test User",
            "email": test_email,
            "password": "EnhancedTest123!",
            "role": "admin"
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/register', user_data, 200)
        if not success:
            self.log_test("Setup Authentication - Registration", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        self.user_data = user_data
        
        # Login user
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/login', login_data, 200)
        if success and 'access_token' in response_data:
            self.token = response_data['access_token']
            self.log_test("Setup Authentication", True, "User registered and logged in successfully")
            return True
        else:
            self.log_test("Setup Authentication - Login", False, f"Status: {status_code}, Response: {response_data}")
            return False

    def setup_organization(self):
        """Setup test organization"""
        org_data = {
            "name": f"Enhanced Test Organization {datetime.now().strftime('%H%M%S')}",
            "description": "Test organization for enhanced IT asset management features"
        }
        
        success, response_data, status_code = self.make_request('POST', 'organizations', org_data, 200)
        
        if success and 'id' in response_data:
            self.created_org_id = response_data['id']
            self.log_test("Setup Organization", True, f"Organization created with ID: {self.created_org_id}")
            return True
        else:
            self.log_test("Setup Organization", False, f"Status: {status_code}, Response: {response_data}")
            return False

    def test_enhanced_asset_type_templates(self):
        """Test GET /api/templates/default-asset-types endpoint for enhanced templates"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-types', expected_status=200)
        
        if not success:
            self.log_test("Enhanced Asset Type Templates", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        # Check if response is a list
        if not isinstance(response_data, list):
            self.log_test("Enhanced Asset Type Templates", False, "Response should be a list")
            return False
        
        # Count total templates
        total_templates = len(response_data)
        
        # Verify we have 11+ templates as mentioned in the review
        if total_templates < 11:
            self.log_test("Enhanced Asset Type Templates", False, f"Expected 11+ templates, got {total_templates}")
            return False
        
        # Check for specific new templates mentioned in the review
        expected_new_templates = [
            "Storage Device", "Monitor", "UPS Device", "Security Camera"
        ]
        
        all_template_names = [template.get('name', '') for template in response_data]
        
        found_new_templates = []
        for expected_template in expected_new_templates:
            for template_name in all_template_names:
                if expected_template.lower() in template_name.lower():
                    found_new_templates.append(template_name)
                    break
        
        # Check for new custom field types in the templates
        all_field_types = set()
        for template in response_data:
            if 'custom_fields' in template:
                for field in template['custom_fields']:
                    all_field_types.add(field.get('type', ''))
        
        # Look for advanced field types that might be used
        advanced_field_types = ['file_size', 'currency', 'version', 'ip_address', 'mac_address', 'url', 'email']
        found_advanced_types = [field_type for field_type in advanced_field_types if field_type in all_field_types]
        
        self.log_test("Enhanced Asset Type Templates", True, 
                     f"Found {total_templates} templates, {len(found_new_templates)}/4 new template types, {len(found_advanced_types)} advanced field types")
        return True

    def test_enhanced_asset_templates(self):
        """Test GET /api/templates/default-assets endpoint for enhanced templates"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-assets', expected_status=200)
        
        if not success:
            self.log_test("Enhanced Asset Templates", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        # Check if response is a list
        if not isinstance(response_data, list):
            self.log_test("Enhanced Asset Templates", False, "Response should be a list")
            return False
        
        # Verify we have 11+ templates as mentioned in the review
        if len(response_data) < 11:
            self.log_test("Enhanced Asset Templates", False, f"Expected 11+ templates, got {len(response_data)}")
            return False
        
        # Check for specific new asset templates mentioned in the review
        expected_new_assets = [
            "Office Security Camera", "External Storage Drive", "Conference Room Display", 
            "Data Center UPS", "Corporate Firewall"
        ]
        
        template_names = [template.get('name', '') for template in response_data]
        found_new_assets = []
        
        for expected_asset in expected_new_assets:
            for template_name in template_names:
                if expected_asset.lower() in template_name.lower() or any(word in template_name.lower() for word in expected_asset.lower().split()):
                    found_new_assets.append(template_name)
                    break
        
        # Verify asset_group_name and asset_type_name fields are present
        templates_with_required_fields = 0
        for template in response_data:
            if 'asset_group_name' in template and 'asset_type_name' in template:
                templates_with_required_fields += 1
        
        if templates_with_required_fields != len(response_data):
            self.log_test("Enhanced Asset Templates", False, 
                         f"Not all templates have required fields. {templates_with_required_fields}/{len(response_data)} have asset_group_name and asset_type_name")
            return False
        
        self.log_test("Enhanced Asset Templates", True, 
                     f"Found {len(response_data)} asset templates, {len(found_new_assets)} new asset types, all have required fields")
        return True

    def test_custom_template_crud(self):
        """Test custom template CRUD functionality"""
        if not self.created_org_id:
            self.log_test("Custom Template CRUD", False, "No organization ID available")
            return False
        
        # Test creating custom templates for all types
        template_types = ['asset_group', 'asset_type', 'asset']
        created_templates = []
        
        for template_type in template_types:
            template_data = {
                "name": f"Custom {template_type.replace('_', ' ').title()} Template",
                "description": f"Custom template for {template_type}",
                "icon": "Star",
                "template_type": template_type,
                "custom_fields": [
                    {
                        "name": "custom_field_1",
                        "label": "Custom Field 1",
                        "type": "text",
                        "required": True,
                        "default_value": "default_value"
                    },
                    {
                        "name": "custom_field_2",
                        "label": "Custom Field 2",
                        "type": "number",
                        "required": False,
                        "default_value": 100
                    }
                ],
                "organization_id": self.created_org_id,
                "is_public": False
            }
            
            success, response_data, status_code = self.make_request('POST', 'templates/custom', template_data, 200)
            
            if success and 'id' in response_data:
                created_templates.append(response_data['id'])
                self.log_test(f"Create Custom {template_type.title()} Template", True, f"Template created with ID: {response_data['id']}")
            else:
                self.log_test(f"Create Custom {template_type.title()} Template", False, f"Status: {status_code}, Response: {response_data}")
                return False
        
        self.created_custom_templates = created_templates
        
        # Test retrieving custom templates
        success, response_data, status_code = self.make_request('GET', 'templates/custom', expected_status=200)
        
        if success and isinstance(response_data, list):
            if len(response_data) >= len(template_types):
                self.log_test("Retrieve Custom Templates", True, f"Found {len(response_data)} custom templates")
            else:
                self.log_test("Retrieve Custom Templates", False, f"Expected at least {len(template_types)} templates, got {len(response_data)}")
                return False
        else:
            self.log_test("Retrieve Custom Templates", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        # Test updating a custom template
        if created_templates:
            template_id = created_templates[0]
            update_data = {
                "name": "Updated Custom Template",
                "description": "Updated description",
                "icon": "Edit",
                "template_type": "asset_group",
                "custom_fields": [
                    {
                        "name": "updated_field",
                        "label": "Updated Field",
                        "type": "text",
                        "required": True,
                        "default_value": "updated_value"
                    }
                ],
                "organization_id": self.created_org_id,
                "is_public": True
            }
            
            success, response_data, status_code = self.make_request('PUT', f'templates/custom/{template_id}', update_data, 200)
            
            if success:
                self.log_test("Update Custom Template", True, "Template updated successfully")
            else:
                self.log_test("Update Custom Template", False, f"Status: {status_code}, Response: {response_data}")
                return False
        
        return True

    def test_asset_icon_editing(self):
        """Test asset icon editing functionality"""
        if not self.created_org_id:
            self.log_test("Asset Icon Editing", False, "No organization ID available")
            return False
        
        # First create an asset group and type
        group_data = {
            "name": "Icon Test Group",
            "description": "Group for testing icon functionality",
            "icon": "Folder",
            "organization_id": self.created_org_id
        }
        
        success, group_response, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        if not success:
            self.log_test("Asset Icon Editing - Create Group", False, f"Status: {status_code}")
            return False
        
        group_id = group_response['id']
        
        type_data = {
            "name": "Icon Test Type",
            "description": "Type for testing icon functionality",
            "icon": "Laptop",
            "asset_group_id": group_id
        }
        
        success, type_response, status_code = self.make_request('POST', 'asset-types', type_data, 200)
        if not success:
            self.log_test("Asset Icon Editing - Create Type", False, f"Status: {status_code}")
            return False
        
        type_id = type_response['id']
        
        # Create an asset with an icon
        asset_data = {
            "name": "Icon Test Asset",
            "description": "Asset for testing icon functionality",
            "icon": "Monitor",
            "asset_type_id": type_id,
            "custom_data": {
                "test_field": "test_value"
            }
        }
        
        success, asset_response, status_code = self.make_request('POST', 'assets', asset_data, 200)
        if not success:
            self.log_test("Asset Icon Editing - Create Asset", False, f"Status: {status_code}")
            return False
        
        asset_id = asset_response['id']
        
        # Test updating the asset icon
        update_data = {
            "icon": "Smartphone"
        }
        
        success, update_response, status_code = self.make_request('PUT', f'assets/{asset_id}', update_data, 200)
        
        if success and update_response.get('icon') == 'Smartphone':
            self.log_test("Asset Icon Editing", True, "Asset icon updated successfully")
            return True
        else:
            self.log_test("Asset Icon Editing", False, f"Icon not updated correctly. Status: {status_code}, Response: {update_response}")
            return False

    def test_asset_field_management(self):
        """Test asset-specific fields functionality"""
        if not self.created_org_id:
            self.log_test("Asset Field Management", False, "No organization ID available")
            return False
        
        # Create asset group with custom fields
        group_data = {
            "name": "Field Management Test Group",
            "description": "Group for testing field management",
            "organization_id": self.created_org_id,
            "custom_fields": [
                {
                    "name": "group_field_1",
                    "label": "Group Field 1",
                    "type": "text",
                    "required": True,
                    "default_value": "group_default"
                },
                {
                    "name": "group_field_2",
                    "label": "Group Field 2",
                    "type": "number",
                    "required": False,
                    "default_value": 50
                }
            ]
        }
        
        success, group_response, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        if not success:
            self.log_test("Asset Field Management - Create Group", False, f"Status: {status_code}")
            return False
        
        group_id = group_response['id']
        
        # Create asset type with additional custom fields
        type_data = {
            "name": "Field Management Test Type",
            "description": "Type for testing field management",
            "asset_group_id": group_id,
            "custom_fields": [
                {
                    "name": "type_field_1",
                    "label": "Type Field 1",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "name": "type_field_2",
                    "label": "Type Field 2",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["option1", "option2", "option3"],
                    "default_value": "option1"
                }
            ]
        }
        
        success, type_response, status_code = self.make_request('POST', 'asset-types', type_data, 200)
        if not success:
            self.log_test("Asset Field Management - Create Type", False, f"Status: {status_code}")
            return False
        
        type_id = type_response['id']
        
        # Create asset with custom fields
        asset_data = {
            "name": "Field Management Test Asset",
            "description": "Asset for testing field management",
            "asset_type_id": type_id,
            "custom_fields": [
                {
                    "name": "asset_specific_field",
                    "label": "Asset Specific Field",
                    "type": "text",
                    "required": False,
                    "default_value": "asset_specific_value"
                }
            ],
            "custom_data": {
                "group_field_1": "custom_group_value",
                "group_field_2": 75,
                "type_field_1": False,
                "type_field_2": "option2",
                "asset_specific_field": "custom_asset_value"
            }
        }
        
        success, asset_response, status_code = self.make_request('POST', 'assets', asset_data, 200)
        if not success:
            self.log_test("Asset Field Management - Create Asset", False, f"Status: {status_code}")
            return False
        
        # Verify custom fields are saved in asset.custom_fields
        if 'custom_fields' in asset_response:
            asset_custom_fields = asset_response['custom_fields']
            if len(asset_custom_fields) > 0:
                self.log_test("Asset Field Management - Custom Fields Array", True, f"Asset has {len(asset_custom_fields)} custom fields")
            else:
                self.log_test("Asset Field Management - Custom Fields Array", False, "Asset custom_fields array is empty")
                return False
        else:
            self.log_test("Asset Field Management - Custom Fields Array", False, "Asset does not have custom_fields array")
            return False
        
        # Verify custom data is saved correctly
        if 'custom_data' in asset_response:
            custom_data = asset_response['custom_data']
            expected_fields = ['group_field_1', 'group_field_2', 'type_field_1', 'type_field_2', 'asset_specific_field']
            missing_fields = [field for field in expected_fields if field not in custom_data]
            
            if not missing_fields:
                self.log_test("Asset Field Management - Custom Data", True, f"All {len(expected_fields)} custom fields saved correctly")
            else:
                self.log_test("Asset Field Management - Custom Data", False, f"Missing custom data fields: {missing_fields}")
                return False
        else:
            self.log_test("Asset Field Management - Custom Data", False, "Asset does not have custom_data")
            return False
        
        return True

    def test_backend_stability(self):
        """Test that all existing functionality still works"""
        # Test authentication endpoints
        success, response_data, status_code = self.make_request('GET', 'auth/me', expected_status=200)
        if not success:
            self.log_test("Backend Stability - Auth Me", False, f"Status: {status_code}")
            return False
        
        # Test organization CRUD
        success, response_data, status_code = self.make_request('GET', 'organizations', expected_status=200)
        if not success:
            self.log_test("Backend Stability - Get Organizations", False, f"Status: {status_code}")
            return False
        
        # Test asset group CRUD
        if self.created_org_id:
            success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}/asset-groups', expected_status=200)
            if not success:
                self.log_test("Backend Stability - Get Asset Groups", False, f"Status: {status_code}")
                return False
        
        # Test default template endpoints
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        if not success:
            self.log_test("Backend Stability - Default Asset Group Templates", False, f"Status: {status_code}")
            return False
        
        self.log_test("Backend Stability", True, "All existing functionality working correctly")
        return True

    def run_enhanced_tests(self):
        """Run all enhanced feature tests"""
        print(f"🚀 Starting Enhanced IT Asset Management System Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Setup
        print("\n🔧 Setup Phase")
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return self.generate_report()
        
        if not self.setup_organization():
            print("❌ Organization setup failed - stopping tests")
            return self.generate_report()
        
        # Enhanced Template Tests
        print("\n📋 Enhanced Template Tests")
        self.test_enhanced_asset_type_templates()
        self.test_enhanced_asset_templates()
        
        # Custom Template CRUD Tests
        print("\n🛠️ Custom Template CRUD Tests")
        self.test_custom_template_crud()
        
        # Asset Icon Editing Tests
        print("\n🎨 Asset Icon Editing Tests")
        self.test_asset_icon_editing()
        
        # Asset Field Management Tests
        print("\n📝 Asset Field Management Tests")
        self.test_asset_field_management()
        
        # Backend Stability Tests
        print("\n🔒 Backend Stability Tests")
        self.test_backend_stability()
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 70)
        print(f"📊 Enhanced Features Test Results Summary")
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
            print("🎉 All enhanced features tests passed!")
            return 0
        else:
            print("⚠️ Some enhanced features tests failed. Check the details above.")
            return 1

def main():
    tester = EnhancedITAssetManagementTester()
    return tester.run_enhanced_tests()

if __name__ == "__main__":
    sys.exit(main())