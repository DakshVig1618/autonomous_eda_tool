import pandas as pd
import numpy as np
import os
from typing import Dict, Any

class DataScanner:
    """
    Scans raw CSV and Excel files to generate a lightweight metadata profile
    and chart-ready aggregated data for visual dashboards.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")
        self.df = self._load_data()
    
    def _load_data(self) -> pd.DataFrame:
        """
        Loads CSV or Excel safely into pandas dataframe
        """
        file_extn = os.path.splitext(self.file_path)[-1].lower()

        try:
            if file_extn == '.csv':
                return pd.read_csv(self.file_path)
            elif file_extn in ['.xlsx', '.xls']:
                return pd.read_excel(self.file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extn}")
        except Exception as e:
            raise RuntimeError(f"Error reading the file: {str(e)}")
    
    def generate_profile(self) -> Dict[str, Any]:
        """
        Analyzes the data to build a schema, statistics, and spot potential anomalies.
        """
        num_rows, num_cols = self.df.shape
        total_cells = num_rows * num_cols
        total_missing_cells = int(self.df.isnull().sum().sum())
        profile = {
            "summary": {
                "total_rows": num_rows,
                "total_cols": num_cols,
                "file_size_bytes": os.path.getsize(self.file_path),
                "total_missing_cells": total_missing_cells,
                "global_missing_percentage": round((total_missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0,
                "duplicate_rows": int(self.df.duplicated().sum())
            },
            "columns": {},
            "anomalies": {
                "high_missing_values": [],
                "single_value_columns": [],
                "highly_correlated_pairs": []
            },
            "charts": {
                "data_types_breakdown": {},
                "missing_values_per_column": [],
                "distributions": {},
                "correlation_matrix": []
            }
        }

        type_counts = {
            "numeric": 0,
            "categorical": 0,
            "datetime": 0,
            "boolean": 0,
            "other": 0
        }

        # Individual column scanning
        for column in self.df.columns:
            # count the total number of missing values
            missing_count = int(self.df[column].isnull().sum())

            # Compiute the percentage of missing values
            missing_percentage = round((missing_count / num_rows) * 100,2)

            # calculate the number of distinct categorical or numerical entries
            unique_count = int(self.df[column].nunique())

            # find the datatype of the column
            dtype = str(self.df[column].dtype)

            # Categorize datatypes for charts
            if pd.api.types.is_numeric_dtype(self.df[column]):
                type_counts["numeric"] += 1
            elif pd.api.types.is_datetime64_any_dtype(self.df[column]):
                type_counts["datetime"] += 1
            elif pd.api.types.is_bool_dtype(self.df[column]):
                type_counts["boolean"] += 1
            elif pd.api.types.is_string_dtype(self.df[column]) or self.df[column].dtype == 'object':
                type_counts["categorical"] += 1
            else:
                type_counts["other"] += 1
            # clean up missing data temporarily, grab the top 3 entries
            samples = self.df[column].dropna().head(3).astype(str).tolist()

            profile["columns"][column] = {
                "data_type": dtype,
                "missing_values": missing_count,
                "missing_percentage": missing_percentage,
                "unique_values_count": unique_count,
                "samples": samples
            }

            # Chart Data: Missing value array for bar charts
            if missing_count > 0:
                profile["charts"]["missing_values_per_column"].append({
                    "column": column,
                    "missing_count": missing_count,
                    "missing_percentage": missing_percentage
                })

            # >> static anamoly detection, flag severe missing data thresholds
            if missing_percentage > 30.0:
                profile["anomalies"]["high_missing_values"].append({
                    "column": column,
                    "percentage": missing_percentage
                })
            
            # columns with only 1 unique value offers zero mathematical variance for ML algorithms
            if unique_count == 1:
                profile["anomalies"]["single_value_columns"].append(column)

            # --- Chart Distributions (Histogram/Frequencies) ---
            if pd.api.types.is_numeric_dtype(self.df[column]) and unique_count > 1:
                # Binned Distributions for Numeric Columns
                clean_series = self.df[column].dropna()
                if len(clean_series) > 0:
                    counts, bin_edges = np.histogram(clean_series, bins=min(10, unique_count))
                    profile["charts"]["distributions"][column] = {
                        "type": "numeric",
                        "bins": [
                            {
                                "bin": f"{round(bin_edges[i], 1)}-{round(bin_edges[i + 1], 1)}",
                                "count": int(counts[i])
                            } for i in range(len(counts))
                        ]
                    }
            elif self.df[column].dtype == 'object' or unique_count <= 10:
                top_values = self.df[column].value_counts().head().to_dict()
                profile["charts"]["distributions"][column] = {
                    "type": "categorical",
                    "frequencies": [
                        {
                            "category": str(k),
                            "count": int (v)
                        } for k, v in top_values.items()
                    ]
                }
        profile["charts"]["data_types_breakdown"] = type_counts

        # --- Correlation Analysis and Heatmap Distribution
        num_df = self.df.select_dtypes(include=np.number)
        if num_df.shape[1] > 1:
            corr_matrix = num_df.corr().fillna(0)

            # Format heatmap charts data
            for col1 in corr_matrix.columns:
                for col2 in corr_matrix.columns:
                    profile["charts"]["correlation_matrix"].append({
                        "x": col1,
                        "y": col2,
                        "value": round(float(corr_matrix.loc[col1, col2]), 2)
                    })

            # Detect anomalies (correlation > 0.85)
            abs_corr = corr_matrix.abs()
            upper_tri = abs_corr.where(np.triu(np.ones(abs_corr.shape), k=1).astype(bool))

            for col in upper_tri.columns:
                high_corr = upper_tri[col][upper_tri[col] > 0.85]
                for row, val in high_corr.items():
                    profile["anomalies"]["highly_correlated_pairs"].append({
                        "col1": row,
                        "col2": col,
                        "correlation_coefficient": round(float(val), 2)
                    })
        return profile