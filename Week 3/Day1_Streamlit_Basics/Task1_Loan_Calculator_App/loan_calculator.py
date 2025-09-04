import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Loan Calculator", page_icon="💸", layout="wide")
st.title("💸 Interactive Loan Calculator")

# --- Inputs ---
st.header("Borrower Details")
name = st.text_input("Full name", placeholder="e.g., John Snow")
age = st.number_input("Age", min_value=18, max_value=100, value=25, step=1)

st.header("Loan Details")
price = st.number_input("Asset Price", min_value=0.0, value=500000.0, step=50000.0)
deposit = st.number_input("Deposit", min_value=0.0, value=100000.0, step=50000.0)
rate = st.slider("Annual Interest Rate (%)", 0.1, 24.0, 8.5, 0.1) / 100
years = st.slider("Duration (years)", 1, 40, 20)

# --- Loan Calculations ---
principal = price - deposit
n = years * 12  # monthly payments
r = rate / 12  # monthly interest rate

def pmt(P, r, n):
    if r == 0:
        return P / n
    return P * r / (1 - (1 + r) ** -n)

payment = pmt(principal, r, n)

# --- Build Amortization Schedule ---
balance = principal
rows = []
for i in range(1, n + 1):
    interest = balance * r
    principal_paid = payment - interest
    balance -= principal_paid
    rows.append([i, round(payment,2), round(principal_paid,2), round(interest,2), round(max(balance,0),2)])

schedule = pd.DataFrame(rows, columns=["Month", "Payment", "Principal", "Interest", "Balance"])

# --- KPIs ---
total_payment = schedule["Payment"].sum()
total_interest = schedule["Interest"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Loan Amount", f"₹ {principal:,.0f}")
col2.metric("Monthly Payment", f"₹ {payment:,.0f}")
col3.metric("Total Interest", f"₹ {total_interest:,.0f}")

# --- Charts ---
st.subheader("📊 Loan Balance Over Time")
chart1 = alt.Chart(schedule).mark_line().encode(
    x="Month",
    y="Balance",
    tooltip=["Month", "Balance"]
).interactive()
st.altair_chart(chart1, use_container_width=True)

# --- Dataframe + Download ---
st.subheader("📋 Loan Payoff Schedule")
st.dataframe(schedule, use_container_width=True)

csv = schedule.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Schedule (CSV)", data=csv, file_name="amortization_schedule.csv", mime="text/csv")
