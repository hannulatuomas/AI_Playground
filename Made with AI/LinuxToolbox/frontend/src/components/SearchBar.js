import React, { useState, useEffect } from 'react';
import { Input } from './ui/input';
import { Button } from './ui/button';

export const SearchBar = ({ onSearch, placeholder = "Search...", value = "", onChange }) => {
  const [query, setQuery] = useState(value);

  // Sync internal state with external value
  useEffect(() => {
    setQuery(value);
  }, [value]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  const handleClear = () => {
    setQuery('');
    if (onChange) onChange('');
    onSearch('');
  };

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setQuery(newValue);
    if (onChange) onChange(newValue);
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Input
            type="text"
            value={query}
            onChange={handleInputChange}
            placeholder={placeholder}
            className="h-12 pl-12 pr-12 text-lg border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-0 search-focus"
            data-testid="search-input"
          />
          
          {/* Search Icon */}
          <div className="absolute left-4 top-1/2 transform -translate-y-1/2 z-10">
            <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          {/* Clear Button */}
          {query && (
            <Button
              type="button"
              onClick={handleClear}
              variant="ghost"
              size="sm"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 h-6 w-6 z-10"
              data-testid="clear-search-btn"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </Button>
          )}
        </div>

        {/* Search Button */}
        <Button
          type="submit"
          className="h-12 px-6 bg-blue-600 hover:bg-blue-700 text-white rounded-xl btn-hover"
          data-testid="search-btn"
        >
          Search
        </Button>
      </div>
    </form>
  );
};