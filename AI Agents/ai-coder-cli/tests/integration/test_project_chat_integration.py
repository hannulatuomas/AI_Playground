
"""
Integration tests for project management and chat history features.

Tests the complete workflow of creating projects, switching between them,
and maintaining separate chat histories with context.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock

from core.project_manager import ProjectManager
from core.memory import MemoryManager
from core.chat_history import ChatHistoryManager


class TestProjectChatIntegration:
    """Integration tests for project, memory, and chat history systems."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        # Cleanup
        if temp_path.exists():
            shutil.rmtree(temp_path)
    
    @pytest.fixture
    def mock_llm_router(self):
        """Create a mock LLM router."""
        mock = Mock()
        mock.query = Mock(return_value={
            'response': 'This is a comprehensive summary of the conversation.'
        })
        return mock
    
    @pytest.fixture
    def integrated_system(self, temp_dir, mock_llm_router):
        """Create an integrated system with all components."""
        project_manager = ProjectManager(
            storage_path=temp_dir / "projects",
            auto_save=True,
            create_default_project=False
        )
        
        memory_manager = MemoryManager(
            storage_path=temp_dir / "memory",
            llm_router=mock_llm_router,
            auto_save=True,
            project_scoped=True
        )
        
        chat_history_manager = ChatHistoryManager(
            storage_path=temp_dir / "chat_history",
            llm_router=mock_llm_router,
            auto_save=True,
            enable_auto_summarization=False
        )
        
        return {
            'project_manager': project_manager,
            'memory_manager': memory_manager,
            'chat_history_manager': chat_history_manager,
            'temp_dir': temp_dir
        }
    
    def test_create_project_with_memory_and_history(self, integrated_system):
        """Test creating a project and linking memory/history."""
        pm = integrated_system['project_manager']
        mm = integrated_system['memory_manager']
        chm = integrated_system['chat_history_manager']
        
        # Create a project
        project_id = pm.create_project(
            name="AI Development",
            description="Working on AI features"
        )
        
        # Set as active
        pm.set_active_project(project_id)
        
        # Create memory session for project
        mm.switch_project_context(project_id)
        session_id = mm.create_project_session(project_id)
        pm.set_project_memory_session_id(project_id, session_id)
        
        # Create chat history for project
        history_id = chm.create_history(project_id=project_id)
        
        # Verify linkage
        assert pm.get_project_memory_session_id(project_id) == session_id
        assert mm.get_project_session_id(project_id) == session_id
        
        history = chm.get_history_by_project(project_id)
        assert history is not None
        assert history.project_id == project_id
    
    def test_switch_projects_with_separate_contexts(self, integrated_system):
        """Test switching between projects maintains separate contexts."""
        pm = integrated_system['project_manager']
        mm = integrated_system['memory_manager']
        chm = integrated_system['chat_history_manager']
        
        # Create two projects
        project1_id = pm.create_project(name="Project 1")
        project2_id = pm.create_project(name="Project 2")
        
        # Setup project 1
        pm.set_active_project(project1_id)
        mm.switch_project_context(project1_id)
        session1_id = mm.create_project_session(project1_id)
        history1_id = chm.create_history(project_id=project1_id)
        
        # Add data to project 1
        mm.add_user_message(session1_id, "Project 1 message")
        chm.add_user_message(history1_id, "Project 1 chat")
        
        # Setup project 2
        pm.set_active_project(project2_id)
        mm.switch_project_context(project2_id)
        session2_id = mm.create_project_session(project2_id)
        history2_id = chm.create_history(project_id=project2_id)
        
        # Add data to project 2
        mm.add_user_message(session2_id, "Project 2 message")
        chm.add_user_message(history2_id, "Project 2 chat")
        
        # Verify separation
        assert session1_id != session2_id
        assert history1_id != history2_id
        
        # Check project 1 data
        session1 = mm.get_session(session1_id)
        assert len(session1.messages) == 1
        assert session1.messages[0].content == "Project 1 message"
        
        history1 = chm.get_history(history1_id)
        assert len(history1.messages) == 1
        assert history1.messages[0].content == "Project 1 chat"
        
        # Check project 2 data
        session2 = mm.get_session(session2_id)
        assert len(session2.messages) == 1
        assert session2.messages[0].content == "Project 2 message"
        
        history2 = chm.get_history(history2_id)
        assert len(history2.messages) == 1
        assert history2.messages[0].content == "Project 2 chat"
    
    def test_project_switch_and_resume_conversation(self, integrated_system):
        """Test switching projects and resuming conversations."""
        pm = integrated_system['project_manager']
        mm = integrated_system['memory_manager']
        chm = integrated_system['chat_history_manager']
        
        # Create project A
        projectA_id = pm.create_project(name="Project A")
        pm.set_active_project(projectA_id)
        mm.switch_project_context(projectA_id)
        sessionA_id = mm.create_project_session(projectA_id)
        historyA_id = chm.create_history(project_id=projectA_id)
        
        # Have a conversation in project A
        chm.add_user_message(historyA_id, "Hello in Project A")
        chm.add_assistant_message(historyA_id, "Response in Project A")
        mm.add_user_message(sessionA_id, "Memory in Project A")
        
        # Create and switch to project B
        projectB_id = pm.create_project(name="Project B")
        pm.set_active_project(projectB_id)
        mm.switch_project_context(projectB_id)
        sessionB_id = mm.create_project_session(projectB_id)
        historyB_id = chm.create_history(project_id=projectB_id)
        
        # Have a conversation in project B
        chm.add_user_message(historyB_id, "Hello in Project B")
        chm.add_assistant_message(historyB_id, "Response in Project B")
        mm.add_user_message(sessionB_id, "Memory in Project B")
        
        # Switch back to project A
        pm.set_active_project(projectA_id)
        mm.switch_project_context(projectA_id)
        
        # Resume conversation in project A
        chm.add_user_message(historyA_id, "Continuing in Project A")
        mm.add_user_message(sessionA_id, "More memory in Project A")
        
        # Verify project A has correct history
        historyA = chm.get_history(historyA_id)
        assert len(historyA.messages) == 3
        assert historyA.messages[0].content == "Hello in Project A"
        assert historyA.messages[2].content == "Continuing in Project A"
        
        # Verify project B history is unchanged
        historyB = chm.get_history(historyB_id)
        assert len(historyB.messages) == 2
        assert historyB.messages[0].content == "Hello in Project B"
    
    def test_delete_project_cleans_up_all_data(self, integrated_system):
        """Test that deleting a project removes all associated data."""
        pm = integrated_system['project_manager']
        mm = integrated_system['memory_manager']
        chm = integrated_system['chat_history_manager']
        
        # Create and setup project
        project_id = pm.create_project(name="Test Project")
        pm.set_active_project(project_id)
        mm.switch_project_context(project_id)
        session_id = mm.create_project_session(project_id)
        history_id = chm.create_history(project_id=project_id)
        
        # Add some data
        chm.add_user_message(history_id, "Test message")
        mm.add_user_message(session_id, "Test memory")
        
        # Verify data exists
        assert pm.get_project(project_id) is not None
        assert mm.get_session(session_id) is not None
        assert chm.get_history(history_id) is not None
        
        # Delete project and associated data
        mm.delete_project_memory(project_id)
        chm.delete_history(history_id)
        pm.delete_project(project_id)
        
        # Verify all data is gone
        assert pm.get_project(project_id) is None
        assert mm.get_session(session_id) is None
        assert chm.get_history(history_id) is None
    
    def test_persistence_across_sessions(self, integrated_system):
        """Test that project, memory, and history persist across sessions."""
        pm = integrated_system['project_manager']
        mm = integrated_system['memory_manager']
        chm = integrated_system['chat_history_manager']
        temp_dir = integrated_system['temp_dir']
        
        # Create and setup project
        project_id = pm.create_project(name="Persistent Project")
        pm.set_active_project(project_id)
        mm.switch_project_context(project_id)
        session_id = mm.create_project_session(project_id)
        pm.set_project_memory_session_id(project_id, session_id)
        history_id = chm.create_history(project_id=project_id)
        
        # Add data
        chm.add_user_message(history_id, "Persistent message")
        chm.add_assistant_message(history_id, "Persistent response")
        mm.add_user_message(session_id, "Persistent memory")
        
        # Save everything
        pm.save_all_projects()
        mm.save_all_sessions()
        chm.save_all_histories()
        
        # Create new instances (simulating restart)
        new_pm = ProjectManager(
            storage_path=temp_dir / "projects",
            auto_save=False,
            create_default_project=False
        )
        
        new_mm = MemoryManager(
            storage_path=temp_dir / "memory",
            llm_router=mm.llm_router,
            auto_save=False,
            project_scoped=True
        )
        
        new_chm = ChatHistoryManager(
            storage_path=temp_dir / "chat_history",
            llm_router=chm.llm_router,
            auto_save=False
        )
        
        # Verify project loaded
        assert len(new_pm.projects) == 1
        loaded_project = new_pm.get_project(project_id)
        assert loaded_project is not None
        assert loaded_project.name == "Persistent Project"
        assert loaded_project.is_active is True
        
        # Verify memory loaded
        loaded_session = new_mm.get_session(session_id)
        assert loaded_session is not None
        assert len(loaded_session.messages) == 1
        assert loaded_session.messages[0].content == "Persistent memory"
        
        # Verify chat history loaded
        loaded_history = new_chm.get_history_by_project(project_id)
        assert loaded_history is not None
        assert len(loaded_history.messages) == 2
        assert loaded_history.messages[0].content == "Persistent message"
        assert loaded_history.messages[1].content == "Persistent response"
    
    def test_chat_history_summarization_per_project(self, integrated_system):
        """Test that chat history summarization works per project."""
        pm = integrated_system['project_manager']
        chm = integrated_system['chat_history_manager']
        
        # Create project
        project_id = pm.create_project(name="Test Project")
        history_id = chm.create_history(project_id=project_id)
        
        # Add many messages
        for i in range(20):
            chm.add_user_message(history_id, f"User message {i}")
            chm.add_assistant_message(history_id, f"Assistant response {i}")
        
        # Summarize
        summary = chm.summarize_history(history_id, keep_recent=10)
        
        assert summary is not None
        assert isinstance(summary, str)
        
        # Verify history was compressed
        history = chm.get_history(history_id)
        assert len(history.messages) == 10  # Only recent messages
        assert len(history.summaries) == 1   # Summary added
        
        # Verify we can still get full context
        full_context = chm.get_full_context(history_id)
        assert len(full_context) > 10  # Summary + recent messages
    
    def test_concurrent_projects_with_independent_state(self, integrated_system):
        """Test multiple projects maintain independent state."""
        pm = integrated_system['project_manager']
        mm = integrated_system['memory_manager']
        chm = integrated_system['chat_history_manager']
        
        projects = []
        
        # Create multiple projects with their own state
        for i in range(3):
            project_id = pm.create_project(name=f"Project {i}")
            pm.set_active_project(project_id)
            mm.switch_project_context(project_id)
            session_id = mm.create_project_session(project_id)
            history_id = chm.create_history(project_id=project_id)
            
            # Add unique data to each project
            chm.add_user_message(history_id, f"Unique message for project {i}")
            mm.add_user_message(session_id, f"Unique memory for project {i}")
            
            projects.append({
                'project_id': project_id,
                'session_id': session_id,
                'history_id': history_id
            })
        
        # Verify each project has its own independent data
        for i, proj_data in enumerate(projects):
            history = chm.get_history(proj_data['history_id'])
            assert len(history.messages) == 1
            assert f"project {i}" in history.messages[0].content
            
            session = mm.get_session(proj_data['session_id'])
            assert len(session.messages) == 1
            assert f"project {i}" in session.messages[0].content
        
        # Verify no data leakage between projects
        for i, proj1 in enumerate(projects):
            for j, proj2 in enumerate(projects):
                if i != j:
                    assert proj1['session_id'] != proj2['session_id']
                    assert proj1['history_id'] != proj2['history_id']
    
    def test_memory_context_switching(self, integrated_system):
        """Test that memory context switches correctly with projects."""
        pm = integrated_system['project_manager']
        mm = integrated_system['memory_manager']
        
        # Create two projects
        proj1_id = pm.create_project(name="Project 1")
        proj2_id = pm.create_project(name="Project 2")
        
        # Setup project 1
        mm.switch_project_context(proj1_id)
        session1_id = mm.create_project_session(proj1_id)
        mm.add_user_message(session1_id, "Context 1")
        
        # Setup project 2
        mm.switch_project_context(proj2_id)
        session2_id = mm.create_project_session(proj2_id)
        mm.add_user_message(session2_id, "Context 2")
        
        # Switch back to project 1
        mm.switch_project_context(proj1_id)
        
        # Verify current context is project 1
        assert mm.get_project_context() == proj1_id
        current_session_id = mm.get_current_session_id()
        assert current_session_id == session1_id
        
        # Add more data to project 1
        mm.add_user_message(session1_id, "More context 1")
        
        # Switch to project 2 and verify context
        mm.switch_project_context(proj2_id)
        assert mm.get_project_context() == proj2_id
        current_session_id = mm.get_current_session_id()
        assert current_session_id == session2_id
