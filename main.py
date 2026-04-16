# main.py
import streamlit as st
import pandas as pd
import os
import zipfile
from utils import get_regione_da_cap, processa_xml_integrale

st.set_page_config(page_title="RNA Enriched Tool", layout="wide")
st.title("🚀 RNA Data Enrichment")

# Input Percorsi
st.sidebar.header("Impostazioni")
cartella = st.sidebar.text_input("Cartella XML (Hard Disk)", "/Volumes/T7 Shield/AIUTI")
file_xlsx = st.sidebar.text_input("File Excel Clienti", "elenco_aziende.xlsx")
file_out = st.sidebar.text_input("Nome file output", "Risultati_RNA.csv")

if st.button("🚀 Avvia Scansione"):
    if os.path.exists(cartella) and os.path.exists(file_xlsx):
        # Caricamento e Normalizzazione
        df_base = pd.read_excel(file_xlsx, dtype=str)
        df_base.columns = [str(c).strip().upper() for c in df_base.columns]
        df_base['NOME_CLEAN'] = df_base['RAGIONE SOCIALE'].astype(str).str.upper().str.strip()
        df_base['REGIONE_DERIVATA'] = df_base['CAP'].apply(get_regione_da_cap)
        
        nomi_target = set(df_base['NOME_CLEAN'].unique())
        files = [f for f in os.listdir(cartella) if f.endswith(('.xml', '.zip'))]
        
        risultati = []
        bar = st.progress(0)
        status = st.empty()

        for i, f_nome in enumerate(files):
            status.text(f"Analisi {f_nome} ({i+1}/{len(files)})")
            f_path = os.path.join(cartella, f_nome)
            
            if f_nome.endswith('.zip'):
                with zipfile.ZipFile(f_path) as z:
                    for x in z.namelist():
                        if x.endswith('.xml'):
                            with z.open(x) as f: processa_xml_integrale(f, nomi_target, df_base, risultati)
            else:
                with open(f_path, 'rb') as f: processa_xml_integrale(f, nomi_target, df_base, risultati)
            
            bar.progress((i + 1) / len(files))
        
        if risultati:
            df_res = pd.DataFrame(risultati)
            df_res.to_csv(file_out, index=False, sep=';', encoding='utf-8-sig')
            st.success(f"Completato! Salvati {len(df_res)} record in {file_out}")
            st.dataframe(df_res.head())
    else:
        st.error("Percorsi non validi. Controlla l'Hard Disk o il nome del file Excel.")
