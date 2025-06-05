# app/main.py

import streamlit as st
from sec_ingestion import get_filing_text
from doc_qa import answer_question
from app.sec_ingestion import get_filing_text
from app.doc_qa import answer_question
from app.utils import clean_filing_html




st.title("📄 Credit Sentinel AI")
st.write("Analyze SEC filings for early credit risk signals.")

ticker = st.text_input("Enter Company Ticker (e.g., AAPL, TSLA)")
question = st.text_input("What do you want to know?", "Does this filing mention liquidity issues?")

if st.button("Analyze Filing"):
    raw_filing = get_filing_text(ticker)
    if raw_filing:
        cleaned_text = clean_filing_html(raw_filing)
        answer = answer_question(cleaned_text, question)
        st.subheader("Answer:")
        st.write(answer)
    else:
        st.error("Could not retrieve filing.")

