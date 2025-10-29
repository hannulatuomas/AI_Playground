import React from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardFooter, CardHeader } from './ui/card';

export const CommandCard = ({ 
  command, 
  user, 
  detailed = false, 
  onView, 
  onEdit, 
  onDelete, 
  onSave, 
  onClose 
}) => {
  const isOwner = user && command.created_by === user.id;
  
  const getCategoryColor = (category) => {
    const colors = {
      'networking': 'bg-blue-100 text-blue-800',
      'file': 'bg-green-100 text-green-800', 
      'system': 'bg-yellow-100 text-yellow-800',
      'security': 'bg-red-100 text-red-800',
      'text': 'bg-purple-100 text-purple-800',
      'process': 'bg-indigo-100 text-indigo-800',
      'package': 'bg-pink-100 text-pink-800',
      'disk': 'bg-orange-100 text-orange-800',
      'user': 'bg-teal-100 text-teal-800',
    };
    const key = category.toLowerCase().split(' ')[0];
    return colors[key] || 'bg-gray-100 text-gray-800';
  };

  if (detailed) {
    return (
      <div className="command-card max-w-none" data-testid={`command-detail-${command.id}`}>
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-gray-900 font-['Space_Grotesk']">{command.name}</h1>
              <Badge className={getCategoryColor(command.category)}>
                {command.category}
              </Badge>
            </div>
            <p className="text-gray-600 text-lg leading-relaxed">{command.description}</p>
          </div>
          
          <div className="flex items-center gap-2 ml-4">
            {isOwner && (
              <>
                <Button
                  onClick={onEdit}
                  variant="outline"
                  size="sm"
                  className="btn-hover"
                  data-testid="edit-command-btn"
                >
                  Edit
                </Button>
                <Button
                  onClick={onDelete}
                  variant="outline"
                  size="sm"
                  className="btn-hover text-red-600 border-red-200 hover:bg-red-50"
                  data-testid="delete-command-btn"
                >
                  Delete
                </Button>
              </>
            )}
            {user && !isOwner && (
              <Button
                onClick={onSave}
                variant="outline"
                size="sm"
                className="btn-hover"
                data-testid="save-command-btn"
              >
                Save
              </Button>
            )}
            <Button
              onClick={onClose}
              variant="ghost"
              size="sm"
              className="btn-hover"
              data-testid="close-detail-btn"
            >
              ✕
            </Button>
          </div>
        </div>

        {/* Syntax */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Syntax</h3>
          <div className="command-syntax" data-testid="command-syntax">
            {command.syntax}
          </div>
        </div>

        {/* Examples */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Examples</h3>
          <div className="space-y-3" data-testid="command-examples">
            {command.examples.map((example, index) => (
              <div key={index} className="command-example">
                {example}
              </div>
            ))}
          </div>
        </div>

        {/* Tags */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Tags</h3>
          <div className="flex flex-wrap gap-2" data-testid="command-tags">
            {command.tags.map((tag, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <Card className="command-card card-hover fade-in" data-testid={`command-card-${command.id}`}>
      <CardHeader className="command-header">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900 font-['Space_Grotesk']">{command.name}</h3>
              <Badge className={getCategoryColor(command.category)} size="sm">
                {command.category}
              </Badge>
            </div>
            <p className="text-gray-600 text-sm line-clamp-2">{command.description}</p>
          </div>
          
          {isOwner && (
            <Badge variant="outline" size="sm" className="ml-2">
              Mine
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <div className="mb-4">
          <div className="command-syntax text-sm" data-testid="command-syntax-preview">
            {command.syntax}
          </div>
        </div>

        <div className="flex flex-wrap gap-1 mb-3">
          {command.tags.slice(0, 3).map((tag, index) => (
            <Badge key={index} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
          {command.tags.length > 3 && (
            <Badge variant="secondary" className="text-xs">
              +{command.tags.length - 3}
            </Badge>
          )}
        </div>
      </CardContent>

      <CardFooter className="flex justify-between items-center pt-4 border-t">
        <div className="text-xs text-gray-500">
          {command.examples.length} example{command.examples.length !== 1 ? 's' : ''}
        </div>
        
        <div className="flex gap-2">
          <Button
            onClick={onView}
            variant="outline"
            size="sm"
            className="btn-hover"
            data-testid="view-command-btn"
          >
            View
          </Button>
          
          {isOwner && (
            <Button
              onClick={onEdit}
              variant="outline"
              size="sm"
              className="btn-hover"
              data-testid="edit-command-btn"
            >
              Edit
            </Button>
          )}
          
          {user && !isOwner && (
            <Button
              onClick={onSave}
              variant="outline"
              size="sm"
              className="btn-hover"
              data-testid="save-command-btn"
            >
              Save
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
};