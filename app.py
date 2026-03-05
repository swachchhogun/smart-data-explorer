import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Data Explorer", layout="wide")

st.title("📊 Smart Data Explorer")
st.write("Upload a dataset and interactively explore insights.")

uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    numeric_cols = df.select_dtypes(include="number").columns
    cat_cols = df.select_dtypes(include="object").columns

    # -------------------------
    # SIDEBAR FILTERS
    # -------------------------

    st.sidebar.header("Filters")

    filtered_df = df.copy()

    for col in cat_cols[:3]:
        options = st.sidebar.multiselect(
            f"Filter {col}",
            df[col].dropna().unique()
        )

        if options:
            filtered_df = filtered_df[filtered_df[col].isin(options)]

    st.sidebar.divider()

    st.sidebar.header("Analysis Options")

    analysis_type = st.sidebar.selectbox(
        "Choose Analysis Type",
        [
            "Dashboard Overview",
            "Distribution Analysis",
            "Category Comparison",
            "Correlation Analysis",
            "Trend Over Time"
        ]
    )

    # -------------------------
    # OVERVIEW METRICS
    # -------------------------

    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", filtered_df.shape[0])
    col2.metric("Columns", filtered_df.shape[1])
    col3.metric("Missing Values", filtered_df.isnull().sum().sum())

    st.divider()

    st.subheader("Preview")
    st.dataframe(filtered_df.head())

    st.divider()

    # -------------------------
    # DASHBOARD OVERVIEW
    # -------------------------

    if analysis_type == "Dashboard Overview":

        if len(numeric_cols) > 0:

            col = st.selectbox("Select numeric column for distribution", numeric_cols)

            fig = px.histogram(
                filtered_df,
                x=col,
                nbins=30,
                title=f"Distribution of {col}"
            )

            st.plotly_chart(fig, use_container_width=True)

        if len(cat_cols) > 0 and len(numeric_cols) > 0:

            cat = st.selectbox("Category column", cat_cols)
            num = st.selectbox("Numeric column", numeric_cols)

            grouped = filtered_df.groupby(cat)[num].mean().reset_index()

            fig = px.bar(
                grouped,
                x=cat,
                y=num,
                title=f"Average {num} by {cat}"
            )

            st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # DISTRIBUTION
    # -------------------------

    elif analysis_type == "Distribution Analysis":

        if len(numeric_cols) == 0:
            st.warning("No numeric columns found.")
        else:

            column = st.selectbox("Select Numeric Column", numeric_cols)

            fig = px.histogram(
                filtered_df,
                x=column,
                nbins=30,
                title=f"Distribution of {column}"
            )

            st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # CATEGORY COMPARISON
    # -------------------------

    elif analysis_type == "Category Comparison":

        if len(cat_cols) == 0 or len(numeric_cols) == 0:
            st.warning("Dataset needs categorical and numeric columns.")

        else:

            cat = st.selectbox("Category Column", cat_cols)
            num = st.selectbox("Numeric Column", numeric_cols)

            grouped = filtered_df.groupby(cat)[num].mean().reset_index()

            fig = px.bar(
                grouped,
                x=cat,
                y=num,
                title=f"Average {num} by {cat}"
            )

            st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # CORRELATION ANALYSIS
    # -------------------------

    elif analysis_type == "Correlation Analysis":

        if len(numeric_cols) < 2:
            st.warning("Need at least two numeric columns.")

        else:

            corr = filtered_df[numeric_cols].corr()

            fig = px.imshow(
                corr,
                text_auto=True,
                title="Correlation Heatmap"
            )

            st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # TREND ANALYSIS
    # -------------------------

    elif analysis_type == "Trend Over Time":

        if len(numeric_cols) == 0:
            st.warning("Need numeric columns.")

        else:

            date_col = st.selectbox("Time Column", filtered_df.columns)
            num_col = st.selectbox("Value Column", numeric_cols)

            fig = px.line(
                filtered_df,
                x=date_col,
                y=num_col,
                title=f"{num_col} over Time"
            )

            st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # KEY INSIGHTS
    # -------------------------

    st.divider()
    st.subheader("Key Insights")

    numeric_df = filtered_df.select_dtypes(include="number")

    if len(numeric_df.columns) > 0:

        highest_mean = numeric_df.mean().idxmax()
        highest_var = numeric_df.var().idxmax()

        st.write(f"📈 Column with highest average value: **{highest_mean}**")
        st.write(f"📊 Column with highest variance: **{highest_var}**")

        if len(numeric_df.columns) > 1:

            corr = numeric_df.corr().abs()
            corr_unstack = corr.unstack()
            corr_unstack = corr_unstack[corr_unstack < 1]

            if not corr_unstack.empty:

                strongest = corr_unstack.idxmax()

                st.write(
                    f"🔗 Strongest correlation between **{strongest[0]}** and **{strongest[1]}**"
                )
