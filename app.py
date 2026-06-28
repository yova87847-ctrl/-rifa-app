import streamlit as st
import pandas as pd
import os
from    pdf.set_font("Arial","",12)from fpdf import FPDF
    pdf.cell(0,10,f"Nombre: {nombre}",ln=True)
    pdf.cell(0,10,f"Telefono: {telefono}",ln=True)
    pdf.cell(0,10,f"Numero: {', '.join(numeros)}",ln=True)

    return pdf.output(dest="S").encode("latin-1")

st.title("RIFA")

tab1, tab2 = st.tabs(["Reservar","Admin"])

# ====================
# RESERVAR
# ====================
with tab1:
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Telefono")

    numero = st.text_input("Numero (ej: 001)")

    if st.button("Reservar"):
        nuevo = pd.DataFrame([{
            "numero": numero,
            "nombre": nombre,
            "telefono": telefono,
            "estado": "Pendiente"
        }])

        df_local = pd.concat([df, nuevo], ignore_index=True)
        guardar(df_local)

        st.success("Guardado ✅")
        st.rerun()

# ====================
# ADMIN
# ====================
with tab2:

    clave = st.text_input("Contraseña", type="password")

    if clave == ADMIN_PASSWORD:

        st.dataframe(df)

        pendientes = df[df["estado"]=="Pendiente"]

        for i,row in pendientes.iterrows():

            if st.button(f"Aprobar {row['numero']}", key=f"a{i}"):

                df.loc[df["numero"]==row["numero"],"estado"]="Vendido"
                guardar(df)

                pdf = generar_pdf(
                    row["nombre"],
                    row["telefono"],
                    [row["numero"]]
                )

                st.download_button("PDF", pdf)

            if st.button(f"Rechazar {row['numero']}", key=f"r{i}"):

                df = df[df["numero"]!=row["numero"]]
                guardar(df)
                st.rerun()

    elif clave:
        st.error("Clave incorrecta")
``
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

def generar_pdf(nombre, telefono, numeros):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"RIFA PREMIUM",ln=True)

