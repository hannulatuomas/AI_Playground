import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import MarkdownEditor from './tools/MarkdownEditor';
import KanbanBoard from './tools/KanbanBoard';
import EvidenceBoard from './tools/EvidenceBoard';
import PostitNotes from './tools/PostitNotes';
import Notebook from './tools/Notebook';
import Canvas from './tools/Canvas';
import FamilyTree from './tools/FamilyTree';
import AssetManagement from './tools/AssetManagement';
import ProjectTimeline from './tools/ProjectTimeline';

export default function ToolWorkspace() {
  return (
    <div className="h-full bg-slate-900" data-testid="tool-workspace">
      <Routes>
        <Route path="/" element={<Navigate to="/markdown" replace />} />
        <Route path="/markdown" element={<MarkdownEditor />} />
        <Route path="/kanban" element={<KanbanBoard />} />
        <Route path="/evidence" element={<EvidenceBoard />} />
        <Route path="/postit" element={<PostitNotes />} />
        <Route path="/notebook" element={<Notebook />} />
        <Route path="/canvas" element={<Canvas />} />
        <Route path="/family" element={<FamilyTree />} />
        <Route path="/assets" element={<AssetManagement />} />
        <Route path="/projects" element={<ProjectTimeline />} />
        <Route path="*" element={<Navigate to="/markdown" replace />} />
      </Routes>
    </div>
  );
}