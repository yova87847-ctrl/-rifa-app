import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# ========================
# CONFIG
#d/%m/%Y %H:%M")# ========================

    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"TRANSACCION EXITOSA",ln=True)

    pdf.ln(5)
    pdf.set_font("Arial","",11)

    pdf.cell(0,8,f"Cliente: {nombre}",ln=True)
    pdf.cell(0,8,f"Telefono: {telefono}",ln=True)

    pdf.cell(0,8,"Destino de pago: Rifa Premium JVR",ln=True)
    pdf.cell(0,8,"Motivo: Compra de numeros",ln=True)

    pdf.cell(0,8,f"Fecha y hora: {fecha}",ln=True)

    pdf.cell(0,8,f"Valor: ${PRECIO * len(numeros)}",ln=True)
    pdf.cell(0,8,"Impuestos: $0",ln=True)
    pdf.cell(0,8,"Costo transaccion: $0",ln=True)

    pdf.cell(0,8,f"Referencia 1: {telefono}",ln=True)
    pdf.cell(0,8,f"Referencia 2: {nombre}",ln=True)

    pdf.cell(0,8,f"Numeros: {' - '.join(numeros)}",ln=True)

    pdf.cell(0,8,f"Codigo unico: {datetime.now().strftime('%Y%m%d%H%M%S')}",ln=True)

    return pdf.output(dest="S").encode("latin-1")

# ========================
# SESSION
# ========================
if "reserva" not in st.session_state:
    st.session_state.reserva = None

# ========================
# HEADER
# ========================
st.markdown("## 🎟️ RIFA PREMIUM")
st.markdown("### Gana un Smart TV o dinero en efectivo")

colA, colB, colC = st.columns(3)

colA.metric("🎫 Vendidos", vendidos_count)
colB.metric("💰 Recaudado", f"${total_dinero}")
colC.metric("🎟️ Precio", f"${PRECIO}")

st.divider()

# ========================
# TABS
# ========================
tab1, tab2 = st.tabs(["🛒 Reservar","🔒 Admin"])

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

    opciones = []
    mapa = {}

    for n in todos:
        if n in vendidos:
            label = f"🔴 {n}"
        elif n in reservados:
            label = f"🟡 {n}"
        else:
            label = f"🟢 {n}"

        opciones.append(label)
        mapa[label]=n

    seleccion = st.multiselect("Selecciona números",opciones)
    numeros = [mapa[s] for s in seleccion if mapa[s] not in vendidos]

    total = len(numeros)*PRECIO
    st.success(f"💰 Total: ${total}")

    if st.button("✅ Reservar"):
        if not nombre or not telefono:
            st.error("Completa los datos")
        elif len(numeros)!=cantidad:
            st.error("Cantidad incorrecta")
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

            st.success("Reserva realizada ✅")

    # PDF
    if st.session_state.reserva:
        datos = st.session_state.reserva

        pdf = generar_pdf(datos["nombre"],datos["telefono"],datos["numeros"])

        st.download_button("📄 Descargar PDF",pdf,"rifa.pdf")

# ========================
# ADMIN
# ========================
with tab2:

    clave = st.text_input("Contraseña",type="password")

    if clave == ADMIN_PASSWORD:

        st.success("Admin activo ✅")

        pendientes = df[df["estado"]=="Pendiente"]

        for i,row in pendientes.iterrows():
            col1,col2 = st.columns(2)

            col1.write(f"{row['numero']} - {row['nombre']}")

            if col1.button("✅",key=f"a{i}"):
                df.loc[df["numero"]==row["numero"],"estado"]="Vendido"
                guardar(df)
                st.rerun()

            if col2.button("❌",key=f"r{i}"):
                df = df[df["numero"]!=row["numero"]]
                guardar(df)
                st.rerun()

        st.divider()

        st.write("### 🧹 Reset")
        if st.button("⚠️ Borrar todo"):
            df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
            guardar(df)
            st.rerun()

    elif clave:
        st.error("Contraseña incorrecta")
st.set_page_config(page_title="Rifa Premium", page_icon="🎟️", layout="wide")

DB_FILE = "rifa_db.csv"
PRECIO = 3000
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
# ESTADISTICAS
# ========================
vendidos_count = len(df[df["estado"]=="Vendido"])
total_dinero = vendidos_count * PRECIO

# ========================
# PDF
# ========================
def generar_pdf(nombre, telefono, numeros):
    pdf = FPDF()
    pdf.add_page()

