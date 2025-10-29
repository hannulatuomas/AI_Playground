
"""
API Agent - Handles various API interactions.

This agent manages API operations including REST, SOAP, and GraphQL APIs.
It can help with API integration, testing, and response handling.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin, urlparse

from .base import Agent


class APIAgent(Agent):
    """
    Agent for working with different API types.
    
    Capabilities:
    - REST API operations (GET, POST, PUT, DELETE, PATCH)
    - SOAP API operations
    - GraphQL API operations
    - API testing and validation
    - Response parsing and formatting
    - Error handling for network operations
    - Authentication support (API keys, Bearer tokens, Basic auth)
    """
    
    def __init__(
        self,
        name: str = "api_agent",
        description: str = "API integration and testing agent",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        super().__init__(
            name=name,
            description=description,
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute API-related task.
        
        Args:
            task: Task description (e.g., "call GET /users endpoint")
            context: Execution context with API details
            
        Returns:
            Dictionary with API response and status
        """
        self._log_action("Starting API operation", task[:100])
        
        try:
            # Determine API operation from task and context
            operation = self._parse_api_task(task, context)
            
            if not operation:
                return self._build_error_result(
                    "Could not determine API operation from task"
                )
            
            # Get web fetch tool for HTTP requests
            web_tool = self._get_tool('web_fetch')
            if not web_tool:
                return self._build_error_result(
                    "Web fetch tool not available for API operations"
                )
            
            # Execute operation based on API type
            api_type = operation.get('api_type', 'rest')
            
            if api_type == 'rest':
                result = self._execute_rest_api(web_tool, operation, context)
            elif api_type == 'graphql':
                result = self._execute_graphql_api(web_tool, operation, context)
            elif api_type == 'soap':
                result = self._execute_soap_api(web_tool, operation, context)
            else:
                return self._build_error_result(f"Unsupported API type: {api_type}")
            
            if result['success']:
                self._log_action("API operation complete", operation.get('description', ''))
                return self._build_success_result(
                    message=f"API {api_type.upper()} operation completed successfully",
                    data=result,
                    next_context={
                        'last_api_call': operation,
                        'api_response': result.get('response'),
                        'status_code': result.get('status_code')
                    }
                )
            else:
                return self._build_error_result(
                    f"API operation failed: {result.get('error')}"
                )
            
        except Exception as e:
            self.logger.exception("API operation failed")
            return self._build_error_result(f"API operation failed: {str(e)}", e)
    
    def _parse_api_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse task to determine API operation.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            Operation dictionary or None
        """
        task_lower = task.lower()
        
        # Check if API details are in context
        if 'api_config' in context:
            api_config = context['api_config']
            
            return {
                'api_type': api_config.get('type', 'rest'),
                'url': api_config.get('url', api_config.get('base_url', '')),
                'method': api_config.get('method', 'GET'),
                'endpoint': api_config.get('endpoint', ''),
                'headers': api_config.get('headers', {}),
                'params': api_config.get('params', {}),
                'body': api_config.get('body', api_config.get('data', {})),
                'auth': api_config.get('auth', {}),
                'description': task
            }
        
        # Try to parse from task description
        operation = {
            'api_type': 'rest',
            'method': 'GET',
            'url': '',
            'endpoint': '',
            'headers': {},
            'params': {},
            'body': {},
            'auth': {},
            'description': task
        }
        
        # Detect API type
        if 'graphql' in task_lower:
            operation['api_type'] = 'graphql'
            operation['method'] = 'POST'
        elif 'soap' in task_lower:
            operation['api_type'] = 'soap'
            operation['method'] = 'POST'
        
        # Detect HTTP method
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        for method in methods:
            if method.lower() in task_lower:
                operation['method'] = method
                break
        
        # Try to extract URL or endpoint
        if 'http://' in task or 'https://' in task:
            # Extract URL from task
            words = task.split()
            for word in words:
                if word.startswith('http://') or word.startswith('https://'):
                    operation['url'] = word.strip('.,;')
                    break
        
        # Use context values if available
        operation['url'] = context.get('api_url', operation['url'])
        operation['endpoint'] = context.get('endpoint', operation['endpoint'])
        operation['headers'] = context.get('headers', operation['headers'])
        operation['params'] = context.get('params', operation['params'])
        operation['body'] = context.get('body', context.get('data', operation['body']))
        operation['auth'] = context.get('auth', operation['auth'])
        
        return operation
    
    def _execute_rest_api(
        self,
        web_tool: Any,
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute REST API operation.
        
        Args:
            web_tool: Web fetch tool
            operation: Operation details
            context: Execution context
            
        Returns:
            Result dictionary
        """
        try:
            # Build full URL
            base_url = operation.get('url', '')
            endpoint = operation.get('endpoint', '')
            full_url = urljoin(base_url, endpoint) if base_url else endpoint
            
            if not full_url:
                return {
                    'success': False,
                    'error': 'No URL or endpoint provided'
                }
            
            # Prepare headers
            headers = operation.get('headers', {}).copy()
            
            # Add authentication
            auth = operation.get('auth', {})
            if auth:
                headers.update(self._build_auth_headers(auth))
            
            # Add content type if body is present
            body = operation.get('body')
            if body and 'Content-Type' not in headers:
                headers['Content-Type'] = 'application/json'
            
            # Prepare request parameters
            request_params = {
                'url': full_url,
                'method': operation.get('method', 'GET'),
                'headers': headers,
            }
            
            # Add query parameters
            params = operation.get('params')
            if params:
                request_params['params'] = params
            
            # Add body
            if body:
                if isinstance(body, dict):
                    request_params['data'] = json.dumps(body)
                else:
                    request_params['data'] = body
            
            # Execute request using web_fetch tool
            result = web_tool.invoke(request_params)
            
            if result.get('success'):
                # Parse response
                response_data = result.get('content', result.get('data', ''))
                status_code = result.get('status_code', 200)
                
                # Try to parse as JSON
                try:
                    if isinstance(response_data, str):
                        parsed_response = json.loads(response_data)
                    else:
                        parsed_response = response_data
                except json.JSONDecodeError:
                    parsed_response = response_data
                
                return {
                    'success': True,
                    'response': parsed_response,
                    'status_code': status_code,
                    'headers': result.get('headers', {}),
                    'method': operation.get('method'),
                    'url': full_url
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Request failed'),
                    'status_code': result.get('status_code'),
                    'url': full_url
                }
            
        except Exception as e:
            self.logger.error(f"REST API execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_graphql_api(
        self,
        web_tool: Any,
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute GraphQL API operation.
        
        Args:
            web_tool: Web fetch tool
            operation: Operation details
            context: Execution context
            
        Returns:
            Result dictionary
        """
        try:
            url = operation.get('url', '')
            if not url:
                return {
                    'success': False,
                    'error': 'No GraphQL endpoint URL provided'
                }
            
            # Get GraphQL query
            query = operation.get('query', operation.get('body', {}).get('query', ''))
            variables = operation.get('variables', operation.get('body', {}).get('variables', {}))
            
            if not query:
                return {
                    'success': False,
                    'error': 'No GraphQL query provided'
                }
            
            # Prepare GraphQL request body
            graphql_body = {
                'query': query
            }
            
            if variables:
                graphql_body['variables'] = variables
            
            # Prepare headers
            headers = operation.get('headers', {}).copy()
            headers['Content-Type'] = 'application/json'
            
            # Add authentication
            auth = operation.get('auth', {})
            if auth:
                headers.update(self._build_auth_headers(auth))
            
            # Execute request
            request_params = {
                'url': url,
                'method': 'POST',
                'headers': headers,
                'data': json.dumps(graphql_body)
            }
            
            result = web_tool.invoke(request_params)
            
            if result.get('success'):
                response_data = result.get('content', result.get('data', ''))
                
                # Parse JSON response
                try:
                    if isinstance(response_data, str):
                        parsed_response = json.loads(response_data)
                    else:
                        parsed_response = response_data
                    
                    # Check for GraphQL errors
                    if 'errors' in parsed_response:
                        return {
                            'success': False,
                            'error': 'GraphQL errors in response',
                            'errors': parsed_response['errors'],
                            'data': parsed_response.get('data'),
                            'url': url
                        }
                    
                    return {
                        'success': True,
                        'response': parsed_response,
                        'data': parsed_response.get('data'),
                        'status_code': result.get('status_code', 200),
                        'url': url
                    }
                    
                except json.JSONDecodeError as e:
                    return {
                        'success': False,
                        'error': f'Failed to parse GraphQL response: {str(e)}',
                        'raw_response': response_data
                    }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'GraphQL request failed'),
                    'url': url
                }
            
        except Exception as e:
            self.logger.error(f"GraphQL API execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_soap_api(
        self,
        web_tool: Any,
        operation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute SOAP API operation.
        
        Args:
            web_tool: Web fetch tool
            operation: Operation details
            context: Execution context
            
        Returns:
            Result dictionary
        """
        try:
            url = operation.get('url', '')
            if not url:
                return {
                    'success': False,
                    'error': 'No SOAP endpoint URL provided'
                }
            
            # Get SOAP envelope
            soap_body = operation.get('body', operation.get('soap_envelope', ''))
            
            if not soap_body:
                return {
                    'success': False,
                    'error': 'No SOAP envelope provided'
                }
            
            # Prepare headers
            headers = operation.get('headers', {}).copy()
            headers['Content-Type'] = 'text/xml; charset=utf-8'
            
            # Add SOAPAction header if provided
            soap_action = operation.get('soap_action', context.get('soap_action'))
            if soap_action:
                headers['SOAPAction'] = soap_action
            
            # Add authentication
            auth = operation.get('auth', {})
            if auth:
                headers.update(self._build_auth_headers(auth))
            
            # Execute request
            request_params = {
                'url': url,
                'method': 'POST',
                'headers': headers,
                'data': soap_body
            }
            
            result = web_tool.invoke(request_params)
            
            if result.get('success'):
                response_data = result.get('content', result.get('data', ''))
                
                return {
                    'success': True,
                    'response': response_data,
                    'status_code': result.get('status_code', 200),
                    'headers': result.get('headers', {}),
                    'url': url
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'SOAP request failed'),
                    'url': url
                }
            
        except Exception as e:
            self.logger.error(f"SOAP API execution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_auth_headers(self, auth: Dict[str, Any]) -> Dict[str, str]:
        """
        Build authentication headers.
        
        Args:
            auth: Authentication configuration
            
        Returns:
            Dictionary with authentication headers
        """
        headers = {}
        auth_type = auth.get('type', '').lower()
        
        if auth_type == 'bearer':
            token = auth.get('token', '')
            if token:
                headers['Authorization'] = f'Bearer {token}'
        
        elif auth_type == 'api_key':
            key = auth.get('key', '')
            value = auth.get('value', '')
            if key and value:
                headers[key] = value
        
        elif auth_type == 'basic':
            import base64
            username = auth.get('username', '')
            password = auth.get('password', '')
            if username and password:
                credentials = f'{username}:{password}'.encode('utf-8')
                encoded = base64.b64encode(credentials).decode('utf-8')
                headers['Authorization'] = f'Basic {encoded}'
        
        elif auth_type == 'custom':
            # Custom headers from auth config
            custom_headers = auth.get('headers', {})
            headers.update(custom_headers)
        
        return headers
    
    def _format_api_response(self, response: Any, format_type: str = 'json') -> str:
        """
        Format API response for display.
        
        Args:
            response: API response data
            format_type: Format type (json, text, xml)
            
        Returns:
            Formatted response string
        """
        try:
            if format_type == 'json':
                if isinstance(response, dict) or isinstance(response, list):
                    return json.dumps(response, indent=2)
                else:
                    return str(response)
            else:
                return str(response)
        except Exception as e:
            self.logger.error(f"Failed to format response: {e}")
            return str(response)


