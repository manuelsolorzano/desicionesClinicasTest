import streamlit as st
import pandas as pd
from streamlit_agraph import agraph, Node, Edge, Config
import graphviz
import math

# Configurar la página para el modo ancho
st.set_page_config(
    layout="wide" # Esta línea establece el modo ancho por defecto
)

#Título 

st.markdown("""
    <style>
    @media (prefers-color-scheme: dark) {
        .titulo-adaptable {
            color: #f1f1f1; /* Texto claro para fondo oscuro */
        }
    }

    @media (prefers-color-scheme: light) {
        .titulo-adaptable {
            color: #2c3e50; /* Texto oscuro para fondo claro */
        }
    }

    .titulo-adaptable {
        font-size: 80px;
        text-align: center;
    }
    </style>

    <h1 class="titulo-adaptable">Análisis Clínico de Decisiones</h1>
""", unsafe_allow_html=True)

# Subtítulo
st.markdown("<h3 style='color: #008080;'>🩺 Indique las opciones a comparar </h3>", unsafe_allow_html=True)
###
# Creamos diccionarios para almacenar las respuestas
analisis={"analisis":{}}
#
# Pregunta 1
num_opciones = st.number_input("¿Cuántas opciones desea comparar?", min_value=1, step=1)
analisis["analisis"]["num_opciones"] = num_opciones
analisis["analisis"].update({"opcion":{}}) # crear un subdiccionario para los casos
st.markdown("Introduzca el planteamiento del problema. Por ejemplo: Tratamiento, Diagnóstico, Cirugía, etc.")
#################
for i in range(int(analisis["analisis"]["num_opciones"])):
    opcion = st.text_input(f"Opción comparativa {i+1}", key=f"opcion_{i}",value=f"Opción {i+1}")
    analisis["analisis"]["opcion"].update({str(opcion):{}}) 

st.divider()
    
# Input info 1: nombres de dilemas
st.markdown("<h3 style='color: #008080;'>⚖️ Indique los dilemas correspondientes a cada opción </h3>", unsafe_allow_html=True)
#

# Pregunta 2
#
for i in range(int(analisis["analisis"]["num_opciones"])):
    num_dilema = st.number_input(f"¿Cuántos dilemas desea considerar para '{list(analisis["analisis"]["opcion"].keys())[i]}'?",key=f"num_dilema_{i}", min_value=1, step=1)
    analisis["analisis"]["opcion"][str(list(analisis["analisis"]["opcion"].keys())[i])].update({"num_dilema":num_dilema})
    analisis["analisis"]["opcion"][str(list(analisis["analisis"]["opcion"].keys())[i])].update({'dilema':{}})

for j in range(int(analisis["analisis"]["num_opciones"])):
    opcion_key = list(analisis["analisis"]["opcion"].keys())[j]
    
    st.markdown(f"<h5 style='color: #339999;'>🔹 Dilemas para la opción: <em>{opcion_key}</em></h5>", unsafe_allow_html=True)
    
    num_dilemas = analisis["analisis"]["opcion"][opcion_key]["num_dilema"]
    
    for i in range(int(num_dilemas)):
        dilema = st.text_input(
            f"Dilema {i+1}",
            key=f"dilema_{j}_{i}",
            value=f"Dilema {i+1}"
        )
        analisis["analisis"]["opcion"][opcion_key]["dilema"].update({str(dilema): {}})

    st.markdown(f"<h6 style='color: #D4AF37;'>🔸 Complicaciones a considerar para cada dilema </h6>", unsafe_allow_html=True)

    for k in range(int(num_dilemas)):
        dilema_key = list(analisis["analisis"]["opcion"][opcion_key]["dilema"].keys())[k]
        num_complicaciones = st.number_input(f"¿Cuántas complicaciones podrían suceder para el dilema {k+1}?", min_value=1, step=1, key=f"num_complicaciones_{j}_{k}")    
        for l in range(num_complicaciones):
            col1, col2 = st.columns(2)
            with col1:
                #for nombre_dilema in dilemas:
                complicacion = st.text_input(f"Complicación {l+1}", key=f"comp_{j}_{k}_{l}", value=f"Complicación {l+1}")
                analisis["analisis"]["opcion"][opcion_key]["dilema"][dilema_key].setdefault("complicacion", {})
                analisis["analisis"]["opcion"][opcion_key]["dilema"][dilema_key]["complicacion"].update({str(complicacion): {}})
            with col2:
                complicacion_key = list(analisis["analisis"]["opcion"][opcion_key]["dilema"][dilema_key]["complicacion"].keys())[l]
                probabilidad_c = st.slider(f"Probabilidad de que ocurra (%)", min_value=0, max_value=100, step=1, key=f"prob_{j}_{k}_{l}")
                analisis["analisis"]["opcion"][opcion_key]["dilema"][dilema_key]["complicacion"][complicacion_key].setdefault("probabilidad_complicacion", {})
                analisis["analisis"]["opcion"][opcion_key]["dilema"][dilema_key]["complicacion"][complicacion_key]["probabilidad_complicacion"] = str(probabilidad_c)

#Ver el json
#st.json(analisis)

st.divider() 

# Input info 2: pesos de consecuencias
st.markdown("<h3 style='color: #008080;'>🪙 Introduzca los pesos para las consecuencias </h3>", unsafe_allow_html=True)

consecuencias_fijas = ["Muerte", "Mejoría Total", "Mejoría Parcial", "Discapacidad", "Insatisfacción"]
pesos = {}
for cons in consecuencias_fijas:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write(cons)
    with col2:
        peso = st.number_input(f"Peso", min_value=0.0, max_value=1.0, key=f"peso_{cons}")
        pesos[cons] = peso

analisis["analisis"]["pesos"] = pesos

st.divider()

# Input info 3–N: Probabilidades por dilema y consecuencia

st.markdown("<h3 style='color: #008080;'>🎲 Introduzca las probabilidades por cada opción, dilema y consecuencia </h3>", unsafe_allow_html=True)

consecuencias_fijas = ["Muerte", "Mejoría Total", "Mejoría Parcial", "Discapacidad", "Insatisfacción"]

for j in range(int(analisis["analisis"]["num_opciones"])):
    opcion_key = list(analisis["analisis"]["opcion"].keys())[j]
    st.markdown(f"<h4 style='color: #339999;'>🔹 Opción: <em>{opcion_key}</em></h4>", unsafe_allow_html=True)

    dilemas = list(analisis["analisis"]["opcion"][opcion_key]["dilema"].keys())

    for i, dilema in enumerate(dilemas):
        st.markdown(f"**Dilema {i+1}: {dilema}**")
        consecuencias_prob = {}

        total = 0.0  # para verificar la suma

        for cons in consecuencias_fijas:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.write(cons)
            with col2:
                prob = st.number_input(
                    f"Probabilidad de '{cons}'",
                    min_value=0,
                    max_value=100,
                    step=1,
                    key=f"prob_{j}_{i}_{cons}"
                )
                consecuencias_prob[cons] = prob
                total += prob

        # Validar suma
        if total > 100:
            st.warning(f"La suma de probabilidades para el dilema '{dilema}' en la opción '{opcion_key}' es mayor a 1")

        # Guardar en el diccionario
        analisis["analisis"]["opcion"][opcion_key]["dilema"][dilema]["probabilidades"] = consecuencias_prob

# Calcular utilidades

st.divider()

# Mostrar encabezado

st.markdown("""
<div style='text-align: center;'>
  <h2 style='color: #8B7E5D;'>Resultados</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("En esta sección podrá visualizar los resultados de las utilidades por dilema y consecuencia mediante una tabla y con un árbol de decisiones. " \
"En la tabla, las utilidades están ordenadas de mayor a menor por lo que la primera fila resaltada en color rojo indica la mayor utilidad. ")

# Consecuencias fijas (deben ser las mismas que usaste antes)
consecuencias_fijas = ["Muerte", "Mejoría Total", "Mejoría Parcial", "Discapacidad", "Insatisfacción"]

# Acceder a pesos
pesos = analisis["analisis"]["pesos"]

# Preparar lista para crear el DataFrame resumen
tabla_utilidades = []

# Calcular utilidades y guardarlas en cada dilema
for opcion_key, opcion_data in analisis["analisis"]["opcion"].items():
    for dilema_key, dilema_data in opcion_data["dilema"].items():
        utilidades_dilema = {}

        for cons in consecuencias_fijas:
            prob = dilema_data["probabilidades"].get(cons, 0.0)
            peso = pesos.get(cons, 0.0)
            utilidad = peso * (prob/100)

            # Guardar la utilidad dentro del dilema
            utilidades_dilema[cons] = round(utilidad, 4)

            # Agregar a tabla para el DataFrame
            tabla_utilidades.append({
                "Opción": opcion_key,
                "Dilema": dilema_key,
                "Consecuencia": cons,
                "Probabilidad (%)": round(prob, 4),
                "Peso": round(peso, 4),
                "Utilidad": round(utilidad, 4)
            })

        # Guardar utilidades por dilema
        analisis["analisis"]["opcion"][opcion_key]["dilema"][dilema_key]["utilidades"] = utilidades_dilema

# Crear DataFrame
df_utilidades = pd.DataFrame(tabla_utilidades)
df_utilidades = df_utilidades.sort_values(by='Utilidad', ascending=False) #Ordenar de mayor a menor

# Guardar en la estructura principal
analisis["analisis"]["tabla_utilidades"] = tabla_utilidades

# Encontrar el índice de la fila con el valor máximo
max_idx = df_utilidades["Utilidad"].idxmax()

# Convertir el DataFrame a HTML con estilo en la fila
def df_to_html(df, max_idx):
    html = "<table style='border-collapse: collapse; width: 100%;'>"
    html += "<tr>" + "".join([f"<th style='background-color: #20B2AA; border: 1px solid #008080; padding: 6px; text-align: center;'>{col}</th>" for col in df.columns]) + "</tr>"
    for i, row in df.iterrows():
        style = "background-color: #FF9999;" if i == max_idx else ""
        html += f"<tr style='{style}'>" + "".join([f"<td style='border: 1px solid #008080; padding: 6px;text-align: center;'>{val}</td>" for val in row]) + "</tr>"
    html += "</table>"
    return html

# Mostrar tabla
st.markdown("<h3 style='color: #008080;'>📋 Tabla de utilidades </h3>", unsafe_allow_html=True)
st.markdown(df_to_html(df_utilidades, max_idx), unsafe_allow_html=True)

# Mostrar resumen en una tabla de las complicaciones de cada dilema 
st.markdown("<h5 style='color: #D4AF37;'> Resumen de las posibles complicaciones </h5>", unsafe_allow_html=True)

filas = []
for opcion_key, opcion_val in analisis["analisis"]["opcion"].items():
    for dilema_key, dilema_val in opcion_val["dilema"].items():
        for complicacion_key, complicacion_val in dilema_val.get("complicacion", {}).items():
            probabilidad = complicacion_val.get("probabilidad_complicacion", "")
            filas.append({
                "Opción": opcion_key,
                "Dilema": dilema_key,
                "Complicación": complicacion_key,
                "Probabilidad (%)": str(probabilidad)  # ← esto mantiene "22" como valor único
            })

df_complicaciones = pd.DataFrame(filas)
max_idx_complicaciones = df_complicaciones["Probabilidad (%)"].idxmax()

# Convertir el DataFrame a HTML con estilo en la fila
def df_complicaciones_to_html(df_complicaciones, max_idx_complicaciones):
    html = "<table style='border-collapse: collapse; width: 100%;'>"
    html += "<tr>" + "".join([f"<th style='background-color: #E8C76F; border: 1px solid #D4AF37; padding: 6px; text-align: center;'>{col}</th>" for col in df_complicaciones.columns]) + "</tr>"
    for i, row in df_complicaciones.iterrows():
        style = "background-color: #FF9999;" if i == max_idx else ""
        html += f"<tr style='{style}'>" + "".join([f"<td style='border: 1px solid #D4AF37; padding: 6px;text-align: center;'>{val}</td>" for val in row]) + "</tr>"
    html += "</table>"
    return html
    
st.markdown(df_complicaciones_to_html(df_complicaciones, max_idx), unsafe_allow_html=True)    

# (Opcional) Graficar árbol
st.markdown("<h3 style='color: #008080;'>🌳 Árbol de decisiones por opción </h3>", unsafe_allow_html=True)

opciones = list(analisis["analisis"]["opcion"].keys())
num_opciones = len(opciones)
num_filas = math.ceil(num_opciones / 2)

for fila in range(num_filas):
    cols = st.columns(2)
    for col_idx in range(2):
        idx = fila * 2 + col_idx
        if idx < num_opciones:
            opcion_key = opciones[idx]
            opcion_data = analisis["analisis"]["opcion"][opcion_key]

            # Crear el árbol con Graphviz
            dot = graphviz.Digraph(comment=f"Árbol de decisión - {opcion_key}")
            dot.attr(rankdir='LR')

            # Nodo raíz
            dot.node(opcion_key, shape='box', style='filled', fillcolor='#CCFFFF')

            dilemas = opcion_data["dilema"]

            for dilema_key, dilema_data in dilemas.items():
                dilema_node = f"{opcion_key}_{dilema_key}"
                dot.node(dilema_node, dilema_key, shape='ellipse', style='filled', fillcolor='#E0FFFF')
                dot.edge(opcion_key, dilema_node)

                utilidades = dilema_data.get("utilidades", {})
                max_utilidad = max(utilidades.values()) if utilidades else None

                for cons, utilidad in utilidades.items():
                    hoja_node = f"{dilema_node}_{cons}"
                    label = f"{cons}\nU={round(utilidad, 4)}"
                    fillcolor = '#FF9999' if utilidad == max_utilidad else '#F0FFF0'
                    dot.node(hoja_node, label, shape='note', style='filled', fillcolor=fillcolor)
                    dot.edge(dilema_node, hoja_node)

            # Mostrar árbol en columna correspondiente
            with cols[col_idx]:
                st.markdown(f"##### Árbol para opción: {opcion_key}")
                st.graphviz_chart(dot)

# Mostrar resumen en una tabla de las complicaciones de cada dilema 
st.markdown("<h5 style='color: #D4AF37;'> Resumen de las posibles complicaciones </h5>", unsafe_allow_html=True)

filas = []
for opcion_key, opcion_val in analisis["analisis"]["opcion"].items():
    for dilema_key, dilema_val in opcion_val["dilema"].items():
        for complicacion_key, complicacion_val in dilema_val.get("complicacion", {}).items():
            probabilidad = complicacion_val.get("probabilidad_complicacion", "")
            filas.append({
                "Opción": opcion_key,
                "Dilema": dilema_key,
                "Complicación": complicacion_key,
                "Probabilidad (%)": str(probabilidad)  # ← esto mantiene "22" como valor único
            })

df_complicaciones = pd.DataFrame(filas)
max_idx_complicaciones = df_complicaciones["Probabilidad (%)"].idxmax()

# Convertir el DataFrame a HTML con estilo en la fila
def df_complicaciones_to_html(df_complicaciones, max_idx_complicaciones):
    html = "<table style='border-collapse: collapse; width: 100%;'>"
    html += "<tr>" + "".join([f"<th style='background-color: #E8C76F; border: 1px solid #D4AF37; padding: 6px; text-align: center;'>{col}</th>" for col in df_complicaciones.columns]) + "</tr>"
    for i, row in df_complicaciones.iterrows():
        style = "background-color: #FF9999;" if i == max_idx else ""
        html += f"<tr style='{style}'>" + "".join([f"<td style='border: 1px solid #D4AF37; padding: 6px;text-align: center;'>{val}</td>" for val in row]) + "</tr>"
    html += "</table>"
    return html
st.markdown(df_complicaciones_to_html(df_complicaciones, max_idx), unsafe_allow_html=True) 
