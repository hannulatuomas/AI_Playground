import requests
import sys
import json
from datetime import datetime

class AIDevToolTester:
    def __init__(self, base_url="https://dev-toolbox-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.provider_id = None
        self.conversation_id = None
        self.local_model_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=default_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=default_headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=default_headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=default_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.text}")
                except:
                    pass
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_create_provider_emergent_key(self):
        """Test creating provider with test API key"""
        provider_data = {
            "name": "OpenAI",
            "model": "gpt-4",
            "api_key": "test-key-for-devgenius-ai",
            "is_active": True
        }
        success, response = self.run_test(
            "Create Provider (Test Key)",
            "POST",
            "providers",
            200,
            data=provider_data
        )
        if success and 'id' in response:
            self.provider_id = response['id']
            print(f"   Provider ID: {self.provider_id}")
        return success

    def test_create_provider_custom_key(self):
        """Test creating provider with custom API key"""
        provider_data = {
            "name": "Claude",
            "model": "claude-4-sonnet-20250514",
            "api_key": "sk-custom-test-key",
            "is_active": True
        }
        return self.run_test(
            "Create Provider (Custom Key)",
            "POST",
            "providers",
            200,
            data=provider_data
        )

    def test_get_providers(self):
        """Test getting all providers"""
        return self.run_test("Get Providers", "GET", "providers", 200)

    def test_update_provider(self):
        """Test updating a provider"""
        if not self.provider_id:
            print("❌ Skipping update test - no provider ID")
            return False
        
        update_data = {
            "name": "OpenAI",
            "model": "gpt-4-turbo",
            "api_key": "test-key-for-devgenius-ai-updated",
            "is_active": True
        }
        return self.run_test(
            "Update Provider",
            "PUT",
            f"providers/{self.provider_id}",
            200,
            data=update_data
        )

    def test_create_conversation(self):
        """Test creating a conversation"""
        if not self.provider_id:
            print("❌ Skipping conversation test - no provider ID")
            return False
            
        conv_data = {
            "title": "Test Programming Chat",
            "agent_type": "programming",
            "provider_id": self.provider_id
        }
        success, response = self.run_test(
            "Create Conversation",
            "POST",
            "conversations",
            200,
            data=conv_data
        )
        if success and 'id' in response:
            self.conversation_id = response['id']
            print(f"   Conversation ID: {self.conversation_id}")
        return success

    def test_get_conversations(self):
        """Test getting conversations"""
        return self.run_test("Get Conversations", "GET", "conversations", 200)

    def test_get_conversations_by_agent(self):
        """Test getting conversations by agent type"""
        return self.run_test(
            "Get Conversations by Agent",
            "GET",
            "conversations?agent_type=programming",
            200
        )

    def test_chat_message(self):
        """Test sending a chat message"""
        if not self.provider_id:
            print("❌ Skipping chat test - no provider ID")
            return False
            
        chat_data = {
            "conversation_id": self.conversation_id,
            "message": "Hello, can you help me with Python programming?",
            "provider_id": self.provider_id,
            "agent_type": "programming",
            "title": "Test Chat"
        }
        
        # Note: Chat endpoint returns streaming response, so we expect different handling
        success, _ = self.run_test(
            "Send Chat Message",
            "POST",
            "chat",
            200,
            data=chat_data
        )
        return success

    def test_enhanced_system_prompts(self):
        """Test that different agent types use enhanced system prompts"""
        if not self.provider_id:
            print("❌ Skipping enhanced prompts test - no provider ID")
            return False
        
        agent_types = ["programming", "website", "youtube", "learning", "ideas", "api-testing", "prompt-engineering"]
        success_count = 0
        
        for agent_type in agent_types:
            # Create conversation for each agent type
            conv_data = {
                "title": f"Test {agent_type.title()} Agent",
                "agent_type": agent_type,
                "provider_id": self.provider_id
            }
            
            conv_success, conv_response = self.run_test(
                f"Create {agent_type} Conversation",
                "POST",
                "conversations",
                200,
                data=conv_data
            )
            
            if conv_success and 'id' in conv_response:
                conv_id = conv_response['id']
                
                # Send a test message
                chat_data = {
                    "conversation_id": conv_id,
                    "message": f"Hello, I need help with {agent_type} related tasks.",
                    "provider_id": self.provider_id,
                    "agent_type": agent_type,
                    "title": f"Test {agent_type} Chat"
                }
                
                chat_success, _ = self.run_test(
                    f"Test {agent_type} Agent Chat",
                    "POST",
                    "chat",
                    200,
                    data=chat_data
                )
                
                if chat_success:
                    success_count += 1
                    print(f"✅ {agent_type} agent working")
                else:
                    print(f"❌ {agent_type} agent failed")
        
        return success_count == len(agent_types)

    def test_basic_summarization_trigger(self):
        """Test basic summarization trigger at 10+ messages"""
        if not self.provider_id:
            print("❌ Skipping basic summarization test - no provider ID")
            return False
        
        # Create a new conversation for this test
        conv_data = {
            "title": "Basic Summarization Test",
            "agent_type": "programming",
            "provider_id": self.provider_id
        }
        
        success, response = self.run_test(
            "Create Basic Summarization Conversation",
            "POST",
            "conversations",
            200,
            data=conv_data
        )
        
        if not success or 'id' not in response:
            return False
        
        basic_conv_id = response['id']
        
        # Send 12 messages to trigger auto-summarization (should trigger at 10+)
        print("   Sending 12 messages to trigger auto-summarization at 10+ messages...")
        for i in range(12):
            chat_data = {
                "conversation_id": basic_conv_id,
                "message": f"Message {i+1}: Testing the enhanced summarization system with progressive updates and semantic scoring.",
                "provider_id": self.provider_id,
                "agent_type": "programming",
                "title": "Basic Summarization Test"
            }
            
            chat_success, _ = self.run_test(
                f"Send Message {i+1}/12",
                "POST",
                "chat",
                200,
                data=chat_data
            )
            
            if not chat_success:
                print(f"❌ Failed to send message {i+1}")
                return False
        
        # Check if conversation has summary and required fields
        conv_success, conv_data = self.run_test(
            "Check Basic Summarization Fields",
            "GET",
            f"conversations",
            200
        )
        
        if conv_success:
            # Find our conversation and check required fields
            for conv in conv_data:
                if conv.get('id') == basic_conv_id:
                    has_summary = bool(conv.get('summary'))
                    has_summary_at = bool(conv.get('summary_at'))
                    has_messages_summarized = conv.get('messages_summarized', 0) > 0
                    has_summary_metadata = bool(conv.get('summary_metadata'))
                    
                    print(f"   Summary: {'✅' if has_summary else '❌'}")
                    print(f"   Summary_at: {'✅' if has_summary_at else '❌'}")
                    print(f"   Messages_summarized: {'✅' if has_messages_summarized else '❌'} ({conv.get('messages_summarized', 0)})")
                    print(f"   Summary_metadata: {'✅' if has_summary_metadata else '❌'}")
                    
                    if has_summary:
                        print(f"   Summary preview: {conv['summary'][:150]}...")
                    
                    if has_summary_metadata:
                        metadata = conv['summary_metadata']
                        print(f"   Metadata keys: {list(metadata.keys())}")
                    
                    return has_summary and has_summary_at and has_messages_summarized and has_summary_metadata
        
        print("❌ Basic summarization not triggered or missing required fields")
        return False

    def test_progressive_summarization(self):
        """Test progressive summarization with incremental updates"""
        if not self.provider_id:
            print("❌ Skipping progressive summarization test - no provider ID")
            return False
        
        # Create a new conversation for progressive testing
        conv_data = {
            "title": "Progressive Summarization Test",
            "agent_type": "programming", 
            "provider_id": self.provider_id
        }
        
        success, response = self.run_test(
            "Create Progressive Summarization Conversation",
            "POST",
            "conversations",
            200,
            data=conv_data
        )
        
        if not success or 'id' not in response:
            return False
        
        prog_conv_id = response['id']
        
        # First batch: Send 12 messages to create initial summary
        print("   Sending first batch of 12 messages...")
        for i in range(12):
            chat_data = {
                "conversation_id": prog_conv_id,
                "message": f"Initial batch message {i+1}: Discussing FastAPI implementation and database design patterns.",
                "provider_id": self.provider_id,
                "agent_type": "programming",
                "title": "Progressive Test"
            }
            
            self.run_test(
                f"Progressive Batch 1 Message {i+1}",
                "POST",
                "chat",
                200,
                data=chat_data
            )
        
        # Get initial summary
        conv_success, conv_data = self.run_test(
            "Get Initial Summary",
            "GET",
            f"conversations",
            200
        )
        
        initial_summary = None
        initial_messages_summarized = 0
        
        if conv_success:
            for conv in conv_data:
                if conv.get('id') == prog_conv_id:
                    initial_summary = conv.get('summary')
                    initial_messages_summarized = conv.get('messages_summarized', 0)
                    break
        
        if not initial_summary:
            print("❌ Initial summary not created")
            return False
        
        print(f"   Initial summary created: {initial_summary[:100]}...")
        print(f"   Initial messages summarized: {initial_messages_summarized}")
        
        # Second batch: Send 12 more messages to trigger progressive update
        print("   Sending second batch of 12 messages for progressive update...")
        for i in range(12):
            chat_data = {
                "conversation_id": prog_conv_id,
                "message": f"Progressive batch message {i+1}: Adding authentication system with JWT tokens and user management features.",
                "provider_id": self.provider_id,
                "agent_type": "programming",
                "title": "Progressive Test"
            }
            
            self.run_test(
                f"Progressive Batch 2 Message {i+1}",
                "POST",
                "chat",
                200,
                data=chat_data
            )
        
        # Check progressive update
        conv_success, conv_data = self.run_test(
            "Check Progressive Update",
            "GET",
            f"conversations",
            200
        )
        
        if conv_success:
            for conv in conv_data:
                if conv.get('id') == prog_conv_id:
                    updated_summary = conv.get('summary')
                    updated_messages_summarized = conv.get('messages_summarized', 0)
                    
                    if updated_summary and updated_summary != initial_summary:
                        print(f"✅ Progressive update successful")
                        print(f"   Updated summary: {updated_summary[:150]}...")
                        print(f"   Messages summarized: {initial_messages_summarized} → {updated_messages_summarized}")
                        
                        # Check if metadata shows incremental changes
                        metadata = conv.get('summary_metadata', {})
                        if metadata:
                            print(f"   Metadata shows: {metadata.get('total_messages', 0)} total messages")
                        
                        return True
                    else:
                        print("❌ Progressive update failed - summary unchanged")
                        return False
        
        return False

    def test_topic_detection_and_importance(self):
        """Test topic detection and importance scoring"""
        if not self.provider_id:
            print("❌ Skipping topic detection test - no provider ID")
            return False
        
        # Create conversation for topic testing
        conv_data = {
            "title": "Topic Detection Test",
            "agent_type": "programming",
            "provider_id": self.provider_id
        }
        
        success, response = self.run_test(
            "Create Topic Detection Conversation",
            "POST",
            "conversations",
            200,
            data=conv_data
        )
        
        if not success or 'id' not in response:
            return False
        
        topic_conv_id = response['id']
        
        # Send messages with different types of content for topic detection
        test_messages = [
            "I'm getting an error in my FastAPI application: 'ModuleNotFoundError: No module named pydantic'",
            "The bug seems to be related to the import statement in my models.py file",
            "I need to fix this issue by installing the correct pydantic version",
            "```python\nfrom pydantic import BaseModel\nclass User(BaseModel):\n    name: str\n    email: str\n```",
            "Here's the code implementation for the user authentication system",
            "The function should handle JWT token generation and validation",
            "We need to implement a new feature for user profile management",
            "The requirement is to add photo upload functionality to user profiles",
            "Users should be able to upload and crop their profile pictures",
            "I've decided to use AWS S3 for storing the uploaded images",
            "We're choosing to implement image resizing on the server side",
            "The final decision is to use Pillow library for image processing"
        ]
        
        print(f"   Sending {len(test_messages)} messages with different content types...")
        for i, message in enumerate(test_messages):
            chat_data = {
                "conversation_id": topic_conv_id,
                "message": message,
                "provider_id": self.provider_id,
                "agent_type": "programming",
                "title": "Topic Detection Test"
            }
            
            self.run_test(
                f"Topic Message {i+1}",
                "POST",
                "chat",
                200,
                data=chat_data
            )
        
        # Check if topics were detected in metadata
        conv_success, conv_data = self.run_test(
            "Check Topic Detection Results",
            "GET",
            f"conversations",
            200
        )
        
        if conv_success:
            for conv in conv_data:
                if conv.get('id') == topic_conv_id:
                    metadata = conv.get('summary_metadata', {})
                    topics_detected = metadata.get('topics_detected', {})
                    
                    print(f"   Topics detected: {topics_detected}")
                    
                    # Check for expected topic categories
                    expected_topics = ['errors_and_fixes', 'code_implementation', 'requirements', 'decisions']
                    detected_topics = [topic for topic in expected_topics if topics_detected.get(topic, 0) > 0]
                    
                    print(f"   Expected topics found: {detected_topics}")
                    
                    # Check importance metrics
                    avg_importance = metadata.get('avg_importance', 0)
                    high_priority_count = metadata.get('high_priority_count', 0)
                    
                    print(f"   Average importance: {avg_importance:.2f}")
                    print(f"   High priority messages: {high_priority_count}")
                    
                    # Success if we detected at least 3 different topic types
                    success = len(detected_topics) >= 3 and avg_importance > 0
                    
                    if success:
                        print("✅ Topic detection and importance scoring working")
                    else:
                        print("❌ Topic detection or importance scoring failed")
                    
                    return success
        
        return False

    def test_agent_memory_integration(self):
        """Test agent memory integration for error resolution patterns"""
        if not self.provider_id:
            print("❌ Skipping agent memory test - no provider ID")
            return False
        
        # Create conversation for agent memory testing
        conv_data = {
            "title": "Agent Memory Test",
            "agent_type": "programming",
            "provider_id": self.provider_id
        }
        
        success, response = self.run_test(
            "Create Agent Memory Conversation",
            "POST",
            "conversations",
            200,
            data=conv_data
        )
        
        if not success or 'id' not in response:
            return False
        
        memory_conv_id = response['id']
        
        # Send error-fix pattern messages
        error_fix_messages = [
            "I'm encountering a database connection error: 'pymongo.errors.ServerSelectionTimeoutError'",
            "The error occurs when trying to connect to MongoDB in my FastAPI application",
            "I think the issue might be with the connection string or network configuration",
            "Let me check the MongoDB service status and connection parameters",
            "I found the problem - the MongoDB service wasn't running on the server",
            "After starting the MongoDB service with 'sudo systemctl start mongod', the connection works",
            "The fix was to ensure MongoDB service is running and accessible on port 27017",
            "Now the application connects successfully to the database",
            "Another error appeared: 'ValidationError: field required' in Pydantic models",
            "This validation error happens when creating new user records",
            "The issue is that some required fields are missing in the request payload",
            "I solved it by adding proper validation and default values to the Pydantic model",
            "The working solution includes comprehensive field validation and error handling"
        ]
        
        print(f"   Sending {len(error_fix_messages)} messages with error-resolution patterns...")
        for i, message in enumerate(error_fix_messages):
            chat_data = {
                "conversation_id": memory_conv_id,
                "message": message,
                "provider_id": self.provider_id,
                "agent_type": "programming",
                "title": "Agent Memory Test"
            }
            
            self.run_test(
                f"Memory Pattern Message {i+1}",
                "POST",
                "chat",
                200,
                data=chat_data
            )
        
        # Check if learnings were detected and stored
        conv_success, conv_data = self.run_test(
            "Check Agent Memory Integration",
            "GET",
            f"conversations",
            200
        )
        
        if conv_success:
            for conv in conv_data:
                if conv.get('id') == memory_conv_id:
                    summary = conv.get('summary', '')
                    
                    # Check if summary contains learnings section
                    has_learnings = '💡 LEARNINGS:' in summary or 'LEARNINGS' in summary
                    
                    print(f"   Summary contains learnings: {'✅' if has_learnings else '❌'}")
                    
                    if has_learnings:
                        print(f"   Summary with learnings: {summary[:200]}...")
                        return True
                    else:
                        print("❌ Agent memory integration not working - no learnings detected")
                        return False
        
        return False

    def test_context_window_optimization(self):
        """Test context window optimization with last 6 messages"""
        if not self.provider_id:
            print("❌ Skipping context optimization test - no provider ID")
            return False
        
        # Create conversation for context optimization testing
        conv_data = {
            "title": "Context Optimization Test",
            "agent_type": "programming",
            "provider_id": self.provider_id
        }
        
        success, response = self.run_test(
            "Create Context Optimization Conversation",
            "POST",
            "conversations",
            200,
            data=conv_data
        )
        
        if not success or 'id' not in response:
            return False
        
        context_conv_id = response['id']
        
        # Send 20 messages to create a long conversation
        print("   Sending 20 messages to test context window optimization...")
        for i in range(20):
            chat_data = {
                "conversation_id": context_conv_id,
                "message": f"Context message {i+1}: Building a comprehensive web application with advanced features and optimizations.",
                "provider_id": self.provider_id,
                "agent_type": "programming",
                "title": "Context Optimization Test"
            }
            
            self.run_test(
                f"Context Optimization Message {i+1}",
                "POST",
                "chat",
                200,
                data=chat_data
            )
        
        # Check conversation state after optimization
        conv_success, conv_data = self.run_test(
            "Check Context Optimization Results",
            "GET",
            f"conversations",
            200
        )
        
        if conv_success:
            for conv in conv_data:
                if conv.get('id') == context_conv_id:
                    has_summary = bool(conv.get('summary'))
                    messages_summarized = conv.get('messages_summarized', 0)
                    
                    # For 20 messages, should have summary and summarized messages
                    # Last 6 messages should be kept for context
                    expected_summarized = 20 - 6  # Should summarize all but last 6
                    
                    print(f"   Has summary: {'✅' if has_summary else '❌'}")
                    print(f"   Messages summarized: {messages_summarized} (expected ~{expected_summarized})")
                    
                    # Check if context window optimization is working
                    optimization_working = has_summary and messages_summarized >= 10
                    
                    if optimization_working:
                        print("✅ Context window optimization working - using summary + recent messages")
                        return True
                    else:
                        print("❌ Context window optimization not working properly")
                        return False
        
        return False

    def test_enhanced_manual_summarization(self):
        """Test enhanced manual conversation summarization endpoint with metadata"""
        if not self.conversation_id:
            print("❌ Skipping enhanced manual summarization test - no conversation ID")
            return False
        
        # First add a few more messages to the conversation
        for i in range(5):
            chat_data = {
                "conversation_id": self.conversation_id,
                "message": f"Enhanced message {i+1} for manual summarization test with metadata tracking.",
                "provider_id": self.provider_id,
                "agent_type": "programming",
                "title": "Test Chat"
            }
            
            self.run_test(
                f"Add Enhanced Message {i+1}",
                "POST",
                "chat",
                200,
                data=chat_data
            )
        
        # Test enhanced manual summarization
        success, response = self.run_test(
            "Enhanced Manual Conversation Summarization",
            "POST",
            f"conversations/{self.conversation_id}/summarize",
            200
        )
        
        if success:
            # Check required response fields
            has_message = 'message' in response
            has_summary = 'summary' in response and response['summary']
            has_metadata = 'metadata' in response and response['metadata']
            
            print(f"   Response message: {'✅' if has_message else '❌'}")
            print(f"   Summary: {'✅' if has_summary else '❌'}")
            print(f"   Metadata: {'✅' if has_metadata else '❌'}")
            
            if has_summary:
                print(f"   Summary preview: {response['summary'][:150]}...")
            
            if has_metadata:
                metadata = response['metadata']
                expected_fields = ['total_messages', 'topics_detected', 'avg_importance']
                
                print(f"   Metadata fields: {list(metadata.keys())}")
                
                # Check for expected metadata fields
                metadata_complete = all(field in metadata for field in expected_fields)
                print(f"   Metadata complete: {'✅' if metadata_complete else '❌'}")
                
                if metadata_complete:
                    print(f"   Total messages: {metadata.get('total_messages', 0)}")
                    print(f"   Topics detected: {metadata.get('topics_detected', {})}")
                    print(f"   Avg importance: {metadata.get('avg_importance', 0):.2f}")
            
            success_result = has_message and has_summary and has_metadata
            
            if success_result:
                print("✅ Enhanced manual summarization successful with metadata")
            else:
                print("❌ Enhanced manual summarization missing required fields")
            
            return success_result
        else:
            print("❌ Enhanced manual summarization failed")
            return False

    def test_context_management(self):
        """Test enhanced context management across messages"""
        if not self.provider_id:
            print("❌ Skipping context management test - no provider ID")
            return False
        
        # Create a new conversation for context testing
        conv_data = {
            "title": "Context Management Test",
            "agent_type": "programming",
            "provider_id": self.provider_id
        }
        
        success, response = self.run_test(
            "Create Context Test Conversation",
            "POST",
            "conversations",
            200,
            data=conv_data
        )
        
        if not success or 'id' not in response:
            return False
        
        context_conv_id = response['id']
        
        # Send messages that build context
        messages = [
            "I'm working on a Python web application using FastAPI.",
            "I need to add user authentication to my app.",
            "Can you help me implement JWT token authentication?",
            "Also, I want to add password hashing with bcrypt."
        ]
        
        for i, message in enumerate(messages):
            chat_data = {
                "conversation_id": context_conv_id,
                "message": message,
                "provider_id": self.provider_id,
                "agent_type": "programming",
                "title": "Context Test"
            }
            
            success, _ = self.run_test(
                f"Context Message {i+1}",
                "POST",
                "chat",
                200,
                data=chat_data
            )
            
            if not success:
                return False
        
        # Get messages to verify context is maintained
        success, messages_response = self.run_test(
            "Get Context Messages",
            "GET",
            f"messages/{context_conv_id}",
            200
        )
        
        if success and len(messages_response) >= 4:  # At least 4 user messages
            print(f"✅ Context management working - {len(messages_response)} messages preserved")
            return True
        else:
            print(f"❌ Context management failed - only {len(messages_response) if success else 0} messages found")
            return False

    def test_get_messages(self):
        """Test getting messages from a conversation"""
        if not self.conversation_id:
            print("❌ Skipping messages test - no conversation ID")
            return False
            
        return self.run_test(
            "Get Messages",
            "GET",
            f"messages/{self.conversation_id}",
            200
        )

    def test_create_local_model(self):
        """Test creating a local model"""
        model_data = {
            "name": "Llama 3.3 70B",
            "endpoint": "http://localhost:8080",
            "model_path": "/models/llama-3.3-70b.gguf",
            "context_size": 4096
        }
        success, response = self.run_test(
            "Create Local Model",
            "POST",
            "local-models",
            200,
            data=model_data
        )
        if success and 'id' in response:
            self.local_model_id = response['id']
            print(f"   Model ID: {self.local_model_id}")
        return success

    def test_get_local_models(self):
        """Test getting local models"""
        return self.run_test("Get Local Models", "GET", "local-models", 200)

    def test_update_model_status(self):
        """Test updating local model status"""
        if not self.local_model_id:
            print("❌ Skipping model status test - no model ID")
            return False
            
        return self.run_test(
            "Update Model Status",
            "PUT",
            f"local-models/{self.local_model_id}/status",
            200,
            data={"status": "running"}
        )

    def test_delete_conversation(self):
        """Test deleting a conversation"""
        if not self.conversation_id:
            print("❌ Skipping delete conversation test - no conversation ID")
            return False
            
        return self.run_test(
            "Delete Conversation",
            "DELETE",
            f"conversations/{self.conversation_id}",
            200
        )

    def test_delete_local_model(self):
        """Test deleting a local model"""
        if not self.local_model_id:
            print("❌ Skipping delete model test - no model ID")
            return False
            
        return self.run_test(
            "Delete Local Model",
            "DELETE",
            f"local-models/{self.local_model_id}",
            200
        )

    def test_delete_provider(self):
        """Test deleting a provider"""
        if not self.provider_id:
            print("❌ Skipping delete provider test - no provider ID")
            return False
            
        return self.run_test(
            "Delete Provider",
            "DELETE",
            f"providers/{self.provider_id}",
            200
        )

def main():
    print("🚀 Starting AI Development Tool API Tests")
    print("=" * 60)
    
    tester = AIDevToolTester()
    
    # Test sequence - Enhanced for DevGenius AI improvements
    tests = [
        # Basic API tests
        tester.test_root_endpoint,
        tester.test_create_provider_emergent_key,
        tester.test_create_provider_custom_key,
        tester.test_get_providers,
        tester.test_update_provider,
        tester.test_create_conversation,
        tester.test_get_conversations,
        tester.test_get_conversations_by_agent,
        tester.test_chat_message,
        tester.test_get_messages,
        
        # Enhanced agent improvements tests
        tester.test_enhanced_system_prompts,
        tester.test_context_management,
        
        # Enhanced conversation summarization system tests
        tester.test_basic_summarization_trigger,
        tester.test_progressive_summarization,
        tester.test_enhanced_manual_summarization,
        tester.test_topic_detection_and_importance,
        tester.test_agent_memory_integration,
        tester.test_context_window_optimization,
        
        # Local models and cleanup
        tester.test_create_local_model,
        tester.test_get_local_models,
        tester.test_update_model_status,
        tester.test_delete_conversation,
        tester.test_delete_local_model,
        tester.test_delete_provider,
    ]
    
    # Run all tests
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} passed")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Backend API tests mostly successful!")
        return 0
    else:
        print("⚠️  Backend API has significant issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())