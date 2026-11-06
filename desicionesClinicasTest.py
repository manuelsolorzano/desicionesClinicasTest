import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Importar tu módulo de análisis
from desicionesClinicasTest import ejecutar_analisis

st.set_page_config(
    page_title="Plataforma Clínica",
    layout="wide"
)

ARCHIVO_PACIENTES = "pacientes.csv"

# Crear CSV vacío si no existe
if not os.path.exists(ARCHIVO_PACIENTES):

    df_vacio = pd.DataFrame(columns=[
        "id_paciente",
        "nombre",
        "edad",
        "sexo",
        "diagnosticos",
        "motivo_consulta",
        "fecha_actualizacion",
        "estado_actual"
    ])

    df_vacio.to_csv(ARCHIVO_PACIENTES, index=False)

st.title("🩺 Plataforma de Apoyo a la Decisión Clínica")

tab1, tab2, tab3 = st.tabs([
    "📋 Nuevo Paciente",
    "👥 Pacientes Registrados",
    "🧠 Análisis Clínico"
])

# =====================================================
# TAB 1 NUEVO PACIENTE
# =====================================================

with tab1:

    st.subheader("Registro de Nuevo Paciente")

    id_paciente = st.text_input("ID del Paciente")

    nombre = st.text_input("Nombre")

    edad = st.number_input(
        "Edad",
        min_value=0,
        max_value=120
    )

    sexo = st.selectbox(
        "Sexo",
        [
            "Masculino",
            "Femenino"
        ]
    )

    diagnosticos = st.text_area(
        "Diagnósticos activos"
    )

    motivo = st.text_area(
        "Motivo de consulta"
    )

    estado = st.selectbox(
        "Estado actual",
        [
            "Estable",
            "Hospitalizado",
            "Observación",
            "Crítico",
            "Alta"
        ]
    )

    if st.button("Guardar Paciente"):

        nuevo = pd.DataFrame([{
            "id_paciente": id_paciente,
            "nombre": nombre,
            "edad": edad,
            "sexo": sexo,
            "diagnosticos": diagnosticos,
            "motivo_consulta": motivo,
            "fecha_actualizacion": datetime.now(),
            "estado_actual": estado
        }])

        nuevo.to_csv(
            ARCHIVO_PACIENTES,
            mode="a",
            header=False,
            index=False
        )

        st.success("Paciente guardado correctamente")

# =====================================================
# TAB 2 PACIENTES REGISTRADOS
# =====================================================

with tab2:

    st.subheader("Pacientes Registrados")

    df = pd.read_csv(ARCHIVO_PACIENTES)

    if len(df) > 0:

        st.dataframe(df)

        paciente_seleccionado = st.selectbox(
            "Seleccione un paciente",
            df["nombre"]
        )

        if st.button("Cargar paciente"):

            fila = df[df["nombre"] == paciente_seleccionado].iloc[0]

            st.session_state["paciente_actual"] = {
                "id": fila["id_paciente"],
                "nombre": fila["nombre"],
                "edad": fila["edad"],
                "sexo": fila["sexo"],
                "diagnosticos": fila["diagnosticos"],
                "motivo": fila["motivo_consulta"],
                "estado": fila["estado_actual"]
            }

            st.success(
                f"Paciente {fila['nombre']} cargado"
            )

    else:

        st.warning(
            "Aún no existen pacientes registrados"
        )

# =====================================================
# TAB 3 ANALISIS CLINICO
# =====================================================

with tab3:

    if "paciente_actual" not in st.session_state:

        st.warning(
            "Primero debe seleccionar un paciente en la pestaña Pacientes Registrados"
        )

    else:

        paciente = st.session_state["paciente_actual"]

        st.subheader("Paciente Activo")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Paciente", paciente["nombre"])

        with col2:
            st.metric("Edad", paciente["edad"])

        with col3:
            st.metric("Estado", paciente["estado"])

        st.write("**Diagnósticos:**")
        st.write(paciente["diagnosticos"])

        st.write("**Motivo de consulta:**")
        st.write(paciente["motivo"])

        st.divider()

        ejecutar_analisis(paciente)
