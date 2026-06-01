import streamlit as pd
import streamlit as st
import pandas as pd
import os
import glob

st.set_page_config(page_title="Mio Bilancio Personale", layout="wide")
st.title("📊 Il mio Bilancio Personale")

# 1. FUNZIONE PER CERCARE TUTTI I FILE CSV NELLA CARTELLA
def elenco_file_bilancio():
    # Cerca tutti i file che iniziano con 'bilancio_' e finiscono con '.csv'
    files = glob.glob("bilancio_*.csv")
    dati_file = []
    
    for f in files:
        # Il nome del file è tipo: bilancio_05_2026.csv
        # Lo dividiamo per prendere mese e anno
        nome_senza_estensione = f.replace(".csv", "")
        parti = nome_senza_estensione.split("_")
        if len(parti) == 3:
            mese = parti[1]
            anno = parti[2]
            dati_file.append({"file": f, "mese": mese, "anno": anno})
            
    return pd.DataFrame(dati_file)

df_files = elenco_file_bilancio()

if df_files.empty:
    st.warning("Non ho trovato nessun file CSV del bilancio. Registra la prima spesa per iniziare!")
else:
    # 2. SELEZIONE DELL'ANNO (Ordinato dal più recente)
    anni_disponibili = sorted(df_files["anno"].unique(), reverse=True)
    
    st.sidebar.header("🗂️ Filtra i Dati")
    anno_scelto = st.sidebar.selectbox("1. Scegli l'Anno", anni_disponibili)
    
    # Filtriamo i file in base all'anno scelto
    df_filtrato_anno = df_files[df_files["anno"] == anno_scelto]
    
    # 3. SELEZIONE DEL MESE (Ordinato in base all'anno scelto)
    mesi_disponibili = sorted(df_filtrato_anno["mese"].unique(), reverse=True)
    
    # Dizionario per mostrare i nomi dei mesi invece dei numeri
    nomi_mesi = {
        "01": "Gennaio", "02": "Febbraio", "03": "Marzo", "04": "Aprile",
        "05": "Maggio", "06": "Giugno", "07": "Luglio", "08": "Agosto",
        "09": "Settembre", "10": "Ottobre", "11": "Novembre", "12": "Dicembre"
    }
    
    mese_scelto_num = st.sidebar.selectbox(
        "2. Scegli il Mese", 
        mesi_disponibles, 
        format_func=lambda x: nomi_mesi.get(x, x)
    )
    
    # Trova il file corrispondente alla scelta
    file_selezionato = df_filtrato_anno[df_filtrato_anno["mese"] == mese_scelto_num]["file"].values[0]
    
    # 4. CARICAMENTO DATI DEL FILE SELEZIONATO
    try:
        df = pd.read_csv(file_selezionato, names=["Tipo", "Cifra", "Nota", "Data"])
        
        # Calcolo Totali
        spese = df[df["Tipo"] == "Spesa"]["Cifra"].sum()
        ricavi = df[df["Tipo"] == "Ricavo"]["Cifra"].sum()
        risparmio = ricavi - spese
        
        # Mostra i dati sullo schermo del telefono
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 Entrate", f"{ricavi:.2f} €")
        col2.metric("🔴 Uscite", f"{spese:.2f} €")
        col3.metric("💰 Portafoglio", f"{risparmio:.2f} €", delta=f"{risparmio:.2f} €")
        
        st.write("---")
        
        # Grafico Spese per Nota
        st.subheader("📈 Analisi delle Uscite")
        df_spese = df[df["Tipo"] == "Spesa"]
        if not df_spese.empty:
            st.bar_chart(data=df_spese, x="Nota", y="Cifra")
        else:
            st.info("Nessuna spesa registrata in questo mese.")
            
        # Tabella Registro Spese
        st.subheader("🗂️ Registro movimenti")
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")

# 5. FORM PER AGGIUNGERE NUOVI MOVIMENTI (Salva nel mese corrente)
st.sidebar.write("---")
st.sidebar.subheader("✍️ Inserisci Movimento")
# ... (qui continua il tuo codice del form per salvare i dati, che rimane identico)
