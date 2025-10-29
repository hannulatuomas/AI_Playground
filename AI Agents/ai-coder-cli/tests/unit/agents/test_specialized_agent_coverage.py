"""
Unit tests for specialized agents with low coverage.

Tests for:
- APIAgent
- CybersecurityAgent
- DataAnalysisAgent
- DatabaseAgent
- LinuxAdminAgent
- WindowsAdminAgent
- PromptRefinerAgent
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_router():
    """Create a mock LLM router."""
    router = Mock()
    router.query.return_value = "Mock LLM response"
    return router


@pytest.fixture
def mock_tool_registry():
    """Create a mock tool registry."""
    registry = Mock()
    return registry


# =============================================================================
# APIAgent Tests
# =============================================================================

class TestAPIAgent:
    """Tests for APIAgent."""
    
    def test_initialization(self, mock_llm_router):
        """Test API agent initialization."""
        from agents.api_agent import APIAgent
        
        agent = APIAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "api_agent"
        assert "API" in agent.description or "api" in agent.description.lower()
        assert agent.llm_router == mock_llm_router
    
    def test_execute_api_design(self, mock_llm_router):
        """Test executing API design task."""
        from agents.api_agent import APIAgent
        
        mock_llm_router.query.return_value = """
        API Design:
        - Endpoint: GET /api/users
        - Response: JSON with user list
        """
        
        agent = APIAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Design a REST API for user management", {})
        
        assert result is not None
    
    def test_execute_api_documentation(self, mock_llm_router):
        """Test API documentation generation."""
        from agents.api_agent import APIAgent
        
        mock_llm_router.query.return_value = """
        API Documentation:
        Endpoint: POST /api/users
        """
        
        agent = APIAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Generate API documentation", {})
        
        assert result is not None


# =============================================================================
# CybersecurityAgent Tests
# =============================================================================

class TestCybersecurityAgent:
    """Tests for CybersecurityAgent."""
    
    def test_initialization(self, mock_llm_router):
        """Test cybersecurity agent initialization."""
        from agents.cybersecurity import CybersecurityAgent
        
        agent = CybersecurityAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "cybersecurity_agent"
        assert "security" in agent.description.lower()
        assert agent.llm_router == mock_llm_router
    
    def test_execute_security_audit(self, mock_llm_router):
        """Test security audit execution."""
        from agents.cybersecurity import CybersecurityAgent
        
        mock_llm_router.query.return_value = """
        Security Audit Results:
        - SQL Injection vulnerabilities found
        - XSS protection needed
        """
        
        agent = CybersecurityAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Audit security of the application", {})
        
        assert result is not None
    
    def test_execute_vulnerability_scan(self, mock_llm_router):
        """Test vulnerability scanning."""
        from agents.cybersecurity import CybersecurityAgent
        
        mock_llm_router.query.return_value = "Vulnerability scan complete"
        
        agent = CybersecurityAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Scan for vulnerabilities", {})
        
        assert result is not None


# =============================================================================
# DataAnalysisAgent Tests
# =============================================================================

class TestDataAnalysisAgent:
    """Tests for DataAnalysisAgent."""
    
    def test_initialization(self, mock_llm_router):
        """Test data analysis agent initialization."""
        from agents.data_analysis import DataAnalysisAgent
        
        agent = DataAnalysisAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "data_analysis_agent"
        assert "data" in agent.description.lower() or "analysis" in agent.description.lower()
        assert agent.llm_router == mock_llm_router
    
    def test_execute_data_analysis(self, mock_llm_router):
        """Test data analysis execution."""
        from agents.data_analysis import DataAnalysisAgent
        
        mock_llm_router.query.return_value = """
        Analysis Results:
        - Mean: 45.2
        - Median: 42.0
        - Standard Deviation: 12.5
        """
        
        agent = DataAnalysisAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Analyze sales data", {})
        
        assert result is not None
    
    def test_execute_statistical_analysis(self, mock_llm_router):
        """Test statistical analysis."""
        from agents.data_analysis import DataAnalysisAgent
        
        mock_llm_router.query.return_value = "Statistical analysis complete"
        
        agent = DataAnalysisAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Perform statistical analysis", {})
        
        assert result is not None


# =============================================================================
# DatabaseAgent Tests
# =============================================================================

class TestDatabaseAgent:
    """Tests for DatabaseAgent."""
    
    def test_initialization(self, mock_llm_router):
        """Test database agent initialization."""
        from agents.database import DatabaseAgent
        
        agent = DatabaseAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "database_agent"
        assert "database" in agent.description.lower() or "db" in agent.description.lower()
        assert agent.llm_router == mock_llm_router
    
    def test_execute_query_generation(self, mock_llm_router):
        """Test SQL query generation."""
        from agents.database import DatabaseAgent
        
        mock_llm_router.query.return_value = """
        SELECT * FROM users WHERE age > 18;
        """
        
        agent = DatabaseAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Generate SQL query to get adult users", {})
        
        assert result is not None
    
    def test_execute_schema_design(self, mock_llm_router):
        """Test database schema design."""
        from agents.database import DatabaseAgent
        
        mock_llm_router.query.return_value = """
        CREATE TABLE users (
            id INT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );
        """
        
        agent = DatabaseAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Design database schema for user management", {})
        
        assert result is not None


# =============================================================================
# PromptRefinerAgent Tests
# =============================================================================

class TestPromptRefinerAgent:
    """Tests for PromptRefinerAgent."""
    
    def test_initialization(self, mock_llm_router):
        """Test prompt refiner agent initialization."""
        from agents.prompt_refiner import PromptRefinerAgent
        
        agent = PromptRefinerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "prompt_refiner"
        assert "prompt" in agent.description.lower()
        assert agent.llm_router == mock_llm_router
    
    def test_refine_prompt(self, mock_llm_router):
        """Test prompt refinement."""
        from agents.prompt_refiner import PromptRefinerAgent
        
        mock_llm_router.query.return_value = """
        Refined Prompt:
        Please analyze the code and provide detailed recommendations for improvements,
        focusing on performance, readability, and maintainability.
        """
        
        agent = PromptRefinerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.refine_prompt("make code better")
        
        assert result is not None
    
    def test_execute_prompt_improvement(self, mock_llm_router):
        """Test execute method for prompt improvement."""
        from agents.prompt_refiner import PromptRefinerAgent
        
        mock_llm_router.query.return_value = "Improved prompt"
        
        agent = PromptRefinerAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Improve this prompt: write code", {})
        
        assert result is not None


# =============================================================================
# LinuxAdminAgent Tests
# =============================================================================

class TestLinuxAdminAgent:
    """Tests for LinuxAdminAgent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Linux admin agent initialization."""
        from agents.linux_admin import LinuxAdminAgent
        
        agent = LinuxAdminAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "linux_admin"
        assert "linux" in agent.description.lower()
        assert agent.llm_router == mock_llm_router
    
    def test_execute_system_command(self, mock_llm_router):
        """Test system command generation."""
        from agents.linux_admin import LinuxAdminAgent
        
        mock_llm_router.query.return_value = """
        Command: sudo apt-get update && sudo apt-get upgrade
        Description: Updates system packages
        """
        
        agent = LinuxAdminAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("How to update system packages?", {})
        
        assert result is not None
    
    def test_execute_user_management(self, mock_llm_router):
        """Test user management command generation."""
        from agents.linux_admin import LinuxAdminAgent
        
        mock_llm_router.query.return_value = "sudo useradd newuser"
        
        agent = LinuxAdminAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Create a new user", {})
        
        assert result is not None


# =============================================================================
# WindowsAdminAgent Tests
# =============================================================================

class TestWindowsAdminAgent:
    """Tests for WindowsAdminAgent."""
    
    def test_initialization(self, mock_llm_router):
        """Test Windows admin agent initialization."""
        from agents.windows_admin import WindowsAdminAgent
        
        agent = WindowsAdminAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        assert agent.name == "windows_admin"
        assert "windows" in agent.description.lower()
        assert agent.llm_router == mock_llm_router
    
    def test_execute_powershell_command(self, mock_llm_router):
        """Test PowerShell command generation."""
        from agents.windows_admin import WindowsAdminAgent
        
        mock_llm_router.query.return_value = """
        PowerShell Command: Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
        """
        
        agent = WindowsAdminAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Show top 10 processes by CPU usage", {})
        
        assert result is not None
    
    def test_execute_registry_operation(self, mock_llm_router):
        """Test registry operation command generation."""
        from agents.windows_admin import WindowsAdminAgent
        
        mock_llm_router.query.return_value = "Registry command generated"
        
        agent = WindowsAdminAgent(
            llm_router=mock_llm_router,
            config={}
        )
        
        result = agent.execute("Modify registry key", {})
        
        assert result is not None
