"""
Tests for API Manager Module
"""

import pytest
from src.modules.api_manager import (
    RESTGenerator, GraphQLGenerator, SOAPGenerator,
    APITester, RESTSpec, Model, Endpoint, GraphQLSchema,
    GraphQLType, GraphQLQuery, SOAPSpec, SOAPOperation
)


class MockAIBackend:
    """Mock AI backend for testing."""
    
    def query(self, prompt, max_tokens=1000):
        """Mock query method."""
        return "Generated code"


@pytest.fixture
def mock_ai():
    """Provide mock AI backend."""
    return MockAIBackend()


def test_rest_generator_fastapi(mock_ai):
    """Test FastAPI REST API generation."""
    generator = RESTGenerator(mock_ai)
    
    spec = RESTSpec(
        name="Test API",
        models=[
            Model(name="User", fields={"name": "str", "email": "str"})
        ],
        endpoints=[
            Endpoint(
                path="/users",
                method="GET",
                description="Get all users"
            )
        ],
        framework="fastapi"
    )
    
    result = generator.generate_rest_api(spec)
    
    assert 'main.py' in result.files
    assert 'models.py' in result.files
    assert len(result.dependencies) > 0
    assert 'fastapi' in result.dependencies


def test_rest_generator_flask(mock_ai):
    """Test Flask REST API generation."""
    generator = RESTGenerator(mock_ai)
    
    spec = RESTSpec(
        name="Test API",
        models=[],
        endpoints=[],
        framework="flask"
    )
    
    result = generator.generate_rest_api(spec)
    
    assert 'app.py' in result.files
    assert 'flask' in result.dependencies


def test_rest_generator_express(mock_ai):
    """Test Express.js REST API generation."""
    generator = RESTGenerator(mock_ai)
    
    spec = RESTSpec(
        name="Test API",
        models=[],
        endpoints=[],
        framework="express"
    )
    
    result = generator.generate_rest_api(spec)
    
    assert 'index.js' in result.files
    assert 'package.json' in result.files


def test_graphql_generator_apollo(mock_ai):
    """Test Apollo Server GraphQL generation."""
    generator = GraphQLGenerator(mock_ai)
    
    schema = GraphQLSchema(
        types=[
            GraphQLType(
                name="User",
                fields={"id": "ID!", "name": "String!"}
            )
        ],
        queries=[
            GraphQLQuery(
                name="users",
                return_type="[User]"
            )
        ],
        mutations=[],
        framework="apollo"
    )
    
    result = generator.generate_graphql_schema(schema)
    
    assert 'schema.graphql' in result
    assert 'resolvers.js' in result
    assert 'server.js' in result


def test_graphql_generator_graphene(mock_ai):
    """Test Graphene (Python) GraphQL generation."""
    generator = GraphQLGenerator(mock_ai)
    
    schema = GraphQLSchema(
        types=[
            GraphQLType(
                name="User",
                fields={"id": "ID", "name": "String"}
            )
        ],
        queries=[
            GraphQLQuery(
                name="user",
                return_type="User"
            )
        ],
        mutations=[],
        framework="graphene"
    )
    
    result = generator.generate_graphql_schema(schema)
    
    assert 'schema.py' in result
    assert 'app.py' in result


def test_soap_generator(mock_ai):
    """Test SOAP service generation."""
    generator = SOAPGenerator(mock_ai)
    
    spec = SOAPSpec(
        service_name="TestService",
        operations=[
            SOAPOperation(
                name="GetUser",
                input_message="GetUserRequest",
                output_message="GetUserResponse",
                description="Get user by ID"
            )
        ]
    )
    
    result = generator.generate_soap_service(spec, 'python')
    
    assert 'service.py' in result
    assert 'service.wsdl' in result


def test_api_tester_basic():
    """Test API tester basic functionality."""
    tester = APITester("http://localhost:8000")
    
    assert tester.base_url == "http://localhost:8000"
    assert len(tester.test_cases) == 0


def test_api_tester_generate_tests():
    """Test test case generation."""
    tester = APITester()
    
    endpoints = [
        {
            'method': 'GET',
            'path': '/users',
            'auth_required': True
        },
        {
            'method': 'POST',
            'path': '/users',
            'auth_required': True
        }
    ]
    
    tests = tester.generate_tests(endpoints)
    
    assert len(tests) > 0
    # Should generate auth tests for protected endpoints
    assert any('Unauthorized' in test.name for test in tests)


def test_rest_spec_creation():
    """Test REST spec creation."""
    spec = RESTSpec(
        name="My API",
        models=[
            Model(name="Product", fields={"name": "str", "price": "float"})
        ],
        endpoints=[
            Endpoint(path="/products", method="GET", description="List products")
        ],
        framework="fastapi"
    )
    
    assert spec.name == "My API"
    assert len(spec.models) == 1
    assert len(spec.endpoints) == 1
    assert spec.framework == "fastapi"


def test_graphql_schema_creation():
    """Test GraphQL schema creation."""
    schema = GraphQLSchema(
        types=[
            GraphQLType(name="Book", fields={"title": "String", "author": "String"})
        ],
        queries=[
            GraphQLQuery(name="books", return_type="[Book]")
        ],
        mutations=[]
    )
    
    assert len(schema.types) == 1
    assert len(schema.queries) == 1
    assert schema.framework == "apollo"  # default
