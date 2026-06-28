import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# ========================
#(DB_FILE):# CONFIG
        df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
        df.to_csv(DB_FILE, index=False)
    return pd.read_csv(DB_FILE, dtype=str).fillna("")

def guardar(df):
    df.to_csv(DB_FILE, index=False)

 df = cargar()

# ========================
# PDF
# ========================
def generar_pdf(nombre, telefono, numeros):
    pdf = FPDF()
    pdf.add_page()

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    total = PRECIO * len(numeros)

    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"COMPROBANTE DE COMPRA",ln=True,align="C")

    pdf.ln(3)

    pdf.set_font("Arial","",11)
    pdf.cell(0,7,"Estado: Transaccion exitosa",ln=True)
    pdf.cell(0,7,"Evento: Rifa Premium J.V.R",ln=True)

    pdf.ln(3)

    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"DATOS DEL COMPRADOR",ln=True)

    pdf.set_font("Arial","",11)
    pdf.cell(0,7,f"Comprador de turno: {nombre}",ln=True)
    pdf.cell(0,7,f"Telefono: {telefono}",ln=True)

    pdf.ln(3)

    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"DETALLE DE LA COMPRA",ln=True)

    pdf.set_font("Arial","",11)
    pdf.cell(0,7,"Numeros adquiridos:",ln=True)
    pdf.multi_cell(0,7," - ".join(numeros))

    pdf.ln(2)

    pdf.cell(0,7,f"Fecha y hora: {fecha}",ln=True)
    pdf.cell(0,7,f"Total pagado: ${total}",ln=True)

    pdf.ln(3)

    pdf.multi_cell(0,7,"Premio: Televisor Smart TV 42 pulgadas o $1.300.000")

    pdf.ln(3)

    pdf.cell(0,7,"Organiza: J.V.R Premium",ln=True)
    pdf.cell(0,7,"Contacto: 3126613272",ln=True)

    pdf.ln(5)

    pdf.set_text_color(0,150,0)
    pdf.cell(0,10,"Gracias por tu compra, mucha suerte!",ln=True,align="C")

    return pdf.output(dest="S").encode("latin-1")

# ========================
# SESSION
# ========================
if "pdf_admin" not in st.session_state:
    st.session_state["pdf_admin"] = None

# ========================
# UI
# ========================
st.title("🎟️ RIFA PREMIUM")

tab1, tab2 = st.tabs(["Reservar","Administrador"])

# ========================
# RESERVAR
# ========================
with tab1:

    cantidad = st.number_input("¿Cuántos números quieres?",1,20,1)
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Telefono")

    todos = [f"{i:03d}" for i in range(1000)]
    vendidos = df[df["estado"]=="Vendido"]["numero"].tolist()
    reservados = df[df["estado"]=="Pendiente"]["numero"].tolist()

    opciones = []
    mapa = {}

    for n in todos:
        if n in vendidos:
            label = f"🔴 {n} (Vendido)"
        elif n in reservados:
            label = f"🟡 {n} (Reservado)"
        else:
            label = f"🟢 {n}"
        opciones.append(label)
        mapa[label] = n

    seleccion = st.multiselect("Selecciona números", opciones)
    numeros = [mapa[s] for s in seleccion if mapa[s] not in vendidos]

    total = len(numeros) * PRECIO
    st.success(f"💰 Total a pagar: ${total}")

    if st.button("Reservar"):
        if not nombre or not telefono:
            st.error("Completa los datos")
        elif len(numeros) != cantidad:
            st.error("Selecciona la cantidad correcta")
        else:
            nuevos=[]
            for n in numeros:
                nuevos.append({
                    "numero":n,
                    "nombre":nombre,
                    "telefono":telefono,
                    "estado":"Pendiente"
                })

            df_local = pd.concat([df,pd.DataFrame(nuevos)],ignore_index=True)
            guardar(df_local)

            st.success("✅ Reserva guardada")

# ========================
# ADMIN
# ========================
with tab2:

    st.subheader("🔒 Panel Administrador")
    clave = st.text_input("Contraseña", type="password")

    if clave == ADMIN_PASSWORD:
        st.success("Acceso concedido ✅")

        pendientes = df[df["estado"]=="Pendiente"]

        if pendientes.empty:
            st.info("No hay reservas")
        else:
            st.write("### 🟡 Pendientes")

            for i, row in pendientes.iterrows():
                st.write(f"{row['numero']} - {row['nombre']}")

                col1, col2 = st.columns(2)

                # ✅ APROBAR + PDF
                with col1:
                    if st.button(f"✅ Aprobar {row['numero']}", key=f"a{i}"):

                        df.loc[df["numero"]==row["numero"],"estado"]="Vendido"
                        guardar(df)

                        cliente = df[
                            (df["telefono"] == row["telefono"]) &
                            (df["estado"] == "Vendido")
                        ]

                        numeros_cliente = cliente["numero"].tolist()

                        pdf_bytes = generar_pdf(
                            row["nombre"],
                            row["telefono"],
                            numeros_cliente
                        )

                        st.session_state["pdf_admin"] = {
                            "file": pdf_bytes,
                            "telefono": row["telefono"]
                        }

                        st.success("✅ Compra aprobada. Descarga el comprobante abajo 👇")

                # ❌ RECHAZAR
                with col2:
                    if st.button(f"❌ Rechazar {row['numero']}", key=f"r{i}"):
                        df = df[df["numero"]!=row["numero"]]
                        guardar(df)
                        st.rerun()

        # ✅ BOTÓN PDF
        if st.session_state["pdf_admin"]:
            data = st.session_state["pdf_admin"]

            st.download_button(
                "📄 Descargar comprobante",
                data=data["file"],
                file_name=f"comprobante_{data['telefono']}.pdf"
            )

        st.write("### 📋 Datos")
        st.dataframe(df)

        # ELIMINAR
        st.write("### ❌ Eliminar número")
        num = st.text_input("Número")

        if st.button("Eliminar"):
            df = df[df["numero"]!=num]
            guardar(df)
            st.rerun()

        # RESET
        st.write("### 🧹 Reiniciar rifa")
        if st.button("⚠️ BORRAR TODO"):
            df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
            guardar(df)
            st.rerun()

    elif clave:
        st.error("Contraseña incorrecta ❌")
# ========================
st.set_page_config(page_title="Rifa", page_icon="🎟️")
DB_FILE = "rifa_db.csv"
PRECIO = 3000

ADMIN_PASSWORD = "JVR_2026_SEGUR0"

# ========================
# BASE DE DATOS
# ========================
def cargar():
