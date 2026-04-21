import streamlit as st
import pandas as pd
import os
import zipfile
import io
from utils import get_regione_da_cap, processa_xml_integrale

st.set_page_config(page_title="RNA Analysis Tool", layout="wide")
st.title("🚀 RNA Data Enrichment")

# --- SIDEBAR: INPUT ---
st.sidebar.header("1. Carica Database Aziende")
uploaded_file = st.sidebar.file_uploader("Trascina qui il tuo Excel/CSV", type=['xlsx', 'csv'])



