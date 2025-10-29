import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { PanelLeft } from 'lucide-react';
import Sidebar from './Sidebar';
import ToolWorkspace from './ToolWorkspace';
import LinkingModal from './LinkingModal';
import { useWorkspace } from '../contexts/WorkspaceContext';

export default function Layout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [linkingModalOpen, setLinkingModalOpen] = useState(false);
  const { selectedNode } = useWorkspace();

  // Auto-collapse sidebar on mobile and handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setSidebarCollapsed(true);
      }
    };

    // Set initial state based on screen size
    if (window.innerWidth < 768) {
      setSidebarCollapsed(true);
    }
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="flex h-screen bg-slate-900">
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      
      <main className={`flex-1 overflow-hidden transition-all duration-300 ${
        sidebarCollapsed 
          ? 'ml-0 md:ml-16' 
          : 'ml-0 md:ml-64'
      }`}>
        <ToolWorkspace />
      </main>

      {/* Mobile menu button */}
      <button
        className={`fixed top-4 left-4 z-60 bg-slate-700 hover:bg-slate-600 text-white p-2 rounded-md shadow-lg md:hidden transition-all ${
          sidebarCollapsed ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
        onClick={() => setSidebarCollapsed(false)}
        data-testid="mobile-menu-btn"
      >
        <PanelLeft className="h-5 w-5" />
      </button>

      {/* Mobile overlay when sidebar is open */}
      {!sidebarCollapsed && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={() => setSidebarCollapsed(true)}
        />
      )}

      <LinkingModal
        isOpen={linkingModalOpen}
        onClose={() => setLinkingModalOpen(false)}
        sourceNode={selectedNode}
      />
    </div>
  );
}