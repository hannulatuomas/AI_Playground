import requests
import json
import sys

class AdvancedSearchTester:
    def __init__(self, base_url="https://linuxcmddb.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
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

    def make_search_request(self, query=None, category=None, tags=None, limit=20, offset=0):
        """Make a search request to the API"""
        url = f"{self.api_url}/commands/search"
        headers = {'Content-Type': 'application/json'}
        
        data = {
            "query": query,
            "category": category,
            "tags": tags,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            return response.status_code, response.json() if response.status_code == 200 else response.text
        except Exception as e:
            return 500, str(e)

    def test_category_filtering_alone(self):
        """Test category filtering alone (e.g., 'Security' category)"""
        print(f"\n🔍 Testing Category Filtering Alone - 'Security'...")
        
        status, data = self.make_search_request(category="Security")
        
        if status == 200 and isinstance(data, list):
            security_commands = 0
            non_security_commands = 0
            
            for command in data:
                if 'category' in command:
                    if 'Security' in command['category']:
                        security_commands += 1
                    else:
                        non_security_commands += 1
                        print(f"   ⚠️  Found non-Security command: {command.get('name', 'Unknown')} in category '{command.get('category', 'Unknown')}'")
            
            total = len(data)
            if total > 0:
                if non_security_commands == 0:
                    success = True
                    details = f"Found {total} commands, all in Security category"
                else:
                    success = False
                    details = f"Found {total} commands, but {non_security_commands} are NOT in Security category"
            else:
                success = True  # No commands is acceptable
                details = "No Security commands found (acceptable)"
        else:
            success = False
            details = f"API error: Status {status}, Response: {str(data)[:200]}"
        
        self.log_test("Category Filtering - Security", success, details)
        return success, data if status == 200 else []

    def test_tag_filtering_alone(self):
        """Test tag filtering alone (e.g., 'kali' tag)"""
        print(f"\n🔍 Testing Tag Filtering Alone - 'kali'...")
        
        status, data = self.make_search_request(tags=["kali"])
        
        if status == 200 and isinstance(data, list):
            kali_commands = 0
            non_kali_commands = 0
            
            for command in data:
                if 'tags' in command and isinstance(command['tags'], list):
                    if 'kali' in command['tags']:
                        kali_commands += 1
                    else:
                        non_kali_commands += 1
                        print(f"   ⚠️  Found non-kali command: {command.get('name', 'Unknown')} with tags {command.get('tags', [])}")
            
            total = len(data)
            if total > 0:
                if non_kali_commands == 0:
                    success = True
                    details = f"Found {total} commands, all have 'kali' tag"
                else:
                    success = False
                    details = f"Found {total} commands, but {non_kali_commands} do NOT have 'kali' tag"
            else:
                success = True  # No commands is acceptable
                details = "No kali commands found (acceptable)"
        else:
            success = False
            details = f"API error: Status {status}, Response: {str(data)[:200]}"
        
        self.log_test("Tag Filtering - kali", success, details)
        return success, data if status == 200 else []

    def test_combined_category_and_tag_filtering(self):
        """Test combined category + tag filtering (e.g., 'Security' category with 'kali' tag)"""
        print(f"\n🔍 Testing Combined Category + Tag Filtering - 'Security' + 'kali'...")
        
        status, data = self.make_search_request(category="Security", tags=["kali"])
        
        if status == 200 and isinstance(data, list):
            matching_commands = 0
            category_mismatch = 0
            tag_mismatch = 0
            
            for command in data:
                category_match = 'category' in command and 'Security' in command['category']
                tag_match = 'tags' in command and isinstance(command['tags'], list) and 'kali' in command['tags']
                
                if category_match and tag_match:
                    matching_commands += 1
                else:
                    if not category_match:
                        category_mismatch += 1
                        print(f"   ⚠️  Category mismatch: {command.get('name', 'Unknown')} in category '{command.get('category', 'Unknown')}'")
                    if not tag_match:
                        tag_mismatch += 1
                        print(f"   ⚠️  Tag mismatch: {command.get('name', 'Unknown')} with tags {command.get('tags', [])}")
            
            total = len(data)
            if total > 0:
                if category_mismatch == 0 and tag_mismatch == 0:
                    success = True
                    details = f"Found {total} commands, all match Security category AND kali tag"
                else:
                    success = False
                    details = f"Found {total} commands, but {category_mismatch} category mismatches and {tag_mismatch} tag mismatches"
            else:
                success = True  # No commands is acceptable
                details = "No commands found matching Security + kali (acceptable)"
        else:
            success = False
            details = f"API error: Status {status}, Response: {str(data)[:200]}"
        
        self.log_test("Combined Category + Tag Filtering", success, details)
        return success, data if status == 200 else []

    def test_text_search_with_category(self):
        """Test text search + category filter"""
        print(f"\n🔍 Testing Text Search + Category Filter - 'nmap' + 'Security'...")
        
        status, data = self.make_search_request(query="nmap", category="Security")
        
        if status == 200 and isinstance(data, list):
            matching_commands = 0
            text_mismatch = 0
            category_mismatch = 0
            
            for command in data:
                # Check if command contains "nmap" in searchable fields
                text_match = (
                    ('name' in command and 'nmap' in command['name'].lower()) or
                    ('description' in command and 'nmap' in command['description'].lower()) or
                    ('syntax' in command and 'nmap' in command['syntax'].lower()) or
                    ('examples' in command and any('nmap' in ex.lower() for ex in command['examples'])) or
                    ('tags' in command and any('nmap' in tag.lower() for tag in command['tags']))
                )
                
                category_match = 'category' in command and 'Security' in command['category']
                
                if text_match and category_match:
                    matching_commands += 1
                else:
                    if not text_match:
                        text_mismatch += 1
                    if not category_match:
                        category_mismatch += 1
            
            total = len(data)
            if total > 0:
                if text_mismatch == 0 and category_mismatch == 0:
                    success = True
                    details = f"Found {total} commands, all match 'nmap' text AND Security category"
                else:
                    success = False
                    details = f"Found {total} commands, but {text_mismatch} text mismatches and {category_mismatch} category mismatches"
            else:
                success = True  # No commands is acceptable
                details = "No commands found matching nmap + Security (acceptable)"
        else:
            success = False
            details = f"API error: Status {status}, Response: {str(data)[:200]}"
        
        self.log_test("Text Search + Category Filter", success, details)
        return success

    def test_text_search_with_tag(self):
        """Test text search + tag filter"""
        print(f"\n🔍 Testing Text Search + Tag Filter - 'scan' + 'kali'...")
        
        status, data = self.make_search_request(query="scan", tags=["kali"])
        
        if status == 200 and isinstance(data, list):
            matching_commands = 0
            text_mismatch = 0
            tag_mismatch = 0
            
            for command in data:
                # Check if command contains "scan" in searchable fields
                text_match = (
                    ('name' in command and 'scan' in command['name'].lower()) or
                    ('description' in command and 'scan' in command['description'].lower()) or
                    ('syntax' in command and 'scan' in command['syntax'].lower()) or
                    ('examples' in command and any('scan' in ex.lower() for ex in command['examples'])) or
                    ('tags' in command and any('scan' in tag.lower() for tag in command['tags']))
                )
                
                tag_match = 'tags' in command and isinstance(command['tags'], list) and 'kali' in command['tags']
                
                if text_match and tag_match:
                    matching_commands += 1
                else:
                    if not text_match:
                        text_mismatch += 1
                    if not tag_match:
                        tag_mismatch += 1
            
            total = len(data)
            if total > 0:
                if text_mismatch == 0 and tag_mismatch == 0:
                    success = True
                    details = f"Found {total} commands, all match 'scan' text AND kali tag"
                else:
                    success = False
                    details = f"Found {total} commands, but {text_mismatch} text mismatches and {tag_mismatch} tag mismatches"
            else:
                success = True  # No commands is acceptable
                details = "No commands found matching scan + kali (acceptable)"
        else:
            success = False
            details = f"API error: Status {status}, Response: {str(data)[:200]}"
        
        self.log_test("Text Search + Tag Filter", success, details)
        return success

    def test_all_three_parameters(self):
        """Test text search + category + tag filter"""
        print(f"\n🔍 Testing All Three Parameters - 'network' + 'Security' + 'kali'...")
        
        status, data = self.make_search_request(query="network", category="Security", tags=["kali"])
        
        if status == 200 and isinstance(data, list):
            matching_commands = 0
            text_mismatch = 0
            category_mismatch = 0
            tag_mismatch = 0
            
            for command in data:
                # Check if command contains "network" in searchable fields
                text_match = (
                    ('name' in command and 'network' in command['name'].lower()) or
                    ('description' in command and 'network' in command['description'].lower()) or
                    ('syntax' in command and 'network' in command['syntax'].lower()) or
                    ('examples' in command and any('network' in ex.lower() for ex in command['examples'])) or
                    ('tags' in command and any('network' in tag.lower() for tag in command['tags']))
                )
                
                category_match = 'category' in command and 'Security' in command['category']
                tag_match = 'tags' in command and isinstance(command['tags'], list) and 'kali' in command['tags']
                
                if text_match and category_match and tag_match:
                    matching_commands += 1
                else:
                    if not text_match:
                        text_mismatch += 1
                    if not category_match:
                        category_mismatch += 1
                    if not tag_match:
                        tag_mismatch += 1
            
            total = len(data)
            if total > 0:
                if text_mismatch == 0 and category_mismatch == 0 and tag_mismatch == 0:
                    success = True
                    details = f"Found {total} commands, all match 'network' text AND Security category AND kali tag"
                else:
                    success = False
                    details = f"Found {total} commands, but {text_mismatch} text, {category_mismatch} category, {tag_mismatch} tag mismatches"
            else:
                success = True  # No commands is acceptable
                details = "No commands found matching network + Security + kali (acceptable)"
        else:
            success = False
            details = f"API error: Status {status}, Response: {str(data)[:200]}"
        
        self.log_test("All Three Parameters", success, details)
        return success

    def test_edge_cases(self):
        """Test various edge cases"""
        print(f"\n🔍 Testing Edge Cases...")
        
        # Test 1: Empty query with filters
        status, data = self.make_search_request(query="", category="Security")
        success1 = status == 200
        self.log_test("Empty Query with Category", success1, f"Status: {status}")
        
        # Test 2: Non-existent category
        status, data = self.make_search_request(category="NonExistentCategory")
        success2 = status == 200 and len(data) == 0
        self.log_test("Non-existent Category", success2, f"Status: {status}, Results: {len(data) if isinstance(data, list) else 'Error'}")
        
        # Test 3: Non-existent tag
        status, data = self.make_search_request(tags=["nonexistenttag"])
        success3 = status == 200 and len(data) == 0
        self.log_test("Non-existent Tag", success3, f"Status: {status}, Results: {len(data) if isinstance(data, list) else 'Error'}")
        
        # Test 4: Multiple tags
        status, data = self.make_search_request(tags=["kali", "networking"])
        success4 = status == 200
        self.log_test("Multiple Tags", success4, f"Status: {status}, Results: {len(data) if isinstance(data, list) else 'Error'}")
        
        return success1 and success2 and success3 and success4

    def run_all_tests(self):
        """Run all advanced search tests"""
        print("🚀 Starting Advanced Search Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)

        # Test the specific scenarios mentioned in the review request
        self.test_category_filtering_alone()
        self.test_tag_filtering_alone()
        self.test_combined_category_and_tag_filtering()
        self.test_text_search_with_category()
        self.test_text_search_with_tag()
        self.test_all_three_parameters()
        self.test_edge_cases()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Advanced Search Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All advanced search tests passed!")
            return 0
        else:
            print("❌ Some advanced search tests failed!")
            print("\nFailed tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['details']}")
            return 1

def main():
    tester = AdvancedSearchTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())