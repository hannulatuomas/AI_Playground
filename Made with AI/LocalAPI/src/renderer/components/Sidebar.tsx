import React from 'react';
import CollectionsTree from './CollectionsTree';
import type { Request } from '../../types/models';

interface SidebarProps {
  onRequestSelect?: (request: Request) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onRequestSelect }) => {
  return <CollectionsTree onRequestSelect={onRequestSelect} />;
};

export default Sidebar;
