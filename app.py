import streamlit as st
import pandas as pd
import os

# ========================
# CONFIG
# ========================
st.set_page_config(page_title="Rifa Premium", layout="wide")

DB_FILE = "rifa_db.csv"
PRECIO = 3000
ADMIN_PASSWORD = "JVR_2026_SEGUR0"

# ========================
# DATOS
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
# INTERFAZ
# ========================
st.title("🎟️ RIFA PREMIUM")

tab1, tab2 = st.tabs(["🛒 Reservar","🔒 Admin"])

# ========================
# RESERVAR
# ========================
with tab1:

    cantidad = st.number_input("Cantidad",1,20,1)
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Telefono")

    todos = [f"{i:03d}" for i in range(100)]
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
    st.success(f"💰 Total: ${total}")

    if st.button("Reservar"):
        if not nombre or not telefono:
            st.error("Completa datos")
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

            df_local=pd.concat([df,pd.DataFrame(nuevos)],ignore_index=True)
            guardar(df_local)
            st.success("Reserva guardada ✅")
            st.rerun()

# ========================
# ADMIN COMPLETO
# ========================
with tab2:

    st.subheader("🔒 Panel Administrador")

    clave = st.text_input("Contraseña", type="password")

    if clave == ADMIN_PASSWORD:

        st.success("✅ Acceso concedido")

        # 🔥 TABLA
        st.dataframe(df)

        # 🔥 PENDIENTES
        pendientes = df[df["estado"]=="Pendiente"]

        st.write("### 🟡 Pendientes")

        for i,row in pendientes.iterrows():

            st.write(f"{row['numero']} - {row['nombre']}")

            col1,col2 = st.columns(2)

            # ✅ APROBAR
            with col1:
                if st.button(f"Aprobar {row['numero']}", key=f"a{i}"):
                    df.loc[df["numero"]==row["numero"],"estado"]="Vendido"
                    guardar(df)
                    st.rerun()

            # ❌ RECHAZAR
            with col2:
                if st.button(f"Rechazar {row['numero']}", key=f"r{i}"):
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
