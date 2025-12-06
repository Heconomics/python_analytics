# This script loads interest rate data from Banxico and the U.S. Federal Reserve,
# aligns them by date, and generates a comparative time-series visualization
# showing how both rates evolve over time.

import pandas as pd
import plotly.graph_objects as go

spanish_months = {
    1: "Ene",  2: "Feb",  3: "Mar",
    4: "Abr",  5: "May",  6: "Jun",
    7: "Jul",  8: "Ago",  9: "Sep",
    10: "Oct", 11: "Nov", 12: "Dic"
}

# Load Banxico data, rename the rate column, and keep only records where the date begins with "01"
# (Banxico publishes monthly series by day; filtering ensures only the first-day entries are used)
banxico = (
    pd.read_csv(r"C:\Users\iker3\Downloads\tasa_banxico.csv",
                encoding="ISO-8859-1", skiprows=12)
    .rename(columns={"SF61745": "Tasa Objetivo"})
    .query("Fecha.str.startswith('01')")
    .reset_index(drop=True)
)

# Load Fed data and merge it with Banxico on index alignment; convert dates to datetime for proper indexing
fed = pd.read_csv(r"C:\Users\iker3\Downloads\tasa_fed.csv")
merged = (
    fed.join(banxico, how="left")
    .assign(observation_date=lambda df: pd.to_datetime(df["observation_date"]))
    .set_index("observation_date")
    # Retain only the final indicators used in the chart
    .loc[:, ["FEDFUNDS", "Tasa Objetivo"]]
)

tickvals_full = merged.index
ticktext_full = [f"{spanish_months[d.month]} {d.year}" for d in merged.index]

# Select every 2 months
tickvals = tickvals_full[::2]
ticktext = ticktext_full[::2]

# Build figure with two interest rate curves
fig = go.Figure()
for col, label in [
    ("FEDFUNDS",      "Federal Reserve"),
    ("Tasa Objetivo", "Banco de México")
]:
    fig.add_trace(go.Scatter(x=merged.index, y=merged[col],
                             mode="lines+markers+text",
                             text=merged[col], textposition="top center",
                             name=label))

# Visual style configuration
fig.update_layout(
    title=dict(text="Evolución de Tasas de Interés: Banxico vs Fed, de 2023 a 2025",
               font=dict(family="Helvetica", size=22, color="#FFFFFF")),
    legend_title=dict(text="Indicadores",
                      font=dict(family="Helvetica", size=14, color="rgba(255,255,255,0.9)")),
    legend=dict(x=.9, y=1.1),
    hovermode="x unified",
    font=dict(family="Helvetica", size=12, color="rgba(255,255,255,0.9)"),
    plot_bgcolor="#293037", paper_bgcolor="#293037",
)

fig.update_xaxes(
    tickmode="array",
    tickvals=tickvals,
    ticktext=ticktext,
    gridcolor="rgba(255,255,255,0.4)",
)
fig.update_yaxes(gridcolor="rgba(255,255,255,0.4)")
fig.show()
