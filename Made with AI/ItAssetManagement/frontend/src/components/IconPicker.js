import React, { useState } from 'react';
import { 
  // Hardware Icons
  Monitor, Cpu, HardDrive, MemoryStick, Smartphone, Tablet, Laptop, Server, Router, 
  Wifi, Printer, Camera, Headphones, Keyboard, Mouse, Speaker, Gamepad2,
  
  // Software Icons  
  Globe, Code, Database, Shield, Lock, Key, Settings, Terminal, FileText, 
  Folder, Archive, Package, Download, Upload, Cloud,
  
  // Network/Identity Icons
  Network, Users, User, Mail, Phone, MapPin, Building2, Building, Home, Cable, Plug, Bug,
  
  // General Business Icons
  Briefcase, Calculator, Clock, Calendar, Tag, Star, Flag, Zap, 
  Wrench, Cog, Activity, BarChart3, TrendingUp,
  
  // Default/Fallback Icons
  Box, Package2, Layers, Grid3X3, Circle, Square, Triangle, Diamond
} from 'lucide-react';

const IconPicker = ({ selectedIcon, onSelect, title = "Select Icon" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Icon categories with their icons
  const iconCategories = {
    'Hardware': {
      icons: [
        { name: 'Monitor', component: Monitor, keywords: ['screen', 'display', 'computer'] },
        { name: 'Cpu', component: Cpu, keywords: ['processor', 'chip', 'computing'] },
        { name: 'HardDrive', component: HardDrive, keywords: ['storage', 'disk', 'drive'] },
        { name: 'MemoryStick', component: MemoryStick, keywords: ['ram', 'memory', 'stick'] },
        { name: 'Smartphone', component: Smartphone, keywords: ['phone', 'mobile', 'device'] },
        { name: 'Tablet', component: Tablet, keywords: ['ipad', 'device', 'touch'] },
        { name: 'Laptop', component: Laptop, keywords: ['notebook', 'computer', 'portable'] },
        { name: 'Server', component: Server, keywords: ['data center', 'hosting', 'cloud'] },
        { name: 'Router', component: Router, keywords: ['network', 'internet', 'wifi'] },
        { name: 'Wifi', component: Wifi, keywords: ['wireless', 'network', 'internet'] },
        { name: 'Printer', component: Printer, keywords: ['print', 'paper', 'office'] },
        { name: 'Camera', component: Camera, keywords: ['photo', 'video', 'lens'] },
        { name: 'Headphones', component: Headphones, keywords: ['audio', 'sound', 'music'] },
        { name: 'Keyboard', component: Keyboard, keywords: ['typing', 'input', 'keys'] },
        { name: 'Mouse', component: Mouse, keywords: ['pointer', 'click', 'input'] },
        { name: 'Speaker', component: Speaker, keywords: ['audio', 'sound', 'volume'] },
        { name: 'Gamepad2', component: Gamepad2, keywords: ['gaming', 'controller', 'joystick'] }
      ]
    },
    'Software': {
      icons: [
        { name: 'Globe', component: Globe, keywords: ['web', 'internet', 'world'] },
        { name: 'Code', component: Code, keywords: ['programming', 'development', 'script'] },
        { name: 'Database', component: Database, keywords: ['data', 'sql', 'storage'] },
        { name: 'Shield', component: Shield, keywords: ['security', 'protection', 'antivirus'] },
        { name: 'Lock', component: Lock, keywords: ['security', 'password', 'encrypted'] },
        { name: 'Key', component: Key, keywords: ['access', 'login', 'authentication'] },
        { name: 'Settings', component: Settings, keywords: ['config', 'preferences', 'options'] },
        { name: 'Terminal', component: Terminal, keywords: ['command', 'console', 'cli'] },
        { name: 'FileText', component: FileText, keywords: ['document', 'text', 'file'] },
        { name: 'Folder', component: Folder, keywords: ['directory', 'files', 'organize'] },
        { name: 'Archive', component: Archive, keywords: ['zip', 'compress', 'backup'] },
        { name: 'Package', component: Package, keywords: ['software', 'install', 'bundle'] },
        { name: 'Download', component: Download, keywords: ['get', 'receive', 'import'] },
        { name: 'Upload', component: Upload, keywords: ['send', 'export', 'share'] },
        { name: 'Cloud', component: Cloud, keywords: ['online', 'service', 'saas'] }
      ]
    },
    'Network & Identity': {
      icons: [
        { name: 'Network', component: Network, keywords: ['connection', 'topology', 'lan'] },
        { name: 'Users', component: Users, keywords: ['team', 'group', 'people'] },
        { name: 'User', component: User, keywords: ['person', 'account', 'profile'] },
        { name: 'Mail', component: Mail, keywords: ['email', 'message', 'contact'] },
        { name: 'Phone', component: Phone, keywords: ['call', 'telephone', 'contact'] },
        { name: 'MapPin', component: MapPin, keywords: ['location', 'address', 'place'] },
        { name: 'Building2', component: Building2, keywords: ['office', 'company', 'organization'] },
        { name: 'Building', component: Building, keywords: ['structure', 'facility', 'location'] },
        { name: 'Home', component: Home, keywords: ['house', 'residence', 'base'] },
        { name: 'Cable', component: Cable, keywords: ['wire', 'connection', 'ethernet'] },
        { name: 'Plug', component: Plug, keywords: ['adapter', 'connector', 'power'] },
        { name: 'Bug', component: Bug, keywords: ['security', 'testing', 'penetration'] },
        { name: 'HardDrive', component: HardDrive, keywords: ['storage', 'disk', 'ssd'] },
        { name: 'FileText', component: FileText, keywords: ['document', 'digital', 'license'] }
      ]
    },
    'Business': {
      icons: [
        { name: 'Briefcase', component: Briefcase, keywords: ['business', 'work', 'professional'] },
        { name: 'Calculator', component: Calculator, keywords: ['math', 'finance', 'accounting'] },
        { name: 'Clock', component: Clock, keywords: ['time', 'schedule', 'duration'] },
        { name: 'Calendar', component: Calendar, keywords: ['date', 'schedule', 'planning'] },
        { name: 'Tag', component: Tag, keywords: ['label', 'category', 'organize'] },
        { name: 'Star', component: Star, keywords: ['favorite', 'important', 'rating'] },
        { name: 'Flag', component: Flag, keywords: ['priority', 'marker', 'status'] },
        { name: 'Zap', component: Zap, keywords: ['energy', 'power', 'electric'] },
        { name: 'Wrench', component: Wrench, keywords: ['fix', 'maintenance', 'tool'] },
        { name: 'Cog', component: Cog, keywords: ['gear', 'mechanical', 'settings'] },
        { name: 'Settings', component: Settings, keywords: ['gear', 'mechanical', 'preferences'] },
        { name: 'Activity', component: Activity, keywords: ['monitoring', 'performance', 'stats'] },
        { name: 'BarChart3', component: BarChart3, keywords: ['analytics', 'data', 'metrics'] },
        { name: 'TrendingUp', component: TrendingUp, keywords: ['growth', 'increase', 'improvement'] }
      ]
    },
    'General': {
      icons: [
        { name: 'Box', component: Box, keywords: ['container', 'package', 'storage'] },
        { name: 'Package2', component: Package2, keywords: ['box', 'delivery', 'container'] },
        { name: 'Layers', component: Layers, keywords: ['stack', 'levels', 'organize'] },
        { name: 'Grid3X3', component: Grid3X3, keywords: ['layout', 'organize', 'structure'] },
        { name: 'Circle', component: Circle, keywords: ['round', 'shape', 'simple'] },
        { name: 'Square', component: Square, keywords: ['box', 'shape', 'simple'] },
        { name: 'Triangle', component: Triangle, keywords: ['shape', 'warning', 'point'] },
        { name: 'Diamond', component: Diamond, keywords: ['gem', 'precious', 'valuable'] }
      ]
    }
  };

  // Get all icons for searching
  const allIcons = Object.values(iconCategories).flatMap(category => category.icons);

  // Filter icons based on search
  const filteredCategories = Object.entries(iconCategories).reduce((acc, [categoryName, category]) => {
    const filteredIcons = category.icons.filter(icon =>
      icon.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      icon.keywords.some(keyword => keyword.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    
    if (filteredIcons.length > 0) {
      acc[categoryName] = { ...category, icons: filteredIcons };
    }
    
    return acc;
  }, {});

  // Get the selected icon component
  const getIconComponent = (iconName) => {
    const icon = allIcons.find(icon => icon.name === iconName);
    return icon ? icon.component : Box; // Default to Box if not found
  };

  const SelectedIconComponent = selectedIcon ? getIconComponent(selectedIcon) : Box;

  const handleIconSelect = (iconName) => {
    onSelect(iconName);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <label className="form-label">{title}</label>
      
      {/* Icon Display/Trigger */}
      <div 
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between p-3 border border-slate-300 rounded-lg cursor-pointer hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <SelectedIconComponent className="w-5 h-5 text-slate-600" />
          <span className="text-sm font-medium text-slate-700">
            {selectedIcon || 'Select Icon'}
          </span>
        </div>
        <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {/* Icon Picker Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-slate-300 rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto">
          <div className="p-4 border-b border-slate-200">
            <input
              type="text"
              placeholder="Search icons..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              autoFocus
            />
          </div>

          <div className="p-4 space-y-4">
            {Object.entries(filteredCategories).map(([categoryName, category]) => (
              <div key={categoryName}>
                <h4 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">
                  {categoryName}
                </h4>
                <div className="grid grid-cols-6 gap-2">
                  {category.icons.map((icon) => {
                    const IconComponent = icon.component;
                    const isSelected = selectedIcon === icon.name;
                    
                    return (
                      <button
                        key={icon.name}
                        onClick={() => handleIconSelect(icon.name)}
                        className={`p-3 rounded-lg border transition-all hover:bg-slate-50 ${
                          isSelected 
                            ? 'border-emerald-500 bg-emerald-50 text-emerald-700' 
                            : 'border-slate-200 text-slate-600 hover:border-slate-300'
                        }`}
                        title={`${icon.name} - ${icon.keywords.join(', ')}`}
                      >
                        <IconComponent className="w-5 h-5 mx-auto" />
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {Object.keys(filteredCategories).length === 0 && (
            <div className="p-8 text-center text-slate-500">
              <p className="text-sm">No icons found matching "{searchTerm}"</p>
            </div>
          )}
        </div>
      )}

      {/* Overlay to close dropdown */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default IconPicker;