import requests
import sys
import json
from datetime import datetime

class NewTemplatesSpecificTester:
    def __init__(self, base_url="https://assetmaster-13.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

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
        """Make HTTP request"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

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

    def test_updated_template_endpoint_count(self):
        """Test that GET /api/templates/default-asset-groups returns the expected number of templates"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if success and isinstance(response_data, list):
            template_count = len(response_data)
            # Based on the backend code, there should be 16 templates total
            expected_count = 16
            if template_count == expected_count:
                self.log_test("Updated Template Endpoint Count", True, f"Found {template_count} templates (expected {expected_count})")
            else:
                self.log_test("Updated Template Endpoint Count", False, f"Found {template_count} templates, expected {expected_count}")
                return False
        else:
            self.log_test("Updated Template Endpoint Count", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_new_template_presence(self):
        """Test that new templates are present with correct names"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("New Template Presence", False, f"Failed to get templates: {status_code}")
            return False

        # Expected new templates based on the review request
        expected_new_templates = [
            "Storage Devices",
            "Cloud & Virtual Resources", 
            "Digital & Data Assets",
            "Databases",
            "Virtual Machines",
            "Licenses & Compliance"
        ]
        
        template_names = [template.get('name', '') for template in response_data]
        missing_templates = []
        
        for expected_template in expected_new_templates:
            if expected_template not in template_names:
                missing_templates.append(expected_template)
        
        if not missing_templates:
            self.log_test("New Template Presence", True, f"All {len(expected_new_templates)} new templates found")
        else:
            self.log_test("New Template Presence", False, f"Missing templates: {missing_templates}")
            return False
        
        return True

    def test_new_template_icons(self):
        """Test that new templates have proper icons"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("New Template Icons", False, f"Failed to get templates: {status_code}")
            return False

        # Expected icons for new templates
        expected_icons = {
            "Storage Devices": "HardDrive",
            "Cloud & Virtual Resources": "Cloud",
            "Digital & Data Assets": "FileText", 
            "Databases": "Database",
            "Virtual Machines": "Server",
            "Licenses & Compliance": "FileText"
        }
        
        templates_by_name = {template.get('name'): template for template in response_data}
        icon_issues = []
        
        for template_name, expected_icon in expected_icons.items():
            if template_name in templates_by_name:
                actual_icon = templates_by_name[template_name].get('icon')
                if actual_icon != expected_icon:
                    icon_issues.append(f"{template_name}: expected '{expected_icon}', got '{actual_icon}'")
            else:
                icon_issues.append(f"{template_name}: template not found")
        
        if not icon_issues:
            self.log_test("New Template Icons", True, f"All new templates have correct icons")
        else:
            self.log_test("New Template Icons", False, f"Icon issues: {icon_issues}")
            return False
        
        return True

    def test_advanced_field_types(self):
        """Test that new templates include advanced field types"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("Advanced Field Types", False, f"Failed to get templates: {status_code}")
            return False

        # Expected advanced field types from the review request
        expected_advanced_types = ["file_size", "duration", "currency", "version", "multi_select"]
        
        found_advanced_types = set()
        
        for template in response_data:
            custom_fields = template.get('custom_fields', [])
            for field in custom_fields:
                field_type = field.get('type')
                if field_type in expected_advanced_types:
                    found_advanced_types.add(field_type)
        
        missing_types = set(expected_advanced_types) - found_advanced_types
        
        if not missing_types:
            self.log_test("Advanced Field Types", True, f"All advanced field types found: {sorted(found_advanced_types)}")
        else:
            self.log_test("Advanced Field Types", False, f"Missing advanced field types: {sorted(missing_types)}")
            return False
        
        return True

    def test_storage_devices_template_content(self):
        """Test Storage Devices template has expected custom fields"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("Storage Devices Template Content", False, f"Failed to get templates: {status_code}")
            return False

        storage_template = None
        for template in response_data:
            if template.get('name') == 'Storage Devices':
                storage_template = template
                break
        
        if not storage_template:
            self.log_test("Storage Devices Template Content", False, "Storage Devices template not found")
            return False

        expected_fields = ["storage_type", "capacity", "interface", "encryption_enabled", "file_system"]
        custom_fields = storage_template.get('custom_fields', [])
        field_names = [field.get('name') for field in custom_fields]
        
        missing_fields = [field for field in expected_fields if field not in field_names]
        
        if not missing_fields:
            self.log_test("Storage Devices Template Content", True, f"All expected fields found: {expected_fields}")
        else:
            self.log_test("Storage Devices Template Content", False, f"Missing fields: {missing_fields}")
            return False
        
        return True

    def test_databases_template_content(self):
        """Test Databases template has expected custom fields"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("Databases Template Content", False, f"Failed to get templates: {status_code}")
            return False

        db_template = None
        for template in response_data:
            if template.get('name') == 'Databases':
                db_template = template
                break
        
        if not db_template:
            self.log_test("Databases Template Content", False, "Databases template not found")
            return False

        expected_fields = ["database_type", "database_version", "environment", "database_size", "backup_frequency"]
        custom_fields = db_template.get('custom_fields', [])
        field_names = [field.get('name') for field in custom_fields]
        
        missing_fields = [field for field in expected_fields if field not in field_names]
        
        if not missing_fields:
            self.log_test("Databases Template Content", True, f"All expected fields found: {expected_fields}")
        else:
            self.log_test("Databases Template Content", False, f"Missing fields: {missing_fields}")
            return False
        
        return True

    def test_virtual_machines_template_content(self):
        """Test Virtual Machines template has expected custom fields"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("Virtual Machines Template Content", False, f"Failed to get templates: {status_code}")
            return False

        vm_template = None
        for template in response_data:
            if template.get('name') == 'Virtual Machines':
                vm_template = template
                break
        
        if not vm_template:
            self.log_test("Virtual Machines Template Content", False, "Virtual Machines template not found")
            return False

        expected_fields = ["hypervisor", "operating_system", "virtualization_type", "allocated_cpu", "allocated_memory", "primary_services"]
        custom_fields = vm_template.get('custom_fields', [])
        field_names = [field.get('name') for field in custom_fields]
        
        missing_fields = [field for field in expected_fields if field not in field_names]
        
        if not missing_fields:
            self.log_test("Virtual Machines Template Content", True, f"All expected fields found: {expected_fields}")
        else:
            self.log_test("Virtual Machines Template Content", False, f"Missing fields: {missing_fields}")
            return False
        
        return True

    def test_cloud_virtual_resources_template_content(self):
        """Test Cloud & Virtual Resources template has expected custom fields"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("Cloud & Virtual Resources Template Content", False, f"Failed to get templates: {status_code}")
            return False

        cloud_template = None
        for template in response_data:
            if template.get('name') == 'Cloud & Virtual Resources':
                cloud_template = template
                break
        
        if not cloud_template:
            self.log_test("Cloud & Virtual Resources Template Content", False, "Cloud & Virtual Resources template not found")
            return False

        expected_fields = ["provider", "region", "instance_type", "monthly_cost", "auto_scaling"]
        custom_fields = cloud_template.get('custom_fields', [])
        field_names = [field.get('name') for field in custom_fields]
        
        missing_fields = [field for field in expected_fields if field not in field_names]
        
        if not missing_fields:
            self.log_test("Cloud & Virtual Resources Template Content", True, f"All expected fields found: {expected_fields}")
        else:
            self.log_test("Cloud & Virtual Resources Template Content", False, f"Missing fields: {missing_fields}")
            return False
        
        return True

    def test_template_structure_validation(self):
        """Test that all new templates have proper structure"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success:
            self.log_test("Template Structure Validation", False, f"Failed to get templates: {status_code}")
            return False

        new_template_names = [
            "Storage Devices", "Cloud & Virtual Resources", "Digital & Data Assets",
            "Databases", "Virtual Machines", "Licenses & Compliance"
        ]
        
        structure_issues = []
        
        for template in response_data:
            if template.get('name') in new_template_names:
                # Check required fields
                required_fields = ['name', 'description', 'icon', 'custom_fields']
                for field in required_fields:
                    if field not in template:
                        structure_issues.append(f"{template.get('name', 'Unknown')}: missing '{field}'")
                
                # Check custom_fields structure
                custom_fields = template.get('custom_fields', [])
                if not isinstance(custom_fields, list):
                    structure_issues.append(f"{template.get('name', 'Unknown')}: custom_fields is not a list")
                else:
                    for i, field in enumerate(custom_fields):
                        field_required = ['id', 'name', 'label', 'type']
                        for req_field in field_required:
                            if req_field not in field:
                                structure_issues.append(f"{template.get('name', 'Unknown')}: field {i} missing '{req_field}'")
        
        if not structure_issues:
            self.log_test("Template Structure Validation", True, f"All new templates have proper structure")
        else:
            self.log_test("Template Structure Validation", False, f"Structure issues: {structure_issues[:5]}")  # Show first 5 issues
            return False
        
        return True

    def run_new_template_tests(self):
        """Run all new template specific tests"""
        print(f"🚀 Starting New Templates Specific Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        print("\n📋 New Template Tests")
        self.test_updated_template_endpoint_count()
        self.test_new_template_presence()
        self.test_new_template_icons()
        self.test_advanced_field_types()
        
        print("\n🔍 Template Content Validation")
        self.test_storage_devices_template_content()
        self.test_databases_template_content()
        self.test_virtual_machines_template_content()
        self.test_cloud_virtual_resources_template_content()
        
        print("\n🏗️ Template Structure Validation")
        self.test_template_structure_validation()
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print(f"📊 New Templates Test Results Summary")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All new template tests passed!")
            return 0
        else:
            print("⚠️ Some new template tests failed. Check the details above.")
            return 1

def main():
    tester = NewTemplatesSpecificTester()
    return tester.run_new_template_tests()

if __name__ == "__main__":
    sys.exit(main())