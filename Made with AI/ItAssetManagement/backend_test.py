import requests
import sys
import json
from datetime import datetime
import uuid

class ITAssetManagementTester:
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

    def test_user_registration(self):
        """Test user registration"""
        test_email = f"test_user_{datetime.now().strftime('%H%M%S')}@example.com"
        user_data = {
            "name": "Test User",
            "email": test_email,
            "password": "TestPass123!",
            "role": "admin"
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/register', user_data, 200)
        
        if success:
            self.user_data = user_data
            self.log_test("User Registration", True, f"User created with email: {test_email}")
        else:
            self.log_test("User Registration", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_user_login(self):
        """Test user login"""
        if not self.user_data:
            self.log_test("User Login", False, "No user data available for login")
            return False
            
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        
        success, response_data, status_code = self.make_request('POST', 'auth/login', login_data, 200)
        
        if success and 'access_token' in response_data:
            self.token = response_data['access_token']
            self.log_test("User Login", True, f"Token received: {self.token[:20]}...")
        else:
            self.log_test("User Login", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response_data, status_code = self.make_request('GET', 'auth/me', expected_status=200)
        
        if success:
            self.log_test("Get Current User", True, f"User: {response_data.get('name', 'Unknown')}")
        else:
            self.log_test("Get Current User", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_create_organization(self):
        """Test creating an organization"""
        org_data = {
            "name": f"Test Organization {datetime.now().strftime('%H%M%S')}",
            "description": "Test organization for IT asset management"
        }
        
        success, response_data, status_code = self.make_request('POST', 'organizations', org_data, 200)
        
        if success and 'id' in response_data:
            self.created_org_id = response_data['id']
            self.log_test("Create Organization", True, f"Organization created with ID: {self.created_org_id}")
        else:
            self.log_test("Create Organization", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_get_organizations(self):
        """Test getting user's organizations"""
        success, response_data, status_code = self.make_request('GET', 'organizations', expected_status=200)
        
        if success and isinstance(response_data, list):
            org_count = len(response_data)
            self.log_test("Get Organizations", True, f"Found {org_count} organizations")
        else:
            self.log_test("Get Organizations", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_get_organization_by_id(self):
        """Test getting specific organization"""
        if not self.created_org_id:
            self.log_test("Get Organization by ID", False, "No organization ID available")
            return False
            
        success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}', expected_status=200)
        
        if success:
            self.log_test("Get Organization by ID", True, f"Organization: {response_data.get('name', 'Unknown')}")
        else:
            self.log_test("Get Organization by ID", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_create_asset_group(self):
        """Test creating an asset group"""
        if not self.created_org_id:
            self.log_test("Create Asset Group", False, "No organization ID available")
            return False
            
        group_data = {
            "name": "Hardware Assets",
            "description": "Physical devices and equipment",
            "organization_id": self.created_org_id
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        
        if success and 'id' in response_data:
            self.created_group_id = response_data['id']
            self.log_test("Create Asset Group", True, f"Asset group created with ID: {self.created_group_id}")
        else:
            self.log_test("Create Asset Group", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_get_asset_groups(self):
        """Test getting asset groups for organization"""
        if not self.created_org_id:
            self.log_test("Get Asset Groups", False, "No organization ID available")
            return False
            
        success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}/asset-groups', expected_status=200)
        
        if success and isinstance(response_data, list):
            group_count = len(response_data)
            self.log_test("Get Asset Groups", True, f"Found {group_count} asset groups")
        else:
            self.log_test("Get Asset Groups", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_create_asset_type(self):
        """Test creating an asset type"""
        if not self.created_group_id:
            self.log_test("Create Asset Type", False, "No asset group ID available")
            return False
            
        type_data = {
            "name": "Laptops",
            "description": "Portable computers and notebooks",
            "asset_group_id": self.created_group_id
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-types', type_data, 200)
        
        if success and 'id' in response_data:
            self.created_type_id = response_data['id']
            self.log_test("Create Asset Type", True, f"Asset type created with ID: {self.created_type_id}")
        else:
            self.log_test("Create Asset Type", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_get_asset_types(self):
        """Test getting asset types for group"""
        if not self.created_group_id:
            self.log_test("Get Asset Types", False, "No asset group ID available")
            return False
            
        success, response_data, status_code = self.make_request('GET', f'asset-groups/{self.created_group_id}/asset-types', expected_status=200)
        
        if success and isinstance(response_data, list):
            type_count = len(response_data)
            self.log_test("Get Asset Types", True, f"Found {type_count} asset types")
        else:
            self.log_test("Get Asset Types", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_create_asset(self):
        """Test creating an asset"""
        if not self.created_type_id:
            self.log_test("Create Asset", False, "No asset type ID available")
            return False
            
        asset_data = {
            "name": "MacBook Pro 16-inch",
            "description": "Development laptop for senior developer",
            "asset_type_id": self.created_type_id,
            "custom_data": {
                "serial_number": "ABC123456",
                "purchase_date": "2024-01-15",
                "warranty_expires": "2027-01-15"
            },
            "tags": ["development", "high-priority"],
            "relationships": []
        }
        
        success, response_data, status_code = self.make_request('POST', 'assets', asset_data, 200)
        
        if success and 'id' in response_data:
            self.created_asset_id = response_data['id']
            self.log_test("Create Asset", True, f"Asset created with ID: {self.created_asset_id}")
        else:
            self.log_test("Create Asset", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_get_assets_by_organization(self):
        """Test getting all assets for organization"""
        if not self.created_org_id:
            self.log_test("Get Assets by Organization", False, "No organization ID available")
            return False
            
        success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}/assets', expected_status=200)
        
        if success and isinstance(response_data, list):
            asset_count = len(response_data)
            self.log_test("Get Assets by Organization", True, f"Found {asset_count} assets")
        else:
            self.log_test("Get Assets by Organization", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_get_assets_by_type(self):
        """Test getting assets by type"""
        if not self.created_type_id:
            self.log_test("Get Assets by Type", False, "No asset type ID available")
            return False
            
        success, response_data, status_code = self.make_request('GET', f'asset-types/{self.created_type_id}/assets', expected_status=200)
        
        if success and isinstance(response_data, list):
            asset_count = len(response_data)
            self.log_test("Get Assets by Type", True, f"Found {asset_count} assets")
        else:
            self.log_test("Get Assets by Type", False, f"Status: {status_code}, Response: {response_data}")
        
        return success

    def test_update_asset(self):
        """Test updating an asset using PUT endpoint"""
        if not self.created_asset_id:
            self.log_test("Update Asset", False, "No asset ID available")
            return False
            
        update_data = {
            "name": "Updated MacBook Pro 16-inch",
            "description": "Updated development laptop for senior developer",
            "custom_data": {
                "serial_number": "ABC123456-UPDATED",
                "purchase_date": "2024-01-15",
                "warranty_expires": "2027-01-15",
                "updated_field": "new_value"
            },
            "tags": ["development", "high-priority", "updated"]
        }
        
        success, response_data, status_code = self.make_request('PUT', f'assets/{self.created_asset_id}', update_data, 200)
        
        if success and 'id' in response_data:
            # Verify the update worked
            if (response_data.get('name') == update_data['name'] and 
                response_data.get('description') == update_data['description']):
                self.log_test("Update Asset", True, f"Asset updated successfully")
            else:
                self.log_test("Update Asset", False, "Asset data not updated correctly")
                return False
        else:
            self.log_test("Update Asset", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_asset_group_with_custom_fields(self):
        """Test creating asset group with custom fields"""
        if not self.created_org_id:
            self.log_test("Asset Group with Custom Fields", False, "No organization ID available")
            return False
            
        group_data = {
            "name": "Software Assets with Custom Fields",
            "description": "Software applications with custom field definitions",
            "organization_id": self.created_org_id,
            "custom_fields": [
                {
                    "name": "license_type",
                    "label": "License Type",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["perpetual", "subscription", "open_source"],
                    "default_value": "subscription"
                },
                {
                    "name": "vendor",
                    "label": "Software Vendor",
                    "type": "text",
                    "required": True
                },
                {
                    "name": "license_count",
                    "label": "Number of Licenses",
                    "type": "number",
                    "required": False,
                    "default_value": 1
                },
                {
                    "name": "renewal_date",
                    "label": "License Renewal Date",
                    "type": "date",
                    "required": False
                },
                {
                    "name": "is_critical",
                    "label": "Critical Application",
                    "type": "boolean",
                    "default_value": False
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        
        if success and 'id' in response_data:
            self.created_group_with_fields_id = response_data['id']
            # Verify custom fields were saved
            if 'custom_fields' in response_data and len(response_data['custom_fields']) == 5:
                self.log_test("Asset Group with Custom Fields", True, f"Asset group with custom fields created")
            else:
                self.log_test("Asset Group with Custom Fields", False, "Custom fields not saved correctly")
                return False
        else:
            self.log_test("Asset Group with Custom Fields", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_asset_type_with_inheritance(self):
        """Test creating asset type that inherits custom fields from asset group"""
        if not hasattr(self, 'created_group_with_fields_id'):
            self.log_test("Asset Type with Inheritance", False, "No asset group with custom fields available")
            return False
            
        type_data = {
            "name": "Enterprise Software",
            "description": "Enterprise-level software applications",
            "asset_group_id": self.created_group_with_fields_id,
            "custom_fields": [
                {
                    "name": "support_level",
                    "label": "Support Level",
                    "type": "dataset",
                    "required": True,
                    "dataset_values": ["basic", "premium", "enterprise"],
                    "default_value": "basic"
                },
                {
                    "name": "deployment_type",
                    "label": "Deployment Type",
                    "type": "multi_select",
                    "dataset_values": ["on_premise", "cloud", "hybrid"],
                    "default_value": ["cloud"]
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-types', type_data, 200)
        
        if success and 'id' in response_data:
            self.created_type_with_inheritance_id = response_data['id']
            # Verify inheritance - should have both inherited and own fields
            if 'custom_fields' in response_data:
                total_fields = len(response_data['custom_fields'])
                inherited_fields = [f for f in response_data['custom_fields'] if f.get('inherited_from')]
                own_fields = [f for f in response_data['custom_fields'] if not f.get('inherited_from')]
                
                if len(inherited_fields) == 5 and len(own_fields) == 2:
                    self.log_test("Asset Type with Inheritance", True, f"Asset type created with {len(inherited_fields)} inherited and {len(own_fields)} own fields")
                else:
                    self.log_test("Asset Type with Inheritance", False, f"Field inheritance not working correctly. Inherited: {len(inherited_fields)}, Own: {len(own_fields)}")
                    return False
            else:
                self.log_test("Asset Type with Inheritance", False, "No custom fields found in response")
                return False
        else:
            self.log_test("Asset Type with Inheritance", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_asset_with_inherited_custom_fields(self):
        """Test creating asset with custom fields from both asset group and asset type"""
        if not hasattr(self, 'created_type_with_inheritance_id'):
            self.log_test("Asset with Inherited Custom Fields", False, "No asset type with inheritance available")
            return False
            
        asset_data = {
            "name": "Microsoft Office 365",
            "description": "Enterprise productivity suite",
            "asset_type_id": self.created_type_with_inheritance_id,
            "custom_data": {
                # Fields from asset group
                "license_type": "subscription",
                "vendor": "Microsoft",
                "license_count": 500,
                "renewal_date": "2025-12-31",
                "is_critical": True,
                # Fields from asset type
                "support_level": "enterprise",
                "deployment_type": ["cloud", "hybrid"],
                # Additional custom data
                "admin_contact": "it-admin@company.com"
            },
            "tags": ["productivity", "enterprise", "microsoft"]
        }
        
        success, response_data, status_code = self.make_request('POST', 'assets', asset_data, 200)
        
        if success and 'id' in response_data:
            self.created_asset_with_fields_id = response_data['id']
            # Verify custom data was saved
            if 'custom_data' in response_data:
                custom_data = response_data['custom_data']
                required_fields = ['license_type', 'vendor', 'support_level', 'deployment_type']
                missing_fields = [field for field in required_fields if field not in custom_data]
                
                if not missing_fields:
                    self.log_test("Asset with Inherited Custom Fields", True, f"Asset created with inherited custom fields")
                else:
                    self.log_test("Asset with Inherited Custom Fields", False, f"Missing custom fields: {missing_fields}")
                    return False
            else:
                self.log_test("Asset with Inherited Custom Fields", False, "No custom data found in response")
                return False
        else:
            self.log_test("Asset with Inherited Custom Fields", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_asset_type_change_update(self):
        """Test updating asset to different asset type and verify field inheritance changes"""
        if not hasattr(self, 'created_asset_with_fields_id') or not self.created_type_id:
            self.log_test("Asset Type Change Update", False, "Required assets/types not available")
            return False
            
        # Update asset to use the original asset type (without custom fields)
        update_data = {
            "asset_type_id": self.created_type_id,
            "custom_data": {
                "serial_number": "NEW123456",
                "model": "Updated Model"
            }
        }
        
        success, response_data, status_code = self.make_request('PUT', f'assets/{self.created_asset_with_fields_id}', update_data, 200)
        
        if success and 'id' in response_data:
            # Verify the asset type was changed
            if response_data.get('asset_type_id') == self.created_type_id:
                self.log_test("Asset Type Change Update", True, f"Asset type changed successfully")
            else:
                self.log_test("Asset Type Change Update", False, "Asset type not updated correctly")
                return False
        else:
            self.log_test("Asset Type Change Update", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_detailed_assets_endpoint(self):
        """Test the detailed assets endpoint that includes type and group information"""
        if not self.created_org_id:
            self.log_test("Detailed Assets Endpoint", False, "No organization ID available")
            return False
            
        success, response_data, status_code = self.make_request('GET', f'organizations/{self.created_org_id}/assets/detailed', expected_status=200)
        
        if success and isinstance(response_data, list):
            if len(response_data) > 0:
                # Check if detailed information is included
                first_asset = response_data[0]
                required_fields = ['asset_type_name', 'asset_group_name']
                missing_fields = [field for field in required_fields if field not in first_asset]
                
                if not missing_fields:
                    self.log_test("Detailed Assets Endpoint", True, f"Found {len(response_data)} detailed assets")
                else:
                    self.log_test("Detailed Assets Endpoint", False, f"Missing detailed fields: {missing_fields}")
                    return False
            else:
                self.log_test("Detailed Assets Endpoint", True, "No assets found (empty response is valid)")
        else:
            self.log_test("Detailed Assets Endpoint", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_field_type_support(self):
        """Test various field types support"""
        if not self.created_org_id:
            self.log_test("Field Type Support", False, "No organization ID available")
            return False
            
        # Create asset group with all supported field types
        group_data = {
            "name": "Field Types Test Group",
            "description": "Testing all supported field types",
            "organization_id": self.created_org_id,
            "custom_fields": [
                {
                    "name": "text_field",
                    "label": "Text Field",
                    "type": "text",
                    "default_value": "default text"
                },
                {
                    "name": "number_field",
                    "label": "Number Field",
                    "type": "number",
                    "default_value": 42
                },
                {
                    "name": "date_field",
                    "label": "Date Field",
                    "type": "date",
                    "default_value": "2024-01-01"
                },
                {
                    "name": "boolean_field",
                    "label": "Boolean Field",
                    "type": "boolean",
                    "default_value": True
                },
                {
                    "name": "dataset_field",
                    "label": "Dataset Field",
                    "type": "dataset",
                    "dataset_values": ["option1", "option2", "option3"],
                    "default_value": "option1"
                },
                {
                    "name": "file_field",
                    "label": "File Field",
                    "type": "file"
                },
                {
                    "name": "rich_text_field",
                    "label": "Rich Text Field",
                    "type": "rich_text",
                    "default_value": "<p>Default rich text</p>"
                },
                {
                    "name": "multi_select_field",
                    "label": "Multi Select Field",
                    "type": "multi_select",
                    "dataset_values": ["tag1", "tag2", "tag3"],
                    "default_value": ["tag1", "tag2"]
                },
                {
                    "name": "asset_reference_field",
                    "label": "Asset Reference Field",
                    "type": "asset_reference"
                }
            ]
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', group_data, 200)
        
        if success and 'id' in response_data:
            # Verify all field types were saved correctly
            if 'custom_fields' in response_data and len(response_data['custom_fields']) == 9:
                field_types = [field['type'] for field in response_data['custom_fields']]
                expected_types = ['text', 'number', 'date', 'boolean', 'dataset', 'file', 'rich_text', 'multi_select', 'asset_reference']
                
                if all(field_type in field_types for field_type in expected_types):
                    self.log_test("Field Type Support", True, f"All {len(expected_types)} field types supported")
                else:
                    missing_types = [t for t in expected_types if t not in field_types]
                    self.log_test("Field Type Support", False, f"Missing field types: {missing_types}")
                    return False
            else:
                self.log_test("Field Type Support", False, "Not all field types were saved")
                return False
        else:
            self.log_test("Field Type Support", False, f"Status: {status_code}, Response: {response_data}")
            return False
        
        return success

    def test_unauthorized_access(self):
        """Test unauthorized access scenarios"""
        # Save current token
        original_token = self.token
        
        # Test without token
        self.token = None
        success, response_data, status_code = self.make_request('GET', 'organizations', expected_status=401)
        
        if status_code in [401, 403]:  # Both 401 and 403 are valid for unauthorized access
            self.log_test("Unauthorized Access - No Token", True, f"Correctly rejected request without token (status: {status_code})")
        else:
            self.log_test("Unauthorized Access - No Token", False, f"Expected 401 or 403, got {status_code}")
        
        # Test with invalid token
        self.token = "invalid_token_12345"
        success, response_data, status_code = self.make_request('GET', 'organizations', expected_status=401)
        
        if status_code in [401, 403]:  # Both 401 and 403 are valid for unauthorized access
            self.log_test("Unauthorized Access - Invalid Token", True, f"Correctly rejected request with invalid token (status: {status_code})")
        else:
            self.log_test("Unauthorized Access - Invalid Token", False, f"Expected 401 or 403, got {status_code}")
        
        # Restore original token
        self.token = original_token
        return True

    def test_validation_errors(self):
        """Test validation error scenarios"""
        if not self.created_org_id:
            self.log_test("Validation Errors", False, "No organization ID available")
            return False
        
        # Test creating asset group with missing required fields
        invalid_group_data = {
            "description": "Missing name field"
            # Missing name and organization_id
        }
        
        success, response_data, status_code = self.make_request('POST', 'asset-groups', invalid_group_data, 422)
        
        if status_code == 422:
            self.log_test("Validation Errors - Missing Required Fields", True, "Correctly rejected invalid data")
        else:
            self.log_test("Validation Errors - Missing Required Fields", False, f"Expected 422, got {status_code}")
        
        return True

    def test_default_templates(self):
        """Test getting default templates"""
        # Test asset group templates
        success1, response_data1, status_code1 = self.make_request('GET', 'templates/default-asset-groups', expected_status=200)
        
        if success1 and isinstance(response_data1, list):
            self.log_test("Get Default Asset Group Templates", True, f"Found {len(response_data1)} templates")
        else:
            self.log_test("Get Default Asset Group Templates", False, f"Status: {status_code1}, Response: {response_data1}")
        
        # Test asset type templates
        success2, response_data2, status_code2 = self.make_request('GET', 'templates/default-asset-types', expected_status=200)
        
        if success2 and isinstance(response_data2, list):
            template_count = len(response_data2)
            self.log_test("Get Default Asset Type Templates", True, f"Found {template_count} type templates")
        else:
            self.log_test("Get Default Asset Type Templates", False, f"Status: {status_code2}, Response: {response_data2}")
        
        return success1 and success2

    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting IT Asset Management System API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Authentication tests
        print("\n🔐 Authentication Tests")
        if not self.test_user_registration():
            print("❌ Registration failed - stopping tests")
            return self.generate_report()
            
        if not self.test_user_login():
            print("❌ Login failed - stopping tests")
            return self.generate_report()
            
        self.test_get_current_user()
        
        # Organization tests
        print("\n🏢 Organization Tests")
        if not self.test_create_organization():
            print("❌ Organization creation failed - stopping tests")
            return self.generate_report()
            
        self.test_get_organizations()
        self.test_get_organization_by_id()
        
        # Asset Group tests
        print("\n📦 Asset Group Tests")
        if not self.test_create_asset_group():
            print("❌ Asset group creation failed - stopping tests")
            return self.generate_report()
            
        self.test_get_asset_groups()
        
        # Asset Type tests
        print("\n🏷️ Asset Type Tests")
        if not self.test_create_asset_type():
            print("❌ Asset type creation failed - stopping tests")
            return self.generate_report()
            
        self.test_get_asset_types()
        
        # Asset tests
        print("\n💻 Asset Tests")
        if not self.test_create_asset():
            print("❌ Asset creation failed - stopping tests")
            return self.generate_report()
            
        self.test_get_assets_by_organization()
        self.test_get_assets_by_type()
        
        # Asset Update tests
        print("\n🔄 Asset Update Tests")
        self.test_update_asset()
        
        # Custom Fields and Inheritance tests
        print("\n🏗️ Custom Fields & Inheritance Tests")
        if self.test_asset_group_with_custom_fields():
            if self.test_asset_type_with_inheritance():
                self.test_asset_with_inherited_custom_fields()
                self.test_asset_type_change_update()
        
        # Field Type Support tests
        print("\n🔧 Field Type Support Tests")
        self.test_field_type_support()
        
        # Detailed Assets tests
        print("\n📊 Detailed Assets Tests")
        self.test_detailed_assets_endpoint()
        
        # Security tests
        print("\n🔒 Security Tests")
        self.test_unauthorized_access()
        self.test_validation_errors()
        
        # Template tests
        print("\n📋 Template Tests")
        self.test_default_templates()
        
        return self.generate_report()

    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print(f"📊 Test Results Summary")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠️ Some tests failed. Check the details above.")
            return 1

def main():
    tester = ITAssetManagementTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())