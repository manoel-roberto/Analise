---
name: data-exploration-profiling
description: Profile and explore datasets to understand their shape, quality, and patterns before analysis. Use when encountering a new dataset, assessing data quality, discovering column distributions, identifying nulls and outliers, or deciding which dimensions to analyze.
metadata:
  mcpmarket-version: 1.1.0
---

# Data Exploration & Profiling Skill

Systematic methodology for profiling datasets, assessing data quality, discovering patterns, performing Exploratory Data Analysis (EDA), and understanding schemas across tabular files (CSV, Excel `.xls`/`.xlsx`, Parquet, JSON) and relational/cloud databases (SQLite, PostgreSQL, BigQuery, DuckDB).

---

## 🎯 When to Use

- **New Dataset Ingestion**: When encountering an unfamiliar dataset or database table.
- **Pre-Modeling Check**: Understanding distributions, missingness, and variance before feature engineering or ML modeling.
- **Data Quality Assessment**: Evaluating completeness, consistency, and detecting anomalies/outliers.
- **Hypothesis Generation**: Discovering relationships, group aggregations, and segment differences.
- **Stakeholder Reporting**: Creating clear schema documentation, visual distributions, and data quality summaries.

---

## 1. Data Profiling Methodology

### Phase 1: Structural Understanding

Before analyzing any data, understand its high-level structure:

**Table-level questions:**
- How many rows and columns? (`df.shape`)
- What is the grain (one row per what)?
- What is the primary key? Is it unique? (`df['id'].nunique() == len(df)`)
- When was the data last updated?
- How far back does the data go?

**Column classification:**
Categorize each column as one of:
- **Identifier**: Unique keys, foreign keys, entity IDs
- **Dimension**: Categorical attributes for grouping/filtering (status, type, region, category)
- **Metric**: Quantitative values for measurement (revenue, count, duration, score)
- **Temporal**: Dates and timestamps (created_at, updated_at, event_date)
- **Text**: Free-form text fields (description, notes, name)
- **Boolean**: True/false flags
- **Structural**: JSON, arrays, nested structures

---

### Phase 2: Column-Level & Advanced Statistical Profiling

For each column, compute:

**All columns:**
- Null count and null rate (`nulls / total`)
- Distinct count and cardinality ratio (`distinct / total`)
- Most common values (top 5–10 with frequencies and normalized rates)
- Least common values (bottom 5 to spot anomalies)

**Numeric columns (metrics):**
- Min, max, mean, median (`p50`)
- Standard deviation and **Variance** (`df[col].var()`)
- Percentiles: `p1`, `p5`, `p25`, `p75`, `p95`, `p99`
- **Skewness** (`df[col].skew()`): Detect right/left tail asymmetry
- **Kurtosis** (`df[col].kurtosis()`): Detect heavy tails and extreme outlier risk
- Zero count and negative count (if unexpected)

**String columns (dimensions, text):**
- Min length, max length, average length
- Empty string count
- Pattern analysis (do values follow expected formats/regex?)
- Case consistency (all upper, all lower, mixed?)
- Leading/trailing whitespace count

**Date/timestamp columns:**
- Min date, max date
- Null dates
- Future dates (if unexpected)
- Distribution by month/week/day
- Gaps in time series

**Boolean columns:**
- True count, false count, null count
- True rate (`true / total`)

---

### Phase 3: Relationship & Groupby Discovery

After profiling individual columns:

- **Foreign key candidates**: ID columns that might link to other tables
- **Hierarchies**: Columns that form natural drill-down paths (`country` > `state` > `city`)
- **Groupby Aggregations**: Compare metric distributions across categories:
  ```python
  df.groupby('region')[['age', 'income']].agg(['mean', 'median', 'std', 'count'])
  ```
- **Correlation with Target Variable**: If a target metric/label exists:
  ```python
  df.corr(numeric_only=True)['target'].sort_values(ascending=False)
  ```
- **Correlations & Multicollinearity**: Numeric columns with high correlation (`|r| > 0.7`)
- **Derived & Redundant columns**: Columns with identical or near-identical information

---

## 2. Quality Assessment Framework

### Completeness Score

Rate each column:
- **Complete** (>99% non-null): 🟢 Green
- **Mostly complete** (95–99%): 🟡 Yellow — investigate nulls
- **Incomplete** (80–95%): 🟠 Orange — understand why and whether it matters
- **Sparse** (<80%): 🔴 Red — may not be usable without imputation

### Consistency Checks

Look for:
- **Value format inconsistency**: Same concept represented differently ("USA", "US", "United States", "us")
- **Type inconsistency**: Numbers stored as strings, dates in various formats
- **Referential integrity**: Foreign keys that don't match any parent record
- **Business rule violations**: Negative quantities, end dates before start dates, percentages > 100
- **Cross-column consistency**: `status = "completed"` but `completed_at` is null

### Accuracy Indicators

Red flags that suggest accuracy issues:
- **Placeholder values**: `0`, `-1`, `999999`, `"N/A"`, `"TBD"`, `"test"`, `"xxx"`
- **Default values**: Suspiciously high frequency of a single value
- **Stale data**: `updated_at` shows no recent changes in an active system
- **Impossible values**: Ages > 150, dates in the far future, negative durations
- **Round number bias**: All values ending in 0 or 5 (suggests estimation, not measurement)

### Timeliness Assessment

- When was the table last updated?
- What is the expected update frequency?
- Is there a lag between event time and load time?
- Are there gaps in the time series?

---

## 3. Pattern Discovery Techniques

### Distribution Analysis

For numeric columns, characterize the distribution:
- **Normal**: Mean and median are close, bell-shaped
- **Skewed right**: Long tail of high values (common for revenue, session duration)
- **Skewed left**: Long tail of low values
- **Bimodal**: Two peaks (suggests two distinct populations)
- **Power law**: Few very large values, many small ones (common for user activity)
- **Uniform**: Roughly equal frequency across range (often synthetic or random)

### Temporal Patterns

For time series data, look for:
- **Trend**: Sustained upward or downward movement
- **Seasonality**: Repeating patterns (weekly, monthly, quarterly, annual)
- **Day-of-week effects**: Weekday vs. weekend differences
- **Holiday effects**: Drops or spikes around known holidays
- **Change points**: Sudden shifts in level or trend
- **Anomalies**: Individual data points that break the pattern

---

## 4. Implementation & Visualization Patterns

### Python Automated Profiling Function

```python
import pandas as pd
import numpy as np

def profile_dataset(df: pd.DataFrame) -> dict:
    """Generate a comprehensive profiling summary of a pandas DataFrame."""
    total_rows = len(df)
    profile = {
        "overview": {
            "num_rows": total_rows,
            "num_cols": len(df.columns),
            "total_nulls": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
        },
        "columns": {}
    }
    
    for col in df.columns:
        s = df[col]
        null_cnt = int(s.isnull().sum())
        null_pct = round((null_cnt / total_rows) * 100, 2) if total_rows > 0 else 0
        
        col_info = {
            "dtype": str(s.dtype),
            "null_count": null_cnt,
            "null_percent": null_pct,
            "n_unique": int(s.nunique())
        }
        
        if pd.api.types.is_numeric_dtype(s):
            s_clean = s.dropna()
            if not s_clean.empty:
                col_info.update({
                    "min": float(s_clean.min()),
                    "p5": float(np.percentile(s_clean, 5)),
                    "p25": float(np.percentile(s_clean, 25)),
                    "median": float(s_clean.median()),
                    "p75": float(np.percentile(s_clean, 75)),
                    "p95": float(np.percentile(s_clean, 95)),
                    "max": float(s_clean.max()),
                    "mean": float(s_clean.mean()),
                    "std": float(s_clean.std()),
                    "var": float(s_clean.var()),
                    "skewness": float(s_clean.skew()),
                    "kurtosis": float(s_clean.kurtosis()),
                    "zeros": int((s_clean == 0).sum()),
                    "negatives": int((s_clean < 0).sum())
                })
        elif pd.api.types.is_datetime64_any_dtype(s):
            s_clean = s.dropna()
            if not s_clean.empty:
                col_info.update({
                    "min_date": str(s_clean.min()),
                    "max_date": str(s_clean.max())
                })
        elif pd.api.types.is_string_dtype(s) or pd.api.types.is_object_dtype(s):
            s_clean = s.dropna().astype(str)
            top_vals = s_clean.value_counts().head(5).to_dict()
            col_info.update({
                "min_length": int(s_clean.str.len().min()) if not s_clean.empty else 0,
                "max_length": int(s_clean.str.len().max()) if not s_clean.empty else 0,
                "empty_strings": int((s_clean == "").sum()),
                "top_5_values": {k: int(v) for k, v in top_vals.items()}
            })
            
        profile["columns"][col] = col_info
        
    return profile
```

### Visualization Patterns (Matplotlib & Seaborn)

```python
import matplotlib.pyplot as plt
import seaborn as sns

def generate_eda_plots(df: pd.DataFrame, num_cols: list, cat_col: str = None):
    """Generate core EDA visual distributions and correlation heatmap."""
    # 1. Distribution Plots & Boxplots
    fig, axes = plt.subplots(len(num_cols), 2, figsize=(12, 4 * len(num_cols)))
    for i, col in enumerate(num_cols):
        # Histogram
        sns.histplot(df[col], kde=True, ax=axes[i, 0] if len(num_cols) > 1 else axes[0])
        (axes[i, 0] if len(num_cols) > 1 else axes[0]).set_title(f'{col} Distribution')
        
        # Boxplot by category (if specified)
        if cat_col and cat_col in df.columns:
            sns.boxplot(x=cat_col, y=col, data=df, ax=axes[i, 1] if len(num_cols) > 1 else axes[1])
            (axes[i, 1] if len(num_cols) > 1 else axes[1]).set_title(f'{col} by {cat_col}')
    plt.tight_layout()
    plt.show()

    # 2. Correlation Matrix Heatmap
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        plt.figure(figsize=(10, 8))
        sns.heatmap(numeric_df.corr(), annot=True, fmt='.2f', cmap='coolwarm', center=0)
        plt.title('Correlation Matrix Heatmap')
        plt.show()
        
    # 3. Pairplot for key metrics
    if len(num_cols) >= 2:
        sns.pairplot(df[num_cols[:4]], diag_kind='kde')
        plt.show()
```

### High-Performance DuckDB Profiling

For zero-setup, ultra-fast profiling directly over CSV or Parquet files:

```sql
-- Summarize full dataset instantly
SUMMARIZE SELECT * FROM 'data.csv';

-- Detect duplicate key counts
SELECT key_column, COUNT(*) 
FROM 'data.csv' 
GROUP BY key_column 
HAVING COUNT(*) > 1;
```

---

## 5. Schema Documentation & Lineage

### Schema Documentation Template

```markdown
## Table: [schema.table_name]

**Description**: [What this table represents]
**Grain**: [One row per...]
**Primary Key**: [column(s)]
**Row Count**: [approximate, with date]
**Update Frequency**: [real-time / hourly / daily / weekly]
**Owner**: [team or person responsible]

### Key Columns

| Column | Type | Description | Example Values | Notes |
|--------|------|-------------|----------------|-------|
| user_id | STRING | Unique user identifier | "usr_abc123" | FK to users.id |
| event_type | STRING | Type of event | "click", "view", "purchase" | 15 distinct values |
| revenue | DECIMAL | Transaction revenue in USD | 29.99, 149.00 | Null for non-purchase events |
| created_at | TIMESTAMP | When the event occurred | 2024-01-15 14:23:01 | Partitioned on this column |

### Relationships
- Joins to `users` on `user_id`
- Joins to `products` on `product_id`
- Parent of `event_details` (1:many on event_id)

### Known Issues
- [List any known data quality issues]
- [Note any gotchas for analysts]

### Common Query Patterns
- [Typical use cases for this table]
```

### Lineage and Dependencies Tracing

When exploring an unfamiliar data environment:
1. Start with the "output" tables (what reports or dashboards consume).
2. Trace upstream: What tables feed into them?
3. Identify raw/staging/mart layers.
4. Map the transformation chain from raw data to analytical tables.
5. Note where data is enriched, filtered, or aggregated.
