# main.py
import streamlit as st
import pandas as pd
import os
import zipfile
import io
from utils import get_regione_da_cap, processa_xml_integrale

st.set_page_config(page_title="RNA Enriched Tool", layout="wide")
st.title("🚀 RNA Data Enrichment Professional")

# --- SIDEBAR: INPUT ---
st.sidebar.header("1. Carica Database Clienti")
uploaded_file = st.sidebar.file_uploader("Scegli il file Excel o CSV", type=['xlsx', 'csv'])

st.sidebar.header("2. Percorso File RNA")
cartella_input = st.sidebar.text_input("Percorso cartella Hard Disk (es. T7 Shield)", "/Volumes/T7 Shield/AIUTI")

st.sidebar.header("3. Nome File Output")
nome_default = st.sidebar.text_input("Nome file desiderato", "Risultati_Arricchiti.csv")

# --- LOGICA PRINCIPALE ---
if uploaded_file is not None and cartella_input:
    if st.button("🚀 Avvia Scansione Database"):
        if not os.path.exists(cartella_input):
            st.error(f"La cartella {cartella_input} non è stata trovata. Controlla la connessione del disco.")
        else:
            # Caricamento dinamico del file caricato
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df_base = pd.read_excel(uploaded_file, dtype=str)
                else:
                    df_base = pd.read_csv(uploaded_file, sep=',', encoding='latin-1', dtype=str)
                
                # Normalizzazione
                df_base.columns = [str(c).strip().upper() for c in df_base.columns]
                df_base['NOME_CLEAN'] = df_base['RAGIONE SOCIALE'].astype(str).str.upper().str.strip()
                df_base['REGIONE_DERIVATA'] = df_base['CAP'].apply(get_regione_da_cap)
                
                nomi_target = set(df_base['NOME_CLEAN'].unique())
                files_rna = [f for f in os.listdir(cartella_input) if f.endswith(('.xml', '.zip'))]
                
                if not files_rna:
                    st.warning("Nessun file XML o ZIP trovato nella cartella specificata.")
                else:
                    risultati = []
                    prog_bar = st.progress(0)
                    status = st.empty()

                    for i, f_nome in enumerate(files_rna):
                        status.text(f"Analisi file {i+1}/{len(files_rna)}: {f_nome}")
                        f_path = os.path.join(cartella_input, f_nome)
                        
                        if f_nome.endswith('.zip'):
                            with zipfile.ZipFile(f_path) as z:
                                for x in z.namelist():
                                    if x.endswith('.xml'):
                                        with z.open(x) as f: 
                                            processa_xml_integrale(f, nomi_target, df_base, risultati)
                        else:
                            with open(f_path, 'rb') as f: 
                                processa_xml_integrale(f, nomi_target, df_base, risultati)
                        
                        prog_bar.progress((i + 1) / len(files_rna))
                    
                    if risultati:
                        df_res = pd.DataFrame(risultati)
                        st.success(f"✅ Elaborazione completata! Trovati {len(df_res)} record.")
                        
                        # Mostra anteprima
                        st.dataframe(df_res.head(50))

                        # --- DOWNLOAD: Scegli dove salvare ---
                        # Generiamo il CSV in memoria
                        csv_buffer = io.StringIO()
                        df_res.to_csv(csv_buffer, index=False, sep=';', encoding='utf-8-sig')
                        csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')

                        st.download_button(
                            label="💾 SALVA IL FILE RISULTANTE",
                            data=csv_bytes,
                            file_name=nome_default,
                            mime='text/csv',
                            help="Clicca qui per scegliere la cartella di destinazione sul tuo PC"
                        )
                    else:
                        st.error("Nessun match trovato tra i tuoi clienti e i file RNA analizzati.")
            
            except Exception as e:
                st.error(f"Errore durante l'elaborazione: {e}")
else:
    st.info("Configura il file dei clienti e il percorso della cartella nella barra laterale per iniziare.")
