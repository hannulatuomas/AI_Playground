import requests
import sys
import json
from datetime import datetime
import uuid

class CustomTemplateTester:
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
        self.created_template_ids = []
        self.test_user_id = None

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
        # Register test user
        test_email = f"template_test_user_{datetime.now().strftime('%H%M%S')}@example.com"
        user_data = {
            "name": "Template Test User",
            "email": test_email,
            "password": "TemplateTest123!",
            "role": "admin"
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/register', user_data, 200)
        
        if not success:
            self.log_test("User Registration", False, f"Status: {status_code}, Response: {response_data}")
            return False
            
        self.user_data = user_data
        self.test_user_id = response_data.get('id')
        self.log_test("User Registration", True, f"User created with email: {test_email}")
        
        # Login
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/login', login_data, 200)
        
        if success and 'access_token' in response_data:
            self.token = response_data['access_token']
            self.log_test("User Login", True, f"Token received")
        else:
            self.log_test("User Login", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        # Create test organization
        org_data = {
            "name": f"Template Test Org {datetime.now().strftime('%H%M%S')}",
            "description": "Test organization for custom template testing"
        }
        
        success, response_data, status_code = self.make_request('POST', 'organizations', org_data, 200)
        
        if success and 'id' in response_data:
            self.created_org_id = response_data['id']
            self.log_test("Create Test Organization", True, f"Organization created with ID: {self.created_org_id}")
        else:
            self.log_test("Create Test Organization", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return True

    def test_create_custom_template_asset_group(self):
        """Test creating custom template for asset_group type"""
        template_data = {
            "name": "Custom Hardware Template",
            "description": "Custom template for hardware assets with specialized fields",
            "icon": "HardDrive",
            "template_type": "asset_group",
            "custom_fields": [
                {
                    "name": "warranty_period",
                    "label": "Warranty Period (Years)",
                    "type": "number",
                    "required": True,
                    "default_value": 3
                },
                {
                    "name": "vendor_contact",
                    "label": "Vendor Contact Email",
                    "type": "email",
                    "required": True,
                    "default_value": None
                },
                {
                    "name": "maintenance_schedule",
                    "label": "Maintenance Schedule",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["Monthly", "Quarterly", "Semi-Annual", "Annual"],
                    "default_value": "Quarterly"
                },
                {
                    "name": "critical_system",
                    "label": "Critical System",
                    "type": "boolean",
                    "required": True,
                    "default_value": False
                }
            ],
            "organization_id": self.created_org_id,
            "is_public": False
        }
        
        success, response_data, status_code = self.make_request('POST', 'templates/custom', template_data, 200)
        
        if success and 'id' in response_data:
            template_id = response_data['id']
            self.created_template_ids.append(template_id)
            
            # Verify template data
            if (response_data.get('name') == template_data['name'] and
                response_data.get('template_type') == 'asset_group' and
                len(response_data.get('custom_fields', [])) == 4):
                self.log_test("Create Custom Template - Asset Group", True, f"Template created with ID: {template_id}")
            else:
                self.log_test("Create Custom Template - Asset Group", False, "Template data not saved correctly")
                return False
        else:
            self.log_test("Create Custom Template - Asset Group", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_create_custom_template_asset_type(self):
        """Test creating custom template for asset_type type"""
        template_data = {
            "name": "Custom Server Template",
            "description": "Custom template for server assets",
            "icon": "Server",
            "template_type": "asset_type",
            "custom_fields": [
                {
                    "name": "cpu_cores",
                    "label": "CPU Cores",
                    "type": "number",
                    "required": True,
                    "default_value": 8
                },
                {
                    "name": "ram_gb",
                    "label": "RAM (GB)",
                    "type": "number",
                    "required": True,
                    "default_value": 32
                },
                {
                    "name": "storage_type",
                    "label": "Storage Type",
                    "type": "multi_select",
                    "required": False,
                    "dataset_values": ["SSD", "HDD", "NVMe", "RAID"],
                    "default_value": ["SSD"]
                }
            ],
            "organization_id": None,  # Global template
            "is_public": True
        }
        
        success, response_data, status_code = self.make_request('POST', 'templates/custom', template_data, 200)
        
        if success and 'id' in response_data:
            template_id = response_data['id']
            self.created_template_ids.append(template_id)
            
            # Verify template data
            if (response_data.get('name') == template_data['name'] and
                response_data.get('template_type') == 'asset_type' and
                response_data.get('is_public') == True and
                response_data.get('organization_id') is None):
                self.log_test("Create Custom Template - Asset Type (Global/Public)", True, f"Template created with ID: {template_id}")
            else:
                self.log_test("Create Custom Template - Asset Type (Global/Public)", False, "Template data not saved correctly")
                return False
        else:
            self.log_test("Create Custom Template - Asset Type (Global/Public)", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_create_custom_template_asset(self):
        """Test creating custom template for asset type"""
        template_data = {
            "name": "Custom Laptop Template",
            "description": "Custom template for laptop assets with specific configurations",
            "icon": "Laptop",
            "template_type": "asset",
            "custom_fields": [
                {
                    "name": "screen_size",
                    "label": "Screen Size (inches)",
                    "type": "number",
                    "required": True,
                    "default_value": 15.6
                },
                {
                    "name": "operating_system",
                    "label": "Operating System",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["Windows 11", "macOS", "Ubuntu", "Other Linux"],
                    "default_value": "Windows 11"
                },
                {
                    "name": "assigned_user",
                    "label": "Assigned User Email",
                    "type": "email",
                    "required": False,
                    "default_value": None
                }
            ],
            "organization_id": self.created_org_id,
            "is_public": False
        }
        
        success, response_data, status_code = self.make_request('POST', 'templates/custom', template_data, 200)
        
        if success and 'id' in response_data:
            template_id = response_data['id']
            self.created_template_ids.append(template_id)
            
            # Verify template data
            if (response_data.get('name') == template_data['name'] and
                response_data.get('template_type') == 'asset' and
                len(response_data.get('custom_fields', [])) == 3):
                self.log_test("Create Custom Template - Asset", True, f"Template created with ID: {template_id}")
            else:
                self.log_test("Create Custom Template - Asset", False, "Template data not saved correctly")
                return False
        else:
            self.log_test("Create Custom Template - Asset", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_get_custom_templates(self):
        """Test retrieving custom templates"""
        success, response_data, status_code = self.make_request('GET', 'templates/custom', expected_status=200)
        
        if success and isinstance(response_data, list):
            # Should see user's own templates and public templates
            user_templates = [t for t in response_data if t.get('created_by') == self.test_user_id]
            public_templates = [t for t in response_data if t.get('is_public') == True]
            
            if len(user_templates) >= 2:  # At least the private templates we created
                self.log_test("Get Custom Templates", True, f"Found {len(response_data)} templates ({len(user_templates)} own, {len(public_templates)} public)")
            else:
                self.log_test("Get Custom Templates", False, f"Expected at least 2 user templates, found {len(user_templates)}")
                return False
        else:
            self.log_test("Get Custom Templates", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_update_custom_template(self):
        """Test updating a custom template"""
        if not self.created_template_ids:
            self.log_test("Update Custom Template", False, "No template ID available")
            return False
        
        template_id = self.created_template_ids[0]  # Use first created template
        
        update_data = {
            "name": "Updated Custom Hardware Template",
            "description": "Updated description for hardware template",
            "template_type": "asset_group",  # Required field for update
            "custom_fields": [
                {
                    "name": "warranty_period",
                    "label": "Warranty Period (Years)",
                    "type": "number",
                    "required": True,
                    "default_value": 5  # Updated default value
                },
                {
                    "name": "vendor_contact",
                    "label": "Vendor Contact Email",
                    "type": "email",
                    "required": True,
                    "default_value": None
                },
                {
                    "name": "maintenance_schedule",
                    "label": "Maintenance Schedule",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["Monthly", "Quarterly", "Semi-Annual", "Annual"],
                    "default_value": "Monthly"  # Updated default value
                },
                {
                    "name": "critical_system",
                    "label": "Critical System",
                    "type": "boolean",
                    "required": True,
                    "default_value": True  # Updated default value
                },
                {
                    "name": "new_field",
                    "label": "New Additional Field",
                    "type": "text",
                    "required": False,
                    "default_value": "New field value"
                }
            ],
            "organization_id": self.created_org_id,  # Required field
            "is_public": True  # Change visibility
        }
        
        success, response_data, status_code = self.make_request('PUT', f'templates/custom/{template_id}', update_data, 200)
        
        if success and 'id' in response_data:
            # Verify updates
            if (response_data.get('name') == update_data['name'] and
                response_data.get('is_public') == True and
                len(response_data.get('custom_fields', [])) == 5):
                self.log_test("Update Custom Template", True, f"Template updated successfully")
            else:
                self.log_test("Update Custom Template", False, "Template not updated correctly")
                return False
        else:
            self.log_test("Update Custom Template", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_template_ownership_validation(self):
        """Test that users can only edit their own templates"""
        if not self.created_template_ids:
            self.log_test("Template Ownership Validation", False, "No template ID available")
            return False
        
        # Create a second user
        test_email2 = f"template_test_user2_{datetime.now().strftime('%H%M%S')}@example.com"
        user_data2 = {
            "name": "Template Test User 2",
            "email": test_email2,
            "password": "TemplateTest123!",
            "role": "user"
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/register', user_data2, 200)
        if not success:
            self.log_test("Template Ownership Validation - User 2 Registration", False, f"Status: {status_code}")
            return False
        
        # Login as second user
        login_data2 = {
            "email": user_data2["email"],
            "password": user_data2["password"]
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/login', login_data2, 200)
        if not success or 'access_token' not in response_data:
            self.log_test("Template Ownership Validation - User 2 Login", False, f"Status: {status_code}")
            return False
        
        # Save original token and use second user's token
        original_token = self.token
        self.token = response_data['access_token']
        
        # Try to update first user's template (should fail)
        template_id = self.created_template_ids[0]
        update_data = {
            "name": "Unauthorized Update Attempt",
            "description": "This should not work",
            "template_type": "asset_group",
            "custom_fields": [],
            "organization_id": self.created_org_id,
            "is_public": False
        }
        
        success, response_data, status_code = self.make_request('PUT', f'templates/custom/{template_id}', update_data, 403)
        
        # Restore original token
        self.token = original_token
        
        if status_code in [403, 404]:  # 403 Forbidden or 404 Not Found are both acceptable
            self.log_test("Template Ownership Validation", True, f"Correctly rejected unauthorized update (status: {status_code})")
        else:
            self.log_test("Template Ownership Validation", False, f"Expected 403 or 404, got {status_code}")
            return False
        
        return True

    def test_delete_custom_template(self):
        """Test deleting a custom template"""
        if len(self.created_template_ids) < 2:
            self.log_test("Delete Custom Template", False, "Need at least 2 templates for deletion test")
            return False
        
        template_id = self.created_template_ids[-1]  # Use last created template
        
        # Get current template count before deletion
        success_before, response_data_before, status_code_before = self.make_request('GET', 'templates/custom', expected_status=200)
        if not success_before:
            self.log_test("Delete Custom Template", False, "Could not get templates before deletion")
            return False
        
        templates_before = len(response_data_before)
        
        # Delete the template
        success, response_data, status_code = self.make_request('DELETE', f'templates/custom/{template_id}', expected_status=200)
        
        if success:
            # Verify template is deleted by checking the list
            success_after, response_data_after, status_code_after = self.make_request('GET', 'templates/custom', expected_status=200)
            
            if success_after:
                templates_after = len(response_data_after)
                template_still_exists = any(t.get('id') == template_id for t in response_data_after)
                
                if templates_after == templates_before - 1 and not template_still_exists:
                    self.log_test("Delete Custom Template", True, f"Template deleted successfully")
                    self.created_template_ids.remove(template_id)
                else:
                    self.log_test("Delete Custom Template", False, f"Template still exists after deletion or count mismatch")
                    return False
            else:
                self.log_test("Delete Custom Template", False, f"Could not verify deletion")
                return False
        else:
            self.log_test("Delete Custom Template", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_template_field_types(self):
        """Test various field types in custom templates"""
        template_data = {
            "name": "Field Types Test Template",
            "description": "Testing all supported field types in custom templates",
            "icon": "TestTube",
            "template_type": "asset_group",
            "custom_fields": [
                {
                    "name": "text_field",
                    "label": "Text Field",
                    "type": "text",
                    "required": False,
                    "default_value": "Sample text"
                },
                {
                    "name": "number_field",
                    "label": "Number Field",
                    "type": "number",
                    "required": True,
                    "default_value": 100
                },
                {
                    "name": "date_field",
                    "label": "Date Field",
                    "type": "date",
                    "required": False,
                    "default_value": "2024-12-31"
                },
                {
                    "name": "boolean_field",
                    "label": "Boolean Field",
                    "type": "boolean",
                    "required": True,
                    "default_value": True
                },
                {
                    "name": "dataset_field",
                    "label": "Dataset Field",
                    "type": "dataset",
                    "required": False,
                    "dataset_values": ["Option A", "Option B", "Option C"],
                    "default_value": "Option A"
                },
                {
                    "name": "multi_select_field",
                    "label": "Multi Select Field",
                    "type": "multi_select",
                    "required": False,
                    "dataset_values": ["Tag1", "Tag2", "Tag3", "Tag4"],
                    "default_value": ["Tag1", "Tag2"]
                },
                {
                    "name": "email_field",
                    "label": "Email Field",
                    "type": "email",
                    "required": False,
                    "default_value": None
                },
                {
                    "name": "url_field",
                    "label": "URL Field",
                    "type": "url",
                    "required": False,
                    "default_value": "https://example.com"
                },
                {
                    "name": "ip_address_field",
                    "label": "IP Address Field",
                    "type": "ip_address",
                    "required": False,
                    "default_value": "192.168.1.1"
                },
                {
                    "name": "mac_address_field",
                    "label": "MAC Address Field",
                    "type": "mac_address",
                    "required": False,
                    "default_value": "00:11:22:33:44:55"
                },
                {
                    "name": "version_field",
                    "label": "Version Field",
                    "type": "version",
                    "required": False,
                    "default_value": "1.0.0"
                },
                {
                    "name": "currency_field",
                    "label": "Currency Field",
                    "type": "currency",
                    "required": False,
                    "default_value": 1000.50
                }
            ],
            "organization_id": self.created_org_id,
            "is_public": False
        }
        
        success, response_data, status_code = self.make_request('POST', 'templates/custom', template_data, 200)
        
        if success and 'id' in response_data:
            template_id = response_data['id']
            self.created_template_ids.append(template_id)
            
            # Verify all field types were saved
            custom_fields = response_data.get('custom_fields', [])
            if len(custom_fields) == 12:
                field_types = [field['type'] for field in custom_fields]
                expected_types = ['text', 'number', 'date', 'boolean', 'dataset', 'multi_select', 
                                'email', 'url', 'ip_address', 'mac_address', 'version', 'currency']
                
                if all(field_type in field_types for field_type in expected_types):
                    self.log_test("Template Field Types Support", True, f"All {len(expected_types)} field types supported")
                else:
                    missing_types = [t for t in expected_types if t not in field_types]
                    self.log_test("Template Field Types Support", False, f"Missing field types: {missing_types}")
                    return False
            else:
                self.log_test("Template Field Types Support", False, f"Expected 12 fields, got {len(custom_fields)}")
                return False
        else:
            self.log_test("Template Field Types Support", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_integration_with_default_templates(self):
        """Test that existing default template endpoints still work"""
        # Test default asset groups
        success1, response_data1, status_code1 = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if success1 and isinstance(response_data1, list) and len(response_data1) > 0:
            self.log_test("Default Asset Group Templates Integration", True, f"Found {len(response_data1)} default templates")
        else:
            self.log_test("Default Asset Group Templates Integration", False, f"Status: {status_code1}, Response: {response_data1}")
        
        # Test default asset types
        success2, response_data2, status_code2 = self.make_request('GET', 'templates/default-asset-types', expected_status=200)
        
        if success2 and isinstance(response_data2, list) and len(response_data2) > 0:
            template_count = len(response_data2)
            self.log_test("Default Asset Type Templates Integration", True, f"Found {template_count} default type templates")
        else:
            self.log_test("Default Asset Type Templates Integration", False, f"Status: {status_code2}, Response: {response_data2}")
        
        return success1 and success2

    def test_unauthorized_template_access(self):
        """Test unauthorized access to custom templates"""
        # Save current token
        original_token = self.token
        
        # Test without token
        self.token = None
        success, response_data, status_code = self.make_request('GET', 'templates/custom', expected_status=401)
        
        if status_code in [401, 403]:
            self.log_test("Unauthorized Template Access - No Token", True, f"Correctly rejected request without token (status: {status_code})")
        else:
            self.log_test("Unauthorized Template Access - No Token", False, f"Expected 401 or 403, got {status_code}")
        
        # Test creating template without token
        template_data = {
            "name": "Unauthorized Template",
            "template_type": "asset_group",
            "custom_fields": []
        }
        
        success, response_data, status_code = self.make_request('POST', 'templates/custom', template_data, expected_status=401)
        
        if status_code in [401, 403]:
            self.log_test("Unauthorized Template Creation", True, f"Correctly rejected template creation without token (status: {status_code})")
        else:
            self.log_test("Unauthorized Template Creation", False, f"Expected 401 or 403, got {status_code}")
        
        # Restore original token
        self.token = original_token
        return True

    def run_all_tests(self):
        """Run all CustomTemplate tests"""
        print(f"🚀 Starting CustomTemplate Functionality Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Setup authentication and test data
        print("\n🔐 Authentication & Setup")
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return self.generate_report()
        
        # Custom Template Creation Tests
        print("\n📝 Custom Template Creation Tests")
        self.test_create_custom_template_asset_group()
        self.test_create_custom_template_asset_type()
        self.test_create_custom_template_asset()
        
        # Custom Template Retrieval Tests
        print("\n📋 Custom Template Retrieval Tests")
        self.test_get_custom_templates()
        
        # Custom Template Update Tests
        print("\n🔄 Custom Template Update Tests")
        self.test_update_custom_template()
        
        # Security and Ownership Tests
        print("\n🔒 Security & Ownership Tests")
        self.test_template_ownership_validation()
        self.test_unauthorized_template_access()
        
        # Custom Template Deletion Tests
        print("\n🗑️ Custom Template Deletion Tests")
        self.test_delete_custom_template()
        
        # Field Types Support Tests
        print("\n🔧 Field Types Support Tests")
        self.test_template_field_types()
        
        # Integration Tests
        print("\n🔗 Integration Tests")
        self.test_integration_with_default_templates()
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print(f"📊 CustomTemplate Test Results Summary")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All CustomTemplate tests passed!")
            return 0
        else:
            print("⚠️ Some CustomTemplate tests failed. Check the details above.")
            return 1

def main():
    tester = CustomTemplateTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())