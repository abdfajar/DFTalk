import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
from pandasai.callbacks import BaseCallback
from pandasai.responses.response_parser import ResponseParser
import os

# Set OpenAI API Token
OPENAI_API_TOKEN = os.getenv("BIT_OPENAI_API_KEY", "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")

# Load OpenAI Mini model
llm = OpenAI(api_token=OPENAI_API_TOKEN, model_name="gpt-4o-mini")

class StreamlitCallback(BaseCallback):
    def __init__(self, container) -> None:
        """Initialize callback handler."""
        self.container = container

    def on_code(self, response: str):
        self.container.code(response)

class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return

def process_file(file):
    file_extension = file.name.split(".")[-1].lower()
    try:
        if file_extension == "csv":
            # Detect if semicolon or comma is used as a separator
            first_line = file.readline().decode("utf-8")
            file.seek(0)  # Reset file pointer
            delimiter = ";" if ";" in first_line else ","
            df = pd.read_csv(file, delimiter=delimiter)
        elif file_extension in ["xls", "xlsx"]:
            import openpyxl  # Ensures openpyxl is available
            df = pd.read_excel(file, engine="openpyxl")
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None
    except ImportError as e:
        st.error(f"Error: {e}. Please install 'openpyxl' for Excel support.")
        return None, None
    
    sdf = SmartDataframe(df, config={
                "llm": llm,
                "save_logs": True,
                "verbose": False,
                "response_parser": StreamlitResponse
                })
    return df, sdf

def main():
    st.title("AI-Powered Dataframe Analysis with OpenAI")
    uploaded_file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xls", "xlsx"])
    
    if uploaded_file:
        df, sdf = process_file(uploaded_file)
        if df is not None:
            st.subheader("🔎 Data Preview")
            
            with st.expander("View Data Summary"):
                st.write("### Data Overview")
                st.dataframe(df.describe(include='all'))
                
                st.write("### First 10 Rows of Data")
                st.dataframe(df.head(10))
                
            
            query = st.text_area("Enter Your Query")
            
            if query:
                container = st.container()
                answer = sdf.chat(query)

if __name__ == "__main__":
    main()
