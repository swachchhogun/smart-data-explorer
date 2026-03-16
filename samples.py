"""
samples.py
──────────
Built-in sample datasets for the DataLens landing page.
All datasets are generated with numpy/pandas — no external files needed.
"""

import pandas as pd
import numpy as np


SAMPLES = {
    "Superstore Sales":  {
        "icon": "🛒", "rows": 500, "cols": 9,
        "desc": "Sales, profit & shipping across regions",
    },
    "Student Scores":    {
        "icon": "🎓", "rows": 300, "cols": 8,
        "desc": "Marks, attendance & grades by course",
    },
    "E-Commerce Orders": {
        "icon": "📦", "rows": 600, "cols": 9,
        "desc": "Orders, revenue & ratings by country",
    },
    "Health & Fitness":  {
        "icon": "❤️", "rows": 365, "cols": 8,
        "desc": "Daily steps, sleep & wellness tracking",
    },
}


def make_sample_dataset(name: str) -> pd.DataFrame:
    """Generate a sample DataFrame by name. Returns empty DataFrame if name unknown."""
    rng = np.random.default_rng(42)

    if name == "Superstore Sales":
        n = 500
        regions    = ["North", "South", "East", "West"]
        categories = ["Furniture", "Technology", "Office Supplies"]
        segments   = ["Consumer", "Corporate", "Home Office"]
        return pd.DataFrame({
            "Order Date": pd.date_range("2022-01-01", periods=n, freq="D").strftime("%Y-%m-%d"),
            "Region":     rng.choice(regions, n),
            "Category":   rng.choice(categories, n),
            "Segment":    rng.choice(segments, n),
            "Sales":      (rng.exponential(200, n) + 20).round(2),
            "Profit":     (rng.normal(30, 60, n)).round(2),
            "Discount":   rng.choice([0, 0.1, 0.2, 0.3, 0.5], n),
            "Quantity":   rng.integers(1, 15, n),
            "Ship Days":  rng.integers(1, 8, n),
        })

    elif name == "Student Scores":
        n = 300
        return pd.DataFrame({
            "Student ID":  [f"S{i:04d}" for i in range(1, n + 1)],
            "Gender":      rng.choice(["Male", "Female"], n),
            "Course":      rng.choice(["Statistics", "Mathematics", "Computer Science", "Economics"], n),
            "Attendance":  np.clip(rng.normal(78, 12, n), 40, 100).round(1),
            "Midterm":     np.clip(rng.normal(62, 15, n), 10, 100).round(1),
            "Final":       np.clip(rng.normal(65, 14, n), 10, 100).round(1),
            "Assignment":  np.clip(rng.normal(72, 10, n), 20, 100).round(1),
            "Grade":       rng.choice(["A", "B", "C", "D", "F"], n, p=[0.2, 0.35, 0.25, 0.15, 0.05]),
        })

    elif name == "E-Commerce Orders":
        n = 600
        countries = ["India", "USA", "UK", "Germany", "France", "Canada"]
        products  = ["Laptop", "Phone", "Tablet", "Headphones", "Keyboard", "Monitor", "Mouse", "Webcam"]
        statuses  = ["Delivered", "Shipped", "Cancelled", "Returned"]
        return (
            pd.DataFrame({
                "Order Date": pd.date_range("2023-01-01", periods=n, freq="14H").strftime("%Y-%m-%d"),
                "Country":    rng.choice(countries, n),
                "Product":    rng.choice(products, n),
                "Status":     rng.choice(statuses, n, p=[0.7, 0.15, 0.1, 0.05]),
                "Units":      rng.integers(1, 6, n),
                "Unit Price": rng.choice([299, 499, 799, 999, 1299, 49, 29, 89], n).astype(float),
                "Revenue":    None,
                "Rating":     np.clip(rng.normal(4.1, 0.7, n), 1, 5).round(1),
                "Return":     rng.choice([0, 1], n, p=[0.92, 0.08]),
            })
            .assign(Revenue=lambda d: (d["Units"] * d["Unit Price"]).round(2))
        )

    elif name == "Health & Fitness":
        n     = 365
        dates = pd.date_range("2023-01-01", periods=n, freq="D")
        steps = np.clip(rng.normal(7500, 2500, n), 500, 25000).astype(int)
        return pd.DataFrame({
            "Date":       dates.strftime("%Y-%m-%d"),
            "Day":        dates.day_name(),
            "Steps":      steps,
            "Calories":   (steps * 0.04 + rng.normal(0, 50, n)).clip(200, 1200).round(0).astype(int),
            "Sleep Hrs":  np.clip(rng.normal(7.2, 1.1, n), 3, 10).round(1),
            "Heart Rate": np.clip(rng.normal(72, 9, n), 50, 110).round(0).astype(int),
            "Water (L)":  np.clip(rng.normal(2.1, 0.5, n), 0.5, 4.5).round(1),
            "Mood":       rng.choice(["Great", "Good", "Okay", "Tired", "Bad"], n,
                                     p=[0.2, 0.4, 0.25, 0.1, 0.05]),
        })

    return pd.DataFrame()
