"""Scratch harness: confirm donut/bar rendering after the stack changes."""
import streamlit as st

from dashboard.components.charts import donut_chart, horizontal_bar_chart

st.title("Chart regression probe")

st.subheader("G: donut, real distribution")
st.altair_chart(donut_chart({"Safe": 12, "Partial": 5, "Vulnerable": 3, "Critical": 1}))

st.subheader("H: donut, all-zero distribution")
st.altair_chart(donut_chart({"Safe": 0, "Partial": 0, "Vulnerable": 0, "Critical": 0}))

st.subheader("I: bar chart")
st.altair_chart(
    horizontal_bar_chart(
        [{"Channel": "SOURCE CODE", "Percentage": 96}, {"Channel": "HSM", "Percentage": 41}],
        x_field="Percentage",
        y_field="Channel",
        height=200,
    )
)
