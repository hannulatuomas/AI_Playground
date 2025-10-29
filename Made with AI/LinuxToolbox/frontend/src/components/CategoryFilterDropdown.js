import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from './ui/command';
import { Check, ChevronDown, ChevronRight, X } from 'lucide-react';
import { cn } from '../lib/utils';

export const CategoryFilterDropdown = ({ 
  categories, 
  selectedCategories = [], 
  onCategoryChange 
}) => {
  const [open, setOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const [categoriesWithSubs, setCategoriesWithSubs] = useState([]);
  const [expandedCategories, setExpandedCategories] = useState(new Set());

  // Filter categories based on search
  const filteredCategories = React.useMemo(() => {
    if (!searchValue) return categoriesWithSubs;
    
    return categoriesWithSubs.filter(catData => {
      const categoryMatch = catData.category.toLowerCase().includes(searchValue.toLowerCase());
      const subcategoryMatch = catData.subcategories && catData.subcategories.some(sub => 
        sub.toLowerCase().includes(searchValue.toLowerCase())
      );
      return categoryMatch || subcategoryMatch;
    });
  }, [categoriesWithSubs, searchValue]);

  useEffect(() => {
    if (categories) {
      // If categories is an array of strings (legacy), convert to new format
      if (categories.length > 0 && typeof categories[0] === 'string') {
        setCategoriesWithSubs(categories.map(cat => ({ category: cat, subcategories: [] })));
      } else {
        setCategoriesWithSubs(categories);
      }
    }
  }, [categories]);

  const toggleCategory = (category) => {
    let newSelected;
    
    if (category === 'all') {
      // If "All Categories" is selected, clear all other selections
      newSelected = selectedCategories.includes('all') ? [] : ['all'];
    } else {
      // Remove "all" if it was selected and add the specific category
      const filteredSelected = selectedCategories.filter(cat => cat !== 'all');
      
      if (filteredSelected.includes(category)) {
        newSelected = filteredSelected.filter(cat => cat !== category);
      } else {
        newSelected = [...filteredSelected, category];
      }
    }
    
    onCategoryChange(newSelected);
  };

  const toggleExpanded = (category) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const removeCategory = (categoryToRemove) => {
    const newSelected = selectedCategories.filter(cat => cat !== categoryToRemove);
    onCategoryChange(newSelected);
  };

  const clearAll = () => {
    onCategoryChange([]);
  };

  const getDisplayText = () => {
    if (selectedCategories.length === 0) return 'Select categories...';
    if (selectedCategories.includes('all')) return 'All Categories';
    if (selectedCategories.length === 1) return selectedCategories[0];
    return `${selectedCategories.length} categories selected`;
  };

  return (
    <div className="w-full" data-testid="category-filter-dropdown">
      <label className="text-sm font-medium text-gray-700 mb-2 block">
        Filter by Categories
      </label>
      
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            className="w-full justify-between text-left"
            data-testid="category-dropdown-trigger"
          >
            <span className="truncate">{getDisplayText()}</span>
            <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
          </Button>
        </PopoverTrigger>
        
        <PopoverContent className="w-full p-0" align="start">
          <Command>
            <CommandInput 
              placeholder="Search categories..." 
              value={searchValue}
              onValueChange={setSearchValue}
              data-testid="category-search-input"
            />
            <CommandList>
              <CommandEmpty>No categories found.</CommandEmpty>
              
              <CommandGroup>
                {/* All Categories option */}
                <CommandItem
                  key="all"
                  value="all"
                  onSelect={() => toggleCategory('all')}
                  className="flex items-center space-x-2"
                  data-testid="category-option-all"
                >
                  <div className={cn(
                    "flex h-4 w-4 items-center justify-center rounded-sm border border-primary",
                    selectedCategories.includes('all') ? "bg-primary text-primary-foreground" : "opacity-50"
                  )}>
                    {selectedCategories.includes('all') && <Check className="h-3 w-3" />}
                  </div>
                  <span className="flex-1">All Categories</span>
                </CommandItem>

                {/* Categories with collapsible subcategories */}
                {filteredCategories.map((catData) => {
                  const category = catData.category;
                  const hasSubcategories = catData.subcategories && catData.subcategories.length > 0;
                  const isExpanded = expandedCategories.has(category);
                  const isSelected = selectedCategories.includes(category);
                  
                  return (
                    <div key={category}>
                      {/* Main Category */}
                      <CommandItem
                        value={category}
                        onSelect={() => toggleCategory(category)}
                        className="flex items-center space-x-2"
                        data-testid={`category-option-${category.toLowerCase().replace(/\s+/g, '-')}`}
                      >
                        <div className={cn(
                          "flex h-4 w-4 items-center justify-center rounded-sm border border-primary",
                          isSelected ? "bg-primary text-primary-foreground" : "opacity-50"
                        )}>
                          {isSelected && <Check className="h-3 w-3" />}
                        </div>
                        <span className="flex-1">{category}</span>
                        {hasSubcategories && (
                          <button
                            onClick={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              toggleExpanded(category);
                            }}
                            className="p-0.5 hover:bg-gray-100 rounded"
                          >
                            {isExpanded ? (
                              <ChevronDown className="h-3 w-3" />
                            ) : (
                              <ChevronRight className="h-3 w-3" />
                            )}
                          </button>
                        )}
                      </CommandItem>

                      {/* Subcategories */}
                      {hasSubcategories && isExpanded && (
                        <div className="ml-6">
                          {catData.subcategories.map((subcategory) => {
                            const fullSubcat = `${category} > ${subcategory}`;
                            const isSubSelected = selectedCategories.includes(fullSubcat);
                            
                            return (
                              <CommandItem
                                key={fullSubcat}
                                value={fullSubcat}
                                onSelect={() => toggleCategory(fullSubcat)}
                                className="flex items-center space-x-2 text-sm text-gray-600"
                                data-testid={`category-option-${fullSubcat.toLowerCase().replace(/\s+/g, '-')}`}
                              >
                                <div className={cn(
                                  "flex h-3 w-3 items-center justify-center rounded-sm border border-primary",
                                  isSubSelected ? "bg-primary text-primary-foreground" : "opacity-50"
                                )}>
                                  {isSubSelected && <Check className="h-2 w-2" />}
                                </div>
                                <span className="flex-1">{subcategory}</span>
                              </CommandItem>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {/* Selected Categories Display */}
      {selectedCategories.length > 0 && !selectedCategories.includes('all') && (
        <div className="mt-3">
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-sm text-gray-600">Selected:</span>
            {selectedCategories.map((category) => (
              <Badge
                key={category}
                variant="secondary"
                className="cursor-pointer hover:bg-gray-200"
                onClick={() => removeCategory(category)}
                data-testid={`selected-category-${category.toLowerCase().replace(/\s+/g, '-')}`}
              >
                {category}
                <X className="ml-1 h-3 w-3" />
              </Badge>
            ))}
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAll}
              className="h-6 px-2 text-xs"
              data-testid="clear-all-categories"
            >
              Clear All
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};