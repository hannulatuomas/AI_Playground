import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import '@/App.css';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { toast } from 'sonner';
import { Code, Globe, Youtube, GraduationCap, Lightbulb, Settings, Plus, Trash2, MessageSquare, Send, Cpu, Power, PowerOff, Key, Menu, X, Server, Database } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Prism from 'prismjs';
import 'prismjs/themes/prism-tomorrow.css';
// import APITesting from '@/components/APITesting';

import FileExplorer from '@/components/FileExplorer';
// Use Enhanced API Testing Component
import APITesting from '@/components/APITestingEnhanced';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AGENTS = [
  { 
    id: 'programming', 
    name: 'Code Assistant', 
    icon: Code, 
    color: 'from-blue-500 to-cyan-500', 
    description: 'Experienced Senior Developer: C#, C++, JS, TS, Python, Bash, PowerShell' 
  },
  { 
    id: 'website', 
    name: 'Web Builder', 
    icon: Globe, 
    color: 'from-purple-500 to-pink-500', 
    description: 'Experienced Senior Web/Full-Stack Developer: React, Next.js, Vue, Node.js' 
  },
  { 
    id: 'api-testing', 
    name: 'API Tester', 
    icon: Send, 
    color: 'from-indigo-500 to-purple-500', 
    description: 'Experienced Senior API Developer: REST, SOAP, GraphQL, WebSocket with AI' 
  },
  { 
    id: 'it-admin', 
    name: 'IT Assistant', 
    icon: Server, 
    color: 'from-cyan-500 to-blue-500', 
    description: 'Experienced Senior IT Administrator: Windows, Linux, Database Management' 
  },
  { 
    id: 'db-assistant', 
    name: 'DB Assistant', 
    icon: Database, 
    color: 'from-emerald-500 to-green-500', 
    description: 'Experienced Senior Database Expert: SQL, NoSQL, GraphDB, Data Analysis' 
  },
  { 
    id: 'learning', 
    name: 'Security Tutor', 
    icon: GraduationCap, 
    color: 'from-green-500 to-teal-500', 
    description: 'Experienced Cyber Security Professional: Ethical Hacking, Security Architecture' 
  },
  { 
    id: 'ideas', 
    name: 'Idea Generator', 
    icon: Lightbulb, 
    color: 'from-yellow-500 to-amber-500', 
    description: 'Experienced Senior Program Designer: AI-friendly project plans & architecture' 
  },
  { 
    id: 'prompt-engineering', 
    name: 'Prompt Expert', 
    icon: MessageSquare, 
    color: 'from-violet-500 to-purple-500', 
    description: 'AI Prompting & Optimization Specialist: GPT-4, Claude, Gemini' 
  },
  { 
    id: 'youtube', 
    name: 'Video Summarizer', 
    icon: Youtube, 
    color: 'from-red-500 to-orange-500', 
    description: 'AI Video Analysis: Summarize & extract insights from YouTube videos' 
  },
];

function Dashboard() {
  const navigate = useNavigate();
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);

  useEffect(() => {
    loadProviders();
  }, []);

  const loadProviders = async () => {
    try {
      const response = await axios.get(`${API}/providers`);
      setProviders(response.data);
      if (response.data.length > 0 && !selectedProvider) {
        setSelectedProvider(response.data[0].id);
      }
    } catch (error) {
      console.error('Failed to load providers:', error);
    }
  };

  const startChat = async (agentType) => {
    // Special handling for API Testing agent
    if (agentType === 'api-testing') {
      navigate('/api-testing');
      return;
    }
    
    // Check if there are any providers
    if (providers.length === 0) {
      toast.error('Please configure an LLM provider first');
      navigate('/settings');
      return;
    }
    
    // Use first provider if none selected
    const providerId = selectedProvider || providers[0]?.id;
    navigate(`/chat/${agentType}?provider=${providerId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none" />
      
      {/* Responsive Navigation */}
      <nav className="relative backdrop-blur-xl bg-white/5 border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-2 sm:gap-3" data-testid="home-link">
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <Code className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <h1 className="text-xl sm:text-2xl font-bold text-white">DevGenius AI</h1>
          </Link>
          <Link to="/settings">
            <Button 
              variant="ghost" 
              className="text-white hover:bg-white/10 h-9 w-9 sm:h-10 sm:w-10 p-0" 
              data-testid="settings-button"
            >
              <Settings className="w-4 h-4 sm:w-5 sm:h-5" />
            </Button>
          </Link>
        </div>
      </nav>

      {/* Responsive Main Content */}
      <main className="relative max-w-7xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
        {/* Hero Section */}
        <div className="text-center mb-10 sm:mb-16">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-3 sm:mb-4 px-2">
            Your AI Development Companion
          </h2>
          <p className="text-base sm:text-lg lg:text-xl text-slate-300 px-4">
            Professional AI tools with GPT-4, Claude, Gemini, and local llama.cpp models
          </p>
        </div>

        {/* Responsive Agent Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 lg:gap-6 mb-8 sm:mb-12">
          {AGENTS.map((agent) => {
            const Icon = agent.icon;
            return (
              <Card
                key={agent.id}
                className="group bg-white/5 backdrop-blur-xl border-white/10 hover:bg-white/10 transition-all duration-300 cursor-pointer hover:scale-[1.02] sm:hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/20 active:scale-[0.98]"
                onClick={() => startChat(agent.id)}
                data-testid={`agent-card-${agent.id}`}
              >
                <CardHeader className="p-4 sm:p-6">
                  <div className={`w-12 h-12 sm:w-16 sm:h-16 rounded-xl sm:rounded-2xl bg-gradient-to-br ${agent.color} flex items-center justify-center mb-3 sm:mb-4 group-hover:scale-110 transition-transform`}>
                    <Icon className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
                  </div>
                  <CardTitle className="text-white text-lg sm:text-xl lg:text-2xl">{agent.name}</CardTitle>
                  <CardDescription className="text-slate-300 text-sm sm:text-base">
                    {agent.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>

        {/* Quick Start Card */}
        <Card className="bg-white/5 backdrop-blur-xl border-white/10">
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="text-white flex items-center gap-2 text-lg sm:text-xl">
              <Cpu className="w-5 h-5 sm:w-6 sm:h-6" />
              Quick Start
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 sm:p-6 pt-0">
            <div className="space-y-2 sm:space-y-3 text-slate-300 text-sm sm:text-base">
              <p>• Configure your LLM providers with API keys in Settings</p>
              <p>• Supports OpenAI, Anthropic Claude, Google Gemini</p>
              <p>• Connect local llama.cpp server with custom endpoint</p>
              <p>• Each agent is specialized for different tasks</p>
              <p className="hidden sm:block">• Code Assistant can execute Python, JS, Bash, PowerShell</p>
              <p className="hidden sm:block">• API Tester supports REST, SOAP, GraphQL, WebSockets</p>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}

function ChatInterface() {
  const { agentType } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const messagesEndRef = useRef(null);
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showFileExplorer, setShowFileExplorer] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false); // Mobile sidebar state

  const agent = AGENTS.find(a => a.id === agentType);
  const Icon = agent?.icon || Code;

  useEffect(() => {
    loadProviders();
    loadConversations();
    loadProjects();
  }, [agentType]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (messages.length > 0) {
      Prism.highlightAll();
    }
  }, [messages]);

  const loadProviders = async () => {
    try {
      const response = await axios.get(`${API}/providers`);
      setProviders(response.data);
      const urlParams = new URLSearchParams(window.location.search);
      const providerId = urlParams.get('provider');
      setSelectedProvider(providerId || response.data[0]?.id);
    } catch (error) {
      console.error('Failed to load providers:', error);
    }
  };

  const loadConversations = async () => {
    try {
      const response = await axios.get(`${API}/conversations?agent_type=${agentType}`);
      setConversations(response.data);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadProjects = async () => {
    try {
      const response = await axios.get(`${API}/code-projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  };

  const loadConversation = async (convId) => {
    try {
      const response = await axios.get(`${API}/messages/${convId}`);
      setMessages(response.data);
      setConversationId(convId);
    } catch (error) {
      console.error('Failed to load messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    let streamingMessage = '';
    
    try {
      const response = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: input,
          provider_id: selectedProvider,
          agent_type: agentType,
          title: agent.name,
          project_id: selectedProject
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      // Add empty assistant message that we'll update
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            
            if (data.type === 'chunk') {
              streamingMessage += data.content;
              // Update the last message with streaming content
              setMessages(prev => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = { 
                  role: 'assistant', 
                  content: streamingMessage 
                };
                return newMessages;
              });
              
              if (data.conversation_id && !conversationId) {
                setConversationId(data.conversation_id);
                loadConversations();
              }
            } else if (data.type === 'done') {
              // Final update
              if (data.conversation_id && !conversationId) {
                setConversationId(data.conversation_id);
                loadConversations();
              }
            } else if (data.type === 'error') {
              toast.error(data.error);
            }
          } catch (e) {
            console.error('Parse error:', e);
          }
        }
      }

    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to send message');
      // Remove the empty assistant message on error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const newChat = () => {
    setMessages([]);
    setConversationId(null);
  };

  const deleteConversation = async (convId) => {
    try {
      await axios.delete(`${API}/conversations/${convId}`);
      loadConversations();
      if (convId === conversationId) {
        newChat();
      }
      toast.success('Conversation deleted');
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex relative">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none" />
      
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Sidebar - Responsive */}
      <div className={`
        fixed lg:relative z-50 lg:z-0
        w-80 backdrop-blur-xl bg-white/5 border-r border-white/10 flex flex-col
        transition-transform duration-300 ease-in-out
        h-full lg:h-auto
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Sidebar Header */}
        <div className="p-4 sm:p-6 border-b border-white/10">
          <div className="flex items-center justify-between mb-4 lg:mb-6">
            <Link to="/" className="flex items-center gap-2 sm:gap-3 flex-1" data-testid="back-to-home">
              <div className={`w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center`}>
                <Icon className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <h2 className="text-lg sm:text-xl font-bold text-white truncate">{agent.name}</h2>
            </Link>
            <Button 
              variant="ghost" 
              className="lg:hidden text-white hover:bg-white/10 h-8 w-8 p-0"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
          <Button 
            onClick={newChat} 
            className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-sm sm:text-base h-9 sm:h-10" 
            data-testid="new-chat-button"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Chat
          </Button>
        </div>

        {/* Conversations List */}
        <ScrollArea className="flex-1 p-3 sm:p-4">
          <div className="space-y-2">
            {conversations.map(conv => (
              <div
                key={conv.id}
                className={`group flex items-center justify-between p-2 sm:p-3 rounded-lg cursor-pointer transition-all ${
                  conv.id === conversationId ? 'bg-white/20' : 'bg-white/5 hover:bg-white/10'
                }`}
                data-testid={`conversation-${conv.id}`}
              >
                <div className="flex-1 min-w-0" onClick={() => {
                  loadConversation(conv.id);
                  setSidebarOpen(false); // Close sidebar on mobile after selecting
                }}>
                  <p className="text-white text-sm truncate">{conv.title}</p>
                  <p className="text-slate-400 text-xs">
                    {new Date(conv.updated_at).toLocaleDateString()}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 hover:bg-red-500/20 h-8 w-8 p-0"
                  onClick={() => deleteConversation(conv.id)}
                  data-testid={`delete-conversation-${conv.id}`}
                >
                  <Trash2 className="w-3 h-3 sm:w-4 sm:h-4" />
                </Button>
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Chat Area */}
      <div className="relative flex-1 flex flex-col w-full lg:w-auto">
        {/* Mobile Header with Hamburger */}
        <div className="backdrop-blur-xl bg-white/5 border-b border-white/10 p-3 sm:p-4 lg:p-6">
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Hamburger Menu Button - Mobile Only */}
            <Button
              variant="ghost"
              className="lg:hidden text-white hover:bg-white/10 h-9 w-9 p-0 flex-shrink-0"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="w-5 h-5" />
            </Button>
            
            <h1 className="text-base sm:text-lg lg:text-2xl font-bold text-white flex-1 truncate">
              {agent.description}
            </h1>
            
            {/* Responsive Controls */}
            <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
              {agentType === 'programming' && (
                <>
                  <Select 
                    value={selectedProject || 'none'} 
                    onValueChange={(val) => setSelectedProject(val === 'none' ? null : val)}
                  >
                    <SelectTrigger className="w-24 sm:w-32 lg:w-48 bg-white/10 border-white/20 text-white text-xs sm:text-sm h-9" data-testid="project-select">
                      <SelectValue placeholder="Project" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">No project</SelectItem>
                      {projects.map(p => (
                        <SelectItem key={p.id} value={p.id}>{p.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button
                    variant={showFileExplorer ? "default" : "outline"}
                    onClick={() => setShowFileExplorer(!showFileExplorer)}
                    className={`h-9 px-2 sm:px-3 text-xs sm:text-sm ${showFileExplorer ? "bg-blue-500" : "border-white/20 text-white"}`}
                    data-testid="toggle-file-explorer"
                  >
                    <Code className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">Files</span>
                  </Button>
                </>
              )}
              <Select value={selectedProvider} onValueChange={setSelectedProvider}>
                <SelectTrigger className="w-24 sm:w-32 lg:w-48 bg-white/10 border-white/20 text-white text-xs sm:text-sm h-9" data-testid="provider-select">
                  <SelectValue placeholder="Model" />
                </SelectTrigger>
                <SelectContent>
                  {providers.map(p => (
                    <SelectItem key={p.id} value={p.id}>
                      <span className="hidden sm:inline">{p.name} - </span>{p.model}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <ScrollArea className="flex-1 p-3 sm:p-4 lg:p-6">
          <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
            {messages.length === 0 && (
              <div className="text-center py-12 sm:py-20">
                <Icon className="w-16 h-16 sm:w-20 sm:h-20 mx-auto text-slate-600 mb-4" />
                <p className="text-slate-400 text-base sm:text-lg px-4">Start a conversation with {agent.name}</p>
                {agentType === 'programming' && (
                  <p className="text-slate-500 text-xs sm:text-sm mt-2 px-4">Tip: Select a project to give the AI access to your codebase</p>
                )}
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex gap-2 sm:gap-4 ${
                  msg.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
                data-testid={`message-${idx}`}
              >
                <div
                  className={`max-w-[85%] sm:max-w-[80%] rounded-xl sm:rounded-2xl p-3 sm:p-4 ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-br from-blue-500 to-cyan-500 text-white'
                      : 'bg-white/10 backdrop-blur-xl text-white border border-white/10'
                  }`}
                >
                  {msg.role === 'assistant' ? (
                    <div className="prose prose-invert max-w-none prose-sm sm:prose-base">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          code({node, inline, className, children, ...props}) {
                            const match = /language-(\w+)/.exec(className || '');
                            return !inline && match ? (
                              <pre className={className}>
                                <code className={className} {...props}>
                                  {children}
                                </code>
                              </pre>
                            ) : (
                              <code className="bg-slate-800 px-1 rounded text-xs sm:text-sm" {...props}>
                                {children}
                              </code>
                            );
                          }
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap text-sm sm:text-base">{msg.content}</p>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        </ScrollArea>

        {/* Message Input - Mobile Optimized */}
        <div className="backdrop-blur-xl bg-white/5 border-t border-white/10 p-3 sm:p-4 lg:p-6">
          <div className="max-w-4xl mx-auto flex gap-2 sm:gap-4">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
              placeholder="Type your message..."
              className="flex-1 bg-white/10 border-white/20 text-white placeholder:text-slate-400 text-sm sm:text-base h-10 sm:h-11"
              disabled={loading}
              data-testid="message-input"
            />
            <Button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 h-10 w-10 sm:h-11 sm:w-11 p-0 flex-shrink-0"
              data-testid="send-button"
            >
              <Send className="w-4 h-4 sm:w-5 sm:h-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* File Explorer Sidebar - Responsive */}
      {showFileExplorer && selectedProject && agentType === 'programming' && (
        <div className="hidden lg:block relative w-96 backdrop-blur-xl bg-white/5 border-l border-white/10">
          <FileExplorer 
            projectId={selectedProject} 
            onProjectChange={loadProjects}
          />
        </div>
      )}
    </div>
  );
}

function SettingsPage() {
  const [providers, setProviders] = useState([]);
  const [localModels, setLocalModels] = useState([]);
  const [showProviderDialog, setShowProviderDialog] = useState(false);
  const [showModelDialog, setShowModelDialog] = useState(false);
  const [newProvider, setNewProvider] = useState({ name: 'OpenAI', model: 'gpt-4', api_key: '', endpoint: '', is_active: true });
  const [newModel, setNewModel] = useState({ name: '', endpoint: 'http://localhost:8080', context_size: 2048 });

  useEffect(() => {
    loadProviders();
    loadLocalModels();
  }, []);

  const loadProviders = async () => {
    try {
      const response = await axios.get(`${API}/providers`);
      setProviders(response.data);
    } catch (error) {
      console.error('Failed to load providers:', error);
    }
  };

  const loadLocalModels = async () => {
    try {
      const response = await axios.get(`${API}/local-models`);
      setLocalModels(response.data);
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const addProvider = async () => {
    try {
      await axios.post(`${API}/providers`, newProvider);
      loadProviders();
      setShowProviderDialog(false);
      setNewProvider({ name: 'OpenAI', model: 'gpt-4', api_key: '', endpoint: '', is_active: true });
      toast.success('Provider added successfully');
    } catch (error) {
      console.error('Failed to add provider:', error);
      toast.error('Failed to add provider');
    }
  };

  const deleteProvider = async (id) => {
    try {
      await axios.delete(`${API}/providers/${id}`);
      loadProviders();
      toast.success('Provider deleted');
    } catch (error) {
      console.error('Failed to delete provider:', error);
    }
  };

  const addLocalModel = async () => {
    try {
      await axios.post(`${API}/local-models`, newModel);
      loadLocalModels();
      setShowModelDialog(false);
      setNewModel({ name: '', endpoint: 'http://localhost:8080', context_size: 2048 });
      toast.success('Model added successfully');
    } catch (error) {
      console.error('Failed to add model:', error);
      toast.error('Failed to add model');
    }
  };

  const testLocalModel = async (id) => {
    try {
      const response = await axios.get(`${API}/local-models/${id}/test`);
      if (response.data.status === 'connected') {
        toast.success(response.data.message);
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error('Failed to connect to model');
    }
  };

  const deleteLocalModel = async (id) => {
    try {
      await axios.delete(`${API}/local-models/${id}`);
      loadLocalModels();
      toast.success('Model deleted');
    } catch (error) {
      console.error('Failed to delete model:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-900/20 via-transparent to-transparent pointer-events-none" />
      
      <nav className="relative backdrop-blur-xl bg-white/5 border-b border-white/10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-3" data-testid="home-link">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <Code className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white">DevGenius AI</h1>
          </Link>
        </div>
      </nav>

      <main className="relative max-w-7xl mx-auto px-6 py-12">
        <h2 className="text-4xl font-bold text-white mb-8">Settings</h2>

        <Tabs defaultValue="providers" className="space-y-6">
          <TabsList className="bg-white/5 backdrop-blur-xl border border-white/10">
            <TabsTrigger value="providers" className="data-[state=active]:bg-white/20" data-testid="providers-tab">
              <Key className="w-4 h-4 mr-2" />
              LLM Providers
            </TabsTrigger>
            <TabsTrigger value="local" className="data-[state=active]:bg-white/20" data-testid="local-models-tab">
              <Cpu className="w-4 h-4 mr-2" />
              Local Models
            </TabsTrigger>
          </TabsList>

          <TabsContent value="providers">
            <Card className="bg-white/5 backdrop-blur-xl border-white/10">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-white">API Providers</CardTitle>
                    <CardDescription className="text-slate-300">
                      Configure your LLM providers (OpenAI, Claude, Google)
                    </CardDescription>
                  </div>
                  <Dialog open={showProviderDialog} onOpenChange={setShowProviderDialog}>
                    <DialogTrigger asChild>
                      <Button className="bg-gradient-to-r from-blue-500 to-cyan-500" data-testid="add-provider-button">
                        <Plus className="w-4 h-4 mr-2" />
                        Add Provider
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-slate-900 border-white/10 max-w-md z-[100]">
                      <DialogHeader>
                        <DialogTitle className="text-white">Add LLM Provider</DialogTitle>
                        <DialogDescription className="text-slate-300">
                          Add API provider with your API key
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 mt-4">
                        <div>
                          <Label className="text-white mb-2 block">Provider</Label>
                          <Select value={newProvider.name} onValueChange={(v) => setNewProvider({...newProvider, name: v})}>
                            <SelectTrigger className="bg-white/10 border-white/20 text-white" data-testid="provider-name-select">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent className="bg-slate-800 border-white/20 z-[200]">
                              <SelectItem value="OpenAI" className="text-white hover:bg-white/10">OpenAI</SelectItem>
                              <SelectItem value="Claude" className="text-white hover:bg-white/10">Anthropic Claude</SelectItem>
                              <SelectItem value="Google" className="text-white hover:bg-white/10">Google Gemini</SelectItem>
                              <SelectItem value="Local" className="text-white hover:bg-white/10">Local (llama.cpp)</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label className="text-white mb-2 block">Model</Label>
                          <Input
                            value={newProvider.model}
                            onChange={(e) => setNewProvider({...newProvider, model: e.target.value})}
                            placeholder="e.g., gpt-4, claude-3-opus-20240229, gemini-pro"
                            className="bg-white/10 border-white/20 text-white placeholder:text-slate-500"
                            data-testid="provider-model-input"
                          />
                        </div>
                        <div>
                          <Label className="text-white mb-2 block">API Key {newProvider.name === 'Local' ? '(Optional for Local)' : '(Required)'}</Label>
                          <Input
                            type="password"
                            value={newProvider.api_key}
                            onChange={(e) => setNewProvider({...newProvider, api_key: e.target.value})}
                            placeholder={newProvider.name === 'Local' ? 'Not required for local' : 'Enter your API key'}
                            className="bg-white/10 border-white/20 text-white placeholder:text-slate-500"
                            data-testid="provider-api-key-input"
                          />
                        </div>
                        {newProvider.name === 'Local' && (
                          <div>
                            <Label className="text-white mb-2 block">Endpoint</Label>
                            <Input
                              value={newProvider.endpoint || ''}
                              onChange={(e) => setNewProvider({...newProvider, endpoint: e.target.value})}
                              placeholder="http://localhost:8080"
                              className="bg-white/10 border-white/20 text-white placeholder:text-slate-500"
                              data-testid="provider-endpoint-input"
                            />
                          </div>
                        )}
                        <Button onClick={addProvider} className="w-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600" data-testid="save-provider-button">
                          Save Provider
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {providers.length === 0 && (
                    <p className="text-slate-400 text-center py-8">No providers configured. Add one to get started.</p>
                  )}
                  {providers.map(provider => (
                    <div
                      key={provider.id}
                      className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10"
                      data-testid={`provider-${provider.id}`}
                    >
                      <div>
                        <h3 className="text-white font-semibold">{provider.name}</h3>
                        <p className="text-slate-400 text-sm">{provider.model}</p>
                        <p className="text-slate-500 text-xs mt-1">
                          {provider.endpoint ? `Endpoint: ${provider.endpoint}` : 'API Key configured'}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteProvider(provider.id)}
                        className="text-red-400 hover:text-red-300 hover:bg-red-500/20"
                        data-testid={`delete-provider-${provider.id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="local">
            <Card className="bg-white/5 backdrop-blur-xl border-white/10">
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="text-white">Local Models (llama.cpp)</CardTitle>
                    <CardDescription className="text-slate-300">
                      Configure llama.cpp server endpoints
                    </CardDescription>
                  </div>
                  <Dialog open={showModelDialog} onOpenChange={setShowModelDialog}>
                    <DialogTrigger asChild>
                      <Button className="bg-gradient-to-r from-purple-500 to-pink-500" data-testid="add-model-button">
                        <Plus className="w-4 h-4 mr-2" />
                        Add Model
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="bg-slate-900 border-white/10 max-w-md z-[100]">
                      <DialogHeader>
                        <DialogTitle className="text-white">Add Local Model</DialogTitle>
                        <DialogDescription className="text-slate-300">
                          Connect to your llama.cpp server
                        </DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4 mt-4">
                        <div>
                          <Label className="text-white mb-2 block">Model Name</Label>
                          <Input
                            value={newModel.name}
                            onChange={(e) => setNewModel({...newModel, name: e.target.value})}
                            placeholder="e.g., Llama 3.3 70B"
                            className="bg-white/10 border-white/20 text-white placeholder:text-slate-500"
                            data-testid="model-name-input"
                          />
                        </div>
                        <div>
                          <Label className="text-white mb-2 block">Server Endpoint</Label>
                          <Input
                            value={newModel.endpoint}
                            onChange={(e) => setNewModel({...newModel, endpoint: e.target.value})}
                            placeholder="http://localhost:8080"
                            className="bg-white/10 border-white/20 text-white placeholder:text-slate-500"
                            data-testid="model-endpoint-input"
                          />
                        </div>
                        <div>
                          <Label className="text-white mb-2 block">Context Size (Optional)</Label>
                          <Input
                            type="number"
                            value={newModel.context_size}
                            onChange={(e) => setNewModel({...newModel, context_size: parseInt(e.target.value) || 2048})}
                            placeholder="2048"
                            className="bg-white/10 border-white/20 text-white placeholder:text-slate-500"
                            data-testid="model-context-input"
                          />
                        </div>
                        <Button onClick={addLocalModel} className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600" data-testid="save-model-button">
                          Save Model
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {localModels.length === 0 && (
                    <p className="text-slate-400 text-center py-8">No local models configured.</p>
                  )}
                  {localModels.map(model => (
                    <div
                      key={model.id}
                      className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10"
                      data-testid={`local-model-${model.id}`}
                    >
                      <div className="flex-1">
                        <h3 className="text-white font-semibold">{model.name}</h3>
                        <p className="text-slate-400 text-sm">{model.endpoint}</p>
                        <p className="text-slate-500 text-xs mt-1">Context: {model.context_size || 2048}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => testLocalModel(model.id)}
                          className="text-blue-400 hover:bg-blue-500/20"
                          data-testid={`test-model-${model.id}`}
                        >
                          Test
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteLocalModel(model.id)}
                          className="text-red-400 hover:text-red-300 hover:bg-red-500/20"
                          data-testid={`delete-model-${model.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/chat/:agentType" element={<ChatInterface />} />
        <Route path="/api-testing" element={<APITesting />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
