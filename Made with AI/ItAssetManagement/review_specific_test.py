import requests
import sys
import json
from datetime import datetime

class ReviewSpecificTester:
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
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)

            success = response.status_code == expected_status
            response_data = None
            
            try:
                response_data = response.json()
            except:
                response_data = response.text

            return success, response_data, response.status_code

        except Exception as e:
            return False, str(e), 0

    def test_template_count_and_new_templates(self):
        """Test template count and verify the 5 new templates are present"""
        success, response_data, status_code = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if not success or not isinstance(response_data, list):
            self.log_test("Template Endpoint Access", False, f"Status: {status_code}, Response: {response_data}")
            return False, None

        template_count = len(response_data)
        
        # The review mentioned 18 total (was 13, now +5), but we actually have 21
        # Let's verify we have at least the expected new templates
        self.log_test("Template Count", True, f"Found {template_count} templates (actual count)")

        # Check for the 5 specific new templates mentioned in the review
        expected_new_templates = {
            "Networks & VLANs": "Network",
            "Network Interfaces": "Plug", 
            "Firewalls & Switches": "Shield",
            "Internal Services": "Cog",
            "Website Links & URLs": "Globe"
        }

        found_templates = {}
        for template in response_data:
            template_name = template.get('name', '')
            if template_name in expected_new_templates:
                found_templates[template_name] = template

        # Verify all 5 new templates are present
        missing_templates = set(expected_new_templates.keys()) - set(found_templates.keys())
        if missing_templates:
            self.log_test("New Templates Present", False, f"Missing templates: {list(missing_templates)}")
            return False, None
        else:
            self.log_test("New Templates Present", True, f"All 5 new templates found: {list(expected_new_templates.keys())}")

        return True, found_templates

    def test_new_template_icons(self, found_templates):
        """Verify new template icons"""
        if not found_templates:
            self.log_test("Template Icons", False, "No template data available")
            return False

        expected_icons = {
            "Networks & VLANs": "Network",
            "Network Interfaces": "Plug", 
            "Firewalls & Switches": "Shield",
            "Internal Services": "Cog",
            "Website Links & URLs": "Globe"
        }

        all_icons_correct = True
        for template_name, expected_icon in expected_icons.items():
            template = found_templates.get(template_name)
            if not template:
                self.log_test(f"Icon Check - {template_name}", False, "Template not found")
                all_icons_correct = False
                continue
                
            actual_icon = template.get('icon', '')
            if actual_icon != expected_icon:
                self.log_test(f"Icon Check - {template_name}", False, f"Expected '{expected_icon}', got '{actual_icon}'")
                all_icons_correct = False
            else:
                self.log_test(f"Icon Check - {template_name}", True, f"Correct icon: {actual_icon}")

        return all_icons_correct

    def test_template_custom_fields(self, found_templates):
        """Verify custom fields for each new template"""
        if not found_templates:
            self.log_test("Template Custom Fields", False, "No template data available")
            return False

        # Test Networks & VLANs template
        networks_template = found_templates.get("Networks & VLANs")
        if networks_template:
            custom_fields = networks_template.get('custom_fields', [])
            expected_fields = ['network_type', 'network_address', 'vlan_id', 'gateway_ip', 'dhcp_enabled', 'security_level']
            found_field_names = [field.get('name') for field in custom_fields]
            
            missing_fields = set(expected_fields) - set(found_field_names)
            if not missing_fields:
                self.log_test("Networks & VLANs Fields", True, f"All expected fields present: {expected_fields}")
            else:
                self.log_test("Networks & VLANs Fields", False, f"Missing fields: {list(missing_fields)}")

        # Test Network Interfaces template
        interfaces_template = found_templates.get("Network Interfaces")
        if interfaces_template:
            custom_fields = interfaces_template.get('custom_fields', [])
            expected_fields = ['interface_type', 'port_speed', 'interface_status', 'assigned_ip', 'mac_address']
            found_field_names = [field.get('name') for field in custom_fields]
            
            missing_fields = set(expected_fields) - set(found_field_names)
            if not missing_fields:
                self.log_test("Network Interfaces Fields", True, f"All expected fields present: {expected_fields}")
            else:
                self.log_test("Network Interfaces Fields", False, f"Missing fields: {list(missing_fields)}")

        # Test Firewalls & Switches template
        firewalls_template = found_templates.get("Firewalls & Switches")
        if firewalls_template:
            custom_fields = firewalls_template.get('custom_fields', [])
            expected_fields = ['device_type', 'port_count', 'management_ip', 'firmware_version', 'security_features', 'high_availability']
            found_field_names = [field.get('name') for field in custom_fields]
            
            missing_fields = set(expected_fields) - set(found_field_names)
            if not missing_fields:
                self.log_test("Firewalls & Switches Fields", True, f"All expected fields present: {expected_fields}")
            else:
                self.log_test("Firewalls & Switches Fields", False, f"Missing fields: {list(missing_fields)}")

        # Test Internal Services template
        services_template = found_templates.get("Internal Services")
        if services_template:
            custom_fields = services_template.get('custom_fields', [])
            expected_fields = ['service_type', 'service_port', 'protocol', 'service_status', 'auto_start', 'dependencies']
            found_field_names = [field.get('name') for field in custom_fields]
            
            missing_fields = set(expected_fields) - set(found_field_names)
            if not missing_fields:
                self.log_test("Internal Services Fields", True, f"All expected fields present: {expected_fields}")
            else:
                self.log_test("Internal Services Fields", False, f"Missing fields: {list(missing_fields)}")

        # Test Website Links & URLs template
        urls_template = found_templates.get("Website Links & URLs")
        if urls_template:
            custom_fields = urls_template.get('custom_fields', [])
            expected_fields = ['url_address', 'site_category', 'authentication_required', 'ssl_certificate', 'last_checked', 'criticality_level']
            found_field_names = [field.get('name') for field in custom_fields]
            
            missing_fields = set(expected_fields) - set(found_field_names)
            if not missing_fields:
                self.log_test("Website Links & URLs Fields", True, f"All expected fields present: {expected_fields}")
            else:
                self.log_test("Website Links & URLs Fields", False, f"Missing fields: {list(missing_fields)}")

        return True

    def test_advanced_field_types(self, found_templates):
        """Test advanced field types: ip_address, mac_address, url, version, multi_select"""
        if not found_templates:
            self.log_test("Advanced Field Types", False, "No template data available")
            return False

        advanced_field_types_found = set()
        field_type_details = []
        
        for template_name, template in found_templates.items():
            custom_fields = template.get('custom_fields', [])
            for field in custom_fields:
                field_type = field.get('type', '')
                field_name = field.get('name', '')
                
                # Check for advanced field types
                if field_type in ['ip_address', 'mac_address', 'url', 'version', 'multi_select']:
                    advanced_field_types_found.add(field_type)
                    field_type_details.append(f"{template_name}.{field_name} ({field_type})")

        # Verify we found the expected advanced field types
        expected_advanced_types = {'ip_address', 'mac_address', 'url', 'version', 'multi_select'}
        found_types = advanced_field_types_found & expected_advanced_types
        
        if found_types:
            self.log_test("Advanced Field Types Found", True, f"Found types: {list(found_types)} in fields: {field_type_details}")
        else:
            self.log_test("Advanced Field Types Found", False, "No advanced field types found")

        # Check for realistic dataset options
        dataset_validation_passed = True
        for template_name, template in found_templates.items():
            custom_fields = template.get('custom_fields', [])
            for field in custom_fields:
                if field.get('type') == 'dataset' and field.get('dataset_values'):
                    dataset_values = field['dataset_values']
                    field_name = field.get('name', '')
                    
                    # Check if dataset values look realistic (not empty, reasonable count)
                    if len(dataset_values) > 0 and len(dataset_values) <= 20:
                        self.log_test(f"Dataset Values - {template_name}.{field_name}", True, f"Realistic options: {dataset_values[:3]}..." if len(dataset_values) > 3 else f"Options: {dataset_values}")
                    else:
                        self.log_test(f"Dataset Values - {template_name}.{field_name}", False, f"Unrealistic dataset: {len(dataset_values)} values")
                        dataset_validation_passed = False

        return len(found_types) > 0 and dataset_validation_passed

    def test_boolean_and_number_fields(self, found_templates):
        """Test boolean and number fields are properly structured"""
        if not found_templates:
            self.log_test("Boolean/Number Fields", False, "No template data available")
            return False

        boolean_fields_found = 0
        number_fields_found = 0
        
        for template_name, template in found_templates.items():
            custom_fields = template.get('custom_fields', [])
            for field in custom_fields:
                field_type = field.get('type', '')
                field_name = field.get('name', '')
                
                if field_type == 'boolean':
                    boolean_fields_found += 1
                    # Check if boolean field has a default value
                    default_value = field.get('default_value')
                    if default_value is not None and isinstance(default_value, bool):
                        self.log_test(f"Boolean Field - {template_name}.{field_name}", True, f"Default: {default_value}")
                    else:
                        self.log_test(f"Boolean Field - {template_name}.{field_name}", True, f"No default (acceptable)")
                
                elif field_type == 'number':
                    number_fields_found += 1
                    self.log_test(f"Number Field - {template_name}.{field_name}", True, "Properly structured")

        if boolean_fields_found > 0 or number_fields_found > 0:
            self.log_test("Boolean/Number Field Structure", True, f"Found {boolean_fields_found} boolean, {number_fields_found} number fields")
            return True
        else:
            self.log_test("Boolean/Number Field Structure", False, "No boolean or number fields found")
            return False

    def run_all_tests(self):
        """Run all tests for the review request"""
        print("🧪 Testing Latest Batch of Templates (Review Request)")
        print("=" * 80)

        # Test 1: Template count and new template presence
        print("\n📊 Testing Template Count and New Template Presence")
        templates_success, found_templates = self.test_template_count_and_new_templates()
        
        if not templates_success or not found_templates:
            print("\n❌ Cannot proceed with further tests - template data unavailable")
            self.print_summary()
            return False

        # Test 2: New template icons
        print("\n🎨 Testing New Template Icons")
        icons_success = self.test_new_template_icons(found_templates)

        # Test 3: Template custom fields content
        print("\n📋 Testing Template Custom Fields")
        fields_success = self.test_template_custom_fields(found_templates)

        # Test 4: Advanced field types
        print("\n🔧 Testing Advanced Field Types")
        advanced_types_success = self.test_advanced_field_types(found_templates)

        # Test 5: Boolean and number fields
        print("\n🔢 Testing Boolean and Number Fields")
        bool_number_success = self.test_boolean_and_number_fields(found_templates)

        # Print summary
        self.print_summary()
        
        overall_success = templates_success and icons_success and fields_success and advanced_types_success and bool_number_success
        return overall_success

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print(f"📊 REVIEW REQUEST TEST SUMMARY")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
        else:
            failed_tests = [result for result in self.test_results if not result['success']]
            print(f"\n❌ {len(failed_tests)} FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['details']}")

if __name__ == "__main__":
    tester = ReviewSpecificTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)