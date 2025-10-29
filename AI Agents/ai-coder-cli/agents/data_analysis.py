
"""
Data Analysis Agent

Production-ready implementation for data analysis using pandas, numpy, and matplotlib.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from .base import Agent

# Import data science libraries
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class DataAnalysisAgent(Agent):
    """
    Production-ready Data Analysis Agent.
    
    Features:
        - Load data (CSV, Excel, JSON)
        - Statistical analysis
        - Data cleaning
        - Correlation analysis
        - Visualization
        - Data export
    """
    
    SUPPORTED_FORMATS = {'.csv': 'CSV', '.xlsx': 'Excel', '.json': 'JSON'}
    
    def __init__(self, name: str = "data_analysis",
                 description: str = "Data analysis agent", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        if not PANDAS_AVAILABLE:
            self.logger.error("pandas not installed. Install with: pip install pandas numpy")
        
        self._datasets: Dict[str, Any] = {}
        self.logger.info("Data Analysis Agent initialized")
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data analysis task."""
        self._log_action("Data analysis task", task[:100])
        
        if not PANDAS_AVAILABLE:
            return self._build_error_result(
                "pandas required. Install with: pip install pandas numpy"
            )
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            
            if operation == 'load':
                return self._load_data(context)
            elif operation == 'statistics':
                return self._calculate_statistics(context)
            elif operation == 'clean':
                return self._clean_data(context)
            elif operation == 'correlation':
                return self._calculate_correlations(context)
            elif operation == 'visualize':
                return self._create_visualization(context)
            elif operation == 'export':
                return self._export_data(context)
            else:
                return self._build_error_result("Unknown operation. Specify 'operation' in context")
        except Exception as e:
            self.logger.error(f"Task failed: {e}", exc_info=True)
            return self._build_error_result(f"Task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect operation from task."""
        task_lower = task.lower()
        if 'load' in task_lower or 'read' in task_lower:
            return 'load'
        elif 'stat' in task_lower or 'describe' in task_lower:
            return 'statistics'
        elif 'clean' in task_lower:
            return 'clean'
        elif 'correl' in task_lower:
            return 'correlation'
        elif 'plot' in task_lower or 'visual' in task_lower:
            return 'visualize'
        elif 'export' in task_lower or 'save' in task_lower:
            return 'export'
        return 'unknown'
    
    def _load_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Load data from file."""
        file_path = context.get('file_path')
        if not file_path:
            return self._build_error_result("File path required in context")
        
        path = Path(file_path)
        if not path.exists():
            return self._build_error_result(f"File not found: {file_path}")
        
        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_FORMATS:
            return self._build_error_result(f"Unsupported format: {suffix}")
        
        try:
            if suffix == '.csv':
                df = pd.read_csv(path)
            elif suffix == '.xlsx':
                df = pd.read_excel(path)
            elif suffix == '.json':
                df = pd.read_json(path)
            
            dataset_id = f"dataset_{len(self._datasets)}"
            self._datasets[dataset_id] = df
            
            return self._build_success_result(
                f"Loaded {df.shape[0]} rows × {df.shape[1]} columns",
                data={
                    'dataset_id': dataset_id,
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
                },
                next_context={'dataset_id': dataset_id, 'data': df}
            )
        except Exception as e:
            return self._build_error_result(f"Load failed: {str(e)}", error=e)
    
    def _calculate_statistics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistics."""
        df = self._get_dataframe(context)
        if df is None:
            return self._build_error_result("Data required. Provide 'data' or 'dataset_id'")
        
        try:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            stats = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'numeric_columns': len(numeric_cols),
                'missing_values': int(df.isna().sum().sum())
            }
            
            if numeric_cols:
                numeric_stats = {}
                for col in numeric_cols:
                    numeric_stats[col] = {
                        'mean': float(df[col].mean()),
                        'median': float(df[col].median()),
                        'std': float(df[col].std()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max())
                    }
                stats['numeric_statistics'] = numeric_stats
            
            return self._build_success_result(
                "Statistics calculated",
                data=stats
            )
        except Exception as e:
            return self._build_error_result(f"Statistics failed: {str(e)}", error=e)
    
    def _clean_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clean data."""
        df = self._get_dataframe(context)
        if df is None:
            return self._build_error_result("Data required")
        
        try:
            original_rows = len(df)
            df_cleaned = df.copy()
            
            # Remove duplicates
            duplicates = df_cleaned.duplicated().sum()
            df_cleaned = df_cleaned.drop_duplicates()
            
            # Handle missing values
            strategy = context.get('missing_strategy', 'drop')
            if strategy == 'drop':
                df_cleaned = df_cleaned.dropna()
            elif strategy == 'fill_mean':
                numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    df_cleaned[col].fillna(df_cleaned[col].mean(), inplace=True)
            
            dataset_id = f"cleaned_{len(self._datasets)}"
            self._datasets[dataset_id] = df_cleaned
            
            return self._build_success_result(
                f"Data cleaned: {len(df_cleaned)} rows remaining",
                data={
                    'dataset_id': dataset_id,
                    'original_rows': original_rows,
                    'final_rows': len(df_cleaned),
                    'rows_removed': original_rows - len(df_cleaned),
                    'duplicates_removed': int(duplicates)
                },
                next_context={'dataset_id': dataset_id, 'data': df_cleaned}
            )
        except Exception as e:
            return self._build_error_result(f"Cleaning failed: {str(e)}", error=e)
    
    def _calculate_correlations(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate correlations."""
        df = self._get_dataframe(context)
        if df is None:
            return self._build_error_result("Data required")
        
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) < 2:
                return self._build_error_result("Need at least 2 numeric columns")
            
            corr_matrix = numeric_df.corr()
            
            # Find strong correlations
            strong_corr = []
            threshold = context.get('threshold', 0.7)
            
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) >= threshold:
                        strong_corr.append({
                            'col1': corr_matrix.columns[i],
                            'col2': corr_matrix.columns[j],
                            'correlation': round(float(corr_val), 4)
                        })
            
            return self._build_success_result(
                f"Found {len(strong_corr)} strong correlations",
                data={
                    'correlation_matrix': corr_matrix.to_dict(),
                    'strong_correlations': strong_corr,
                    'threshold': threshold
                }
            )
        except Exception as e:
            return self._build_error_result(f"Correlation failed: {str(e)}", error=e)
    
    def _create_visualization(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualization."""
        if not MATPLOTLIB_AVAILABLE:
            return self._build_error_result("matplotlib required for visualization")
        
        df = self._get_dataframe(context)
        if df is None:
            return self._build_error_result("Data required")
        
        plot_type = context.get('plot_type', 'histogram')
        output_path = context.get('output_path', f'plot_{plot_type}.png')
        
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if plot_type == 'histogram':
                column = context.get('column')
                if not column:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    column = numeric_cols[0] if len(numeric_cols) > 0 else None
                
                if column:
                    df[column].hist(bins=30, ax=ax)
                    ax.set_title(f'Distribution of {column}')
                    ax.set_xlabel(column)
                    ax.set_ylabel('Frequency')
            
            elif plot_type == 'scatter':
                x_col = context.get('x_column')
                y_col = context.get('y_column')
                if x_col and y_col:
                    ax.scatter(df[x_col], df[y_col], alpha=0.5)
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
                    ax.set_title(f'{y_col} vs {x_col}')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=100)
            plt.close()
            
            return self._build_success_result(
                f"Visualization saved to {output_path}",
                data={'plot_type': plot_type, 'output_path': output_path}
            )
        except Exception as e:
            plt.close('all')
            return self._build_error_result(f"Visualization failed: {str(e)}", error=e)
    
    def _export_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Export data."""
        df = self._get_dataframe(context)
        if df is None:
            return self._build_error_result("Data required")
        
        output_path = context.get('output_path', 'output.csv')
        path = Path(output_path)
        
        try:
            if path.suffix == '.csv':
                df.to_csv(path, index=False)
            elif path.suffix == '.xlsx':
                df.to_excel(path, index=False)
            elif path.suffix == '.json':
                df.to_json(path)
            else:
                return self._build_error_result(f"Unsupported export format: {path.suffix}")
            
            return self._build_success_result(
                f"Data exported to {output_path}",
                data={'output_path': str(path), 'rows': len(df), 'columns': len(df.columns)}
            )
        except Exception as e:
            return self._build_error_result(f"Export failed: {str(e)}", error=e)
    
    def _get_dataframe(self, context: Dict[str, Any]) -> Optional['pd.DataFrame']:
        """Get DataFrame from context."""
        if 'data' in context:
            return context['data']
        
        dataset_id = context.get('dataset_id')
        if dataset_id and dataset_id in self._datasets:
            return self._datasets[dataset_id]
        
        return None
