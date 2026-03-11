🚀 DataLens — Smart Data Explorer

Upload any CSV and instantly generate interactive charts, AI insights, and a beautiful PDF report — all in one place.

🔗 Live Demo
https://smart-data-explorer-mgappjprtpxzeqvn69pew65.streamlit.app

✨ Features
📂 Upload Any Dataset

Simply upload a CSV file and DataLens automatically analyzes it.

🧹 Automatic Data Cleaning

Null value handling

Duplicate removal

Automatic type detection

Dataset health profiling

📊 Interactive Visualizations

Generate 9 chart modes instantly:

Histogram

Heatmap

Scatter plot

Scatter matrix

Correlation analysis

Box plots

Trend over time

Category comparisons

Distribution analysis

All charts are interactive and powered by Plotly.

🤖 AI-Powered Insights

Ask questions about your dataset in natural language.

Example:

Which columns are most correlated?
What trends exist in this dataset?
Which values are outliers?

Powered by Llama 3.3 70B via Groq API.

📈 Data Quality Profiling

Automatically calculates:

Column health scores

Completeness metrics

Outlier detection using the IQR method

📑 PDF Report Generator

Export a professional report containing:

Dataset overview

Statistical summaries

Data cleaning logs

AI insights

🎛 Smart Filters

Filter your dataset by:

Category

Numeric ranges

All charts update instantly.

📤 Export Options

Download results as:

CSV

XLSX

PDF report

🛠 Built With

Core Technologies

Python

Streamlit

Pandas

NumPy

Visualization

Plotly

AI

Groq API

Llama 3.3 70B

Reporting

ReportLab

⚙️ Run Locally

Clone the repository

git clone https://github.com/swachchhogun/smart-data-explorer
cd smart-data-explorer

Install dependencies

pip install -r requirements.txt

Run the app

streamlit run app.py
🔑 Enable AI Features

1️⃣ Create a free account
https://console.groq.com

2️⃣ Generate an API key

3️⃣ Create this file:

.streamlit/secrets.toml

Add:

GROQ_API_KEY = "gsk_xxxxx"
📂 Project Structure
smart-data-explorer/
│
├── app.py
├── requirements.txt
│
└── .streamlit/
    └── secrets.toml
📊 Feature Summary
Feature	Details
File Support	CSV up to 200MB
Chart Types	9 visualization modes
AI Model	Llama 3.3 70B via Groq
Export Formats	CSV, XLSX, PDF
Deployment	Streamlit Cloud
Cost	Completely free

👨‍💻 Author

swachchho gun 

📜 License

MIT License
