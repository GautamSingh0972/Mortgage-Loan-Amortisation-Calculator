"""
Interactive dashboard for the loan calculator.

Run it with either:
    streamlit run dashboard.py
    python dashboard.py          (launches Streamlit for you)

All the maths comes from loan_calculator.py - this file only handles the UI.
If your calculator file has a different name, change the import below.
"""

import sys
import subprocess

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from currency_converter import CurrencyConverter

from loan_calculator import (
    currencies,
    monthly_payment,
    amortisation_schedule,
    total_interest,
)

# Newer Streamlit uses width="stretch"; older versions use use_container_width=True
_v = tuple(int(x) for x in st.__version__.split(".")[:2])
STRETCH = {"width": "stretch"} if _v >= (1, 46) else {"use_container_width": True}

NAVY = "#1b2e52"
GREEN = "#0f8a6b"
ORANGE = "#d9822b"
GREY = "#9aa6bb"


# ---------- Helpers ----------

@st.cache_resource
def get_converter():
    # Loading the ECB rate file takes a moment, so only do it once
    return CurrencyConverter()


def fmt_gbp(x, dp=2):
    return f"£{x:,.{dp}f}"


def fmt_duration(months):
    years, rem = divmod(months, 12)
    parts = []
    if years:
        parts.append(f"{years} yr")
    if rem:
        parts.append(f"{rem} mo")
    return " ".join(parts) or "0 mo"


def yearly_summary(df):
    df = df.copy()
    df["Year"] = (df["Month"] - 1) // 12 + 1
    return df.groupby("Year").agg(
        {
            "Opening Balance": "first",
            "Interest": "sum",
            "Payment": "sum",
            "Principal Repaid": "sum",
            "Closing Balance": "last",
        }
    ).reset_index()


def balance_chart(base_df, over_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=base_df["Month"] / 12, y=base_df["Closing Balance"],
        name="Standard", line=dict(color=GREY, width=2, dash="dash"),
        hovertemplate="Year %{x:.1f}<br>£%{y:,.0f}<extra>Standard</extra>",
    ))
    fig.add_trace(go.Scatter(
        x=over_df["Month"] / 12, y=over_df["Closing Balance"],
        name="With overpayment", line=dict(color=GREEN, width=3),
        fill="tozeroy", fillcolor="rgba(15,138,107,0.12)",
        hovertemplate="Year %{x:.1f}<br>£%{y:,.0f}<extra>With overpayment</extra>",
    ))
    fig.update_layout(
        height=340, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Years", yaxis_title="Outstanding balance (£)",
        yaxis_tickprefix="£", yaxis_tickformat=",.0f",
        legend=dict(orientation="h", y=1.08, x=0),
        hovermode="x unified",
    )
    return fig


def yearly_split_chart(yearly_df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=yearly_df["Year"], y=yearly_df["Principal Repaid"],
        name="Principal", marker_color=GREEN,
        hovertemplate="Year %{x}<br>Principal £%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=yearly_df["Year"], y=yearly_df["Interest"],
        name="Interest", marker_color=ORANGE,
        hovertemplate="Year %{x}<br>Interest £%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(
        barmode="stack", height=340, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Year", yaxis_title="Paid that year (£)",
        yaxis_tickprefix="£", yaxis_tickformat=",.0f",
        legend=dict(orientation="h", y=1.08, x=0),
    )
    return fig


# ---------- Page ----------

def run_dashboard():
    st.set_page_config(page_title="Loan Repayment Dashboard", layout="wide")
    st.markdown(
        f"<h1 style='color:{NAVY};margin-bottom:0'>Loan Repayment Dashboard</h1>",
        unsafe_allow_html=True,
    )
    st.caption("Powered by the functions in loan_calculator.py. Change any input and everything updates.")

    # ----- Sidebar inputs -----
    with st.sidebar:
        st.header("Loan details")

        currency_list = sorted(currencies)
        currency = st.selectbox("Currency", currency_list, index=currency_list.index("GBP"))
        amount = st.number_input(f"Principal ({currency})", min_value=1.0, value=200_000.0, step=1_000.0)

        if currency == "GBP":
            principal_loan = amount
        else:
            c = get_converter()
            try:
                principal_loan = c.convert(amount, currency, "GBP")
                st.info(f"{amount:,.2f} {currency} = **{fmt_gbp(principal_loan)}**")
            except Exception as e:
                # Some legacy codes (e.g. CYP, EEK) have no recent rate
                st.error(f"Couldn't convert {currency}: {e}")
                st.stop()

        annual_rate = st.slider("Annual interest rate (%)", 0.0, 15.0, 4.5, 0.05)
        years = st.slider("Term (years)", 1, 40, 25)
        overpayment = st.number_input("Monthly overpayment (£)", min_value=0.0, value=150.0, step=10.0)

    # ----- Calculations (your functions) -----
    try:
        payment = monthly_payment(principal_loan, annual_rate, years)
        base_df = pd.DataFrame(amortisation_schedule(principal_loan, annual_rate, years, 0))
        over_df = pd.DataFrame(amortisation_schedule(principal_loan, annual_rate, years, overpayment))
        interest_base = total_interest(principal_loan, annual_rate, years, 0)
        interest_over = total_interest(principal_loan, annual_rate, years, overpayment)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    saved = interest_base - interest_over
    months_saved = len(base_df) - len(over_df)

    # ----- Headline figures -----
    row1 = st.columns(3)
    row1[0].metric("Monthly payment", fmt_gbp(payment),
                   f"{fmt_gbp(payment + overpayment)} with overpayment" if overpayment else None,
                   delta_color="off")
    row1[1].metric("Total interest", fmt_gbp(interest_over, 0),
                   f"{interest_over / principal_loan:.1%} of amount borrowed", delta_color="off")
    row1[2].metric("Total repaid", fmt_gbp(principal_loan + interest_over, 0))

    row2 = st.columns(3)
    row2[0].metric("Paid off in", fmt_duration(len(over_df)), f"{len(over_df)} payments", delta_color="off")
    row2[1].metric("Interest saved", fmt_gbp(saved, 0),
                   f"{saved / interest_base:.1%} less" if interest_base > 0 and saved > 0.5 else None)
    row2[2].metric("Time saved", fmt_duration(months_saved),
                   f"vs {fmt_duration(len(base_df))} standard" if months_saved else None,
                   delta_color="off")

    # ----- Charts -----
    yearly_df = yearly_summary(over_df)
    left, right = st.columns(2)
    with left:
        st.subheader("Outstanding balance")
        st.plotly_chart(balance_chart(base_df, over_df), **STRETCH)
    with right:
        st.subheader("Where each year's money goes")
        st.plotly_chart(yearly_split_chart(yearly_df), **STRETCH)

    # ----- Schedule table -----
    st.subheader("Amortisation schedule")
    view = st.radio("View", ["Yearly", "Monthly"], horizontal=True, label_visibility="collapsed")
    table = yearly_df if view == "Yearly" else over_df
    money_cols = ["Opening Balance", "Interest", "Payment", "Principal Repaid", "Closing Balance"]
    st.dataframe(
        table.style.format({col: "£{:,.2f}" for col in money_cols}),
        hide_index=True, height=420, **STRETCH,
    )
    st.download_button(
        "Download schedule as CSV",
        over_df.to_csv(index=False).encode(),
        file_name="amortisation_schedule.csv",
        mime="text/csv",
    )

    with st.expander("How it's calculated"):
        st.latex(r"M = \frac{P \cdot r}{1-(1+r)^{-n}} \qquad r=\frac{\text{annual rate}}{12 \times 100},\; n = 12 \times \text{years}")
        st.write(
            "Each month: interest = opening balance × r, and the payment is "
            "min(M + overpayment, balance + interest). The loop runs until the balance "
            "reaches zero, so overpayments shorten the term rather than lowering M."
        )


def running_in_streamlit():
    try:
        from streamlit.runtime import exists
        return exists()
    except ImportError:
        return False


if running_in_streamlit():
    run_dashboard()
elif __name__ == "__main__":
    # `python dashboard.py` -> relaunch itself through Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])

