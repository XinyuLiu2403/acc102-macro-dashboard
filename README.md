# US Macroeconomic & Financial Market Dashboard

**Module:** ACC102 Mini Assignment | **Track:** 4 — Interactive Data Analysis Tool | **Author:** [Your Name] | **Student ID:** [Your ID]

> **Live App:** [https://acc102-macro-dashboard-wyd7uqg4shqkb23krppnpm.streamlit.app](https://acc102-macro-dashboard-wyd7uqg4shqkb23krppnpm.streamlit.app)


---

## 1. Problem & User

How have US monetary policy shifts — particularly the post-COVID rate-hiking cycle — affected equity market performance, inflation dynamics, and labour market conditions between 2015 and the present? This dashboard is designed for economics and finance students, retail investors, and practitioners who want a clear, interactive, data-driven overview of US macroeconomic cycles without manually navigating multiple data portals.

---

## 2. Data

**Source:** Federal Reserve Bank of St. Louis — [FRED Economic Data](https://fred.stlouisfed.org/)  
**Access method:** Pre-downloaded CSV files from FRED (stored in `data/` folder); no API key required  
**Access date:** April 2026  

| FRED Code | Series | Frequency |
|-----------|--------|-----------|
| SP500 | S&P 500 Index | Daily |
| NASDAQCOM | NASDAQ Composite | Daily |
| VIXCLS | CBOE Volatility Index (VIX) | Daily |
| FEDFUNDS | Federal Funds Effective Rate | Monthly |
| DGS10 | 10-Year Treasury Yield | Daily |
| DGS2 | 2-Year Treasury Yield | Daily |
| T10Y2Y | Yield Curve Spread (10Y – 2Y) | Daily |
| CPIAUCSL | Consumer Price Index (All Urban) | Monthly |
| UNRATE | Unemployment Rate | Monthly |
| INDPRO | Industrial Production Index | Monthly |
| A191RL1Q225SBEA | Real GDP Growth Rate (QoQ %) | Quarterly |
| USREC | NBER Recession Indicator | Monthly |

FRED is a publicly maintained US government database widely used in academic economics research. All series are lawful to use for educational analysis and are fully reproducible.

---

## 3. Methods

1. **Data acquisition** — downloaded 12 FRED series as CSV files; stored in `data/` folder; app reads locally for reliability
2. **Cleaning & alignment** — forward-filled isolated gaps (limit 3 periods); resampled mixed-frequency series to monthly for cross-series analysis
3. **Return & volatility calculation** — daily simple returns; 30-day rolling annualised volatility (σ × √252)
4. **Inflation derivation** — CPI YoY change computed as 12-period percentage change on the monthly price level index
5. **Yield curve analysis** — 10Y–2Y spread plotted with inversion (< 0) highlighted as a recession signal; NBER recession dates shaded on all charts
6. **Correlation analysis** — Pearson correlation matrix on monthly-resampled data to avoid frequency mismatch noise
7. **Phillips curve regression** — OLS via `scipy.stats.linregress` to quantify the unemployment–inflation relationship
8. **Interactive product** — built with Streamlit + Plotly; sidebar controls for date range, series selection, and recession shading toggle

---

## 4. Key Findings

- **COVID crash & recovery:** The S&P 500 fell ~34% in March 2020 then recovered to new highs, driven by near-zero interest rates and fiscal stimulus — the fastest post-war recovery on record.
- **Rate-hike bear market:** The 2022 NASDAQ decline (~33%) directly coincided with the Fed's fastest tightening cycle since the 1980s, confirming the inverse relationship between rates and equity valuations.
- **Yield curve inversion:** The 10Y–2Y spread turned negative in 2022–23, a historically reliable recession signal, as the Fed pushed short-term rates above long-term rates.
- **Phillips curve breakdown:** Post-2020 data shows a weakened inverse unemployment–inflation relationship (OLS R² < 0.10 for 2020–present), indicating supply-side rather than demand-driven inflation — a departure from textbook predictions.
- **Cross-market correlations:** VIX shows a strong negative correlation with equity indices; the Fed Funds Rate is negatively correlated with S&P 500 performance over this period, consistent with the monetary transmission mechanism.

---

## 5. How to Run

### Requirements

- Python 3.8+

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the interactive dashboard

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Data is loaded from local CSV files in the `data/` folder (no internet connection required).

### Run the analytical notebook

Open `analysis.ipynb` in Jupyter Notebook or JupyterLab and run all cells from top to bottom.

---

## 6. Product Link / Demo

| Item | Link |
|------|------|
| Live Streamlit App | [https://acc102-macro-dashboard-wyd7uqg4shqkb23krppnpm.streamlit.app](https://acc102-macro-dashboard-wyd7uqg4shqkb23krppnpm.streamlit.app) |
| Demo Video (1–3 min) | [link to your video] |
| GitHub Repository | [https://github.com/XinyuLiu2403/acc102-macro-dashboard](https://github.com/XinyuLiu2403/acc102-macro-dashboard) |

---

## 7. Limitations & Next Steps

**Limitations:**
- FRED series have different native frequencies (daily / monthly / quarterly); resampling decisions affect granularity and may obscure intra-period movements
- Correlation does not imply causation — observed relationships may reflect shared underlying macro drivers (e.g., the pandemic shock) rather than direct links
- The S&P 500 series on FRED has occasional gaps (e.g., public holidays); forward-fill smooths short-term movements slightly
- Phillips curve regression is sensitive to the structural break introduced by COVID-19; the 2015–present pooled estimate has limited predictive validity

**Next Steps:**
- Incorporate a VAR (Vector Autoregression) model to quantify dynamic interactions between monetary policy and economic outcomes
- Add global context: ECB rate, European CPI, and emerging market indicators
- Build an automated inversion alert that flags when the yield curve turns negative
- Expand to a sector-level analysis using ETF data once network access to Yahoo Finance is available

---

## Project Structure

```
.
├── app.py               # Streamlit interactive dashboard (entry file)
├── analysis.ipynb       # Jupyter notebook — full analytical workflow
├── requirements.txt     # Python dependencies
├── data/                # Pre-downloaded FRED CSV files (12 series)
└── README.md            # This file
```

---

## Data Citation

Federal Reserve Bank of St. Louis. *FRED Economic Data*. Retrieved April 2026.  
URL: https://fred.stlouisfed.org  
Series accessed via direct FRED CSV download (https://fred.stlouisfed.org/graph/fredgraph.csv).

---

## AI Use Disclosure

**Tool used:** Qoder (AI coding assistant embedded in IDE)  
**Model version:** Not disclosed by provider  
**Access date:** April 2026

AI assistance was used selectively for the following specific tasks:

| Task | AI role | Student contribution |
|------|---------|----------------------|
| Streamlit tab layout and sidebar widget syntax | AI suggested the `st.tabs()` / `st.multiselect()` structure | Student decided which tabs and controls were analytically meaningful |
| Plotly dual-axis chart (`make_subplots`) | AI provided the `secondary_y` syntax pattern | Student decided to overlay Fed Funds Rate with S&P 500 as an analytical question |
| NBER recession shading loop | AI wrote the `axvspan` iteration over USREC series | Student identified this as important context for interpreting crashes |
| Identifying FRED series codes | AI suggested codes such as `T10Y2Y`, `A191RL1Q225SBEA` | Student selected which economic concepts to include and why |
| Debugging `pandas-datareader` when `yfinance` was inaccessible | AI diagnosed the network issue and suggested the FRED fallback | Student made the decision to change data source and verified data quality |
| Drafting the reflection report structure | AI produced an initial outline | Student rewrote and personalised all content, including all interpretations |

**What was not AI-generated:**  
The research question, the choice of analytical framework (monetary transmission mechanism, Phillips curve, yield curve as recession predictor), the selection of which 12 FRED indicators to use, all interpretation of findings, all limitations identified, and the decision to build an interactive multi-tab product rather than a static notebook were made independently by myself. Every code cell in analysis.ipynb was read, understood, and manually verified by myself before submission.

This submission complies with the University Academic Integrity Policy. AI was used as a productivity tool, not as a substitute for independent analytical thinking.
