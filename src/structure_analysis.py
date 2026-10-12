import os
from pathlib import Path
import pandas as pd

# 1. Define folder paths using pathlib
raw_data_dir = Path("../dataset")
structure_dir = Path("data_quality_audit/structure_analysis")

# 2. Ensure the output folder exists
structure_dir.mkdir(parents=True, exist_ok=True)

# 3. Find all CSV files in the raw folder
csv_files = list(raw_data_dir.glob("*.csv"))

if not csv_files:
    print(f" No CSV files found in '{raw_data_dir}'. Make sure your raw files are in this folder!")
else:
    print(f" Found {len(csv_files)} files. Starting Automated Structure Analysis...")

# 4. Loop through each file and generate its Markdown file
for file_path in csv_files:
    try:
        # Load a small sample (first 1000 rows) to analyze structure efficiently
        df = pd.read_csv(file_path, nrows=1000)
        
        file_name = file_path.name
        base_name = file_path.stem  # e.g., 'branches' from 'branches.csv'
        output_md_path = structure_dir / f"schema_{base_name}.md"
        
        # Build the markdown content as a string
        md_content = f"""# Structure Analysis: `{file_name}`
**Phase 1 Component:** Data Foundation & Preparation  
**Objective:** Document file layout, schemas, and relational keys before database ingestion.

### 1. File Metadata & Physical Layout
*   **File Name:** `{file_name}`
*   **Format:** Comma-Separated Values (`.csv`)
*   **Delimiter:** Comma (`,`)
*   **Granularity:** One row per individual record.

### 2. Physical Schema Blueprint

| Column Name | Inferred Data Type | Sample Value | Structural Rule / Constraint |
| :--- | :--- | :--- | :--- |
"""
        # Automatically populate the markdown table rows for each column
        for column in df.columns:
            sample_val = df[column].iloc[0] if not df[column].empty else "NULL"
            inferred_type = str(df[column].dtype).upper()
            
            # Map pandas objects/strings to standard database terms for clarity
            if inferred_type == 'OBJECT':
                inferred_type = 'VARCHAR / TEXT'
                
            # Add a basic blueprint flag reminder for your team
            constraint_flag = "Verify Key Constraint" if "id" in column.lower() or "code" in column.lower() else "Quantitative/Descriptive"
            
            # Format rows nicely into the Markdown template
            md_content += f"| **`{column}`** | `{inferred_type}` | `{sample_val}` | {constraint_flag} |\n"
            
        md_content += f"""
### 3. Relational Mapping & Required Transformations
*   **Primary Key Status:** *[Team to verify if an ID column uniquely identifies each row]*
*   **Required dbt Cleaning (Staging Layer):**
    1. Check for trailing whitespaces using `TRIM()`.
    2. Ensure proper numeric casting for metric fields.
    3. Standardize column cases to snake_case if necessary.
"""
        # Save the string to its individual markdown file
        output_md_path.write_text(md_content)
        print(f" Generated: schema_{base_name}.md")
        
    except FileNotFoundError:
        print(f" Error: The file {file_path.name} was missing mid-process.")
    except PermissionError:
        print(f" Error: Permission denied. Is {file_path.name} open in another program?")
    except Exception as e:
        print(f" Could not process {file_path.name} due to an error: {str(e)}")

print("\n Automation complete! Your structure analysis documentation folder is ready.")
