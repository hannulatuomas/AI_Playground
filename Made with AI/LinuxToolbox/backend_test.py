import requests
import sys
import json
from datetime import datetime

class LinuxAdminAPITester:
    def __init__(self, base_url="https://linuxcmddb.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}, Expected: {expected_status}"
            
            if not success:
                try:
                    error_detail = response.json()
                    details += f", Response: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                return False, {}

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_categories_endpoint(self):
        """Test categories endpoint"""
        return self.run_test("Get Categories", "GET", "categories", 200)

    def test_tags_endpoint(self):
        """Test tags endpoint"""
        return self.run_test("Get Tags", "GET", "tags", 200)

    def test_register(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        user_data = {
            "email": f"test_user_{timestamp}@example.com",
            "username": f"testuser_{timestamp}",
            "password": "TestPass123"
        }
        
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, user_data)
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Registered user: {response['user']['username']}")
            return True
        return False

    def test_login(self):
        """Test user login with existing credentials"""
        if not self.token:
            print("⚠️  Skipping login test - no registered user")
            return False
            
        # We'll use the same credentials from registration
        # For this test, we'll just verify the token works
        return self.run_test("Verify Token", "GET", "auth/me", 200)[0]

    def test_get_commands(self):
        """Test getting all commands"""
        return self.run_test("Get All Commands", "GET", "commands", 200)

    def test_search_commands(self):
        """Test command search"""
        # Use query parameters instead of JSON body
        url = f"{self.api_url}/commands/search?query=ls&limit=10&offset=0"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing Search Commands...")
        print(f"   URL: {url}")
        
        try:
            response = requests.post(url, headers=test_headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Expected: 200"
            
            if not success:
                try:
                    error_detail = response.json()
                    details += f", Response: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("Search Commands", success, details)
            return success
            
        except Exception as e:
            self.log_test("Search Commands", False, f"Exception: {str(e)}")
            return False

    def test_categories_with_subcategories(self):
        """Test the new categories-with-subcategories endpoint"""
        print(f"\n🔍 Testing Categories with Subcategories...")
        url = f"{self.api_url}/categories-with-subcategories"
        
        try:
            response = requests.get(url)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if 'categories' in data and isinstance(data['categories'], list):
                    # Check if categories have subcategories structure
                    has_proper_structure = True
                    for category in data['categories']:
                        if not isinstance(category, dict) or 'category' not in category or 'subcategories' not in category:
                            has_proper_structure = False
                            break
                    
                    if has_proper_structure:
                        details = f"Status: 200, Found {len(data['categories'])} categories with subcategories"
                        print(f"   Found categories: {[cat['category'] for cat in data['categories'][:3]]}...")
                    else:
                        success = False
                        details = "Categories don't have proper structure (missing category/subcategories fields)"
                else:
                    success = False
                    details = "Response missing 'categories' field or not a list"
            else:
                details = f"Status: {response.status_code}, Expected: 200"
                try:
                    error_detail = response.json()
                    details += f", Response: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("Categories with Subcategories", success, details)
            return success, data if success else {}
            
        except Exception as e:
            self.log_test("Categories with Subcategories", False, f"Exception: {str(e)}")
            return False, {}

    def test_advanced_search_tag_filtering(self):
        """Test advanced search functionality with tag filtering"""
        print(f"\n🔍 Testing Advanced Search Tag Filtering...")
        
        # First, let's get all available tags to see what we're working with
        try:
            tags_response = requests.get(f"{self.api_url}/tags")
            if tags_response.status_code == 200:
                tags_data = tags_response.json()
                available_tags = tags_data.get('tags', [])
                print(f"   Available tags: {available_tags[:10]}...")  # Show first 10 tags
                
                # Test 1: Search for commands with "kali" tag specifically
                self.test_tag_filtering("kali", available_tags)
                
                # Test 2: Search for commands with other common tags
                common_tags = ["networking", "security", "system", "file"]
                for tag in common_tags:
                    if tag in available_tags:
                        self.test_tag_filtering(tag, available_tags)
                        break
                
                # Test 3: Test combination of category + tag filtering
                self.test_category_and_tag_filtering()
                
                return True
            else:
                self.log_test("Get Tags for Advanced Search", False, f"Failed to get tags: {tags_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Advanced Search Tag Filtering", False, f"Exception: {str(e)}")
            return False

    def test_tag_filtering(self, tag, available_tags):
        """Test filtering by a specific tag"""
        print(f"\n🔍 Testing Tag Filtering for '{tag}'...")
        
        if tag not in available_tags:
            print(f"   ⚠️  Tag '{tag}' not found in available tags, skipping...")
            return False
        
        # Test using the search endpoint with tags parameter
        url = f"{self.api_url}/commands/search"
        test_headers = {'Content-Type': 'application/json'}
        
        # Test with POST method and JSON body
        search_data = {
            "query": None,
            "tags": [tag],
            "limit": 20,
            "offset": 0
        }
        
        try:
            response = requests.post(url, json=search_data, headers=test_headers)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if isinstance(data, list):
                    # Check if returned commands actually have the requested tag
                    commands_with_tag = 0
                    total_commands = len(data)
                    
                    for command in data:
                        if 'tags' in command and tag in command['tags']:
                            commands_with_tag += 1
                    
                    if total_commands > 0:
                        if commands_with_tag == total_commands:
                            details = f"Found {total_commands} commands, all have '{tag}' tag"
                        else:
                            success = False
                            details = f"Found {total_commands} commands, but only {commands_with_tag} have '{tag}' tag"
                    else:
                        details = f"No commands found with '{tag}' tag"
                        # This might be expected if no commands have this tag
                        
                    print(f"   {details}")
                else:
                    success = False
                    details = "Response is not a list of commands"
            else:
                details = f"Status: {response.status_code}, Expected: 200"
                try:
                    error_detail = response.json()
                    details += f", Response: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(f"Tag Filtering - {tag}", success, details)
            return success
            
        except Exception as e:
            self.log_test(f"Tag Filtering - {tag}", False, f"Exception: {str(e)}")
            return False

    def test_category_and_tag_filtering(self):
        """Test combination of category and tag filtering"""
        print(f"\n🔍 Testing Category + Tag Filtering...")
        
        url = f"{self.api_url}/commands/search"
        test_headers = {'Content-Type': 'application/json'}
        
        # Test with both category and tag filters
        search_data = {
            "query": None,
            "category": "Security",
            "tags": ["kali"],
            "limit": 20,
            "offset": 0
        }
        
        try:
            response = requests.post(url, json=search_data, headers=test_headers)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if isinstance(data, list):
                    # Check if returned commands match both category and tag criteria
                    matching_commands = 0
                    total_commands = len(data)
                    
                    for command in data:
                        category_match = 'category' in command and 'Security' in command['category']
                        tag_match = 'tags' in command and 'kali' in command['tags']
                        
                        if category_match and tag_match:
                            matching_commands += 1
                    
                    if total_commands > 0:
                        if matching_commands == total_commands:
                            details = f"Found {total_commands} commands matching Security category and kali tag"
                        else:
                            details = f"Found {total_commands} commands, but only {matching_commands} match both criteria"
                    else:
                        details = "No commands found matching Security category and kali tag"
                        
                    print(f"   {details}")
                else:
                    success = False
                    details = "Response is not a list of commands"
            else:
                details = f"Status: {response.status_code}, Expected: 200"
                try:
                    error_detail = response.json()
                    details += f", Response: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("Category + Tag Filtering", success, details)
            return success
            
        except Exception as e:
            self.log_test("Category + Tag Filtering", False, f"Exception: {str(e)}")
            return False

    def test_commands_with_tags(self):
        """Test that commands API returns commands with proper tags"""
        print(f"\n🔍 Testing Commands API with Tags...")
        
        url = f"{self.api_url}/commands?limit=10"
        
        try:
            response = requests.get(url)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check if commands have tags
                    commands_with_tags = 0
                    commands_with_kali_tag = 0
                    total_commands = len(data)
                    
                    for command in data:
                        if 'tags' in command and isinstance(command['tags'], list):
                            commands_with_tags += 1
                            if 'kali' in command['tags']:
                                commands_with_kali_tag += 1
                    
                    details = f"Found {total_commands} commands, {commands_with_tags} have tags, {commands_with_kali_tag} have 'kali' tag"
                    print(f"   {details}")
                    
                    # Success if we have commands with tags structure
                    success = commands_with_tags > 0
                    if not success:
                        details += " - No commands have tags!"
                        
                else:
                    success = False
                    details = "No commands found or response is not a list"
            else:
                details = f"Status: {response.status_code}, Expected: 200"
                try:
                    error_detail = response.json()
                    details += f", Response: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test("Commands with Tags", success, details)
            return success
            
        except Exception as e:
            self.log_test("Commands with Tags", False, f"Exception: {str(e)}")
            return False

    def test_create_command(self):
        """Test creating a new command"""
        if not self.token:
            print("⚠️  Skipping create command test - not authenticated")
            return False, None
            
        command_data = {
            "name": "test-cmd",
            "description": "A test command for API testing",
            "syntax": "test-cmd [options]",
            "examples": ["test-cmd --help", "test-cmd -v"],
            "category": "System Monitoring",
            "tags": ["test", "api"],
            "is_public": True
        }
        
        success, response = self.run_test("Create Command", "POST", "commands", 200, command_data)
        
        if success and 'id' in response:
            return True, response['id']
        return False, None

    def test_get_command_by_id(self, command_id):
        """Test getting a specific command"""
        if not command_id:
            print("⚠️  Skipping get command by ID test - no command ID")
            return False
            
        return self.run_test("Get Command by ID", "GET", f"commands/{command_id}", 200)

    def test_update_command(self, command_id):
        """Test updating a command"""
        if not command_id or not self.token:
            print("⚠️  Skipping update command test - missing requirements")
            return False
            
        update_data = {
            "description": "Updated test command description",
            "tags": ["test", "api", "updated"]
        }
        
        return self.run_test("Update Command", "PUT", f"commands/{command_id}", 200, update_data)

    def test_save_command(self, command_id):
        """Test saving a command"""
        if not command_id or not self.token:
            print("⚠️  Skipping save command test - missing requirements")
            return False
            
        save_data = {
            "command_id": command_id,
            "notes": "Test save"
        }
        
        return self.run_test("Save Command", "POST", "saved-commands", 200, save_data)

    def test_get_saved_commands(self):
        """Test getting saved commands"""
        if not self.token:
            print("⚠️  Skipping get saved commands test - not authenticated")
            return False
            
        return self.run_test("Get Saved Commands", "GET", "saved-commands", 200)

    def test_unsave_command(self, command_id):
        """Test unsaving a command"""
        if not command_id or not self.token:
            print("⚠️  Skipping unsave command test - missing requirements")
            return False
            
        return self.run_test("Unsave Command", "DELETE", f"saved-commands/{command_id}", 200)

    def test_delete_command(self, command_id):
        """Test deleting a command"""
        if not command_id or not self.token:
            print("⚠️  Skipping delete command test - missing requirements")
            return False
            
        return self.run_test("Delete Command", "DELETE", f"commands/{command_id}", 200)

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Linux Admin API Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 50)

        # Test basic endpoints
        self.test_root_endpoint()
        self.test_categories_endpoint()
        self.test_tags_endpoint()
        
        # Test NEW CATEGORY SYSTEM - categories with subcategories
        self.test_categories_with_subcategories()
        
        # Test authentication
        if self.test_register():
            self.test_login()
        
        # Test command operations
        self.test_get_commands()
        self.test_search_commands()
        
        # Test COMMANDS API with proper tags
        self.test_commands_with_tags()
        
        # Test ADVANCED SEARCH FUNCTIONALITY with tag filtering
        self.test_advanced_search_tag_filtering()
        
        # Test authenticated operations
        created_command_id = None
        if self.token:
            success, command_id = self.test_create_command()
            if success:
                created_command_id = command_id
                self.test_get_command_by_id(command_id)
                self.test_update_command(command_id)
                self.test_save_command(command_id)
                self.test_get_saved_commands()
                self.test_unsave_command(command_id)
                self.test_delete_command(command_id)

        # Print results
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed!")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
            return 1

def main():
    tester = LinuxAdminAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())