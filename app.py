import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Smart Data Explorer")

file = st.file_uploader("Upload CSV dataset", type=["csv"])

if file:
    df = pd.read_csv(file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    st.subheader("Dataset Shape")
    st.write(df.shape)

    st.subheader("Summary Statistics")
    st.write(df.describe())

    numeric_cols = df.select_dtypes(include=["float64","int64"]).columns

    if len(numeric_cols) > 0:
        column = st.selectbox("Choose column for visualization", numeric_cols)

        fig, ax = plt.subplots()
        ax.hist(df[column], bins=20)
        ax.set_title(column)

        st.pyplot(fig)

        st.subheader("Correlation Matrix")
        st.write(df[numeric_cols].corr())