import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
const SEARCH_TYPES = [
  { value: 'all', label: 'All Fields' },
  { value: 'name', label: 'Command Name Only' },
  { value: 'description', label: 'Description Only' },
  { value: 'examples', label: 'Examples Only' },
  { value: 'tags', label: 'Tags Only' }
];

// We'll get actual tags from props instead of hardcoded list

export const AdvancedSearch = ({ 
  onSearch, 
  categories, 
  tags, 
  isOpen, 
  onToggle 
}) => {
  const [searchFilters, setSearchFilters] = useState({
    query: '',
    searchType: 'all',
    selectedTags: [],
    exactMatch: false
  });
  const [functionalTagsFilter, setFunctionalTagsFilter] = useState('');

  const handleSearch = () => {
    onSearch(searchFilters);
  };

  const handleReset = () => {
    setSearchFilters({
      query: '',
      searchType: 'all',
      selectedTags: [],
      exactMatch: false
    });
    setFunctionalTagsFilter('');
    onSearch(null); // Reset to show all commands
  };

  const addTag = (tag) => {
    if (!searchFilters.selectedTags.includes(tag)) {
      setSearchFilters({
        ...searchFilters,
        selectedTags: [...searchFilters.selectedTags, tag]
      });
    }
  };

  const removeTag = (tagToRemove) => {
    setSearchFilters({
      ...searchFilters,
      selectedTags: searchFilters.selectedTags.filter(tag => tag !== tagToRemove)
    });
  };

  return (
    <div>
      <Button 
        onClick={onToggle}
        variant="outline" 
        className="mb-4 btn-hover"
        data-testid="advanced-search-toggle"
      >
        {isOpen ? 'Hide' : 'Show'} Advanced Search
      </Button>
      
      {isOpen && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Advanced Search Filters</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Search Query */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <Label htmlFor="adv-search-query">Search Term</Label>
                <Input
                  id="adv-search-query"
                  type="text"
                  value={searchFilters.query}
                  onChange={(e) => setSearchFilters({ ...searchFilters, query: e.target.value })}
                  placeholder="Enter search term..."
                  data-testid="advanced-search-input"
                />
              </div>
              
              <div>
                <Label htmlFor="search-type">Search In</Label>
                <Select 
                  value={searchFilters.searchType} 
                  onValueChange={(value) => setSearchFilters({ ...searchFilters, searchType: value })}
                >
                  <SelectTrigger data-testid="search-type-select">
                    <SelectValue placeholder="Select search type" />
                  </SelectTrigger>
                  <SelectContent>
                    {SEARCH_TYPES.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Selected Tags */}
            {searchFilters.selectedTags.length > 0 && (
              <div>
                <Label>Selected Tags</Label>
                <div className="flex flex-wrap gap-2 p-2 border rounded" data-testid="selected-tags-advanced">
                  {searchFilters.selectedTags.map((tag, index) => (
                    <Badge 
                      key={index} 
                      variant="secondary" 
                      className="cursor-pointer" 
                      onClick={() => removeTag(tag)}
                    >
                      {tag} ✕
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Tag Selection */}
            <div>
              <Label>Filter by Tags</Label>
              
              {/* Linux Distributions */}
              <div className="mt-3">
                <Label className="text-sm text-gray-600 font-medium">Linux Distributions:</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {(tags || [])
                    .filter(tag => ['alpine', 'arch', 'centos', 'debian', 'fedora', 'gentoo', 'kali', 'manjaro', 'opensuse', 'rhel', 'suse', 'ubuntu', 'mint', 'elementary', 'pop', 'zorin', 'parrot', 'freebsd', 'openbsd', 'netbsd', 'mx-linux', 'endeavouros'].includes(tag.toLowerCase()))
                    .filter(tag => !searchFilters.selectedTags.includes(tag))
                    .map(tag => (
                      <Badge
                        key={tag}
                        variant="outline"
                        className="cursor-pointer hover:bg-blue-100 border-blue-300 text-blue-700"
                        onClick={() => addTag(tag)}
                        data-testid={`distro-tag-${tag}`}
                      >
                        + {tag.charAt(0).toUpperCase() + tag.slice(1)}
                      </Badge>
                    ))}
                </div>
              </div>

              {/* Functional Tags */}
              <div className="mt-4">
                <Label className="text-sm text-gray-600 font-medium">Functional Tags:</Label>
                
                {/* Search box for functional tags */}
                <Input
                  type="text"
                  placeholder="Filter functional tags..."
                  value={functionalTagsFilter}
                  onChange={(e) => setFunctionalTagsFilter(e.target.value)}
                  className="mt-2 mb-3 text-sm"
                  data-testid="functional-tags-filter"
                />
                
                <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                  {(tags || [])
                    .filter(tag => !['alpine', 'arch', 'centos', 'debian', 'fedora', 'gentoo', 'kali', 'manjaro', 'opensuse', 'rhel', 'suse', 'ubuntu', 'mint', 'elementary', 'pop', 'zorin', 'parrot', 'freebsd', 'openbsd', 'netbsd', 'mx-linux', 'endeavouros'].includes(tag.toLowerCase()))
                    .filter(tag => !searchFilters.selectedTags.includes(tag))
                    .filter(tag => functionalTagsFilter === '' || tag.toLowerCase().includes(functionalTagsFilter.toLowerCase()))
                    .map(tag => (
                      <Badge
                        key={tag}
                        variant="outline"
                        className="cursor-pointer hover:bg-gray-100"
                        onClick={() => addTag(tag)}
                        data-testid={`functional-tag-${tag}`}
                      >
                        + {tag}
                      </Badge>
                    ))}
                </div>
                
                {functionalTagsFilter && (tags || [])
                  .filter(tag => !['alpine', 'arch', 'centos', 'debian', 'fedora', 'gentoo', 'kali', 'manjaro', 'opensuse', 'rhel', 'suse', 'ubuntu', 'mint', 'elementary', 'pop', 'zorin', 'parrot', 'freebsd', 'openbsd', 'netbsd', 'mx-linux', 'endeavouros'].includes(tag.toLowerCase()))
                  .filter(tag => !searchFilters.selectedTags.includes(tag))
                  .filter(tag => tag.toLowerCase().includes(functionalTagsFilter.toLowerCase())).length === 0 && (
                  <p className="text-sm text-gray-500 mt-2">No functional tags found matching "{functionalTagsFilter}"</p>
                )}
              </div>
              
              {tags && tags.length === 0 && (
                <p className="text-sm text-gray-500 mt-2">No tags available</p>
              )}
            </div>

            {/* Search Options */}
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="exact-match"
                checked={searchFilters.exactMatch}
                onChange={(e) => setSearchFilters({ ...searchFilters, exactMatch: e.target.checked })}
                data-testid="exact-match-checkbox"
              />
              <Label htmlFor="exact-match" className="text-sm">
                Exact match (case-sensitive)
              </Label>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4 border-t">
              <Button
                onClick={handleSearch}
                className="bg-blue-600 hover:bg-blue-700 btn-hover"
                data-testid="advanced-search-btn"
              >
                Apply Filters
              </Button>
              <Button
                onClick={handleReset}
                variant="outline"
                className="btn-hover"
                data-testid="advanced-search-reset-btn"
              >
                Reset Filters
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};