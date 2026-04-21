import pandas as pd
import streamlit as st
import io



# *********
# LOADING 
# *********

"""
Carica i dati RNA e pulisce la colonna importi (rendendoli numeri).
"""

@st.cache_data
def load_rna_data(file):
    
    # Caricamento file
    df = pd.read_csv(file, sep=';', encoding='utf-8-sig', low_memory=False)
    
    # Pulizia colonna importo (trasforma stringa con virgola in numero)
    if 'RNA_ELEMENTO_DI_AIUTO' in df.columns:
        df['RNA_ELEMENTO_DI_AIUTO'] = pd.to_numeric(
            df['RNA_ELEMENTO_DI_AIUTO'].astype(str).str.replace(',', '.'), 
            errors='coerce'
        ).fillna(0)
        
    return df


def verifica_stato_clienti(df_rna, uploaded_clienti):
    """
    Confronta il database RNA con il file Clienti tramite Codice Fiscale/P.IVA.
    Ritorna il dataframe RNA arricchito con la colonna 'STATO'.
    """
    try:
        # 1. Caricamento del file Clienti (assicuriamoci che legga le P.IVA come stringhe)
        df_clienti = pd.read_csv(uploaded_clienti, sep=';', encoding='utf-8-sig', dtype=str, low_memory=False)
        
        # Verifichiamo se la colonna esiste (adattala se nel tuo file clienti ha un nome diverso)
        col_piva_clienti = 'Partita IVA' 
        if col_piva_clienti not in df_clienti.columns:
            st.error(f"⚠️ Errore: Colonna '{col_piva_clienti}' non trovata nel file clienti!")
            return df_rna

        # 2. Pulizia e Normalizzazione P.IVA Clienti
        # Creiamo un set (più veloce della lista per i confronti) di stringhe pulite
        lista_piva_clienti = set(
            df_clienti[col_piva_clienti]
            .astype(str)
            .str.strip()
            .str.replace(' ', '')
            .unique()
        )

        # 3. Matching usando il nome colonna UFFICIALE RNA
        # La colonna corretta è 'RNA_CODICE_FISCALE_BENEFICIARIO'
        def check_stato(val):
            clean_val = str(val).strip().replace(' ', '')
            return "🟢 CLIENTE" if clean_val in lista_piva_clienti else "⚪ PROSPECT"

        df_rna['STATO'] = df_rna['RNA_CODICE_FISCALE_BENEFICIARIO'].apply(check_stato)
        
        st.sidebar.success(f"✅ Confronto completato: {len(lista_piva_clienti)} codici caricati.")
        return df_rna

    except Exception as e:
        st.error(f"❌ Errore durante il confronto: {e}")
        return df_rna
