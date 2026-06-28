import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# ========================
# CONFIG
# ========================
st.set_page_config(page_title="Rifa", page_icon="🎟️")
DB_FILE = "rifa_db.csv"
PRECIO = 3000

# 🔒 CONTRASEÑA SEGURA
ADMIN_PASSWORD = "JVR_2026_SEGUR0"

# ========================
# BASE DE DATOS
# ========================
def cargar():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
        df.to_csv(DB_FILE, index=False)
    return pd.read_csv(DB_FILE, dtype=str).fillna("")

def guardar(df):
    df.to_csv(DB_FILE, index=False)

df = cargar()

# ========================
# PDF PROFESIONAL
# ========================
def generar_pdf(nombre, telefono, numeros):
    pdf = FPDF()
    pdf.add_page()

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf.set_font("Arial","B",18)
    pdf.set_text_color(200,0,0)
    pdf.cell(0,10,"J.V.R PREMIUM RIFA",ln=True,align="C")

    pdf.ln(5)

    pdf.set_text_color(0,0,0)
    pdf.set_font("Arial","",11)

    pdf.cell(0,8,f"Nombre: {nombre}",ln=True)
    pdf.cell(0,8,f"Telefono: {telefono}",ln=True)

    pdf.ln(3)

    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"NUMEROS DE BOLETO",ln=True)

    pdf.set_font("Arial","",11)
    pdf.cell(0,8," - ".join(numeros),ln=True)

    pdf.ln(3)

    pdf.cell(0,8,f"Fecha: {fecha}",ln=True)
    pdf.cell(0,8,f"Total pagado: ${PRECIO * len(numeros)}",ln=True)

    pdf.ln(4)

    pdf.multi_cell(0,7,"Premio: Televisor Smart TV 42 pulgadas o $1.300.000")

    pdf.ln(4)

    pdf.cell(0,7,"Responsable: Jovanis Vanegas",ln=True)
    pdf.cell(0,7,"Contacto: 3126613272",ln=True)

    pdf.ln(5)

    pdf.set_text_color(0,150,0)
    pdf.cell(0,10,"Gracias por tu compra, mucha suerte!",ln=True,align="C")

    return pdf.output(dest="S").encode("latin-1")

# ========================
# SESSION
# ========================
if "reserva" not in st.session_state:
    st.session_state.reserva = None

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
        mapa[label]=n

    seleccion = st.multiselect("Selecciona números",opciones)
    numeros = [mapa[s] for s in seleccion if mapa[s] not in vendidos]

    total = len(numeros)*PRECIO
    st.success(f"💰 Total a pagar: ${total}")

    if st.button("Reservar"):
        if not nombre or not telefono:
            st.error("Completa los datos")
        elif len(numeros)!=cantidad:
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

            st.session_state.reserva={
                "nombre":nombre,
                "telefono":telefono,
                "numeros":numeros
            }

            st.success("✅ Reserva guardada")

    # ✅ PDF Y WHATSAPP
    if st.session_state.reserva:
        datos = st.session_state.reserva

        pdf_bytes = generar_pdf(datos["nombre"],datos["telefono"],datos["numeros"])

        st.download_button("📄 Descargar comprobante",data=pdf_bytes,file_name="rifa.pdf")

        mensaje = f"Hola, reservé {', '.join(datos['numeros'])}. Total ${len(datos['numeros'])*PRECIO}"
        link = f"https://wa.me/{datos['telefono']}?text={mensaje.replace(' ','%20')}"
        st.markdown(link)

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

                # ✅ APROBAR
                with col1:
                    if st.button(f"✅ Aprobar {row['numero']}", key=f"a{i}"):
                        df.loc[df["numero"]==row["numero"],"estado"]="Vendido"
                        guardar(df)
                        st.rerun()

                # ✅ RECHAZAR
                with col2:
                    if st.button(f"❌ Rechazar {row['numero']}", key=f"r{i}"):
                        df = df[df["numero"]!=row["numero"]]
                        guardar(df)
                        st.rerun()

        st.write("### 📋 Datos")
        st.dataframe(df)

        # ❌ ELIMINAR MANUAL
        st.write("### ❌ Eliminar número")
        num = st.text_input("Número")

        if st.button("Eliminar"):
            df = df[df["numero"]!=num]
            guardar(df)
            st.rerun()

        # 🧹 RESET TOTAL
        st.write("### 🧹 Reiniciar rifa")
        if st.button("⚠️ BORRAR TODO"):
            df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
            guardar(df)
            st.rerun()

    elif clave:
        st.error("Contraseña incorrecta ❌")

