export const formatLabel = (name: string): string => {
  if (!name) return '';
  
  // Convert camelCase or snake_case to Title Case
  return name
    .replace(/([A-Z])/g, ' $1') // Add space before capital letters
    .replace(/_/g, ' ') // Replace underscores with spaces
    .replace(/\b\w/g, l => l.toUpperCase()) // Capitalize first letter of each word
    .trim();
}; 