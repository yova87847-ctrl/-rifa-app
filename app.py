with tab2:

    st.subheader("🔒 Panel Administrador")

    clave = st.text_input("Contraseña", type="password")

    if clave == ADMIN_PASSWORD:

        st.success("✅ Acceso concedido")

        # ✅ MOSTRAR TABLA
        st.markdown("### 📋 Todas las reservas")
        st.dataframe(df)

        st.divider()

        # ✅ PENDIENTES
        pendientes = df[df["estado"] == "Pendiente"]

        st.markdown("### 🟡 Reservas pendientes")

        if pendientes.empty:
            st.info("No hay reservas")
        else:
            for i, row in pendientes.iterrows():

                st.markdown(f"**🎟️ Número {row['numero']}**  |  {row['nombre']}")

                col1, col2 = st.columns(2)

                # ✅ APROBAR
                with col1:
                    if st.button(f"✅ Aprobar {row['numero']}", key=f"a{i}"):
                        df.loc[df["numero"] == row["numero"], "estado"] = "Vendido"
                        guardar(df)
                        st.success(f"Número {row['numero']} vendido ✅")
                        st.rerun()

                # ✅ RECHAZAR
                with col2:
                    if st.button(f"❌ Rechazar {row['numero']}", key=f"r{i}"):
                        df = df[df["numero"] != row["numero"]]
                        guardar(df)
                        st.warning(f"Número {row['numero']} eliminado ❌")
                        st.rerun()

        st.divider()

        # ✅ ELIMINAR MANUAL
        st.markdown("### ❌ Eliminar número manual")

        numero_eliminar = st.text_input("Escribe el número (ej: 005)")

        if st.button("Eliminar número"):
            if numero_eliminar in df["numero"].values:
                df = df[df["numero"] != numero_eliminar]
                guardar(df)
                st.success("Número eliminado ✅")
                st.rerun()
            else:
                st.error("Número no existe")

        st.divider()

        # ✅ REINICIAR
        st.markdown("### 🧹 Reiniciar rifa completa")

        if st.button("⚠️ BORRAR TODO"):
            df = pd.DataFrame(columns=["numero","nombre","telefono","estado"])
            guardar(df)
            st.success("Rifa reiniciada ✅")
            st.rerun()

    elif clave:
        st.error("Contraseña incorrecta ❌")
