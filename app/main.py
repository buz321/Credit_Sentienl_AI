# app/main.py

import streamlit as st
from .sec_ingestion import get_filing_text
from .document_processor import SECDocumentProcessor
from .doc_qa import answer_question

# Set page config
st.set_page_config(
    page_title="Credit Sentinel AI",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 Credit Sentinel AI")
st.write("Analyze SEC filings for early credit risk signals using advanced NLP. This tool helps identify potential financial distress indicators in company filings.")

# Sidebar controls
st.sidebar.title("Analysis Controls")

# Company ticker input
st.sidebar.write("Company Ticker (e.g., AAPL, TSLA)")
ticker = st.sidebar.text_input("", key="ticker_input")

# Quick questions dropdown
st.sidebar.write("Quick Questions")
st.sidebar.write("Select a question or type your own below:")
questions = [
    "What is the company's debt situation?",
    "What are the main risk factors?",
    "How is their liquidity position?",
    "What are their major financial challenges?",
    "Are there any going concern issues?",
    "What is their cash flow situation?",
]
selected_question = st.sidebar.selectbox("", questions)

# Custom question input
custom_question = st.sidebar.text_input("Or type your own question:", "")

# Use either selected or custom question
question = custom_question if custom_question else selected_question

# Initialize session state
if 'doc_processor' not in st.session_state:
    st.session_state.doc_processor = None

# Process the filing when ticker is entered
if ticker:
    try:
        # Get the filing text
        filing_text = get_filing_text(ticker)
        
        if filing_text:
            # Process the filing
            if not st.session_state.doc_processor:
                st.session_state.doc_processor = SECDocumentProcessor()
            st.session_state.doc_processor.process_filing(filing_text)
        else:
            st.error(f"Could not retrieve SEC filing for {ticker}. Please check the ticker symbol and try again.")
            
    except Exception as e:
        st.error(f"Error processing filing: {e}")

# Answer the question
if ticker and question and st.session_state.doc_processor:
    try:
        # Get answer
        response = answer_question(
            st.session_state.doc_processor.get_relevant_context(question),
            question
        )
        
        # Display answer
        if response:
            st.write("### Answer")
            st.write(response)
        else:
            st.warning("Could not find a confident answer to your question. Try rephrasing or asking about a different topic.")
            
    except Exception as e:
        st.error(f"Error answering question: {e}")
elif ticker and question:
    st.warning("Please wait while we process the filing...")

