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
# ESTADISTICAS 💰
# ========================
vendidos = df[df["estado"] == "Vendido"]
total_vendidos = len(vendidos)
total_dinero = total_vendidos * PRECIO

# ========================
# INTERFAZ
# ========================
st.title("🎟️ RIFA PREMIUM")
st.markdown("### Gana un Smart TV o dinero en efectivo")

col1, col2, col3 = st.columns(3)
col1.metric("🎫 Vendidos", total_vendidos)
col2.metric("💰 Recaudado", f"${total_dinero}")
col3.metric("💵 Precio", f"${PRECIO}")

st.divider()

tab1, tab2 = st.tabs(["🛒 Reservar","🔒 Admin"])

# ========================
# RESERVAR
# ========================
with tab1:

    cantidad = st.number_input("Cantidad", 1, 20, 1)
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Telefono")

    # 🔥 CORRECTO 000 → 999
    todos = [f"{i:03d}" for i in range(1000)]

    vendidos_list = df[df["estado"] == "Vendido"]["numero"].tolist()
    reservados_list = df[df["estado"] == "Pendiente"]["numero"].tolist()

    opciones = []
    mapa = {}

    for n in todos:
        if n in vendidos_list:
            label = f"🔴 {n} Vendido"
        elif n in reservados_list:
            label = f"🟡 {n} Reservado"
        else:
            label = f"🟢 {n}"

        opciones.append(label)
        mapa[label] = n

    seleccion = st.multiselect("Selecciona números", opciones)

    numeros = [mapa[s] for s in seleccion if mapa[s] not in vendidos_list]

    total = len(numeros) * PRECIO
    st.success(f"💰 Total: ${total}")

    if st.button("✅ Reservar"):
        if not nombre or not telefono:
            st.error("Completa los datos")
        elif len(numeros) != cantidad:
            st.error("Selecciona la cantidad correcta")
        else:
            nuevos = []
            for n in numeros:
                nuevos.append({
                    "numero": n,
                    "nombre": nombre,
                    "telefono": telefono,
                    "estado": "Pendiente"
                })

            df_local = pd.concat([df, pd.DataFrame(nuevos)], ignore_index=True)
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
            for i, row in pendientes.iterrows():

                st.markdown(f"**🎟️ {row['numero']}** | {row['nombre']}")

                col1, col2 = st.columns(2)

                # ✅ APROBAR
                with col1:
                    if st.button(f"✅ Aprobar {row['numero']}", key=f"a{i}"):
                        df.loc[df["numero"] == row["numero"], "estado"] = "Vendido"
                        guardar(df)
                        st.rerun()

                # ❌ RECHAZAR
                with col2:
                    if st.button(f"❌ Rechazar {row['numero']}", key=f"r{i}"):
                        df = df[df["numero"] != row["numero"]]
                        guardar(df)
                        st.rerun()

        st.divider()

        # ❌ ELIMINAR MANUAL
        st.markdown("### ❌ Eliminar número manual")

        numero_eliminar = st.text_input("Número (ej: 005)")

        if st.button("Eliminar número"):
            if numero_eliminar in df["numero"].values:
                df = df[df["numero"] != numero_eliminar]
                guardar(df)
                st.success("Número eliminado ✅")
                st.rerun()
            else:
                st.error("Número no existe")

        st.divider()

        # 🧹 RESET
        st.markdown("### 🧹 Reiniciar rifa")

        if st.button("⚠️ BORRAR TODO"):
            df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
            guardar(df)
            st.success("Rifa reiniciada ✅")
            st.rerun()

    elif clave:
        st.error("Contraseña incorrecta ❌")
