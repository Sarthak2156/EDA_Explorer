"""
EDA Explorer - Interactive Exploratory Data Analysis App
Upload any CSV and instantly get statistics, visualizations, cleaning tools,
correlation insights, and anomaly detection.

Run with: streamlit run eda_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# ---------------------------------------------------------------------------
# Page config & style
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EDA Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid")
PALETTE = "viridis"

CUSTOM_CSS = """
<style>
    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #64748b;
        font-size: 1.05rem;
        margin-top: 0.2rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<p class="main-header">📊 EDA Explorer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Upload any CSV and instantly perform complete '
    'Exploratory Data Analysis — statistics, visualizations, and anomaly detection.</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar - Upload & Info
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    st.markdown("---")
    st.markdown(
        """
        **What this app does**
        - 🔍 Instant dataset overview
        - 🧹 Data cleaning (missing values, duplicates)
        - 📈 Descriptive statistics
        - 📊 Univariate analysis
        - 🔗 Bivariate & multivariate analysis
        - 🚨 Anomaly / outlier detection
        - 💡 Auto-generated insights
        """
    )

if uploaded_file is None:
    st.info("👆 Upload a CSV file from the sidebar to get started.")
    st.markdown(
        """
        ### How to use
        1. Upload a CSV file (any dataset — sales, weather, Titanic, Iris, etc.)
        2. Explore each tab: Overview, Descriptive Stats, Univariate, Bivariate/Multivariate, Anomalies
        3. Pick columns from the dropdowns to generate charts on demand
        """
    )
    st.stop()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read this file as CSV: {e}")
    st.stop()

numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
categorical_cols = df.select_dtypes(exclude=np.number).columns.tolist()

st.success(f"Loaded **{uploaded_file.name}** — {df.shape[0]} rows × {df.shape[1]} columns")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_overview, tab_clean, tab_stats, tab_uni, tab_bi, tab_anomaly, tab_insights = st.tabs(
    ["🔍 Overview", "🧹 Clean Data", "📈 Descriptive Stats", "📊 Univariate",
     "🔗 Bivariate & Multivariate", "🚨 Anomalies", "💡 Insights"]
)

# ---------------------------------------------------------------------------
# TAB 1: Overview
# ---------------------------------------------------------------------------
with tab_overview:
    st.subheader("Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Numeric Columns", len(numeric_cols))
    c4.metric("Missing Values", int(df.isnull().sum().sum()))

    st.subheader("Column Info")
    info_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values,
        "Missing Values": df.isnull().sum().values,
        "Missing %": (df.isnull().sum().values / len(df) * 100).round(2),
        "Unique Values": [df[c].nunique() for c in df.columns],
    })
    st.dataframe(info_df, use_container_width=True)

    if df.duplicated().sum() > 0:
        st.warning(f"⚠️ Found {df.duplicated().sum()} duplicate rows in the dataset.")
    else:
        st.success("✅ No duplicate rows found.")

# ---------------------------------------------------------------------------
# TAB 2: Clean Data
# ---------------------------------------------------------------------------
with tab_clean:
    st.subheader("Data Cleaning")
    st.caption("Handle missing values, duplicates, and outliers, then download the cleaned dataset.")

    clean_df = df.copy()

    col1, col2 = st.columns(2)
    with col1:
        missing_strategy = st.selectbox(
            "Missing value strategy",
            ["Leave as-is", "Drop rows with missing values", "Fill numeric with median", "Fill numeric with mean"],
        )
    with col2:
        dedupe = st.checkbox("Remove duplicate rows", value=True)
        cap_outliers = st.checkbox("Cap outliers (IQR method) on numeric columns", value=False)

    if missing_strategy == "Drop rows with missing values":
        clean_df = clean_df.dropna()
    elif missing_strategy == "Fill numeric with median":
        for c in numeric_cols:
            clean_df[c] = clean_df[c].fillna(clean_df[c].median())
    elif missing_strategy == "Fill numeric with mean":
        for c in numeric_cols:
            clean_df[c] = clean_df[c].fillna(clean_df[c].mean())

    if dedupe:
        clean_df = clean_df.drop_duplicates()

    if cap_outliers:
        for c in numeric_cols:
            q1, q3 = clean_df[c].quantile(0.25), clean_df[c].quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            clean_df[c] = clean_df[c].clip(lower=lower, upper=upper)

    c1, c2, c3 = st.columns(3)
    c1.metric("Original Rows", df.shape[0])
    c2.metric("Cleaned Rows", clean_df.shape[0])
    c3.metric("Remaining Missing Values", int(clean_df.isnull().sum().sum()))

    st.dataframe(clean_df.head(20), use_container_width=True)

    st.download_button(
        "⬇️ Download cleaned CSV",
        data=clean_df.to_csv(index=False).encode("utf-8"),
        file_name=f"cleaned_{uploaded_file.name}",
        mime="text/csv",
    )

# ---------------------------------------------------------------------------
# TAB 3: Descriptive Statistics
# ---------------------------------------------------------------------------
with tab_stats:
    if not numeric_cols:
        st.info("No numeric columns found for descriptive statistics.")
    else:
        st.subheader("Measures of Central Tendency & Dispersion")

        desc_rows = []
        for col in numeric_cols:
            series = df[col].dropna()
            mode_val = series.mode()
            desc_rows.append({
                "Column": col,
                "Mean": round(series.mean(), 3),
                "Median": round(series.median(), 3),
                "Mode": round(mode_val.iloc[0], 3) if not mode_val.empty else np.nan,
                "Range": round(series.max() - series.min(), 3),
                "Variance": round(series.var(), 3),
                "Std Dev": round(series.std(), 3),
                "Skewness": round(series.skew(), 3),
                "Kurtosis": round(series.kurt(), 3),
            })
        stats_df = pd.DataFrame(desc_rows)
        st.dataframe(stats_df, use_container_width=True)

        st.caption(
            "**Skewness** > 0 → right-tailed, < 0 → left-tailed. "
            "**Kurtosis** > 0 → heavier tails than normal distribution."
        )

        st.subheader("Distribution Shape")
        shape_col = st.selectbox("Choose a column to inspect its distribution", numeric_cols, key="shape_col")
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.histplot(df[shape_col].dropna(), kde=True, ax=ax, color="#6366f1")
        ax.axvline(df[shape_col].mean(), color="red", linestyle="--", label="Mean")
        ax.axvline(df[shape_col].median(), color="green", linestyle="--", label="Median")
        ax.legend()
        ax.set_title(f"Distribution of {shape_col}")
        st.pyplot(fig)

# ---------------------------------------------------------------------------
# TAB 4: Univariate Analysis
# ---------------------------------------------------------------------------
with tab_uni:
    if not numeric_cols:
        st.info("No numeric columns found for univariate analysis.")
    else:
        st.subheader("Histogram & Box Plot")
        uni_col = st.selectbox("Choose a numeric column", numeric_cols, key="uni_col")

        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.histplot(df[uni_col].dropna(), kde=True, ax=ax, color="#06b6d4")
            ax.set_title(f"Histogram of {uni_col}")
            st.pyplot(fig)
        with col2:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.boxplot(y=df[uni_col].dropna(), ax=ax, color="#a78bfa")
            ax.set_title(f"Box Plot of {uni_col}")
            st.pyplot(fig)

    if categorical_cols:
        st.subheader("Categorical Column Frequency")
        cat_col = st.selectbox("Choose a categorical column", categorical_cols, key="cat_col")
        fig, ax = plt.subplots(figsize=(8, 4))
        df[cat_col].value_counts().head(15).plot(kind="bar", ax=ax, color="#06b6d4")
        ax.set_title(f"Frequency of {cat_col}")
        ax.set_ylabel("Count")
        st.pyplot(fig)

# ---------------------------------------------------------------------------
# TAB 5: Bivariate & Multivariate Analysis
# ---------------------------------------------------------------------------
with tab_bi:
    if len(numeric_cols) < 2:
        st.info("Need at least 2 numeric columns for bivariate/multivariate analysis.")
    else:
        st.subheader("Scatter Plot (Bivariate)")
        c1, c2 = st.columns(2)
        x_col = c1.selectbox("X-axis column", numeric_cols, index=0, key="x_col")
        y_col = c2.selectbox("Y-axis column", numeric_cols, index=1, key="y_col")

        fig, ax = plt.subplots(figsize=(7, 4.5))
        sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax, color="#6366f1", alpha=0.7)
        ax.set_title(f"{x_col} vs {y_col}")
        st.pyplot(fig)

        corr_val = df[x_col].corr(df[y_col])
        st.metric(f"Correlation ({x_col} ↔ {y_col})", round(corr_val, 3))

        st.subheader("Correlation Matrix & Heatmap")
        corr_matrix = df[numeric_cols].corr()
        st.dataframe(corr_matrix.round(2), use_container_width=True)

        fig, ax = plt.subplots(figsize=(min(2 + len(numeric_cols), 10), min(2 + len(numeric_cols), 8)))
        sns.heatmap(corr_matrix, annot=True, cmap=PALETTE, fmt=".2f", ax=ax)
        ax.set_title("Correlation Heatmap")
        st.pyplot(fig)

        st.subheader("Pair Plot (Multivariate)")
        max_pairplot_cols = 5
        default_cols = numeric_cols[:min(4, len(numeric_cols))]
        pair_cols = st.multiselect(
            "Choose columns for pair plot (max 5 recommended)",
            numeric_cols, default=default_cols, key="pair_cols"
        )
        if len(pair_cols) >= 2:
            if len(pair_cols) > max_pairplot_cols:
                st.warning(f"Using first {max_pairplot_cols} columns to keep rendering fast.")
                pair_cols = pair_cols[:max_pairplot_cols]
            with st.spinner("Generating pair plot..."):
                pair_fig = sns.pairplot(df[pair_cols].dropna(), diag_kind="kde", plot_kws={"alpha": 0.6})
                st.pyplot(pair_fig)
        else:
            st.info("Select at least 2 columns to generate a pair plot.")

        st.subheader("Strongest Relationships Detected")
        corr_pairs = (
            corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            .stack()
            .reset_index()
        )
        corr_pairs.columns = ["Column 1", "Column 2", "Correlation"]
        corr_pairs["Abs Correlation"] = corr_pairs["Correlation"].abs()
        top_corr = corr_pairs.sort_values("Abs Correlation", ascending=False).head(5)
        st.dataframe(top_corr[["Column 1", "Column 2", "Correlation"]].round(3), use_container_width=True)

# ---------------------------------------------------------------------------
# TAB 6: Anomaly Detection
# ---------------------------------------------------------------------------
with tab_anomaly:
    if not numeric_cols:
        st.info("No numeric columns found for anomaly detection.")
    else:
        st.subheader("Outlier Detection")
        method = st.radio("Detection method", ["IQR (Interquartile Range)", "Z-Score"], horizontal=True)
        anomaly_col = st.selectbox("Choose a column to check for outliers", numeric_cols, key="anomaly_col")

        series = df[anomaly_col].dropna()

        if method.startswith("IQR"):
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outliers = df[(df[anomaly_col] < lower) | (df[anomaly_col] > upper)]
        else:
            z_scores = np.abs(stats.zscore(series))
            outlier_idx = series.index[z_scores > 3]
            outliers = df.loc[outlier_idx]
            lower, upper = series.mean() - 3 * series.std(), series.mean() + 3 * series.std()

        c1, c2, c3 = st.columns(3)
        c1.metric("Outliers Found", len(outliers))
        c2.metric("Lower Bound", round(lower, 2))
        c3.metric("Upper Bound", round(upper, 2))

        fig, ax = plt.subplots(figsize=(8, 3.5))
        sns.boxplot(x=series, ax=ax, color="#f97316")
        ax.set_title(f"Box Plot with Outlier Bounds — {anomaly_col}")
        st.pyplot(fig)

        if len(outliers) > 0:
            st.write("**Flagged rows:**")
            st.dataframe(outliers, use_container_width=True)
            st.download_button(
                "⬇️ Download flagged rows as CSV",
                data=outliers.to_csv(index=False).encode("utf-8"),
                file_name=f"outliers_{anomaly_col}.csv",
                mime="text/csv",
            )
        else:
            st.success("No outliers detected with this method.")

# ---------------------------------------------------------------------------
# TAB 7: Auto-Generated Insights
# ---------------------------------------------------------------------------
with tab_insights:
    st.subheader("Quick Insights")
    st.caption("A plain-language summary automatically generated from the dataset.")

    insights = []

    insights.append(f"The dataset has **{df.shape[0]} rows** and **{df.shape[1]} columns** "
                     f"({len(numeric_cols)} numeric, {len(categorical_cols)} categorical).")

    total_missing = int(df.isnull().sum().sum())
    if total_missing > 0:
        worst_col = df.isnull().sum().idxmax()
        insights.append(f"There are **{total_missing} missing values** in total — the column with the "
                         f"most gaps is **{worst_col}** ({df[worst_col].isnull().sum()} missing).")
    else:
        insights.append("No missing values were found — the dataset is complete.")

    dup_count = df.duplicated().sum()
    if dup_count > 0:
        insights.append(f"Found **{dup_count} duplicate rows** — consider removing them in the Clean Data tab.")

    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        corr_pairs = (
            corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            .stack().reset_index()
        )
        corr_pairs.columns = ["Col1", "Col2", "Correlation"]
        if not corr_pairs.empty:
            top = corr_pairs.loc[corr_pairs["Correlation"].abs().idxmax()]
            strength = "strong" if abs(top["Correlation"]) > 0.7 else "moderate" if abs(top["Correlation"]) > 0.4 else "weak"
            direction = "positive" if top["Correlation"] > 0 else "negative"
            insights.append(f"The strongest relationship is between **{top['Col1']}** and **{top['Col2']}** "
                             f"— a {strength} {direction} correlation ({top['Correlation']:.2f}).")

    for col in numeric_cols[:6]:
        skew = df[col].dropna().skew()
        if abs(skew) > 1:
            direction = "right" if skew > 0 else "left"
            insights.append(f"**{col}** is noticeably skewed to the {direction} (skewness = {skew:.2f}).")

    for i, text in enumerate(insights, 1):
        st.markdown(f"{i}. {text}")

    if categorical_cols:
        st.subheader("Categorical Column Summary")
        for col in categorical_cols[:5]:
            top_val = df[col].value_counts().idxmax()
            top_pct = df[col].value_counts(normalize=True).max() * 100
            st.markdown(f"- **{col}**: most common value is `{top_val}` ({top_pct:.1f}% of rows)")

st.markdown("---")
st.caption("EDA Explorer — Interactive Exploratory Data Analysis")