# This script loads interest-rate data from Banxico and the U.S. Federal Reserve,
# aligns both datasets on their observation dates, formats month labels in Spanish,
# and generates an HTML time-series visualization comparing both benchmark rates.

import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo

# Month abbreviations used for x-axis labels
SPANISH_MONTHS = {
    1: "Ene",  2: "Feb",  3: "Mar",  4: "Abr",  5: "May",  6: "Jun",
    7: "Jul",  8: "Ago",  9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}


def load_banxico(path):
    # Banxico CSV contains extra metadata rows and daily entries; only first-day entries are retained
    return (pd.read_csv(path, encoding="ISO-8859-1", skiprows=12)
              .rename(columns={"SF61745": "Tasa Objetivo"})
              .query("Fecha.str.startswith('01')")
              .reset_index(drop=True))


def load_fed(path):
    # FED data is already clean; no filtering required
    return pd.read_csv(path)


# Load datasets
banxico = load_banxico("YOUR FILE PATH GOES HERE")
fed = load_fed("YOUR FILE PATH GOES HERE")

# Merge: FED dates act as the unified timeline, Banxico data is aligned onto it
merged = (fed.join(banxico, how="left")
          .assign(observation_date=lambda df: pd.to_datetime(df["observation_date"]))
          .set_index("observation_date")
          [["FEDFUNDS", "Tasa Objetivo"]])


def format_ticks(idx):
    # Reduces tick density for readability and maps month numbers to Spanish labels
    vals = idx[::2]
    txt = [f"{SPANISH_MONTHS[d.month]} {d.year}" for d in vals]
    return vals, txt


tickvals, ticktext = format_ticks(merged.index)

# Plot setup
fig = go.Figure()
series_info = [
    ("FEDFUNDS",      "Federal Reserve"),
    ("Tasa Objetivo", "Banco de México")
]

# Add both rate series to the plot
for col, label in series_info:
    fig.add_trace(go.Scatter(
        x=merged.index, y=merged[col],
        mode="lines+markers+text",
        text=merged[col], textposition="top center",
        name=label,
        hovertemplate=f"<b>{label}:</b> %{{y}}<extra></extra>"
    ))

# Styling
fig.update_layout(
    title=dict(text="Evolución de Tasas de Interés: Banxico vs Fed, de 2023 a 2025",
               font=dict(family="Helvetica", size=22, color="#FFFFFF")),
    legend_title=dict(text="Indicadores",
                      font=dict(family="Helvetica", size=14, color="rgba(255,255,255,0.9)")),
    legend=dict(x=.9, y=1.1),
    hovermode="x unified",
    font=dict(family="Helvetica", size=12, color="rgba(255,255,255,0.9)"),
    plot_bgcolor="#293037", paper_bgcolor="#293037"
)

fig.update_xaxes(tickmode="array", tickvals=tickvals, ticktext=ticktext,
                 gridcolor="rgba(255,255,255,0.4)")
fig.update_yaxes(gridcolor="rgba(255,255,255,0.4)")

# Export plot as HTML (reliable for .py execution)
pyo.plot(fig, filename="interest_rates.html", auto_open=True)
