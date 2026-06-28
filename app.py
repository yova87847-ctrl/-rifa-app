import streamlit as st
import osimport pandas as pd
from fpdf import FPDF
from datetime import datetime

# ========================
# CONFIG
# ========================
st.set_page_config(page_title="Rifa Premium", layout="wide")

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
# PDF
# ========================
def generar_pdf(nombre, telefono, numeros):

    numeros = [str(n) for n in numeros]
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"J.V.R PREMIUM RIFA",ln=True,align="C")

    pdf.ln(5)

    pdf.set_font("Arial","",12)
    pdf.cell(0,8,f"Nombre: {nombre}",ln=True)
    pdf.cell(0,8,f"Telefono: {telefono}",ln=True)

    pdf.ln(3)

    pdf.set_font("Arial","B",12)
    pdf.cell(0,8,"NUMERO DE BOLETO:",ln=True)

    pdf.set_font("Arial","B",14)
    pdf.cell(0,10," - ".join(numeros),ln=True)

    pdf.ln(2)

    pdf.set_font("Arial","",11)
    pdf.cell(0,7,f"Fecha: {fecha}",ln=True)
    pdf.cell(0,7,f"Total pagado: ${PRECIO * len(numeros)}",ln=True)

    pdf.ln(4)

    pdf.set_font("Arial","B",11)
    pdf.cell(0,7,"Premio principal:",ln=True)

    pdf.set_font("Arial","",11)
    pdf.multi_cell(0,6,"Televisor Smart TV 42 pulgadas Android Full HD")
    pdf.cell(0,6,"Opcion alternativa: $1.300.000 en efectivo",ln=True)
    pdf.cell(0,6,"Sorteo: Loteria de Medellin",ln=True)

    pdf.ln(4)

    pdf.set_font("Arial","B",11)
    pdf.cell(0,7,"Responsable: Jovanis Vanegas Ropain",ln=True)

    pdf.set_font("Arial","",11)
    pdf.cell(0,7,"Contacto: 3126613272",ln=True)

    pdf.ln(5)
    pdf.cell(0,8,"Gracias por tu compra, mucha suerte!",ln=True,align="C")

    return pdf.output(dest="S").encode("latin-1")

# ========================
# ESTADISTICAS
# ========================
vendidos = df[df["estado"]=="Vendido"]
total_vendidos = len(vendidos)
total_dinero = total_vendidos * PRECIO

# ========================
# INTERFAZ
# ========================
st.title("🎟️ RIFA PREMIUM")

col1,col2,col3 = st.columns(3)
col1.metric("🎫 Vendidos", total_vendidos)
col2.metric("💰 Recaudado", f"${total_dinero}")
col3.metric("💵 Precio", f"${PRECIO}")

st.divider()

tab1, tab2 = st.tabs(["🛒 Reservar","🔒 Admin"])

# ========================
# RESERVAR
# ========================
with tab1:

    cantidad = st.number_input("Cantidad",1,20,1)
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Telefono")

    todos = [f"{i:03d}" for i in range(1000)]

    vendidos_list = df[df["estado"]=="Vendido"]["numero"].tolist()
    reservados_list = df[df["estado"]=="Pendiente"]["numero"].tolist()

    opciones = []
    mapa = {}

    for n in todos:
        if n in vendidos_list:
            label = f"🔴 {n}"
        elif n in reservados_list:
            label = f"🟡 {n}"
        else:
            label = f"🟢 {n}"

        opciones.append(label)
        mapa[label] = n

    seleccion = st.multiselect("Selecciona números", opciones)
    numeros = [mapa[s] for s in seleccion if mapa[s] not in vendidos_list]

    total = len(numeros)*PRECIO
    st.success(f"Total: ${total}")

    if st.button("✅ Reservar"):

        if not nombre or not telefono:
            st.error("Completa los datos")

        elif len(numeros)!=cantidad:
            st.error("Selecciona la cantidad correcta")

        else:
            nuevos = []

            for n in numeros:
                nuevos.append({
                    "numero":n,
                    "nombre":nombre,
                    "telefono":telefono,
                    "estado":"Pendiente"
                })

            df_local = pd.concat([df,pd.DataFrame(nuevos)], ignore_index=True)
            guardar(df_local)

            st.success("✅ Reserva guardada")
            st.rerun()

# ========================
# ADMIN COMPLETO
# ========================
with tab2:

    st.subheader("🔒 Panel Administrador")

    clave = st.text_input("Contraseña", type="password")

    if clave == ADMIN_PASSWORD:

        st.success("✅ Acceso concedido")

        st.markdown("### 📋 Todas las reservas")
        st.dataframe(df)

        st.divider()

        pendientes = df[df["estado"] == "Pendiente"]

        st.markdown("### 🟡 Reservas pendientes")

        if pendientes.empty:
            st.info("No hay reservas")
        else:
            for i,row in pendientes.iterrows():

                st.markdown(f"🎟️ **Número: {row['numero']}** | {row['nombre']}")

                col1,col2 = st.columns(2)

                # ✅ APROBAR
                with col1:
                    if st.button(f"✅ Aprobar {row['numero']}", key=f"a{i}"):

                        df.loc[df["numero"]==row["numero"],"estado"]="Vendido"
                        guardar(df)

                        pdf = generar_pdf(
                            row["nombre"],
                            row["telefono"],
                            [row["numero"]]
                        )

                        st.success("✅ Venta aprobada")

                        st.download_button(
                            "📄 Descargar comprobante",
                            pdf,
                            file_name=f"boleto_{row['numero']}.pdf"
                        )

                # ❌ RECHAZAR
                with col2:
                    if st.button(f"❌ Rechazar {row['numero']}", key=f"r{i}"):
                        df = df[df["numero"]!=row["numero"]]
                        guardar(df)
                        st.rerun()

        st.divider()

        # ❌ ELIMINAR
        num = st.text_input("Eliminar número")

        if st.button("Eliminar"):
            df = df[df["numero"]!=num]
            guardar(df)
            st.rerun()

        # 🧹 RESET
        if st.button("⚠️ BORRAR TODO"):
            df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
            guardar(df)
            st.rerun()

    elif clave:
        st.error("Contraseña incorrecta")
``
