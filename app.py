import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Configurazione della pagina
st.set_page_config(page_title="Bilancio Mensile", layout="wide")
st.title("📅 Il mio Bilancio Mensile")

# --- 1. INSERIMENTO MANUALE DATI (BARRA LATERALE) ---
st.sidebar.header("📝 Inserisci Movimento")

tipo = st.sidebar.selectbox("Tipo di movimento", ["Ricavo", "Spesa"])
nuova_cifra = st.sidebar.number_input("Importo (€)", min_value=0.0, step=1.0, format="%.2f")
nuova_nota = st.sidebar.text_input("Descrizione")

# Calendario in formato italiano
data_selezionata = st.sidebar.date_input("Data", format="DD/MM/YYYY")
data_formattata = data_selezionata.strftime("%d-%m-%Y")

# Logica di divisione mensile dei file
mese_anno_scelto = data_selezionata.strftime("%m_%Y")
FILE_CORRENTE = f"bilancio_{mese_anno_scelto}.csv"

if st.sidebar.button("Registra Movimento"):
    if nuova_cifra > 0 and nuova_nota:
        riga = f"{tipo},{nuova_cifra},{nuova_nota},{data_formattata}\n"
        with open(FILE_CORRENTE, "a") as file:
            file.write(riga)
        st.sidebar.success(f"{tipo} registrato con successo!")
        st.rerun()
    else:
        st.sidebar.error("Inserisci una cifra maggiore di 0 e una nota!")


# --- 2. SELETTORE DEL MESE DA VISUALIZZARE ---
file_nella_cartella = os.listdir(".")
file_bilanci = [f for f in file_nella_cartella if f.startswith("bilancio_") and f.endswith(".csv")]

if not file_bilanci:
    mese_corrente_testo = datetime.now().strftime("%m_%Y")
    file_bilanci = [f"bilancio_{mese_corrente_testo}.csv"]

mesi_disponibili = [f.replace("bilancio_", "").replace(".csv", "") for f in file_bilanci]
mesi_disponibili.sort(reverse=True)

mesi_formattati_per_utente = [m.replace("_", "/") for m in mesi_disponibili]
mese_selezionato_utente = st.selectbox("Seleziona il mese da visualizzare:", mesi_formattati_per_utente)

mese_da_vedere = mese_selezionato_utente.replace("/", "_")
FILE_VISUALIZZATO = f"bilancio_{mese_da_vedere}.csv"


# --- 3. LETTURA DATI, GRAFICI E STRUTTURA VISIVA ---
st.markdown(f"### 📈 Statistiche del mese: {mese_selezionato_utente}")

if os.path.exists(FILE_VISUALIZZATO) and os.path.getsize(FILE_VISUALIZZATO) > 0:
    df = pd.read_csv(FILE_VISUALIZZATO, names=["Tipo", "Cifra", "Nota", "Data"], on_bad_lines='skip')
    
    # 🌟 PROTEZIONE ANTI-ERRORE: Rimuoviamo righe completamente vuote o con spazi
    df = df.dropna(subset=["Data"])
    df["Data"] = df["Data"].astype(str).str.strip()
    df = df[df["Data"] != ""]
    
    totale_ricavi = df[df["Tipo"] == "Ricavo"]["Cifra"].sum()
    totale_spese = df[df["Tipo"] == "Spesa"]["Cifra"].sum()
    bilancio_netto = totale_ricavi - totale_spese
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Entrate", f"{totale_ricavi:.2f} €")
    col2.metric("🔴 Uscite", f"{totale_spese:.2f} €")
    col3.metric("⚖️ Totale", f"{bilancio_netto:.2f} €")
        
    st.subheader("Andamento Cronologico")
    
    # Creiamo una copia ordinata cronologicamente mettendo 'errors=coerce' per saltare eventuali testi errati
    df_grafico = df.copy()
    df_grafico["Data_Date"] = pd.to_datetime(df_grafico["Data"], format="%d-%m-%Y", errors='coerce')
    df_grafico = df_grafico.dropna(subset=["Data_Date"]) # Elimina definitivamente la riga problematica nel grafico
    df_grafico = df_grafico.sort_values("Data_Date")
    
    df_grafico["Cifra_Grafico"] = df_grafico.apply(lambda row: row["Cifra"] if row["Tipo"] == "Ricavo" else -row["Cifra"], axis=1)
    colori_sequenza = df_grafico["Tipo"].map({"Ricavo": "#2ca02c", "Spesa": "#d62728"}).tolist()
    
    fig_bar = px.bar(df_grafico, x="Data", y="Cifra_Grafico", hover_data=["Nota", "Tipo"])
    fig_bar.update_traces(marker_color=colori_sequenza)
    
    fig_bar.update_xaxes(type='category', categoryorder='trace')
    fig_bar.update_yaxes(title_text="Importo (€)")
    fig_bar.update_layout(showlegend=False)
    
    st.plotly_chart(fig_bar, use_container_width=True)
        
    # --- 4. REGISTRO MODIFICABILE ---
    st.subheader("🗂️ Registro spese")
    
    dati_modificati = st.data_editor(df, use_container_width=True, num_rows="dynamic", key="editor_spese")
    
    if not dati_modificati.equals(df):
        st.warning("⚠️ Hai modificato o eliminato dei dati nella tabella!")
        if st.button("💾 Conferma e Salva modifiche"):
            dati_modificati.reset_index(drop=True).to_csv(FILE_VISUALIZZATO, header=False, index=False)
            st.success("Modifiche salvate nel file CSV!")
            st.rerun()
            
else:
    st.info(f"Nessun dato presente per il mese {mese_selezionato_utente}.")
