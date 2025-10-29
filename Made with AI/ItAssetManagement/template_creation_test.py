import requests
import sys
import json
from datetime import datetime

class TemplateCreationTester:
    def __init__(self, base_url="https://assetmaster-13.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
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

            success = response.status_code == expected_status
            response_data = None
            
            try:
                response_data = response.json()
            except:
                response_data = response.text

            return success, response_data, response.status_code

        except Exception as e:
            return False, str(e), 0

    def setup_auth_and_org(self):
        """Setup authentication and organization for testing"""
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
            self.log_test("User Registration", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        self.user_data = user_data
        
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
        
        # Create organization
        org_data = {
            "name": f"Template Test Org {datetime.now().strftime('%H%M%S')}",
            "description": "Test organization for template testing"
        }
        
        success, response_data, status_code = self.make_request('POST', 'organizations', org_data, 200)
        if not success or 'id' not in response_data:
            self.log_test("Create Organization", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        self.created_org_id = response_data['id']
        self.log_test("Setup Auth and Organization", True, "Authentication and organization setup complete")
        return True

    def test_create_asset_group_from_storage_template(self):
        """Test creating asset group using Storage Devices template"""
        # Get templates first
        success, templates_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        if not success:
            self.log_test("Create Asset Group from Storage Template", False, f"Failed to get templates: {status_code}")
            return False

        # Find Storage Devices template
        storage_template = None
        for template in templates_data:
            if template.get('name') == 'Storage Devices':
                storage_template = template
                break
        
        if not storage_template:
            self.log_test("Create Asset Group from Storage Template", False, "Storage Devices template not found")
            return False

        # Create asset group using template data
        group_data = {
            "name": "Test Storage Assets",
            "description": storage_template.get('description', ''),
            "icon": storage_template.get('icon'),
            "organization_id": self.created_org_id,
            "custom_fields": storage_template.get('custom_fields', [])
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        
        if success and 'id' in response_data:
            # Verify custom fields were preserved
            created_fields = response_data.get('custom_fields', [])
            template_fields = storage_template.get('custom_fields', [])
            
            if len(created_fields) == len(template_fields):
                self.log_test("Create Asset Group from Storage Template", True, f"Asset group created with {len(created_fields)} custom fields")
            else:
                self.log_test("Create Asset Group from Storage Template", False, f"Field count mismatch: created {len(created_fields)}, expected {len(template_fields)}")
                return False
        else:
            self.log_test("Create Asset Group from Storage Template", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return True

    def test_create_asset_group_from_database_template(self):
        """Test creating asset group using Databases template"""
        # Get templates first
        success, templates_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        if not success:
            self.log_test("Create Asset Group from Database Template", False, f"Failed to get templates: {status_code}")
            return False

        # Find Databases template
        db_template = None
        for template in templates_data:
            if template.get('name') == 'Databases':
                db_template = template
                break
        
        if not db_template:
            self.log_test("Create Asset Group from Database Template", False, "Databases template not found")
            return False

        # Create asset group using template data
        group_data = {
            "name": "Test Database Assets",
            "description": db_template.get('description', ''),
            "icon": db_template.get('icon'),
            "organization_id": self.created_org_id,
            "custom_fields": db_template.get('custom_fields', [])
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        
        if success and 'id' in response_data:
            # Verify advanced field types are preserved
            created_fields = response_data.get('custom_fields', [])
            version_field = None
            file_size_field = None
            
            for field in created_fields:
                if field.get('type') == 'version':
                    version_field = field
                elif field.get('type') == 'file_size':
                    file_size_field = field
            
            if version_field and file_size_field:
                self.log_test("Create Asset Group from Database Template", True, f"Asset group created with advanced field types (version, file_size)")
            else:
                self.log_test("Create Asset Group from Database Template", False, f"Advanced field types not preserved correctly")
                return False
        else:
            self.log_test("Create Asset Group from Database Template", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return True

    def test_create_asset_group_from_vm_template(self):
        """Test creating asset group using Virtual Machines template"""
        # Get templates first
        success, templates_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        if not success:
            self.log_test("Create Asset Group from VM Template", False, f"Failed to get templates: {status_code}")
            return False

        # Find Virtual Machines template
        vm_template = None
        for template in templates_data:
            if template.get('name') == 'Virtual Machines':
                vm_template = template
                break
        
        if not vm_template:
            self.log_test("Create Asset Group from VM Template", False, "Virtual Machines template not found")
            return False

        # Create asset group using template data
        group_data = {
            "name": "Test Virtual Machine Assets",
            "description": vm_template.get('description', ''),
            "icon": vm_template.get('icon'),
            "organization_id": self.created_org_id,
            "custom_fields": vm_template.get('custom_fields', [])
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        
        if success and 'id' in response_data:
            # Verify multi_select field type is preserved
            created_fields = response_data.get('custom_fields', [])
            multi_select_field = None
            
            for field in created_fields:
                if field.get('type') == 'multi_select':
                    multi_select_field = field
                    break
            
            if multi_select_field:
                dataset_values = multi_select_field.get('dataset_values', [])
                if len(dataset_values) > 0:
                    self.log_test("Create Asset Group from VM Template", True, f"Asset group created with multi_select field having {len(dataset_values)} options")
                else:
                    self.log_test("Create Asset Group from VM Template", False, "Multi_select field missing dataset_values")
                    return False
            else:
                self.log_test("Create Asset Group from VM Template", False, "Multi_select field not found")
                return False
        else:
            self.log_test("Create Asset Group from VM Template", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return True

    def run_template_creation_tests(self):
        """Run all template creation tests"""
        print(f"🚀 Starting Template Creation Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Setup authentication and organization
        if not self.setup_auth_and_org():
            print("❌ Setup failed - stopping tests")
            return self.generate_report()
        
        print("\n🏗️ Template Creation Tests")
        self.test_create_asset_group_from_storage_template()
        self.test_create_asset_group_from_database_template()
        self.test_create_asset_group_from_vm_template()
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print(f"📊 Template Creation Test Results Summary")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All template creation tests passed!")
            return 0
        else:
            print("⚠️ Some template creation tests failed. Check the details above.")
            return 1

def main():
    tester = TemplateCreationTester()
    return tester.run_template_creation_tests()

if __name__ == "__main__":
    sys.exit(main())