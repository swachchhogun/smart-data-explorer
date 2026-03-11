Here's a clean README for DataLens:

DataLens — Smart Data Explorer

Upload any CSV. Get instant charts, AI insights, and a beautiful PDF report — all free.

Live Demo: smart-data-explorer-mgappjprtpxzeqvn69pew65.streamlit.app

What it does
DataLens is a no-code data analysis web app. Drop in a CSV and instantly get:

Auto data cleaning — nulls filled, duplicates removed, types inferred
9 chart modes — histogram, heatmap, scatter matrix, correlation, trend over time, box plots, and more
AI-powered insights — ask natural language questions about your data via Llama 3.3 70B (Groq, free)
Data quality profiling — column health scores, outlier detection via IQR, completeness metrics
Column type editor — override auto-detected types and watch changes apply live across all tabs
PDF report generator — exports dataset overview, stats, cleaning log, and AI insights as a formatted PDF
Sidebar filters — slice by category or numeric range; all charts update instantly
Export — filtered CSV or full XLSX download


Built with

Python · Streamlit · Pandas · NumPy
Plotly — interactive charts
Groq API — free LLM inference (Llama 3.3 70B)
ReportLab — PDF generation


Run locally
bashgit clone https://github.com/swachchhogun/smart-data-explorer
cd smart-data-explorer
pip install -r requirements.txt
streamlit run app.py
To enable AI features, add your free Groq API key:

Sign up at console.groq.com — no card needed
Create an API key
Create a .streamlit/secrets.toml file:

tomlGROQ_API_KEY = "gsk_xxxx"
```

---

## Project structure
```
smart-data-explorer/
├── app.py               # Main application
├── requirements.txt     # Dependencies
└── .streamlit/
    └── secrets.toml     # API keys (not committed)

Features at a glance
FeatureDetailsFile supportCSV up to 200MBChart types9 modesAI modelLlama 3.3 70B via GroqExport formatsCSV, XLSX, PDFDeploymentStreamlit CloudCostCompletely free

Author
Swachchho Gun · swachchhogun@gmail.com · github.com/swachchhogun
