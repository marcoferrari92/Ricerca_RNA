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

st.sidebar.header("2. Sorgente Dati RNA")
cartella_input = st.sidebar.text_input("Percorso cartella Hard Disk", "/Volumes/T7 Shield/AIUTI")

st.sidebar.header("3. Opzioni Output")
nome_file_output = st.sidebar.text_input("Nome per il download", "risultati_finali.csv")

# --- STATO DELL'APPLICAZIONE ---
# Usiamo session_state per conservare i risultati anche se Streamlit ricarica la pagina
if 'risultati_finali' not in st.session_state:
    st.session_state.risultati_finali = None

# --- LOGICA DI ANALISI ---
if uploaded_file and cartella_input:
    if st.button("🏁 Avvia Analisi Integrale"):
        if not os.path.exists(cartella_input):
            st.error("Percorso cartella non trovato!")
        else:
            try:
                # Lettura file aziende (Excel o CSV)
                if uploaded_file.name.endswith('.xlsx'):
                    df_base = pd.read_excel(uploaded_file, dtype=str)
                else:
                    df_base = pd.read_csv(uploaded_file, sep=',', encoding='latin-1', dtype=str)
                
                # Normalizzazione
                df_base.columns = [str(c).strip().upper() for c in df_base.columns]
                df_base['NOME_CLEAN'] = df_base['RAGIONE SOCIALE'].astype(str).str.upper().str.strip()
                df_base['REGIONE_DERIVATA'] = df_base['CAP'].apply(get_regione_da_cap)
                
                nomi_target = set(df_base['NOME_CLEAN'].unique())
                lista_files = [f for f in os.listdir(cartella_input) if f.endswith(('.xml', '.zip'))]
                
                risultati_accumulati = []
                
                # Interfaccia di progresso
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, nome_f in enumerate(lista_files):
                    status_text.text(f"Analizzando file {i+1}/{len(lista_files)}: {nome_f}")
                    f_path = os.path.join(cartella_input, nome_f)
                    
                    if nome_f.endswith('.zip'):
                        with zipfile.ZipFile(f_path) as z:
                            for x in z.namelist():
                                if x.endswith('.xml'):
                                    with z.open(x) as f:
                                        processa_xml_integrale(f, nomi_target, df_base, risultati_accumulati)
                    else:
                        with open(f_path, 'rb') as f:
                            processa_xml_integrale(f, nomi_target, df_base, risultati_accumulati)
                    
                    progress_bar.progress((i + 1) / len(lista_files))
                
                if risultati_accumulati:
                    st.session_state.risultati_finali = pd.DataFrame(risultati_accumulati)
                    st.success(f"Analisi completata! Trovati {len(st.session_state.risultati_finali)} match.")
                else:
                    st.warning("Analisi conclusa, ma nessun match trovato.")
                    st.session_state.risultati_finali = None
                    
            except Exception as e:
                st.error(f"Errore tecnico: {e}")

# --- PULSANTE DI DOWNLOAD (Appare solo se l'analisi è finita) ---
if st.session_state.risultati_finali is not None:
    st.divider()
    st.subheader("💾 Risultati Pronti")
    st.write(f"Puoi scaricare il file con {len(st.session_state.risultati_finali)} righe estratte.")
    
    # Preparazione del CSV in memoria (buffer)
    csv_buffer = io.StringIO()
    st.session_state.risultati_finali.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig')
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label="📥 SCARICA FILE CSV FINALE",
        data=csv_data,
        file_name=nome_file_output,
        mime='text/csv',
    )
    
    # Mostra un'anteprima dei primi 20 risultati
    st.dataframe(st.session_state.risultati_finali.head(20))
