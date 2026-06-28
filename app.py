import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
st.set_page_config(page_title="Rifa Premium", layout="wide")

DB_FILE = "rifa_db.csv"
PRECIO = 3000
ADMIN_PASSWORD = "1234"
def cargar():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
        df.to_csv(DB_FILE, index=False)
    return pd.read_csv(DB_FILE, dtype=str).fillna("")

def guardar(df):
    df.to_csv(DB_FILE, index=False)

df = cargar()

st.title("🎟️ RIFA")

tab1, tab2 = st.tabs(["Reservar","Admin"])
