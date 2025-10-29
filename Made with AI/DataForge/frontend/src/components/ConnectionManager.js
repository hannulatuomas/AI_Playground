import { useState } from 'react';
import axios from 'axios';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Plus, Trash2, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function ConnectionManager({ connections, onConnectionCreated, onConnectionDeleted }) {
  const [showDialog, setShowDialog] = useState(false);
  const [testingConnection, setTestingConnection] = useState(null);
  const [useConnectionString, setUseConnectionString] = useState(false);
  const [connectionData, setConnectionData] = useState({
    name: '',
    db_type: 'postgresql',
    host: '',
    port: '',
    database: '',
    username: '',
    password: '',
    file_path: '',
    connection_string: ''
  });

  const dbTypes = [
    { value: 'postgresql', label: 'PostgreSQL', defaultPort: 5432 },
    { value: 'mysql', label: 'MySQL', defaultPort: 3306 },
    { value: 'mongodb', label: 'MongoDB', defaultPort: 27017 },
    { value: 'sqlite', label: 'SQLite', defaultPort: null },
    { value: 'mssql', label: 'MS SQL Server', defaultPort: 1433 }
  ];

  const handleDbTypeChange = (type) => {
    const dbType = dbTypes.find(db => db.value === type);
    setConnectionData({
      ...connectionData,
      db_type: type,
      port: dbType.defaultPort || '',
      connection_string: '',
      host: '',
      database: '',
      username: '',
      password: '',
      file_path: ''
    });
    // Reset connection string toggle for SQLite and MongoDB
    if (type === 'sqlite') {
      setUseConnectionString(false);
    } else if (type === 'mongodb') {
      setUseConnectionString(true);
    }
  };

  const handleTestConnection = async () => {
    setTestingConnection('testing');
    try {
      const response = await axios.post(`${API}/connections/test`, connectionData);
      if (response.data.status === 'success') {
        setTestingConnection('success');
        toast.success('Connection successful!');
      } else {
        setTestingConnection('error');
        toast.error(response.data.message || 'Connection failed');
      }
    } catch (error) {
      setTestingConnection('error');
      toast.error(error.response?.data?.message || 'Connection test failed');
    }
  };

  const handleCreateConnection = async () => {
    try {
      const response = await axios.post(`${API}/connections`, connectionData);
      onConnectionCreated(response.data);
      setShowDialog(false);
      setConnectionData({
        name: '',
        db_type: 'postgresql',
        host: '',
        port: '',
        database: '',
        username: '',
        password: '',
        file_path: '',
        connection_string: ''
      });
      setTestingConnection(null);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create connection');
    }
  };

  const handleDeleteConnection = async (connectionId) => {
    if (!window.confirm('Are you sure you want to delete this connection?')) return;
    
    try {
      await axios.delete(`${API}/connections/${connectionId}`);
      onConnectionDeleted();
    } catch (error) {
      toast.error('Failed to delete connection');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Database Connections</h2>
          <p className="text-slate-600 dark:text-slate-400 mt-2">Manage your database connections</p>
        </div>
        <Dialog open={showDialog} onOpenChange={setShowDialog}>
          <DialogTrigger asChild>
            <Button className="bg-cyan-600 hover:bg-cyan-700" data-testid="add-connection-button">
              <Plus className="w-4 h-4 mr-2" />
              Add Connection
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-800 border-slate-700 text-white max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-2xl">Create Database Connection</DialogTitle>
              <DialogDescription className="text-slate-400">
                Configure your database connection details
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4 mt-4">
              <div>
                <Label className="text-slate-300">Connection Name</Label>
                <Input
                  placeholder="My Database"
                  value={connectionData.name}
                  onChange={(e) => setConnectionData({ ...connectionData, name: e.target.value })}
                  className="bg-slate-700 border-slate-600 text-white"
                  data-testid="connection-name-input"
                />
              </div>

              <div>
                <Label className="text-slate-300">Database Type</Label>
                <Select value={connectionData.db_type} onValueChange={handleDbTypeChange}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white" data-testid="db-type-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-700 border-slate-600">
                    {dbTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Connection Method Toggle (not for SQLite) */}
              {connectionData.db_type !== 'sqlite' && (
                <div className="flex items-center space-x-2 p-3 bg-slate-900/50 rounded border border-slate-700">
                  <button
                    type="button"
                    onClick={() => setUseConnectionString(false)}
                    className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${
                      !useConnectionString 
                        ? 'bg-cyan-600 text-white' 
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                    data-testid="individual-fields-button"
                  >
                    Individual Fields
                  </button>
                  <button
                    type="button"
                    onClick={() => setUseConnectionString(true)}
                    className={`flex-1 px-3 py-2 rounded text-sm font-medium transition ${
                      useConnectionString 
                        ? 'bg-cyan-600 text-white' 
                        : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                    }`}
                    data-testid="connection-string-button"
                  >
                    Connection String
                  </button>
                </div>
              )}

              {connectionData.db_type === 'sqlite' ? (
                <div>
                  <Label className="text-slate-300">File Path</Label>
                  <Input
                    placeholder="/path/to/database.db"
                    value={connectionData.file_path}
                    onChange={(e) => setConnectionData({ ...connectionData, file_path: e.target.value })}
                    className="bg-slate-700 border-slate-600 text-white"
                    data-testid="file-path-input"
                  />
                  <p className="text-xs text-slate-500 mt-1">Example: /var/data/mydb.sqlite or ./local.db</p>
                </div>
              ) : useConnectionString ? (
                <div>
                  <Label className="text-slate-300">Connection String</Label>
                  <Input
                    placeholder={
                      connectionData.db_type === 'postgresql' 
                        ? 'postgresql://user:password@localhost:5432/dbname'
                        : connectionData.db_type === 'mysql'
                        ? 'mysql://user:password@localhost:3306/dbname'
                        : connectionData.db_type === 'mssql'
                        ? 'mssql://user:password@localhost:1433/dbname'
                        : 'mongodb://localhost:27017/mydb'
                    }
                    value={connectionData.connection_string}
                    onChange={(e) => setConnectionData({ ...connectionData, connection_string: e.target.value })}
                    className="bg-slate-700 border-slate-600 text-white"
                    data-testid="connection-string-input"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    {connectionData.db_type === 'postgresql' && 'Format: postgresql://[user[:password]@][host][:port][/dbname]'}
                    {connectionData.db_type === 'mysql' && 'Format: mysql://[user[:password]@][host][:port][/dbname]'}
                    {connectionData.db_type === 'mssql' && 'Format: mssql://[user[:password]@][host][:port][/dbname]'}
                    {connectionData.db_type === 'mongodb' && 'Format: mongodb://[user:password@]host[:port][/database]'}
                  </p>
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-slate-300">Host</Label>
                      <Input
                        placeholder="localhost"
                        value={connectionData.host}
                        onChange={(e) => setConnectionData({ ...connectionData, host: e.target.value })}
                        className="bg-slate-700 border-slate-600 text-white"
                        data-testid="host-input"
                      />
                    </div>
                    <div>
                      <Label className="text-slate-300">Port</Label>
                      <Input
                        placeholder="5432"
                        value={connectionData.port}
                        onChange={(e) => setConnectionData({ ...connectionData, port: e.target.value })}
                        className="bg-slate-700 border-slate-600 text-white"
                        data-testid="port-input"
                      />
                    </div>
                  </div>

                  <div>
                    <Label className="text-slate-300">Database</Label>
                    <Input
                      placeholder="mydatabase"
                      value={connectionData.database}
                      onChange={(e) => setConnectionData({ ...connectionData, database: e.target.value })}
                      className="bg-slate-700 border-slate-600 text-white"
                      data-testid="database-input"
                    />
                  </div>

                  <div>
                    <Label className="text-slate-300">Username</Label>
                    <Input
                      placeholder="user"
                      value={connectionData.username}
                      onChange={(e) => setConnectionData({ ...connectionData, username: e.target.value })}
                      className="bg-slate-700 border-slate-600 text-white"
                      data-testid="username-input"
                    />
                  </div>

                  <div>
                    <Label className="text-slate-300">Password</Label>
                    <Input
                      type="password"
                      placeholder="••••••••"
                      value={connectionData.password}
                      onChange={(e) => setConnectionData({ ...connectionData, password: e.target.value })}
                      className="bg-slate-700 border-slate-600 text-white"
                      data-testid="password-input"
                    />
                  </div>
                </>
              )}

              <div className="flex space-x-3">
                <Button
                  onClick={handleTestConnection}
                  variant="outline"
                  className="flex-1 border-slate-600"
                  data-testid="test-connection-button"
                >
                  {testingConnection === 'testing' && 'Testing...'}
                  {testingConnection === 'success' && (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                      Connected
                    </>
                  )}
                  {testingConnection === 'error' && (
                    <>
                      <XCircle className="w-4 h-4 mr-2 text-red-500" />
                      Failed
                    </>
                  )}
                  {!testingConnection && 'Test Connection'}
                </Button>
                <Button
                  onClick={handleCreateConnection}
                  className="flex-1 bg-cyan-600 hover:bg-cyan-700"
                  disabled={!connectionData.name}
                  data-testid="save-connection-button"
                >
                  Save Connection
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Connections List */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {connections.length === 0 ? (
          <Card className="col-span-full bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700">
            <CardContent className="py-12 text-center">
              <p className="text-slate-600 dark:text-slate-400 text-lg">No connections yet. Create your first connection!</p>
            </CardContent>
          </Card>
        ) : (
          connections.map((connection) => (
            <Card key={connection.id} className="bg-white dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 hover:border-cyan-500 transition-all" data-testid="connection-card">
              <CardHeader>
                <CardTitle className="text-slate-900 dark:text-white flex items-center justify-between">
                  <span>{connection.name}</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDeleteConnection(connection.id)}
                    className="text-red-400 hover:text-red-300 hover:bg-red-400/10"
                    data-testid="delete-connection-button"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </CardTitle>
                <CardDescription className="text-slate-600 dark:text-slate-400">
                  {connection.db_type.toUpperCase()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm text-slate-700 dark:text-slate-300">
                  {connection.db_type === 'sqlite' ? (
                    <p><span className="text-slate-500">File:</span> {connection.file_path}</p>
                  ) : connection.db_type === 'mongodb' ? (
                    <p><span className="text-slate-500">Database:</span> {connection.database}</p>
                  ) : (
                    <>
                      <p><span className="text-slate-500">Host:</span> {connection.host}:{connection.port}</p>
                      <p><span className="text-slate-500">Database:</span> {connection.database}</p>
                      <p><span className="text-slate-500">User:</span> {connection.username}</p>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
