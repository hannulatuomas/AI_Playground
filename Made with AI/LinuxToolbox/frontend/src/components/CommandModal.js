import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';

const PREDEFINED_CATEGORIES = [
  'File Management',
  'Text Processing', 
  'Networking',
  'System Monitoring',
  'User Management',
  'Security',
  'Package Management',
  'Process Control',
  'Disk Management'
];

const COMMON_TAGS = [
  'basic', 'advanced', 'networking', 'security', 'files', 'text', 'system',
  'monitoring', 'backup', 'compression', 'permissions', 'ssh', 'firewall',
  'processes', 'memory', 'disk', 'cpu', 'logs', 'cron', 'service'
];

export const CommandModal = ({ isOpen, onClose, onSubmit, initialData, categories, tags }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    syntax: '',
    examples: [''],
    category: '',
    tags: [],
    is_public: true
  });
  const [newTag, setNewTag] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || '',
        description: initialData.description || '',
        syntax: initialData.syntax || '',
        examples: initialData.examples || [''],
        category: initialData.category || '',
        tags: initialData.tags || [],
        is_public: initialData.is_public !== undefined ? initialData.is_public : true
      });
    } else {
      setFormData({
        name: '',
        description: '',
        syntax: '',
        examples: [''],
        category: '',
        tags: [],
        is_public: true
      });
    }
  }, [initialData, isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Filter out empty examples
      const cleanedData = {
        ...formData,
        examples: formData.examples.filter(ex => ex.trim() !== '')
      };
      await onSubmit(cleanedData);
    } finally {
      setLoading(false);
    }
  };

  const handleExampleChange = (index, value) => {
    const newExamples = [...formData.examples];
    newExamples[index] = value;
    setFormData({ ...formData, examples: newExamples });
  };

  const addExample = () => {
    setFormData({ ...formData, examples: [...formData.examples, ''] });
  };

  const removeExample = (index) => {
    if (formData.examples.length > 1) {
      const newExamples = formData.examples.filter((_, i) => i !== index);
      setFormData({ ...formData, examples: newExamples });
    }
  };

  const addTag = (tag) => {
    if (tag && !formData.tags.includes(tag)) {
      setFormData({ ...formData, tags: [...formData.tags, tag] });
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData({ ...formData, tags: formData.tags.filter(tag => tag !== tagToRemove) });
  };

  const handleAddNewTag = () => {
    if (newTag.trim()) {
      addTag(newTag.trim());
      setNewTag('');
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="command-modal">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold font-['Space_Grotesk']">
            {initialData ? 'Edit Command' : 'Add New Command'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6" data-testid="command-form">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="command-name">Command Name *</Label>
            <Input
              id="command-name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., ls, grep, find"
              required
              data-testid="command-name-input"
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="command-description">Description *</Label>
            <Textarea
              id="command-description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of what this command does"
              required
              rows={3}
              data-testid="command-description-input"
            />
          </div>

          {/* Syntax */}
          <div className="space-y-2">
            <Label htmlFor="command-syntax">Syntax *</Label>
            <Input
              id="command-syntax"
              value={formData.syntax}
              onChange={(e) => setFormData({ ...formData, syntax: e.target.value })}
              placeholder="e.g., ls [options] [directory]"
              required
              className="font-mono"
              data-testid="command-syntax-input"
            />
          </div>

          {/* Category */}
          <div className="space-y-2">
            <Label htmlFor="command-category">Category *</Label>
            <Select 
              value={formData.category} 
              onValueChange={(value) => setFormData({ ...formData, category: value })}
            >
              <SelectTrigger data-testid="command-category-select">
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
              <SelectContent>
                {PREDEFINED_CATEGORIES.map(cat => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
                {categories?.filter(cat => !PREDEFINED_CATEGORIES.includes(cat)).map(cat => (
                  <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Examples */}
          <div className="space-y-2">
            <Label>Examples *</Label>
            {formData.examples.map((example, index) => (
              <div key={index} className="flex gap-2">
                <Input
                  value={example}
                  onChange={(e) => handleExampleChange(index, e.target.value)}
                  placeholder={`Example ${index + 1}`}
                  className="font-mono flex-1"
                  data-testid={`command-example-input-${index}`}
                />
                {formData.examples.length > 1 && (
                  <Button
                    type="button"
                    onClick={() => removeExample(index)}
                    variant="outline"
                    size="sm"
                    className="px-3"
                    data-testid={`remove-example-btn-${index}`}
                  >
                    ✕
                  </Button>
                )}
              </div>
            ))}
            <Button
              type="button"
              onClick={addExample}
              variant="outline"
              size="sm"
              data-testid="add-example-btn"
            >
              + Add Example
            </Button>
          </div>

          {/* Tags */}
          <div className="space-y-2">
            <Label>Tags</Label>
            
            {/* Selected Tags */}
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 p-2 border rounded" data-testid="selected-tags">
                {formData.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="cursor-pointer" onClick={() => removeTag(tag)}>
                    {tag} ✕
                  </Badge>
                ))}
              </div>
            )}
            
            {/* Add Tag Input */}
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add a tag"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddNewTag();
                  }
                }}
                data-testid="new-tag-input"
              />
              <Button
                type="button"
                onClick={handleAddNewTag}
                variant="outline"
                size="sm"
                data-testid="add-tag-btn"
              >
                Add
              </Button>
            </div>
            
            {/* Common Tags */}
            <div className="space-y-2">
              <Label className="text-sm text-gray-600">Common tags:</Label>
              <div className="flex flex-wrap gap-2">
                {COMMON_TAGS.filter(tag => !formData.tags.includes(tag)).slice(0, 10).map(tag => (
                  <Badge
                    key={tag}
                    variant="outline"
                    className="cursor-pointer hover:bg-gray-100"
                    onClick={() => addTag(tag)}
                    data-testid={`common-tag-${tag}`}
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Public/Private */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="is-public"
              checked={formData.is_public}
              onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
              data-testid="is-public-checkbox"
            />
            <Label htmlFor="is-public" className="text-sm">
              Make this command public (visible to all users)
            </Label>
          </div>

          {/* Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button
              type="button"
              onClick={onClose}
              variant="outline"
              data-testid="cancel-command-btn"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 btn-hover"
              data-testid="save-command-btn"
            >
              {loading ? 'Saving...' : (initialData ? 'Update Command' : 'Create Command')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};