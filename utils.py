# utils.py
import pandas as pd
import xml.etree.ElementTree as ET
from config import PARAMETRI_ATTESI

def get_regione_da_cap(cap):
    if pd.isna(cap) or str(cap).strip() == '': return "SCONOSCIUTA"
    cap_str = str(cap).strip().split('.')[0].zfill(5)[:2]
    mapping = {
        '00': 'Lazio', '01': 'Lazio', '02': 'Lazio', '03': 'Lazio', '04': 'Lazio',
        '05': 'Umbria', '06': 'Umbria', '07': 'Sardegna', '08': 'Sardegna', '09': 'Sardegna',
        '10': 'Piemonte', '11': "Valle d'Aosta/Vallée d'Aoste", '12': 'Piemonte', '13': 'Piemonte', 
        '14': 'Piemonte', '15': 'Piemonte', '16': 'Liguria', '17': 'Liguria', '18': 'Liguria', '19': 'Liguria',
        '20': 'Lombardia', '21': 'Lombardia', '22': 'Lombardia', '23': 'Lombardia', '24': 'Lombardia', 
        '25': 'Lombardia', '26': 'Lombardia', '27': 'Lombardia', '28': 'Lombardia', '29': 'Lombardia',
        '30': 'Veneto', '31': 'Veneto', '32': 'Veneto', '33': 'Friuli-Venezia Giulia', '34': 'Friuli-Venezia Giulia',
        '35': 'Veneto', '36': 'Veneto', '37': 'Veneto', '38': 'Provincia Autonoma di Trento',
        '39': 'Provincia Autonoma di Bolzano/Bozen', '40': 'Emilia-Romagna', '41': 'Emilia-Romagna', 
        '42': 'Emilia-Romagna', '43': 'Emilia-Romagna', '44': 'Emilia-Romagna', '45': 'Emilia-Romagna', 
        '46': 'Emilia-Romagna', '47': 'Emilia-Romagna', '48': 'Emilia-Romagna', '50': 'Toscana', 
        '51': 'Toscana', '52': 'Toscana', '53': 'Toscana', '54': 'Toscana', '55': 'Toscana', '56': 'Toscana', 
        '57': 'Toscana', '58': 'Toscana', '59': 'Toscana', '60': 'Marche', '61': 'Marche', '62': 'Marche', 
        '63': 'Marche', '64': 'Abruzzo', '65': 'Abruzzo', '66': 'Abruzzo', '67': 'Abruzzo', '70': 'Puglia', 
        '71': 'Puglia', '72': 'Puglia', '73': 'Puglia', '74': 'Puglia', '76': 'Puglia', '75': 'Basilicata', 
        '85': 'Basilicata', '80': 'Campania', '81': 'Campania', '82': 'Campania', '83': 'Campania', 
        '84': 'Campania', '86': 'Molise', '87': 'Calabria', '88': 'Calabria', '89': 'Calabria',
        '90': 'Sicilia', '91': 'Sicilia', '92': 'Sicilia', '93': 'Sicilia', '94': 'Sicilia', '95': 'Sicilia', 
        '96': 'Sicilia', '97': 'Sicilia', '98': 'Sicilia'
    }
    return mapping.get(cap_str, "Sconosciuta").upper()

def processa_xml_integrale(file_obj, nomi_target_set, df_base, risultati_totali):
    try:
        context = ET.iterparse(file_obj, events=('end',))
        _, root = next(context)
        curr_data = {}
        for event, elem in context:
            tag = elem.tag.split('}')[-1]
            if elem.text and elem.text.strip() and len(elem) == 0:
                curr_data[tag] = elem.text.strip()
            if tag == 'AIUTO':
                nome_rna = curr_data.get('DENOMINAZIONE_BENEFICIARIO', '')
                reg_rna = curr_data.get('REGIONE_BENEFICIARIO', '').upper().strip()
                if nome_rna:
                    n_rna_c = nome_rna.upper().strip()
                    if n_rna_c in nomi_target_set:
                        matches = df_base[df_base['NOME_CLEAN'] == n_rna_c]
                        if len(matches) > 1 and reg_rna:
                            matches = matches[matches['REGIONE_DERIVATA'] == reg_rna]
                        for _, riga in matches.iterrows():
                            record = riga.to_dict()
                            for k, v in curr_data.items(): record[f"RNA_{k}"] = v
                            mancanti = [p for p in PARAMETRI_ATTESI if p not in curr_data]
                            record['INTEGRITA'] = "OK" if not mancanti else f"MANCA: {mancanti}"
                            risultati_totali.append(record)
                curr_data = {}
                root.clear()
    except: pass
