"""The WACC card.

Run from the repo root:   streamlit run app.py

Owner: the product manager. Works on FAKE numbers until outputs/wacc.csv exists.
When the developer's pull request is merged, the app switches to real numbers automatically.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="WACC Card – AO Smith", layout="centered")

real = Path("outputs/wacc.csv")
card = pd.read_csv(real if real.exists() else "outputs/wacc_FAKE.csv").iloc[0]
inputs = pd.read_csv("inputs/assumptions.csv", index_col="item")

if not real.exists():
    st.warning(
        "Showing FAKE numbers. Run `python code/wacc.py` to generate outputs/wacc.csv."
    )

# ── Header ────────────────────────────────────────────────────────────────────
st.title(f"WACC Card: {card['ticker']}")
st.caption(f"Returns through {card['asof']}")

wacc = float(card["wacc"])
st.info(
    f"**Hurdle rate interpretation:** With a WACC of **{wacc:.2%}**, AO Smith should "
    f"accept new projects only if they are expected to return more than **{wacc:.2%}**. "
    f"Any project returning less destroys value for shareholders and debtholders."
)

st.divider()

# ── Key metrics ───────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("WACC", f"{card['wacc']:.2%}")
c2.metric("Cost of Equity", f"{card['cost_of_equity']:.2%}")
c3.metric("Beta (β)", f"{card['beta']:.2f}")

st.divider()

# ── Live sensitivity slider ───────────────────────────────────────────────────
st.subheader("Sensitivity: What if leverage changes?")
st.caption(
    "Drag the slider to see how a different capital structure would change AO Smith's WACC."
)

w_d_pct = st.slider(
    "Debt weight (w_d)",
    min_value=0,
    max_value=60,
    value=int(round(float(card["w_d"]) * 100)),
    step=1,
    format="%d%%",
)
w_d_adj = w_d_pct / 100
w_e_adj = 1.0 - w_d_adj
wacc_adj = w_e_adj * float(card["cost_of_equity"]) + w_d_adj * float(card["rd"]) * (
    1 - float(card["tax"])
)

s1, s2, s3 = st.columns(3)
s1.metric("Equity Weight", f"{w_e_adj:.0%}")
s2.metric("Debt Weight", f"{w_d_adj:.0%}")
s3.metric(
    "Adjusted WACC",
    f"{wacc_adj:.2%}",
    delta=f"{wacc_adj - wacc:+.2%}",
    delta_color="inverse",
)

st.divider()

# ── Inputs table ──────────────────────────────────────────────────────────────
st.subheader("Inputs and Sources")

LABELS = {
    "rf":  "Risk-Free Rate (rf)",
    "mrp": "Market Risk Premium (mrp)",
    "rd":  "Pre-Tax Cost of Debt (rd)",
    "tax": "Tax Rate",
    "w_e": "Equity Weight (wₑ)",
    "w_d": "Debt Weight (w_d)",
}

analyst_rows = [
    {
        "Input":  LABELS.get(item, item),
        "Value":  f"{float(row['value']):.2%}",
        "Source": row["source"],
    }
    for item, row in inputs.iterrows()
]

computed_rows = [
    {
        "Input":  "Beta (β)",
        "Value":  f"{card['beta']:.2f}",
        "Source": "Estimated from 5-year daily returns vs. SPY (code/wacc.py)",
    },
    {
        "Input":  "Cost of Equity (Ke)",
        "Value":  f"{card['cost_of_equity']:.2%}",
        "Source": (
            f"CAPM: rf + β × mrp = {card['rf']:.2%} + "
            f"{card['beta']:.2f} × {card['mrp']:.2%}"
        ),
    },
    {
        "Input":  "WACC",
        "Value":  f"{card['wacc']:.2%}",
        "Source": "wₑ × Ke + w_d × rd × (1 − tax)",
    },
]

st.markdown("**Analyst inputs** (`inputs/assumptions.csv`)")
st.dataframe(pd.DataFrame(analyst_rows), use_container_width=True, hide_index=True)

st.markdown("**Computed values** (`code/wacc.py`)")
st.dataframe(pd.DataFrame(computed_rows), use_container_width=True, hide_index=True)
