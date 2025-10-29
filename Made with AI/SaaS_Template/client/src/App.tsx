import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import BuySubscription from './pages/BuySubscription';
import UserProfile from './pages/UserProfile';
import Register from './pages/Register';
import Login from './pages/Login';
import UpgradeSubscription from './pages/UpgradeSubscription';
import { AuthProvider } from './auth/AuthProvider';
import { useAuth } from './auth/useAuth';
import VerifyEmail from './pages/VerifyEmail';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';

import React, { useEffect, useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const auth = useAuth();
  const user = auth?.user;
  const loading = auth?.loading ?? false;
  const refreshUser = auth?.refreshUser;
  const navigate = useNavigate();
  const [localLoading, setLocalLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    async function checkAuth() {
      if (!user) {
        setLocalLoading(true);
        await refreshUser?.(); // Force fresh fetch, optional chaining for safety
        setLocalLoading(false);
      }
    }
    checkAuth();
    return () => { cancelled = true; };
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    if (!loading && !localLoading && !user) {
      navigate('/login', { replace: true });
    }
  }, [user, loading, localLoading, navigate]);

  if (loading || localLoading) return <div>Loading...</div>;
  if (!user) return null; // Will redirect
  return children;
}

const App = () => (
  <AuthProvider>
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/buy" element={<BuySubscription />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/profile" element={<ProtectedRoute><UserProfile /></ProtectedRoute>} />
        <Route path="/upgrade" element={<ProtectedRoute><UpgradeSubscription /></ProtectedRoute>} />
        <Route path="/verify-email" element={<VerifyEmail />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="*" element={<div className="flex flex-col items-center justify-center min-h-screen">
          <h1 className="text-4xl font-bold mb-4">404 - Page Not Found</h1>
          <p className="mb-4">Sorry, the page you are looking for does not exist.</p>
          <a href="/" className="text-blue-600 underline">Go to Home</a>
        </div>} />
      </Routes>
    </Router>
  </AuthProvider>
);

export default App;
