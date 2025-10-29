import requests
import sys
import json
from datetime import datetime

class TemplateEndpointTester:
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
        """Setup authentication for testing"""
        # Register user
        test_email = f"template_test_{datetime.now().strftime('%H%M%S')}@example.com"
        user_data = {
            "name": "Template Test User",
            "email": test_email,
            "password": "TestPass123!",
            "role": "admin"
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/register', user_data, 200)
        
        if not success:
            print(f"❌ User registration failed: {status_code}, {response_data}")
            return False
            
        self.user_data = user_data
        
        # Login
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/login', login_data, 200)
        
        if success and 'access_token' in response_data:
            self.token = response_data['access_token']
            print(f"✅ Authentication setup complete")
            return True
        else:
            print(f"❌ Login failed: {status_code}, {response_data}")
            return False

    def setup_organization(self):
        """Create organization for testing"""
        org_data = {
            "name": f"Template Test Org {datetime.now().strftime('%H%M%S')}",
            "description": "Organization for template testing"
        }
        
        success, response_data, status_code = self.make_request('POST', 'organizations', org_data, 200)
        
        if success and 'id' in response_data:
            self.created_org_id = response_data['id']
            print(f"✅ Organization created: {self.created_org_id}")
            return True
        else:
            print(f"❌ Organization creation failed: {status_code}, {response_data}")
            return False

    def test_default_asset_group_templates(self):
        """Test GET /api/templates/default-asset-groups endpoint"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("Default Asset Group Templates - Basic Request", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        # Verify response is a list
        if not isinstance(response_data, list):
            self.log_test("Default Asset Group Templates - Response Type", False, f"Expected list, got {type(response_data)}")
            return False
        
        self.log_test("Default Asset Group Templates - Basic Request", True, f"Found {len(response_data)} templates")
        
        # Verify template structure
        if len(response_data) == 0:
            self.log_test("Default Asset Group Templates - Template Count", False, "No templates returned")
            return False
        
        # Check first template structure
        first_template = response_data[0]
        required_fields = ['name', 'description', 'icon', 'custom_fields']
        missing_fields = [field for field in required_fields if field not in first_template]
        
        if missing_fields:
            self.log_test("Default Asset Group Templates - Structure", False, f"Missing fields: {missing_fields}")
            return False
        
        self.log_test("Default Asset Group Templates - Structure", True, "All required fields present")
        
        # Verify custom_fields structure
        custom_fields = first_template.get('custom_fields', [])
        if not isinstance(custom_fields, list):
            self.log_test("Default Asset Group Templates - Custom Fields Type", False, f"custom_fields should be list, got {type(custom_fields)}")
            return False
        
        if len(custom_fields) == 0:
            self.log_test("Default Asset Group Templates - Custom Fields Count", False, "No custom fields in template")
            return False
        
        # Check custom field structure
        first_field = custom_fields[0]
        required_field_attrs = ['id', 'name', 'label', 'type', 'required']
        missing_field_attrs = [attr for attr in required_field_attrs if attr not in first_field]
        
        if missing_field_attrs:
            self.log_test("Default Asset Group Templates - Custom Field Structure", False, f"Missing field attributes: {missing_field_attrs}")
            return False
        
        self.log_test("Default Asset Group Templates - Custom Field Structure", True, "Custom field structure is correct")
        
        # Verify specific field types are present
        all_field_types = []
        for template in response_data:
            for field in template.get('custom_fields', []):
                all_field_types.append(field.get('type'))
        
        expected_types = ['ip_address', 'mac_address', 'currency', 'date', 'password', 'version', 'url']
        found_types = [t for t in expected_types if t in all_field_types]
        
        if len(found_types) < 5:  # At least 5 of the expected types should be present
            self.log_test("Default Asset Group Templates - Field Types", False, f"Only found {len(found_types)} expected field types: {found_types}")
            return False
        
        self.log_test("Default Asset Group Templates - Field Types", True, f"Found {len(found_types)} expected field types: {found_types}")
        
        # Verify icons are specified
        templates_with_icons = [t for t in response_data if t.get('icon')]
        if len(templates_with_icons) != len(response_data):
            self.log_test("Default Asset Group Templates - Icons", False, f"Only {len(templates_with_icons)}/{len(response_data)} templates have icons")
            return False
        
        self.log_test("Default Asset Group Templates - Icons", True, "All templates have icons specified")
        
        return True

    def test_default_asset_type_templates(self):
        """Test GET /api/templates/default-asset-types endpoint"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-types', expected_status=200)
        
        if not success:
            self.log_test("Default Asset Type Templates - Basic Request", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        # Verify response is a list
        if not isinstance(response_data, list):
            self.log_test("Default Asset Type Templates - Response Type", False, f"Expected list, got {type(response_data)}")
            return False
        
        self.log_test("Default Asset Type Templates - Basic Request", True, f"Found {len(response_data)} templates")
        
        # Verify template structure
        if len(response_data) == 0:
            self.log_test("Default Asset Type Templates - Template Count", False, "No templates returned")
            return False
        
        # Check first template structure
        first_template = response_data[0]
        required_fields = ['name', 'description', 'icon', 'custom_fields']
        missing_fields = [field for field in required_fields if field not in first_template]
        
        if missing_fields:
            self.log_test("Default Asset Type Templates - Structure", False, f"Missing fields: {missing_fields}")
            return False
        
        self.log_test("Default Asset Type Templates - Structure", True, "All required fields present")
        
        # Verify custom_fields structure
        custom_fields = first_template.get('custom_fields', [])
        if not isinstance(custom_fields, list):
            self.log_test("Default Asset Type Templates - Custom Fields Type", False, f"custom_fields should be list, got {type(custom_fields)}")
            return False
        
        # Check custom field structure (if fields exist)
        if len(custom_fields) > 0:
            first_field = custom_fields[0]
            required_field_attrs = ['id', 'name', 'label', 'type', 'required']
            missing_field_attrs = [attr for attr in required_field_attrs if attr not in first_field]
            
            if missing_field_attrs:
                self.log_test("Default Asset Type Templates - Custom Field Structure", False, f"Missing field attributes: {missing_field_attrs}")
                return False
            
            self.log_test("Default Asset Type Templates - Custom Field Structure", True, "Custom field structure is correct")
        
        # Verify specific field types are present
        all_field_types = []
        for template in response_data:
            for field in template.get('custom_fields', []):
                all_field_types.append(field.get('type'))
        
        expected_types = ['serial_number', 'number', 'text', 'dataset']
        found_types = [t for t in expected_types if t in all_field_types]
        
        if len(found_types) < 3:  # At least 3 of the expected types should be present
            self.log_test("Default Asset Type Templates - Field Types", False, f"Only found {len(found_types)} expected field types: {found_types}")
            return False
        
        self.log_test("Default Asset Type Templates - Field Types", True, f"Found {len(found_types)} expected field types: {found_types}")
        
        # Verify icons are specified
        templates_with_icons = [t for t in response_data if t.get('icon')]
        if len(templates_with_icons) != len(response_data):
            self.log_test("Default Asset Type Templates - Icons", False, f"Only {len(templates_with_icons)}/{len(response_data)} templates have icons")
            return False
        
        self.log_test("Default Asset Type Templates - Icons", True, "All templates have icons specified")
        
        return True

    def test_asset_group_creation_with_template_data(self):
        """Test creating asset group using template data structure"""
        if not self.created_org_id:
            self.log_test("Asset Group Creation with Template Data", False, "No organization ID available")
            return False
        
        # First get template data
        success, template_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success or not isinstance(template_data, list) or len(template_data) == 0:
            self.log_test("Asset Group Creation with Template Data - Get Template", False, "Could not get template data")
            return False
        
        # Use first template as basis for asset group creation
        template = template_data[0]
        
        group_data = {
            "name": f"Test {template['name']} Group",
            "description": template['description'],
            "icon": template['icon'],
            "organization_id": self.created_org_id,
            "custom_fields": template['custom_fields']
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        
        if not success:
            self.log_test("Asset Group Creation with Template Data", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        # Verify the created group includes all template fields
        if 'custom_fields' not in response_data:
            self.log_test("Asset Group Creation with Template Data - Custom Fields", False, "No custom_fields in response")
            return False
        
        created_fields = response_data['custom_fields']
        template_fields = template['custom_fields']
        
        if len(created_fields) != len(template_fields):
            self.log_test("Asset Group Creation with Template Data - Field Count", False, f"Expected {len(template_fields)} fields, got {len(created_fields)}")
            return False
        
        # Verify field names match
        created_field_names = [f['name'] for f in created_fields]
        template_field_names = [f['name'] for f in template_fields]
        
        missing_fields = [name for name in template_field_names if name not in created_field_names]
        if missing_fields:
            self.log_test("Asset Group Creation with Template Data - Field Names", False, f"Missing fields: {missing_fields}")
            return False
        
        # Verify icon was saved
        if response_data.get('icon') != template['icon']:
            self.log_test("Asset Group Creation with Template Data - Icon", False, f"Expected icon '{template['icon']}', got '{response_data.get('icon')}'")
            return False
        
        self.log_test("Asset Group Creation with Template Data", True, f"Asset group created with {len(created_fields)} custom fields and icon")
        
        return True

    def test_template_data_completeness(self):
        """Test that template data includes all expected rich data"""
        # Test asset group templates
        success, ag_templates, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("Template Data Completeness - Asset Groups", False, f"Could not get asset group templates")
            return False
        
        # Check for specific templates we expect
        template_names = [t['name'] for t in ag_templates]
        expected_templates = ['Hardware', 'Software', 'Network Equipment', 'Cloud Services', 'Security']
        
        missing_templates = [name for name in expected_templates if name not in template_names]
        if missing_templates:
            self.log_test("Template Data Completeness - Asset Group Names", False, f"Missing templates: {missing_templates}")
            return False
        
        # Test asset type templates
        success, at_templates, status_code = self.make_request('GET', 'templates/default-asset-types', expected_status=200)
        
        if not success:
            self.log_test("Template Data Completeness - Asset Types", False, f"Could not get asset type templates")
            return False
        
        # Check for specific asset type templates
        at_template_names = [t['name'] for t in at_templates]
        expected_at_templates = ['Desktop Computer', 'Laptop', 'Server']
        
        missing_at_templates = [name for name in expected_at_templates if name not in at_template_names]
        if missing_at_templates:
            self.log_test("Template Data Completeness - Asset Type Names", False, f"Missing asset type templates: {missing_at_templates}")
            return False
        
        self.log_test("Template Data Completeness", True, f"Found all expected templates: {len(expected_templates)} asset groups, {len(expected_at_templates)} asset types")
        
        return True

    def run_template_tests(self):
        """Run all template-focused tests"""
        print(f"🚀 Starting Template Endpoint Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Setup
        print("\n🔐 Setting up authentication...")
        if not self.setup_authentication():
            print("❌ Authentication setup failed - stopping tests")
            return self.generate_report()
        
        print("\n🏢 Setting up organization...")
        if not self.setup_organization():
            print("❌ Organization setup failed - stopping tests")
            return self.generate_report()
        
        # Template tests
        print("\n📋 Template Endpoint Tests")
        self.test_default_asset_group_templates()
        self.test_default_asset_type_templates()
        self.test_template_data_completeness()
        
        print("\n🏗️ Template Integration Tests")
        self.test_asset_group_creation_with_template_data()
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print(f"📊 Template Test Results Summary")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All template tests passed!")
            return 0
        else:
            print("⚠️ Some template tests failed. Check the details above.")
            return 1

def main():
    tester = TemplateEndpointTester()
    return tester.run_template_tests()

if __name__ == "__main__":
    sys.exit(main())