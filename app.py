import streamlit as st
import pandas as pd
import os
from.csv"from fpdf import FPDF
PRECIO = 3000
ADMIN_PASSWORD = "JVR_2026_SEGUR0"

def cargar():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
        df.to_csv(DB_FILE, index=False)
    return pd.read_csv(DB_FILE).fillna("")

def guardar(df):
    df.to_csv(DB_FILE, index=False)

df = cargar()

def generar_pdf(nombre, telefono, numeros):
    pdf = FPDF()
    pdf.add_page()

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"RIFA PREMIUM",ln=True,align="C")

    pdf.set_font("Arial","",12)
    pdf.cell(0,10,f"Nombre: {nombre}",ln=True)
    pdf.cell(0,10,f"Telefono: {telefono}",ln=True)

    pdf.cell(0,10,"Numeros:",ln=True)
    pdf.multi_cell(0,8," - ".join(numeros))

    pdf.cell(0,10,f"Total: ${PRECIO * len(numeros)}",ln=True)
    pdf.cell(0,10,f"Fecha: {fecha}",ln=True)

    return pdf.output(dest="S").encode("latin-1")

st.title("🎟️ RIFA PREMIUM")

tab1, tab2 = st.tabs(["Reservar","Admin"])

# ========================
# RESERVAR
# ========================
with tab1:

    cantidad = st.number_input("Cantidad",1,20,1)
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Telefono")

    todos = [f"{i:03d}" for i in range(1000)]

    vendidos = df[df["estado"]=="Vendido"]["numero"].tolist()
    reservados = df[df["estado"]=="Pendiente"]["numero"].tolist()

    opciones=[]
    mapa={}

    for n in todos:
        if n in vendidos:
            label=f"🔴 {n}"
        elif n in reservados:
            label=f"🟡 {n}"
        else:
            label=f"🟢 {n}"
        opciones.append(label)
        mapa[label]=n

    seleccion = st.multiselect("Numeros", opciones)
    numeros = [mapa[s] for s in seleccion if mapa[s] not in vendidos]

    total=len(numeros)*PRECIO
    st.success(f"Total: ${total}")

    if st.button("Reservar"):
        nuevos=[]
        for n in numeros:
            nuevos.append({
                "numero":n,
                "nombre":nombre,
                "telefono":telefono,
                "estado":"Pendiente"
            })

        df = pd.concat([df,pd.DataFrame(nuevos)], ignore_index=True)
        guardar(df)

        st.success("Reserva guardada ✅")
        st.rerun()

# ========================
# ADMIN
# ========================
with tab2:

    clave = st.text_input("Contraseña", type="password")

    if clave == ADMIN_PASSWORD:

        st.dataframe(df)

        pendientes = df[df["estado"]=="Pendiente"]

        for i,row in pendientes.iterrows():

            col1,col2 = st.columns(2)

            with col1:
                if st.button(f"Aprobar {row['numero']}", key=f"a{i}"):

                    df.loc[df["numero"]==row["numero"],"estado"]="Vendido"
                    guardar(df)

                    pdf = generar_pdf(
                        row["nombre"],
                        row["telefono"],
                        [row["numero"]]
                    )

                    st.download_button(
                        "Descargar PDF",
                        pdf,
                        file_name="boleto.pdf"
                    )

            with col2:
                if st.button(f"Rechazar {row['numero']}", key=f"r{i}"):
                    df = df[df["numero"]!=row["numero"]]
                    guardar(df)
                    st.rerun()

    elif clave:
        st.error("Contraseña incorrecta")
from datetime import datetime

st.set_page_config(page_title="Rifa Premium", layout="wide")

