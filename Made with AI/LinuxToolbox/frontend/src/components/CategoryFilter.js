import React from 'react';

export const CategoryFilter = ({ categories, selectedCategory, onCategoryChange }) => {
  const displayCategories = categories || ['all'];
  
  return (
    <div className="flex flex-wrap gap-3 justify-center" data-testid="category-filter">
      {displayCategories.map((category) => (
        <button
          key={category}
          onClick={() => onCategoryChange(category)}
          className={`category-pill ${
            selectedCategory === category
              ? 'category-pill-active'
              : 'category-pill-inactive'
          }`}
          data-testid={`category-${category.toLowerCase().replace(/\s+/g, '-')}`}
        >
          {category === 'all' ? 'All Commands' : category}
        </button>
      ))}
    </div>
  );
};