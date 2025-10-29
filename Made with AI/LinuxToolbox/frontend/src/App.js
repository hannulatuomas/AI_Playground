import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

// Import components
import { Navbar } from './components/Navbar';
import { AuthModal } from './components/AuthModal';
import { SearchBar } from './components/SearchBar';
import { CommandCard } from './components/CommandCard';
import { CommandModal } from './components/CommandModal';
import { CategoryFilter } from './components/CategoryFilter';
import { CategoryFilterDropdown } from './components/CategoryFilterDropdown';
import { LoadingSpinner } from './components/LoadingSpinner';
import { AdvancedSearch } from './components/AdvancedSearch';
import { Pagination } from './components/Pagination';
import { useToast } from './hooks/use-toast';
import { useDebounce } from './hooks/useDebounce';
import { Toaster } from './components/ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Set up axios defaults
axios.defaults.baseURL = API;

function App() {
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showCommandModal, setShowCommandModal] = useState(false);
  const [commands, setCommands] = useState([]);
  const [filteredCommands, setFilteredCommands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [advancedSearchResults, setAdvancedSearchResults] = useState([]);
  
  // Debounced search query for real-time filtering
  const debouncedSearchQuery = useDebounce(searchQuery, 300);
  const [selectedCommand, setSelectedCommand] = useState(null);
  const [editingCommand, setEditingCommand] = useState(null);
  const [showAdvancedSearch, setShowAdvancedSearch] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12); // 12 commands per page (4 rows of 3)
  const { toast } = useToast();

  // Initialize app
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUserProfile();
    }
    fetchCommands();
    fetchCategories();
    fetchTags();
  }, []);

  // Filter commands when search/category changes (debounced)
  useEffect(() => {
    filterCommands();
    setCurrentPage(1); // Reset to first page when filtering
  }, [commands, debouncedSearchQuery, selectedCategories, selectedCategory, advancedSearchResults]);

  const fetchUserProfile = async () => {
    try {
      const response = await axios.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const fetchCommands = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/commands?limit=1000'); // Fetch all commands
      setCommands(response.data);
    } catch (error) {
      console.error('Failed to fetch commands:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch commands',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get('/categories-with-subcategories');
      setCategories(response.data.categories);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
      // Fallback to legacy categories endpoint
      try {
        const fallbackResponse = await axios.get('/categories');
        const legacyCategories = fallbackResponse.data.categories.map(cat => ({
          category: cat,
          subcategories: []
        }));
        setCategories(legacyCategories);
      } catch (fallbackError) {
        console.error('Failed to fetch legacy categories:', fallbackError);
      }
    }
  };

  const fetchTags = async () => {
    try {
      const response = await axios.get('/tags');
      setTags(response.data.tags);
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    }
  };

  const filterCommands = () => {
    let filtered = commands;

    // Apply Advanced Search filters first if they exist
    if (advancedSearchResults.length > 0) {
      filtered = advancedSearchResults;
    }

    // Filter by multiple categories (new multiselect system)
    if (selectedCategories.length > 0 && !selectedCategories.includes('all')) {
      filtered = filtered.filter(cmd => {
        return selectedCategories.some(selectedCat => {
          // Handle subcategory selection (e.g., "File Management > Permissions")
          if (selectedCat.includes(' > ')) {
            const [mainCat, subCat] = selectedCat.split(' > ');
            return cmd.category.toLowerCase() === mainCat.toLowerCase();
          }
          // Handle main category selection
          return cmd.category.toLowerCase() === selectedCat.toLowerCase();
        });
      });
    }
    
    // Legacy category filter (for backwards compatibility)
    if (selectedCategory !== 'all' && selectedCategories.length === 0) {
      filtered = filtered.filter(cmd => 
        cmd.category.toLowerCase() === selectedCategory.toLowerCase()
      );
    }

    // Filter by search query (debounced)
    if (debouncedSearchQuery) {
      const query = debouncedSearchQuery.toLowerCase();
      filtered = filtered.filter(cmd =>
        cmd.name.toLowerCase().includes(query) ||
        cmd.description.toLowerCase().includes(query) ||
        cmd.syntax.toLowerCase().includes(query) ||
        cmd.examples.some(example => example.toLowerCase().includes(query)) ||
        cmd.tags.some(tag => tag.toLowerCase().includes(query))
      );
    }

    setFilteredCommands(filtered);
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    if (query.trim()) {
      setLoading(true);
      try {
        const params = {
          query: query,
          limit: 50
        };
        if (selectedCategory !== 'all') {
          params.category = selectedCategory;
        }
        
        const response = await axios.post('/commands/search', null, { params });
        setCommands(response.data);
      } catch (error) {
        console.error('Search failed, using client-side filter:', error);
        // Fallback to client-side search
        try {
          const allCommands = await axios.get('/commands');
          const filtered = allCommands.data.filter(cmd =>
            cmd.name.toLowerCase().includes(query.toLowerCase()) ||
            cmd.description.toLowerCase().includes(query.toLowerCase()) ||
            cmd.syntax.toLowerCase().includes(query.toLowerCase()) ||
            cmd.examples.some(example => example.toLowerCase().includes(query.toLowerCase())) ||
            cmd.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
          );
          setCommands(filtered);
        } catch (fallbackError) {
          console.error('Fallback search also failed:', fallbackError);
          toast({
            title: 'Search Error',
            description: 'Failed to search commands',
            variant: 'destructive',
          });
        }
      } finally {
        setLoading(false);
      }
    } else {
      fetchCommands();
    }
  };

  const handleLogin = async (credentials) => {
    try {
      const response = await axios.post('/auth/login', credentials);
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(userData);
      setShowAuthModal(false);
      
      toast({
        title: 'Success',
        description: `Welcome back, ${userData.username}!`,
      });
      
      fetchCommands(); // Refresh to show user's commands
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      toast({
        title: 'Login Error',
        description: message,
        variant: 'destructive',
      });
    }
  };

  const handleRegister = async (userData) => {
    try {
      const response = await axios.post('/auth/register', userData);
      const { access_token, user: newUser } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(newUser);
      setShowAuthModal(false);
      
      toast({
        title: 'Success',
        description: `Welcome, ${newUser.username}!`,
      });
      
      fetchCommands();
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed';
      toast({
        title: 'Registration Error',
        description: message,
        variant: 'destructive',
      });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    fetchCommands(); // Refresh to hide private commands
    toast({
      title: 'Logged out',
      description: 'You have been successfully logged out',
    });
  };

  const handleCreateCommand = async (commandData) => {
    try {
      await axios.post('/commands', commandData);
      setShowCommandModal(false);
      fetchCommands();
      fetchCategories();
      fetchTags();
      toast({
        title: 'Success',
        description: 'Command created successfully!',
      });
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to create command';
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      });
    }
  };

  const handleUpdateCommand = async (commandId, commandData) => {
    try {
      await axios.put(`/commands/${commandId}`, commandData);
      setShowCommandModal(false);
      setEditingCommand(null);
      fetchCommands();
      fetchCategories();
      fetchTags();
      toast({
        title: 'Success',
        description: 'Command updated successfully!',
      });
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to update command';
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      });
    }
  };

  const handleDeleteCommand = async (commandId) => {
    if (!window.confirm('Are you sure you want to delete this command?')) {
      return;
    }

    try {
      await axios.delete(`/commands/${commandId}`);
      fetchCommands();
      fetchCategories();
      fetchTags();
      toast({
        title: 'Success',
        description: 'Command deleted successfully!',
      });
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to delete command';
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      });
    }
  };

  const handleCategoryChange = (newSelectedCategories) => {
    setSelectedCategories(newSelectedCategories);
    setCurrentPage(1); // Reset to first page when filtering
  };

  const handleAdvancedSearch = async (filters) => {
    if (!filters) {
      // Reset Advanced Search - clear results so main filters take over
      setAdvancedSearchResults([]);
      return;
    }

    setLoading(true);
    try {
      let searchResults = [];
      
      if (filters.query) {
        // Use backend search if there's a query
        const params = {
          query: filters.query,
          limit: 1000
        };
        
        const response = await axios.post('/commands/search', null, { params });
        searchResults = response.data;
      } else {
        // Get all commands for filtering
        const response = await axios.get('/commands');
        searchResults = response.data;
      }

      // Apply additional client-side filtering
      let filtered = searchResults;

      // Filter by search type
      if (filters.query && filters.searchType !== 'all') {
        const query = filters.exactMatch ? filters.query : filters.query.toLowerCase();
        filtered = filtered.filter(cmd => {
          const getValue = (field) => filters.exactMatch ? cmd[field] : cmd[field].toLowerCase();
          
          switch (filters.searchType) {
            case 'name':
              return getValue('name').includes(query);
            case 'description':
              return getValue('description').includes(query);
            case 'examples':
              return cmd.examples.some(ex => 
                filters.exactMatch ? ex.includes(query) : ex.toLowerCase().includes(query)
              );
            case 'tags':
              return cmd.tags.some(tag => 
                filters.exactMatch ? tag.includes(query) : tag.toLowerCase().includes(query)
              );
            default:
              return true;
          }
        });
      }

      // Filter by tags (Advanced Search tags)
      if (filters.selectedTags.length > 0) {
        filtered = filtered.filter(cmd => 
          filters.selectedTags.some(tag => cmd.tags.includes(tag))
        );
      }

      // Store Advanced Search results - filterCommands() will combine with category filters
      setAdvancedSearchResults(filtered);
      setCurrentPage(1); // Reset to first page
    } catch (error) {
      console.error('Advanced search failed:', error);
      toast({
        title: 'Search Error',
        description: 'Advanced search failed. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCommand = async (commandId) => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    try {
      await axios.post('/saved-commands', { command_id: commandId });
      toast({
        title: 'Success',
        description: 'Command saved to your collection!',
      });
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to save command';
      toast({
        title: 'Error',
        description: message,
        variant: 'destructive',
      });
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        <Navbar
          user={user}
          onLogin={() => setShowAuthModal(true)}
          onLogout={handleLogout}
          onAddCommand={() => {
            if (!user) {
              setShowAuthModal(true);
              return;
            }
            setEditingCommand(null);
            setShowCommandModal(true);
          }}
        />
        
        <main className="container mx-auto px-6 py-8">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4 font-['Space_Grotesk']">
              Linux Admin Toolbox
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Your comprehensive database of Linux commands, tools, and examples.
              Search, learn, and master system administration.
            </p>
            
            <SearchBar 
              onSearch={handleSearch} 
              placeholder="Search commands, descriptions, examples..." 
              value={searchQuery}
              onChange={setSearchQuery}
            />
          </div>

          {/* Advanced Search */}
          <div className="mb-6">
            <AdvancedSearch
              onSearch={handleAdvancedSearch}
              categories={categories.map(cat => cat.category || cat)}
              tags={tags}
              isOpen={showAdvancedSearch}
              onToggle={() => setShowAdvancedSearch(!showAdvancedSearch)}
            />
          </div>

          {/* Filters */}
          <div className="mb-8">
            <CategoryFilterDropdown
              categories={categories}
              selectedCategories={selectedCategories}
              onCategoryChange={handleCategoryChange}
            />
          </div>

          {/* Commands Grid */}
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <LoadingSpinner />
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCommands
                  .slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
                  .map((command) => (
                    <CommandCard
                      key={command.id}
                      command={command}
                      user={user}
                      onView={() => setSelectedCommand(command)}
                      onEdit={() => {
                        setEditingCommand(command);
                        setShowCommandModal(true);
                      }}
                      onDelete={() => handleDeleteCommand(command.id)}
                      onSave={() => handleSaveCommand(command.id)}
                    />
                  ))}
              </div>

              {/* Pagination */}
              <Pagination
                currentPage={currentPage}
                totalItems={filteredCommands.length}
                itemsPerPage={itemsPerPage}
                onPageChange={(page) => {
                  setCurrentPage(page);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
              />
            </>
          )}

          {filteredCommands.length === 0 && !loading && (
            <div className="text-center py-12">
              <div className="text-gray-500 text-lg">
                {debouncedSearchQuery || selectedCategories.length > 0 || selectedCategory !== 'all' 
                  ? 'No commands found matching your criteria.'
                  : 'No commands available. Be the first to add one!'
                }
              </div>
            </div>
          )}
        </main>

        {/* Modals */}
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          onLogin={handleLogin}
          onRegister={handleRegister}
        />

        <CommandModal
          isOpen={showCommandModal}
          onClose={() => {
            setShowCommandModal(false);
            setEditingCommand(null);
          }}
          onSubmit={editingCommand ? 
            (data) => handleUpdateCommand(editingCommand.id, data) : 
            handleCreateCommand
          }
          initialData={editingCommand}
          categories={categories.map(cat => cat.category || cat)}
          tags={tags}
        />

        {selectedCommand && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedCommand(null)}
          >
            <div 
              className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={e => e.stopPropagation()}
            >
              <CommandCard
                command={selectedCommand}
                user={user}
                detailed={true}
                onEdit={() => {
                  setEditingCommand(selectedCommand);
                  setShowCommandModal(true);
                  setSelectedCommand(null);
                }}
                onDelete={() => {
                  handleDeleteCommand(selectedCommand.id);
                  setSelectedCommand(null);
                }}
                onSave={() => handleSaveCommand(selectedCommand.id)}
                onClose={() => setSelectedCommand(null)}
              />
            </div>
          </div>
        )}

        <Toaster />
      </div>
    </Router>
  );
}

export default App;
