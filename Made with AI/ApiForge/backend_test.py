import requests
import sys
import json
from datetime import datetime
import uuid

class APIForgeBackendTester:
    def __init__(self, base_url="https://devforge-api.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data
        self.test_username = f"testuser_{datetime.now().strftime('%H%M%S')}"
        self.test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
        self.test_password = "TestPass123!"
        
        self.collection_id = None
        self.request_id = None
        self.environment_id = None

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        result = {
            "test_name": name,
            "status": status,
            "success": success,
            "details": details
        }
        self.test_results.append(result)
        print(f"{status} - {name}: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f" (Expected: {expected_status})"
                if response.text:
                    try:
                        error_data = response.json()
                        details += f" - {error_data.get('detail', response.text[:100])}"
                    except:
                        details += f" - {response.text[:100]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "username": self.test_username,
                "email": self.test_email,
                "password": self.test_password
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            return True
        return False

    def test_user_login(self):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={
                "username": self.test_username,
                "password": self.test_password
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_get_user_profile(self):
        """Test getting user profile"""
        success, response = self.run_test(
            "Get User Profile",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_collection(self):
        """Test creating a collection"""
        success, response = self.run_test(
            "Create Collection",
            "POST",
            "collections",
            200,
            data={
                "name": "Test Collection",
                "description": "A test collection for API testing"
            }
        )
        
        if success and 'id' in response:
            self.collection_id = response['id']
            return True
        return False

    def test_get_collections(self):
        """Test getting collections"""
        success, response = self.run_test(
            "Get Collections",
            "GET",
            "collections",
            200
        )
        return success

    def test_get_collection_by_id(self):
        """Test getting a specific collection"""
        if not self.collection_id:
            self.log_test("Get Collection by ID", False, "No collection ID available")
            return False
            
        success, response = self.run_test(
            "Get Collection by ID",
            "GET",
            f"collections/{self.collection_id}",
            200
        )
        return success

    def test_update_collection(self):
        """Test updating a collection"""
        if not self.collection_id:
            self.log_test("Update Collection", False, "No collection ID available")
            return False
            
        success, response = self.run_test(
            "Update Collection",
            "PUT",
            f"collections/{self.collection_id}",
            200,
            data={
                "name": "Updated Test Collection",
                "description": "Updated description"
            }
        )
        return success

    def test_create_request(self):
        """Test creating an API request"""
        if not self.collection_id:
            self.log_test("Create Request", False, "No collection ID available")
            return False
            
        success, response = self.run_test(
            "Create Request",
            "POST",
            "requests",
            200,
            data={
                "name": "Test GET Request",
                "method": "GET",
                "url": "https://httpbin.org/get",
                "headers": {"Content-Type": "application/json"},
                "collection_id": self.collection_id
            }
        )
        
        if success and 'id' in response:
            self.request_id = response['id']
            return True
        return False

    def test_get_requests(self):
        """Test getting requests for a collection"""
        if not self.collection_id:
            self.log_test("Get Requests", False, "No collection ID available")
            return False
            
        success, response = self.run_test(
            "Get Requests",
            "GET",
            f"requests/{self.collection_id}",
            200
        )
        return success

    def test_update_request(self):
        """Test updating a request"""
        if not self.request_id:
            self.log_test("Update Request", False, "No request ID available")
            return False
            
        success, response = self.run_test(
            "Update Request",
            "PUT",
            f"requests/{self.request_id}",
            200,
            data={
                "name": "Updated Test Request",
                "method": "POST",
                "url": "https://httpbin.org/post",
                "headers": {"Content-Type": "application/json"},
                "body": '{"test": "data"}',
                "collection_id": self.collection_id
            }
        )
        return success

    def test_execute_request(self):
        """Test executing an API request"""
        success, response = self.run_test(
            "Execute API Request",
            "POST",
            "execute",
            200,
            data={
                "method": "GET",
                "url": "https://httpbin.org/get",
                "headers": {"Content-Type": "application/json"}
            }
        )
        return success

    def test_multi_protocol_rest(self):
        """Test REST protocol execution"""
        success, response = self.run_test(
            "REST Protocol Execution",
            "POST",
            "execute",
            200,
            data={
                "protocol": "REST",
                "method": "POST",
                "url": "https://httpbin.org/post",
                "headers": {"Content-Type": "application/json"},
                "body": '{"test": "rest_data"}',
                "query_params": {"param1": "value1"}
            }
        )
        return success

    def test_multi_protocol_soap(self):
        """Test SOAP protocol execution"""
        soap_body = """<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <test>SOAP Test</test>
            </soap:Body>
        </soap:Envelope>"""
        
        success, response = self.run_test(
            "SOAP Protocol Execution",
            "POST",
            "execute",
            200,
            data={
                "protocol": "SOAP",
                "method": "POST",
                "url": "https://httpbin.org/post",
                "headers": {"Content-Type": "text/xml; charset=utf-8", "SOAPAction": "test"},
                "body": soap_body
            }
        )
        return success

    def test_multi_protocol_graphql(self):
        """Test GraphQL protocol execution"""
        success, response = self.run_test(
            "GraphQL Protocol Execution",
            "POST",
            "execute",
            200,
            data={
                "protocol": "GraphQL",
                "method": "POST",
                "url": "https://httpbin.org/post",
                "headers": {"Content-Type": "application/json"},
                "body": '{"query": "{ test }"}'
            }
        )
        return success

    def test_auth_bearer_token(self):
        """Test Bearer token authentication"""
        success, response = self.run_test(
            "Bearer Token Auth",
            "POST",
            "execute",
            200,
            data={
                "method": "GET",
                "url": "https://httpbin.org/bearer",
                "auth": {
                    "type": "bearer",
                    "token": "test-bearer-token"
                }
            }
        )
        return success

    def test_auth_basic(self):
        """Test Basic authentication"""
        success, response = self.run_test(
            "Basic Auth",
            "POST",
            "execute",
            200,
            data={
                "method": "GET",
                "url": "https://httpbin.org/basic-auth/testuser/testpass",
                "auth": {
                    "type": "basic",
                    "username": "testuser",
                    "password": "testpass"
                }
            }
        )
        return success

    def test_auth_api_key_header(self):
        """Test API Key authentication in header"""
        success, response = self.run_test(
            "API Key Auth (Header)",
            "POST",
            "execute",
            200,
            data={
                "method": "GET",
                "url": "https://httpbin.org/get",
                "auth": {
                    "type": "apikey",
                    "key": "X-API-Key",
                    "value": "test-api-key",
                    "location": "header"
                }
            }
        )
        return success

    def test_auth_api_key_query(self):
        """Test API Key authentication in query parameter"""
        success, response = self.run_test(
            "API Key Auth (Query)",
            "POST",
            "execute",
            200,
            data={
                "method": "GET",
                "url": "https://httpbin.org/get",
                "auth": {
                    "type": "apikey",
                    "key": "api_key",
                    "value": "test-query-key",
                    "location": "query"
                }
            }
        )
        return success

    def test_environment_variable_substitution(self):
        """Test environment variable substitution"""
        # First create an environment with variables
        env_success, env_response = self.run_test(
            "Create Environment for Variable Test",
            "POST",
            "environments",
            200,
            data={
                "name": "Variable Test Environment",
                "variables": {"BASE_URL": "https://httpbin.org", "API_KEY": "test-key-123"},
                "is_active": True
            }
        )
        
        if not env_success:
            return False
        
        # Test variable substitution in URL and headers
        success, response = self.run_test(
            "Environment Variable Substitution",
            "POST",
            "execute",
            200,
            data={
                "method": "GET",
                "url": "{{BASE_URL}}/get",
                "headers": {"X-API-Key": "{{API_KEY}}"}
            }
        )
        return success

    def test_request_history(self):
        """Test request history functionality"""
        # Execute a request first to create history
        self.run_test(
            "Execute Request for History",
            "POST",
            "execute",
            200,
            data={
                "method": "GET",
                "url": "https://httpbin.org/get",
                "headers": {"Content-Type": "application/json"}
            }
        )
        
        # Now test getting history
        success, response = self.run_test(
            "Get Request History",
            "GET",
            "history?limit=10",
            200
        )
        return success

    def test_import_openapi(self):
        """Test OpenAPI/Swagger import"""
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "servers": [{"url": "https://api.example.com"}],
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "summary": "Get all users",
                        "responses": {"200": {"description": "Success"}}
                    }
                }
            }
        }
        
        success, response = self.run_test(
            "Import OpenAPI Specification",
            "POST",
            "import",
            200,
            data={
                "type": "openapi",
                "content": json.dumps(openapi_spec),
                "collection_name": "Imported OpenAPI Collection"
            }
        )
        return success

    def test_import_postman(self):
        """Test Postman collection import"""
        postman_collection = {
            "info": {"name": "Test Collection"},
            "item": [
                {
                    "name": "Test Request",
                    "request": {
                        "method": "GET",
                        "url": "https://api.example.com/test",
                        "header": [{"key": "Content-Type", "value": "application/json"}]
                    }
                }
            ]
        }
        
        success, response = self.run_test(
            "Import Postman Collection",
            "POST",
            "import",
            200,
            data={
                "type": "postman",
                "content": json.dumps(postman_collection),
                "collection_name": "Imported Postman Collection"
            }
        )
        return success

    def test_import_wsdl(self):
        """Test WSDL import"""
        wsdl_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <definitions xmlns="http://schemas.xmlsoap.org/wsdl/"
                     xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
                     targetNamespace="http://example.com/test">
            <service name="TestService">
                <port name="TestPort" binding="tns:TestBinding">
                    <soap:address location="http://example.com/test"/>
                </port>
            </service>
            <binding name="TestBinding" type="tns:TestPortType">
                <operation name="TestOperation">
                    <soap:operation soapAction="test"/>
                </operation>
            </binding>
        </definitions>'''
        
        success, response = self.run_test(
            "Import WSDL Specification",
            "POST",
            "import",
            200,
            data={
                "type": "wsdl",
                "content": wsdl_content,
                "collection_name": "Imported WSDL Collection"
            }
        )
        return success

    def test_graphql_introspection(self):
        """Test GraphQL schema introspection"""
        # This will likely fail with httpbin, but we test the endpoint exists
        success, response = self.run_test(
            "GraphQL Schema Introspection",
            "POST",
            "graphql/introspect?url=https://httpbin.org/post",
            400  # Expected to fail with httpbin, but endpoint should exist
        )
        # We consider this successful if we get a 400 (bad request) rather than 404 (not found)
        return success

    def test_enhanced_request_with_all_fields(self):
        """Test creating request with all enhanced fields"""
        if not self.collection_id:
            self.log_test("Enhanced Request Creation", False, "No collection ID available")
            return False
            
        success, response = self.run_test(
            "Create Enhanced Request",
            "POST",
            "requests",
            200,
            data={
                "name": "Enhanced Test Request",
                "protocol": "REST",
                "method": "POST",
                "url": "https://httpbin.org/post",
                "headers": {
                    "Content-Type": "application/json",
                    "X-Custom-Header": "test-value"
                },
                "query_params": {
                    "param1": "value1",
                    "param2": "value2"
                },
                "body": '{"enhanced": true, "test": "data"}',
                "auth": {
                    "type": "bearer",
                    "token": "test-token"
                },
                "collection_id": self.collection_id
            }
        )
        return success

    def test_create_environment(self):
        """Test creating an environment"""
        success, response = self.run_test(
            "Create Environment",
            "POST",
            "environments",
            200,
            data={
                "name": "Test Environment",
                "variables": {"BASE_URL": "https://api.example.com"},
                "is_active": True
            }
        )
        
        if success and 'id' in response:
            self.environment_id = response['id']
            return True
        return False

    def test_get_environments(self):
        """Test getting environments"""
        success, response = self.run_test(
            "Get Environments",
            "GET",
            "environments",
            200
        )
        return success

    def test_update_environment(self):
        """Test updating an environment"""
        if not self.environment_id:
            self.log_test("Update Environment", False, "No environment ID available")
            return False
            
        success, response = self.run_test(
            "Update Environment",
            "PUT",
            f"environments/{self.environment_id}",
            200,
            data={
                "name": "Updated Test Environment",
                "variables": {"BASE_URL": "https://api.updated.com"},
                "is_active": False
            }
        )
        return success

    def test_delete_request(self):
        """Test deleting a request"""
        if not self.request_id:
            self.log_test("Delete Request", False, "No request ID available")
            return False
            
        success, response = self.run_test(
            "Delete Request",
            "DELETE",
            f"requests/{self.request_id}",
            200
        )
        return success

    def test_delete_environment(self):
        """Test deleting an environment"""
        if not self.environment_id:
            self.log_test("Delete Environment", False, "No environment ID available")
            return False
            
        success, response = self.run_test(
            "Delete Environment",
            "DELETE",
            f"environments/{self.environment_id}",
            200
        )
        return success

    def test_delete_collection(self):
        """Test deleting a collection"""
        if not self.collection_id:
            self.log_test("Delete Collection", False, "No collection ID available")
            return False
            
        success, response = self.run_test(
            "Delete Collection",
            "DELETE",
            f"collections/{self.collection_id}",
            200
        )
        return success

    def test_unauthorized_access(self):
        """Test unauthorized access"""
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Unauthorized Access Test",
            "GET",
            "collections",
            401
        )
        
        # Restore token
        self.token = original_token
        return success

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Enhanced APIForge Backend Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Authentication tests
        print("\n🔐 Authentication Tests")
        if not self.test_user_registration():
            print("❌ Registration failed - stopping tests")
            return False
            
        self.test_user_login()
        self.test_get_user_profile()
        self.test_unauthorized_access()
        
        # Collection tests
        print("\n📁 Collection Management Tests")
        self.test_create_collection()
        self.test_get_collections()
        self.test_get_collection_by_id()
        self.test_update_collection()
        
        # Request tests
        print("\n🔧 Request Management Tests")
        self.test_create_request()
        self.test_get_requests()
        self.test_update_request()
        self.test_execute_request()
        self.test_enhanced_request_with_all_fields()
        
        # Multi-protocol tests
        print("\n🌐 Multi-Protocol Support Tests")
        self.test_multi_protocol_rest()
        self.test_multi_protocol_soap()
        self.test_multi_protocol_graphql()
        
        # Authentication type tests
        print("\n🔑 Enhanced Authentication Tests")
        self.test_auth_bearer_token()
        self.test_auth_basic()
        self.test_auth_api_key_header()
        self.test_auth_api_key_query()
        
        # Environment tests
        print("\n🌍 Environment Management Tests")
        self.test_create_environment()
        self.test_get_environments()
        self.test_update_environment()
        self.test_environment_variable_substitution()
        
        # History tests
        print("\n📜 Request History Tests")
        self.test_request_history()
        
        # Import functionality tests
        print("\n📥 Import Functionality Tests")
        self.test_import_openapi()
        self.test_import_postman()
        self.test_import_wsdl()
        
        # GraphQL specific tests
        print("\n🔍 GraphQL Features Tests")
        self.test_graphql_introspection()
        
        # Cleanup tests
        print("\n🗑️ Cleanup Tests")
        self.test_delete_request()
        self.test_delete_environment()
        self.test_delete_collection()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️ Some tests failed")
            return False

def main():
    tester = APIForgeBackendTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())