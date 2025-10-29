import React, { useState, useEffect } from 'react';
import { useAuth } from '../App';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Building2, 
  Package, 
  Users, 
  Activity,
  Plus,
  Settings,
  LogOut,
  TrendingUp,
  Shield,
  Database
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [organizations, setOrganizations] = useState([]);
  const [stats, setStats] = useState({
    totalOrganizations: 0,
    totalAssets: 0,
    recentActivity: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const orgsResponse = await axios.get(`${API}/organizations`);
      setOrganizations(orgsResponse.data);
      
      // Calculate stats
      let totalAssets = 0;
      for (const org of orgsResponse.data) {
        try {
          const assetsResponse = await axios.get(`${API}/organizations/${org.id}/assets`);
          totalAssets += assetsResponse.data.length;
        } catch (error) {
          console.error('Error fetching assets for org:', org.id, error);
        }
      }
      
      setStats({
        totalOrganizations: orgsResponse.data.length,
        totalAssets,
        recentActivity: [
          { action: 'System initialized', time: '2 minutes ago', type: 'info' },
          { action: 'Ready to manage assets', time: 'Just now', type: 'success' }
        ]
      });

      // Auto-redirect to assets page only on fresh login, not when manually navigating to dashboard
      const justLoggedIn = sessionStorage.getItem('justLoggedIn');
      if (justLoggedIn && orgsResponse.data.length > 0) {
        sessionStorage.removeItem('justLoggedIn'); // Clear the flag
        navigate(`/organizations/${orgsResponse.data[0].id}/assets`);
        return;
      }
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="container py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-900">IT Asset Manager</h1>
                <p className="text-sm text-slate-600">Dashboard</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-slate-600">
                <Shield className="w-4 h-4" />
                <span className="font-medium">{user?.name}</span>
                <span className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-medium capitalize">
                  {user?.role}
                </span>
              </div>
              
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-3 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                data-testid="logout-button"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="container py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-900 mb-2">
            Welcome back, {user?.name}!
          </h2>
          <p className="text-lg text-slate-600">
            Manage your IT assets across organizations with powerful tools and insights.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Organizations</p>
                <p className="text-3xl font-bold text-slate-900" data-testid="org-count">
                  {stats.totalOrganizations}
                </p>
              </div>
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center">
                <Building2 className="w-6 h-6 text-emerald-600" />
              </div>
            </div>
            <div className="flex items-center mt-4 text-sm text-emerald-600">
              <TrendingUp className="w-4 h-4 mr-1" />
              <span>Ready to manage</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Total Assets</p>
                <p className="text-3xl font-bold text-slate-900" data-testid="asset-count">
                  {stats.totalAssets}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Package className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="flex items-center mt-4 text-sm text-blue-600">
              <Activity className="w-4 h-4 mr-1" />
              <span>Across all orgs</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">Your Role</p>
                <p className="text-2xl font-bold text-slate-900 capitalize">
                  {user?.role}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="flex items-center mt-4 text-sm text-purple-600">
              <Shield className="w-4 h-4 mr-1" />
              <span>Access level</span>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Organizations Section */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-slate-900">Your Organizations</h3>
                <Link 
                  to="/organizations"
                  className="btn-primary flex items-center space-x-2"
                  data-testid="manage-orgs-button"
                >
                  <Settings className="w-4 h-4" />
                  <span>Manage Organizations</span>
                </Link>
              </div>
              
              {organizations.length === 0 ? (
                <div className="text-center py-12">
                  <Building2 className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                  <h4 className="text-lg font-medium text-slate-900 mb-2">No Organizations Yet</h4>
                  <p className="text-slate-600 mb-4">
                    Create your first organization to start managing IT assets.
                  </p>
                  <Link to="/organizations" className="btn-primary" data-testid="create-first-org">
                    Create Organization
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {organizations.map((org) => (
                    <div 
                      key={org.id}
                      className="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-200 hover:bg-slate-100 transition-colors"
                      data-testid={`org-item-${org.id}`}
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center">
                          <Building2 className="w-5 h-5 text-emerald-600" />
                        </div>
                        <div>
                          <h4 className="font-medium text-slate-900">{org.name}</h4>
                          <p className="text-sm text-slate-600">{org.description || 'No description'}</p>
                        </div>
                      </div>
                      <Link 
                        to={`/organizations/${org.id}/assets`}
                        className="btn-outline flex items-center space-x-2"
                        data-testid={`view-assets-${org.id}`}
                      >
                        <Package className="w-4 h-4" />
                        <span>View Assets</span>
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions & Activity */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Link 
                  to="/organizations"
                  className="flex items-center space-x-3 p-3 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors group"
                  data-testid="quick-create-org"
                >
                  <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
                    <Plus className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-900 group-hover:text-emerald-700">New Organization</p>
                    <p className="text-xs text-slate-600">Create and configure</p>
                  </div>
                </Link>
                
                <div className="flex items-center space-x-3 p-3 bg-slate-50 rounded-lg opacity-75">
                  <div className="w-8 h-8 bg-slate-400 rounded-lg flex items-center justify-center">
                    <Package className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-600">Add Assets</p>
                    <p className="text-xs text-slate-500">Select an organization first</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {stats.recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center space-x-3 text-sm">
                    <div className={`w-2 h-2 rounded-full ${
                      activity.type === 'success' ? 'bg-green-500' : 
                      activity.type === 'warning' ? 'bg-yellow-500' : 'bg-blue-500'
                    }`} />
                    <div className="flex-1">
                      <p className="text-slate-900">{activity.action}</p>
                      <p className="text-slate-500">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
