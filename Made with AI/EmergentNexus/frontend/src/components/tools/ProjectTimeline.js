import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  Calendar, 
  Plus, 
  Edit,
  Trash,
  Link as LinkIcon,
  Clock,
  User,
  Flag,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useWorkspace } from '../../contexts/WorkspaceContext';

const priorityOptions = [
  { value: 'low', label: 'Low', color: 'bg-green-100 text-green-800' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800' },
  { value: 'critical', label: 'Critical', color: 'bg-red-100 text-red-800' }
];

const statusOptions = [
  { value: 'planning', label: 'Planning', color: 'bg-slate-100 text-slate-800' },
  { value: 'active', label: 'Active', color: 'bg-blue-100 text-blue-800' },
  { value: 'on-hold', label: 'On Hold', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'completed', label: 'Completed', color: 'bg-green-100 text-green-800' },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-800' }
];

export default function ProjectTimeline() {
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [isProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [viewMode, setViewMode] = useState('timeline'); // 'timeline', 'kanban', 'list'
  const [currentDate, setCurrentDate] = useState(new Date());
  const [projectForm, setProjectForm] = useState({
    name: '',
    description: '',
    startDate: '',
    endDate: '',
    status: 'planning',
    priority: 'medium',
    manager: '',
    budget: ''
  });
  const [taskForm, setTaskForm] = useState({
    name: '',
    description: '',
    projectId: '',
    startDate: '',
    endDate: '',
    status: 'planning',
    priority: 'medium',
    assignee: '',
    progress: 0,
    dependencies: []
  });
  
  const { nodes, api, actions } = useWorkspace();
  
  useEffect(() => {
    const projectItems = nodes.filter(node => node.node_type === 'project-item');
    const taskItems = nodes.filter(node => node.node_type === 'task-item');
    
    setProjects(projectItems);
    setTasks(taskItems);
    
    if (projectItems.length > 0 && !selectedProject) {
      setSelectedProject(projectItems[0]);
    }
  }, [nodes, selectedProject]);

  const openNewProjectModal = () => {
    setSelectedProject(null);
    setProjectForm({
      name: '',
      description: '',
      startDate: '',
      endDate: '',
      status: 'planning',
      priority: 'medium',
      manager: '',
      budget: ''
    });
    setIsProjectModalOpen(true);
  };

  const openEditProjectModal = (project) => {
    setSelectedProject(project);
    setProjectForm({
      name: project.title,
      description: project.content.description || '',
      startDate: project.content.startDate || '',
      endDate: project.content.endDate || '',
      status: project.content.status || 'planning',
      priority: project.content.priority || 'medium',
      manager: project.content.manager || '',
      budget: project.content.budget || ''
    });
    setIsProjectModalOpen(true);
  };

  const openNewTaskModal = (projectId = null) => {
    setSelectedTask(null);
    setTaskForm({
      name: '',
      description: '',
      projectId: projectId || selectedProject?.id || '',
      startDate: '',
      endDate: '',
      status: 'planning',
      priority: 'medium',
      assignee: '',
      progress: 0,
      dependencies: []
    });
    setIsTaskModalOpen(true);
  };

  const openEditTaskModal = (task) => {
    setSelectedTask(task);
    setTaskForm({
      name: task.title,
      description: task.content.description || '',
      projectId: task.content.projectId || '',
      startDate: task.content.startDate || '',
      endDate: task.content.endDate || '',
      status: task.content.status || 'planning',
      priority: task.content.priority || 'medium',
      assignee: task.content.assignee || '',
      progress: task.content.progress || 0,
      dependencies: task.content.dependencies || []
    });
    setIsTaskModalOpen(true);
  };

  const saveProject = async () => {
    if (!projectForm.name.trim()) return;
    
    const projectData = {
      node_type: 'project-item',
      title: projectForm.name.trim(),
      content: {
        description: projectForm.description,
        startDate: projectForm.startDate,
        endDate: projectForm.endDate,
        status: projectForm.status,
        priority: projectForm.priority,
        manager: projectForm.manager,
        budget: projectForm.budget
      },
      tags: ['project']
    };

    try {
      if (selectedProject) {
        await api.updateNode(selectedProject.id, projectData);
      } else {
        const newProject = await api.createNode(projectData);
        setSelectedProject(newProject);
      }
      setIsProjectModalOpen(false);
    } catch (error) {
      console.error('Failed to save project:', error);
    }
  };

  const saveTask = async () => {
    if (!taskForm.name.trim()) return;
    
    const taskData = {
      node_type: 'task-item',
      title: taskForm.name.trim(),
      content: {
        description: taskForm.description,
        projectId: taskForm.projectId,
        startDate: taskForm.startDate,
        endDate: taskForm.endDate,
        status: taskForm.status,
        priority: taskForm.priority,
        assignee: taskForm.assignee,
        progress: taskForm.progress,
        dependencies: taskForm.dependencies
      },
      tags: ['task', 'project']
    };

    try {
      if (selectedTask) {
        await api.updateNode(selectedTask.id, taskData);
      } else {
        await api.createNode(taskData);
      }
      setIsTaskModalOpen(false);
    } catch (error) {
      console.error('Failed to save task:', error);
    }
  };

  const deleteProject = async (projectId) => {
    try {
      // Delete associated tasks first
      const projectTasks = tasks.filter(task => task.content.projectId === projectId);
      await Promise.all(projectTasks.map(task => api.deleteNode(task.id)));
      
      // Delete project
      await api.deleteNode(projectId);
      
      if (selectedProject?.id === projectId) {
        setSelectedProject(projects.find(p => p.id !== projectId) || null);
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await api.deleteNode(taskId);
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  };

  const getProjectTasks = (projectId) => {
    return tasks.filter(task => task.content.projectId === projectId);
  };

  const getStatusStyle = (status, type = 'status') => {
    const option = (type === 'priority' ? priorityOptions : statusOptions)
      .find(opt => opt.value === status);
    return option ? option.color : 'bg-gray-100 text-gray-800';
  };

  const calculateProjectProgress = (project) => {
    const projectTasks = getProjectTasks(project.id);
    if (projectTasks.length === 0) return 0;
    
    const totalProgress = projectTasks.reduce((sum, task) => sum + (task.content.progress || 0), 0);
    return Math.round(totalProgress / projectTasks.length);
  };

  const renderTimelineView = () => {
    const monthStart = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const monthEnd = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    const daysInMonth = monthEnd.getDate();
    
    return (
      <div className="flex-1 overflow-auto">
        {/* Calendar Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1))}
              data-testid="prev-month-btn"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            
            <h3 className="text-lg font-semibold text-white">
              {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h3>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1))}
              data-testid="next-month-btn"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCurrentDate(new Date())}
            data-testid="today-btn"
          >
            Today
          </Button>
        </div>

        {/* Timeline Content */}
        <div className="p-4">
          {selectedProject ? (
            <div>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">{selectedProject.title}</h3>
                  <div className="flex items-center gap-4">
                    <Badge className={getStatusStyle(selectedProject.content.status)}>
                      {statusOptions.find(s => s.value === selectedProject.content.status)?.label}
                    </Badge>
                    <span className="text-sm text-slate-400">
                      Progress: {calculateProjectProgress(selectedProject)}%
                    </span>
                  </div>
                </div>
                
                <Button
                  size="sm"
                  onClick={() => openNewTaskModal(selectedProject.id)}
                  className="bg-blue-600 hover:bg-blue-700"
                  data-testid="add-task-btn"
                >
                  <Plus className="h-4 w-4 mr-1" />
                  Add Task
                </Button>
              </div>

              {/* Tasks List */}
              <div className="space-y-3">
                {getProjectTasks(selectedProject.id).map((task) => (
                  <div
                    key={task.id}
                    className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:bg-slate-700 cursor-pointer transition-colors"
                    onClick={() => openEditTaskModal(task)}
                    data-testid={`task-item-${task.id}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-white">{task.title}</h4>
                      <div className="flex items-center gap-2">
                        <Badge className={getStatusStyle(task.content.priority, 'priority')}>
                          {priorityOptions.find(p => p.value === task.content.priority)?.label}
                        </Badge>
                        <Badge className={getStatusStyle(task.content.status)}>
                          {statusOptions.find(s => s.value === task.content.status)?.label}
                        </Badge>
                      </div>
                    </div>
                    
                    {task.content.description && (
                      <p className="text-sm text-slate-400 mb-3">{task.content.description}</p>
                    )}
                    
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-xs text-slate-400">
                        {task.content.assignee && (
                          <div className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            {task.content.assignee}
                          </div>
                        )}
                        
                        {task.content.startDate && (
                          <div className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {new Date(task.content.startDate).toLocaleDateString()} - 
                            {task.content.endDate ? new Date(task.content.endDate).toLocaleDateString() : 'Ongoing'}
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <div className="text-xs text-slate-400">
                          {task.content.progress || 0}%
                        </div>
                        <div className="w-20 h-2 bg-slate-600 rounded-full">
                          <div
                            className="h-full bg-blue-500 rounded-full transition-all"
                            style={{ width: `${task.content.progress || 0}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                {getProjectTasks(selectedProject.id).length === 0 && (
                  <div className="text-center py-12 text-slate-400">
                    <Clock className="h-12 w-12 mx-auto mb-4 text-slate-500" />
                    <div className="text-lg font-medium mb-2">No Tasks</div>
                    <div className="text-sm mb-4">Add tasks to track project progress</div>
                    <Button
                      onClick={() => openNewTaskModal(selectedProject.id)}
                      variant="outline"
                    >
                      Add First Task
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-slate-400">
              <Calendar className="h-12 w-12 mx-auto mb-4 text-slate-500" />
              <div className="text-lg font-medium mb-2">No Project Selected</div>
              <div className="text-sm">Select a project to view its timeline</div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="h-full bg-slate-900 flex" data-testid="project-timeline">
      {/* Projects Sidebar */}
      <div className="w-80 border-r border-slate-700 bg-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Calendar className="h-5 w-5 text-red-400" />
              Projects
            </h2>
            
            <Button
              size="sm"
              onClick={openNewProjectModal}
              className="bg-red-600 hover:bg-red-700"
              data-testid="add-project-btn"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="flex gap-1 p-1 bg-slate-700 rounded">
            {['timeline', 'list'].map((mode) => (
              <Button
                key={mode}
                variant={viewMode === mode ? "secondary" : "ghost"}
                size="sm"
                onClick={() => setViewMode(mode)}
                className="flex-1 capitalize"
                data-testid={`view-${mode}-btn`}
              >
                {mode}
              </Button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <div className="space-y-2">
            {projects.map((project) => (
              <div
                key={project.id}
                className={`p-3 rounded cursor-pointer transition-colors group ${
                  selectedProject?.id === project.id
                    ? 'bg-slate-700 text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-700'
                }`}
                onClick={() => setSelectedProject(project)}
                data-testid={`project-item-${project.id}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium truncate">{project.title}</h4>
                  
                  <div className="opacity-0 group-hover:opacity-100 flex gap-1">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        openEditProjectModal(project);
                      }}
                      className="h-6 w-6 p-0 text-slate-400 hover:text-white"
                      data-testid={`edit-project-${project.id}`}
                    >
                      <Edit className="h-3 w-3" />
                    </Button>
                    
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={(e) => {
                        e.stopPropagation();
                        actions.setSelectedNode(project);
                      }}
                      className="h-6 w-6 p-0 text-blue-400 hover:text-blue-300"
                      data-testid={`link-project-${project.id}`}
                    >
                      <LinkIcon className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
                
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className={getStatusStyle(project.content.status)}>
                    {statusOptions.find(s => s.value === project.content.status)?.label}
                  </Badge>
                  
                  <Badge variant="outline" className={getStatusStyle(project.content.priority, 'priority')}>
                    {priorityOptions.find(p => p.value === project.content.priority)?.label}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>{getProjectTasks(project.id).length} tasks</span>
                  <span>{calculateProjectProgress(project)}% complete</span>
                </div>
                
                <div className="mt-2 w-full h-1 bg-slate-600 rounded-full">
                  <div
                    className="h-full bg-red-500 rounded-full transition-all"
                    style={{ width: `${calculateProjectProgress(project)}%` }}
                  />
                </div>
              </div>
            ))}
            
            {projects.length === 0 && (
              <div className="text-center text-slate-400 py-8">
                <Calendar className="h-8 w-8 mx-auto mb-2 text-slate-500" />
                <div className="text-sm">No projects</div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={openNewProjectModal}
                  className="mt-2"
                >
                  Create Project
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      {renderTimelineView()}

      {/* Project Modal */}
      <Dialog open={isProjectModalOpen} onOpenChange={setIsProjectModalOpen}>
        <DialogContent className="max-w-lg bg-slate-800 border-slate-700" data-testid="project-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Calendar className="h-5 w-5 text-red-400" />
              {selectedProject ? 'Edit Project' : 'New Project'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Project Name *
              </label>
              <Input
                placeholder="Enter project name..."
                value={projectForm.name}
                onChange={(e) => setProjectForm({ ...projectForm, name: e.target.value })}
                className="bg-slate-700 border-slate-600 text-white"
                data-testid="project-name-input"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Description
              </label>
              <textarea
                placeholder="Project description..."
                value={projectForm.description}
                onChange={(e) => setProjectForm({ ...projectForm, description: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2 resize-none"
                rows={3}
                data-testid="project-description-input"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Start Date
                </label>
                <Input
                  type="date"
                  value={projectForm.startDate}
                  onChange={(e) => setProjectForm({ ...projectForm, startDate: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="project-start-date-input"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  End Date
                </label>
                <Input
                  type="date"
                  value={projectForm.endDate}
                  onChange={(e) => setProjectForm({ ...projectForm, endDate: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="project-end-date-input"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Status
                </label>
                <select
                  value={projectForm.status}
                  onChange={(e) => setProjectForm({ ...projectForm, status: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                  data-testid="project-status-select"
                >
                  {statusOptions.map(status => (
                    <option key={status.value} value={status.value}>{status.label}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Priority
                </label>
                <select
                  value={projectForm.priority}
                  onChange={(e) => setProjectForm({ ...projectForm, priority: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                  data-testid="project-priority-select"
                >
                  {priorityOptions.map(priority => (
                    <option key={priority.value} value={priority.value}>{priority.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Manager
                </label>
                <Input
                  placeholder="Project manager..."
                  value={projectForm.manager}
                  onChange={(e) => setProjectForm({ ...projectForm, manager: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="project-manager-input"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Budget
                </label>
                <Input
                  placeholder="$0"
                  value={projectForm.budget}
                  onChange={(e) => setProjectForm({ ...projectForm, budget: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="project-budget-input"
                />
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <div>
                {selectedProject && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      deleteProject(selectedProject.id);
                      setIsProjectModalOpen(false);
                    }}
                    className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                    data-testid="delete-project-btn"
                  >
                    <Trash className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                )}
              </div>
              
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => setIsProjectModalOpen(false)}
                  data-testid="cancel-project-btn"
                >
                  Cancel
                </Button>
                <Button
                  onClick={saveProject}
                  disabled={!projectForm.name.trim()}
                  className="bg-red-600 hover:bg-red-700"
                  data-testid="save-project-btn"
                >
                  {selectedProject ? 'Update' : 'Create'} Project
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Task Modal */}
      <Dialog open={isTaskModalOpen} onOpenChange={setIsTaskModalOpen}>
        <DialogContent className="max-w-lg bg-slate-800 border-slate-700" data-testid="task-modal">
          <DialogHeader>
            <DialogTitle className="text-white flex items-center gap-2">
              <Clock className="h-5 w-5 text-blue-400" />
              {selectedTask ? 'Edit Task' : 'New Task'}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Task Name *
              </label>
              <Input
                placeholder="Enter task name..."
                value={taskForm.name}
                onChange={(e) => setTaskForm({ ...taskForm, name: e.target.value })}
                className="bg-slate-700 border-slate-600 text-white"
                data-testid="task-name-input"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Description
              </label>
              <textarea
                placeholder="Task description..."
                value={taskForm.description}
                onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2 resize-none"
                rows={3}
                data-testid="task-description-input"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-slate-300 mb-2 block">
                Project
              </label>
              <select
                value={taskForm.projectId}
                onChange={(e) => setTaskForm({ ...taskForm, projectId: e.target.value })}
                className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                data-testid="task-project-select"
              >
                <option value="">Select Project</option>
                {projects.map(project => (
                  <option key={project.id} value={project.id}>{project.title}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Start Date
                </label>
                <Input
                  type="date"
                  value={taskForm.startDate}
                  onChange={(e) => setTaskForm({ ...taskForm, startDate: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="task-start-date-input"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Due Date
                </label>
                <Input
                  type="date"
                  value={taskForm.endDate}
                  onChange={(e) => setTaskForm({ ...taskForm, endDate: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="task-end-date-input"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Status
                </label>
                <select
                  value={taskForm.status}
                  onChange={(e) => setTaskForm({ ...taskForm, status: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                  data-testid="task-status-select"
                >
                  {statusOptions.map(status => (
                    <option key={status.value} value={status.value}>{status.label}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Priority
                </label>
                <select
                  value={taskForm.priority}
                  onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}
                  className="w-full bg-slate-700 border border-slate-600 text-white rounded-md px-3 py-2"
                  data-testid="task-priority-select"
                >
                  {priorityOptions.map(priority => (
                    <option key={priority.value} value={priority.value}>{priority.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Assignee
                </label>
                <Input
                  placeholder="Assign to..."
                  value={taskForm.assignee}
                  onChange={(e) => setTaskForm({ ...taskForm, assignee: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="task-assignee-input"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium text-slate-300 mb-2 block">
                  Progress (%)
                </label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={taskForm.progress}
                  onChange={(e) => setTaskForm({ ...taskForm, progress: parseInt(e.target.value) || 0 })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="task-progress-input"
                />
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <div>
                {selectedTask && (
                  <Button
                    variant="outline"
                    onClick={() => {
                      deleteTask(selectedTask.id);
                      setIsTaskModalOpen(false);
                    }}
                    className="text-red-400 border-red-400 hover:bg-red-400 hover:text-white"
                    data-testid="delete-task-btn"
                  >
                    <Trash className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                )}
              </div>
              
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  onClick={() => setIsTaskModalOpen(false)}
                  data-testid="cancel-task-btn"
                >
                  Cancel
                </Button>
                <Button
                  onClick={saveTask}
                  disabled={!taskForm.name.trim()}
                  className="bg-blue-600 hover:bg-blue-700"
                  data-testid="save-task-btn"
                >
                  {selectedTask ? 'Update' : 'Create'} Task
                </Button>
              </div>
            </div>

            {selectedTask && (
              <div className="pt-2 border-t border-slate-700">
                <Button
                  variant="outline"
                  onClick={() => {
                    actions.setSelectedNode(selectedTask);
                    setIsTaskModalOpen(false);
                  }}
                  className="w-full text-blue-400 border-blue-400 hover:bg-blue-400 hover:text-white"
                  data-testid="link-task-btn"
                >
                  <LinkIcon className="h-4 w-4 mr-1" />
                  Link to Other Nodes
                </Button>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}