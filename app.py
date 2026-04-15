import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from datetime import date

SERIES = {
    "Equity & Volatility": {
        "S&P 500": "SP500",
        "NASDAQ Composite": "NASDAQCOM",
        "VIX (Fear Index)": "VIXCLS",
    },
    "Interest Rates": {
        "Fed Funds Rate": "FEDFUNDS",
        "10-Year Treasury Yield": "DGS10",
        "2-Year Treasury Yield": "DGS2",
        "Yield Curve Spread (10Y-2Y)": "T10Y2Y",
    },
    "Macroeconomic": {
        "CPI Inflation (YoY %)": "CPIAUCSL",
        "Unemployment Rate": "UNRATE",
        "Industrial Production Index": "INDPRO",
        "Real GDP Growth (QoQ %)": "A191RL1Q225SBEA",
    },
}

ALL_SERIES = {k: v for group in SERIES.values() for k, v in group.items()}
GROUP_OF = {name: grp for grp, items in SERIES.items() for name in items}

EQUITY_NAMES = list(SERIES["Equity & Volatility"].keys())
RATE_NAMES = list(SERIES["Interest Rates"].keys())
MACRO_NAMES = list(SERIES["Macroeconomic"].keys())

st.set_page_config(
    page_title="US Macro & Markets Dashboard",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 US Macroeconomic & Financial Market Dashboard")
st.markdown(
    "Explore the relationship between monetary policy, inflation, labour markets, "
    "and equity performance. All data sourced from the **Federal Reserve (FRED)**."
)

with st.sidebar:
    st.header("⚙️ Controls")

    start_date = st.date_input("Start Date", value=date(2015, 1, 1), max_value=date.today())
    end_date = st.date_input("End Date", value=date.today(), max_value=date.today())

    st.markdown("---")
    st.subheader("Series Selection")
    selected_equity = st.multiselect(
        "Equity & Volatility",
        EQUITY_NAMES,
        default=["S&P 500", "NASDAQ Composite", "VIX (Fear Index)"],
    )
    selected_rates = st.multiselect(
        "Interest Rates",
        RATE_NAMES,
        default=["Fed Funds Rate", "10-Year Treasury Yield", "Yield Curve Spread (10Y-2Y)"],
    )
    selected_macro = st.multiselect(
        "Macroeconomic",
        MACRO_NAMES,
        default=["CPI Inflation (YoY %)", "Unemployment Rate"],
    )

    st.markdown("---")
    recession_shade = st.checkbox("Show Recession Periods (NBER)", value=True)

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

all_selected = selected_equity + selected_rates + selected_macro
if not all_selected:
    st.warning("Please select at least one series.")
    st.stop()


def _fetch_fred_csv(code, start, end):
    url = f"https://fred.stlouisfed.org/graph/freddata.csv?id={code}"
    df = pd.read_csv(url, index_col=0, parse_dates=True, na_values=".")
    df.columns = [code]
    df.index = pd.to_datetime(df.index)
    df = df.loc[str(start):str(end)]
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_series(names_tuple, start, end):
    frames = {}
    failed = []
    for name in names_tuple:
        code = ALL_SERIES[name]
        try:
            s = _fetch_fred_csv(code, start, end)
            s.columns = [name]
            frames[name] = s[name]
        except Exception:
            failed.append(name)
    if not frames:
        return pd.DataFrame(), failed
    df = pd.DataFrame(frames)
    df.index = pd.to_datetime(df.index)
    return df, failed


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_recession_dates(start, end):
    try:
        rec = _fetch_fred_csv("USREC", start, end)
        rec.columns = ["USREC"]
        return rec
    except Exception:
        return None


def add_recession_shading(fig, rec_df):
    if rec_df is None or rec_df.empty:
        return fig
    rec = rec_df["USREC"]
    in_recession = False
    r_start = None
    for dt, val in rec.items():
        if val == 1 and not in_recession:
            in_recession = True
            r_start = dt
        elif val == 0 and in_recession:
            in_recession = False
            fig.add_vrect(
                x0=r_start, x1=dt,
                fillcolor="grey", opacity=0.15,
                layer="below", line_width=0,
                annotation_text="Recession", annotation_position="top left",
                annotation_font_size=9,
            )
    if in_recession:
        fig.add_vrect(
            x0=r_start, x1=rec.index[-1],
            fillcolor="grey", opacity=0.15,
            layer="below", line_width=0,
        )
    return fig


with st.spinner("Fetching data from FRED…"):
    data, failed = fetch_series(tuple(all_selected), start_date, end_date)
    rec_df = fetch_recession_dates(start_date, end_date) if recession_shade else None

if failed:
    st.warning(f"Could not load: {', '.join(failed)}")

if data.empty:
    st.error("No data returned. Please check your date range or internet connection.")
    st.stop()

equity_cols = [c for c in selected_equity if c in data.columns]
rate_cols = [c for c in selected_rates if c in data.columns]
macro_cols = [c for c in selected_macro if c in data.columns]

equity_data = data[equity_cols].dropna(how="all") if equity_cols else pd.DataFrame()
rate_data = data[rate_cols].dropna(how="all") if rate_cols else pd.DataFrame()
macro_data = data[macro_cols].dropna(how="all") if macro_cols else pd.DataFrame()

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Markets", "🏛️ Monetary Policy", "🌍 Macroeconomics", "📊 Cross-Market Analysis"]
)

with tab1:
    if not equity_data.empty:
        price_cols = [c for c in equity_cols if c != "VIX (Fear Index)" and c in equity_data.columns]
        vix_col = "VIX (Fear Index)" if "VIX (Fear Index)" in equity_data.columns else None

        if price_cols:
            st.subheader("Equity Index Performance (Normalised, Base = 100)")
            norm = equity_data[price_cols].dropna(how="all")
            norm = norm / norm.bfill().iloc[0] * 100
            fig_eq = px.line(norm.reset_index(), x=norm.index.name or "DATE",
                             y=price_cols, template="plotly_white", height=400,
                             labels={"value": "Indexed Price", "variable": ""})
            fig_eq.update_layout(hovermode="x unified", legend_title_text="")
            fig_eq.add_hline(y=100, line_dash="dash", line_color="grey", opacity=0.5)
            fig_eq = add_recession_shading(fig_eq, rec_df)
            st.plotly_chart(fig_eq, use_container_width=True)

            st.subheader("Rolling 30-Day Returns (%)")
            ret = equity_data[price_cols].pct_change(30) * 100
            fig_ret = px.line(ret.reset_index(), x=ret.index.name or "DATE",
                              y=price_cols, template="plotly_white", height=350,
                              labels={"value": "30-Day Return (%)", "variable": ""})
            fig_ret.update_layout(hovermode="x unified", legend_title_text="")
            fig_ret.add_hline(y=0, line_dash="dash", line_color="grey", opacity=0.5)
            fig_ret = add_recession_shading(fig_ret, rec_df)
            st.plotly_chart(fig_ret, use_container_width=True)

        if vix_col:
            st.subheader("VIX — Market Volatility / Fear Index")
            fig_vix = px.area(
                equity_data[[vix_col]].reset_index(),
                x=equity_data.index.name or "DATE", y=vix_col,
                template="plotly_white", height=300,
                labels={"value": "VIX Level", vix_col: "VIX"},
                color_discrete_sequence=["crimson"],
            )
            fig_vix.add_hline(y=20, line_dash="dot", line_color="orange",
                              annotation_text="Elevated (20)", annotation_position="right")
            fig_vix.add_hline(y=30, line_dash="dot", line_color="red",
                              annotation_text="Extreme Fear (30)", annotation_position="right")
            fig_vix = add_recession_shading(fig_vix, rec_df)
            st.plotly_chart(fig_vix, use_container_width=True)
    else:
        st.info("Select equity/volatility series in the sidebar.")

with tab2:
    if not rate_data.empty:
        ff_col = "Fed Funds Rate" if "Fed Funds Rate" in rate_data.columns else None
        dgs10_col = "10-Year Treasury Yield" if "10-Year Treasury Yield" in rate_data.columns else None
        dgs2_col = "2-Year Treasury Yield" if "2-Year Treasury Yield" in rate_data.columns else None
        spread_col = "Yield Curve Spread (10Y-2Y)" if "Yield Curve Spread (10Y-2Y)" in rate_data.columns else None

        yield_line_cols = [c for c in [ff_col, dgs10_col, dgs2_col] if c]
        if yield_line_cols:
            st.subheader("Interest Rates (%)")
            fig_rates = px.line(
                rate_data[yield_line_cols].reset_index(),
                x=rate_data.index.name or "DATE", y=yield_line_cols,
                template="plotly_white", height=400,
                labels={"value": "Rate (%)", "variable": ""},
            )
            fig_rates.update_layout(hovermode="x unified", legend_title_text="")
            fig_rates = add_recession_shading(fig_rates, rec_df)
            st.plotly_chart(fig_rates, use_container_width=True)

        if spread_col:
            st.subheader("Yield Curve Spread (10Y − 2Y) — Recession Predictor")
            spread_series = rate_data[[spread_col]].dropna()
            fig_spread = go.Figure()
            fig_spread.add_trace(
                go.Scatter(
                    x=spread_series.index, y=spread_series[spread_col],
                    mode="lines", name="10Y-2Y Spread",
                    line=dict(color="steelblue", width=1.5),
                    fill="tozeroy",
                    fillcolor="rgba(70,130,180,0.15)",
                )
            )
            fig_spread.add_hline(y=0, line_color="red", line_dash="dash",
                                 annotation_text="Inversion (recession signal)",
                                 annotation_position="right")
            fig_spread.update_layout(template="plotly_white", height=320,
                                     hovermode="x unified",
                                     yaxis_title="Spread (pp)", xaxis_title="")
            fig_spread = add_recession_shading(fig_spread, rec_df)
            st.plotly_chart(fig_spread, use_container_width=True)

        if equity_cols and ff_col and "S&P 500" in data.columns:
            st.subheader("Fed Funds Rate vs S&P 500")
            combined = pd.DataFrame({
                "S&P 500 (left)": data["S&P 500"],
                "Fed Funds Rate % (right)": rate_data[ff_col],
            }).dropna(how="all")
            fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
            fig_dual.add_trace(
                go.Scatter(x=combined.index, y=combined["S&P 500 (left)"],
                           name="S&P 500", line=dict(color="steelblue")),
                secondary_y=False,
            )
            fig_dual.add_trace(
                go.Scatter(x=combined.index, y=combined["Fed Funds Rate % (right)"],
                           name="Fed Funds Rate", line=dict(color="firebrick", dash="dash")),
                secondary_y=True,
            )
            fig_dual.update_layout(template="plotly_white", height=380,
                                   hovermode="x unified", legend_title_text="")
            fig_dual.update_yaxes(title_text="S&P 500", secondary_y=False)
            fig_dual.update_yaxes(title_text="Fed Funds Rate (%)", secondary_y=True)
            st.plotly_chart(fig_dual, use_container_width=True)
    else:
        st.info("Select interest rate series in the sidebar.")

with tab3:
    if not macro_data.empty:
        cpi_col = "CPI Inflation (YoY %)" if "CPI Inflation (YoY %)" in macro_data.columns else None
        unemp_col = "Unemployment Rate" if "Unemployment Rate" in macro_data.columns else None
        ip_col = "Industrial Production Index" if "Industrial Production Index" in macro_data.columns else None
        gdp_col = "Real GDP Growth (QoQ %)" if "Real GDP Growth (QoQ %)" in macro_data.columns else None

        if cpi_col:
            st.subheader("Consumer Price Index — Inflation (%)")
            cpi = macro_data[[cpi_col]].dropna()
            cpi_yoy = cpi.pct_change(12) * 100
            cpi_yoy.columns = ["CPI YoY Change (%)"]
            fig_cpi = px.area(
                cpi_yoy.reset_index(),
                x=cpi_yoy.index.name or "DATE", y="CPI YoY Change (%)",
                template="plotly_white", height=340,
                labels={"value": "YoY Change (%)", "CPI YoY Change (%)": "Inflation"},
                color_discrete_sequence=["darkorange"],
            )
            fig_cpi.add_hline(y=2, line_dash="dot", line_color="green",
                              annotation_text="Fed Target (2%)", annotation_position="right")
            fig_cpi = add_recession_shading(fig_cpi, rec_df)
            st.plotly_chart(fig_cpi, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if unemp_col:
                st.subheader("Unemployment Rate (%)")
                fig_unemp = px.line(
                    macro_data[[unemp_col]].dropna().reset_index(),
                    x=macro_data.index.name or "DATE", y=unemp_col,
                    template="plotly_white", height=320,
                    labels={"value": "%", unemp_col: "Unemployment"},
                    color_discrete_sequence=["seagreen"],
                )
                fig_unemp = add_recession_shading(fig_unemp, rec_df)
                st.plotly_chart(fig_unemp, use_container_width=True)

        with col_b:
            if ip_col:
                st.subheader("Industrial Production Index")
                fig_ip = px.line(
                    macro_data[[ip_col]].dropna().reset_index(),
                    x=macro_data.index.name or "DATE", y=ip_col,
                    template="plotly_white", height=320,
                    labels={"value": "Index", ip_col: "Ind. Production"},
                    color_discrete_sequence=["purple"],
                )
                fig_ip = add_recession_shading(fig_ip, rec_df)
                st.plotly_chart(fig_ip, use_container_width=True)

        if gdp_col and gdp_col in macro_data.columns:
            st.subheader("Real GDP Growth Rate (QoQ %)")
            gdp = macro_data[[gdp_col]].dropna()
            colors = ["firebrick" if v < 0 else "steelblue" for v in gdp[gdp_col]]
            fig_gdp = go.Figure(
                go.Bar(x=gdp.index, y=gdp[gdp_col], marker_color=colors, name="GDP Growth")
            )
            fig_gdp.add_hline(y=0, line_color="black", line_width=0.8)
            fig_gdp.update_layout(template="plotly_white", height=320,
                                  yaxis_title="QoQ %", xaxis_title="",
                                  hovermode="x unified")
            st.plotly_chart(fig_gdp, use_container_width=True)
    else:
        st.info("Select macroeconomic series in the sidebar.")

with tab4:
    st.subheader("Cross-Correlation Matrix")
    all_data_clean = data.resample("MS").last().dropna(how="all")

    if len(all_data_clean.columns) >= 2:
        corr = all_data_clean.corr()
        fig_corr = px.imshow(
            corr, color_continuous_scale="RdBu_r", color_continuous_midpoint=0,
            text_auto=".2f", template="plotly_white", height=520, zmin=-1, zmax=1,
        )
        fig_corr.update_layout(xaxis_tickangle=-40)
        st.plotly_chart(fig_corr, use_container_width=True)

        st.subheader("Scatter: Unemployment vs Inflation (Phillips Curve)")
        if "CPI Inflation (YoY %)" in data.columns and "Unemployment Rate" in data.columns:
            scatter_df = data[["CPI Inflation (YoY %)", "Unemployment Rate"]].resample("MS").last().dropna()
            scatter_df["CPI YoY (%)"] = scatter_df["CPI Inflation (YoY %)"].pct_change(12) * 100
            scatter_df = scatter_df.dropna()
            scatter_df["Year"] = scatter_df.index.year.astype(str)
            fig_ph = px.scatter(
                scatter_df.reset_index(), x="Unemployment Rate", y="CPI YoY (%)",
                color="Year", template="plotly_white", height=420,
                trendline="ols",
                labels={"Unemployment Rate": "Unemployment (%)", "CPI YoY (%)": "Inflation YoY (%)"},
                title="Phillips Curve: Unemployment vs Inflation",
            )
            st.plotly_chart(fig_ph, use_container_width=True)

    st.subheader("Summary Statistics")
    summary = data.describe().T.round(3)
    st.dataframe(summary, use_container_width=True)

    csv_all = data.to_csv().encode("utf-8")
    st.download_button("⬇️ Download All Data (CSV)", csv_all, "fred_data.csv", "text/csv")

st.markdown("---")
st.caption(
    f"Data sourced from **FRED (Federal Reserve Bank of St. Louis)** via direct CSV API. "
    f"Series: SP500, NASDAQCOM, VIXCLS, DGS10, DGS2, T10Y2Y, FEDFUNDS, CPIAUCSL, UNRATE, INDPRO, A191RL1Q225SBEA. "
    f"Retrieved: {date.today().strftime('%d %B %Y')}."
)
