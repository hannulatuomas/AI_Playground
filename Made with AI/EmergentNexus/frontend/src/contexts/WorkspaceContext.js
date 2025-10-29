import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { toast } from 'sonner';

const WorkspaceContext = createContext();

// Action types
const ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_NODES: 'SET_NODES',
  ADD_NODE: 'ADD_NODE',
  UPDATE_NODE: 'UPDATE_NODE',
  DELETE_NODE: 'DELETE_NODE',
  SET_RELATIONS: 'SET_RELATIONS',
  ADD_RELATION: 'ADD_RELATION',
  DELETE_RELATION: 'DELETE_RELATION',
  SET_CURRENT_TOOL: 'SET_CURRENT_TOOL',
  SET_SELECTED_NODE: 'SET_SELECTED_NODE',
  SET_ERROR: 'SET_ERROR'
};

const initialState = {
  nodes: [],
  relations: [],
  currentTool: 'markdown',
  selectedNode: null,
  loading: false,
  error: null
};

function workspaceReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    case ACTIONS.SET_NODES:
      return { ...state, nodes: action.payload };
    case ACTIONS.ADD_NODE:
      return { ...state, nodes: [...state.nodes, action.payload] };
    case ACTIONS.UPDATE_NODE:
      return {
        ...state,
        nodes: state.nodes.map(node =>
          node.id === action.payload.id ? action.payload : node
        )
      };
    case ACTIONS.DELETE_NODE:
      return {
        ...state,
        nodes: state.nodes.filter(node => node.id !== action.payload)
      };
    case ACTIONS.SET_RELATIONS:
      return { ...state, relations: action.payload };
    case ACTIONS.ADD_RELATION:
      return { ...state, relations: [...state.relations, action.payload] };
    case ACTIONS.DELETE_RELATION:
      return {
        ...state,
        relations: state.relations.filter(relation =>
          !(relation.from_id === action.payload.from_id && 
            relation.to_id === action.payload.to_id)
        )
      };
    case ACTIONS.SET_CURRENT_TOOL:
      return { ...state, currentTool: action.payload };
    case ACTIONS.SET_SELECTED_NODE:
      return { ...state, selectedNode: action.payload };
    case ACTIONS.SET_ERROR:
      return { ...state, error: action.payload };
    default:
      return state;
  }
}

export function WorkspaceProvider({ children }) {
  const [state, dispatch] = useReducer(workspaceReducer, initialState);

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  // API functions
  const api = {
    async fetchNodes() {
      try {
        dispatch({ type: ACTIONS.SET_LOADING, payload: true });
        const response = await fetch(`${API_BASE}/nodes`);
        if (!response.ok) throw new Error('Failed to fetch nodes');
        const nodes = await response.json();
        dispatch({ type: ACTIONS.SET_NODES, payload: nodes });
      } catch (error) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to fetch nodes');
      } finally {
        dispatch({ type: ACTIONS.SET_LOADING, payload: false });
      }
    },

    async createNode(nodeData) {
      try {
        const response = await fetch(`${API_BASE}/nodes`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(nodeData)
        });
        if (!response.ok) throw new Error('Failed to create node');
        const node = await response.json();
        dispatch({ type: ACTIONS.ADD_NODE, payload: node });
        toast.success('Node created successfully');
        return node;
      } catch (error) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to create node');
        throw error;
      }
    },

    async updateNode(nodeId, nodeData) {
      try {
        const response = await fetch(`${API_BASE}/nodes/${nodeId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(nodeData)
        });
        if (!response.ok) throw new Error('Failed to update node');
        const node = await response.json();
        dispatch({ type: ACTIONS.UPDATE_NODE, payload: node });
        toast.success('Node updated successfully');
        return node;
      } catch (error) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to update node');
        throw error;
      }
    },

    async deleteNode(nodeId) {
      try {
        const response = await fetch(`${API_BASE}/nodes/${nodeId}`, {
          method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete node');
        dispatch({ type: ACTIONS.DELETE_NODE, payload: nodeId });
        toast.success('Node deleted successfully');
      } catch (error) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to delete node');
        throw error;
      }
    },

    async fetchRelations() {
      try {
        const response = await fetch(`${API_BASE}/relations`);
        if (!response.ok) throw new Error('Failed to fetch relations');
        const relations = await response.json();
        dispatch({ type: ACTIONS.SET_RELATIONS, payload: relations });
      } catch (error) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to fetch relations');
      }
    },

    async createRelation(relationData) {
      try {
        const response = await fetch(`${API_BASE}/relations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(relationData)
        });
        if (!response.ok) throw new Error('Failed to create relation');
        const relation = await response.json();
        dispatch({ type: ACTIONS.ADD_RELATION, payload: relation });
        toast.success('Link created successfully');
        return relation;
      } catch (error) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to create link');
        throw error;
      }
    },

    async deleteRelation(fromId, toId) {
      try {
        const response = await fetch(`${API_BASE}/relations/${fromId}/${toId}`, {
          method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete relation');
        dispatch({ type: ACTIONS.DELETE_RELATION, payload: { from_id: fromId, to_id: toId } });
        toast.success('Link removed successfully');
      } catch (error) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to remove link');
        throw error;
      }
    },

    async getNodesByType(type) {
      try {
        const response = await fetch(`${API_BASE}/nodes/type/${type}`);
        if (!response.ok) throw new Error('Failed to fetch nodes by type');
        return await response.json();
      } catch (error) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error(`Failed to fetch ${type} nodes`);
        return [];
      }
    },

    async getNodeRelations(nodeId) {
      try {
        const response = await fetch(`${API_BASE}/relations/node/${nodeId}`);
        if (!response.ok) throw new Error('Failed to fetch node relations');
        return await response.json();
      } catch (error) {
        dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
        toast.error('Failed to fetch node relations');
        return [];
      }
    }
  };

  // Actions
  const actions = {
    setCurrentTool: (tool) => dispatch({ type: ACTIONS.SET_CURRENT_TOOL, payload: tool }),
    setSelectedNode: (node) => dispatch({ type: ACTIONS.SET_SELECTED_NODE, payload: node }),
    clearError: () => dispatch({ type: ACTIONS.SET_ERROR, payload: null })
  };

  // Load initial data
  useEffect(() => {
    api.fetchNodes();
    api.fetchRelations();
  }, []);

  const value = {
    ...state,
    api,
    actions
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
}