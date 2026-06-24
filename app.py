import streamlit as st
import requests
import json
from datetime import datetime

# ================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ================================
st.set_page_config(
    page_title="Predicción de Bajo Peso al Nacer",
    page_icon="👶",
    layout="centered"
)

# ================================
# ESTILOS PERSONALIZADOS
# ================================
st.markdown("""
<style>
    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 18px;
        color: #7F8C8D;
        text-align: center;
        margin-bottom: 30px;
    }
    .result-card {
        background-color: #F8F9F9;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #D5D8DC;
        text-align: center;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# ENCABEZADO
# ================================
st.markdown("<div class='main-title'>Predicción de Bajo Peso al Nacer</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Modelo entrenado con DataRobot – Hospital General de Medellín</div>", unsafe_allow_html=True)

# ================================
# CARGAR VARIABLES SECRETAS
# ================================
DR_API_KEY = st.secrets["DATAROBOT_API_KEY"]
DR_DEPLOYMENT_ID = st.secrets["DATAROBOT_DEPLOYMENT_ID"]
DR_HOST = st.secrets["DATAROBOT_HOST"]

PREDICTION_URL = f"{DR_HOST}/api/v2/deployments/{DR_DEPLOYMENT_ID}/predictions"

# ================================
# SIDEBAR
# ================================
st.sidebar.title("⚙️ Configuración del Modelo")
st.sidebar.info("Este modelo utiliza DataRobot Deployment API para generar predicciones en tiempo real.")

# ================================
# FORMULARIO DE ENTRADA (solo variables importantes)
# ================================
st.header("📝 Ingrese los datos del nacimiento")

col1, col2 = st.columns(2)

with col1:
    edad_madre = st.number_input("Edad de la madre", min_value=12, max_value=55, value=25)
    tiempo_de_gestacion = st.number_input("Semanas de gestación", min_value=20, max_value=42, value=38)
    numero_consultas_prenatales = st.number_input("Consultas prenatales", min_value=0, max_value=20, value=5)
    nivel_educativo_madre = st.selectbox(
        "Nivel educativo de la madre",
        ["Ninguno", "Primaria", "Secundaria", "Universitario"]
    )

with col2:
    sexo = st.selectbox("Sexo del recién nacido", ["MASCULINO", "FEMENINO"])
    tipo_parto = st.selectbox("Tipo de parto", ["Vaginal", "Cesárea"])
    pertenencia_etnica = st.selectbox(
        "Pertenencia étnica",
        ["Ninguna", "Indígena", "Afrodescendiente", "ROM", "Raizal"]
    )
    regimen_seguridad = st.selectbox(
        "Régimen de seguridad",
        ["Subsidiado", "Contributivo", "Especial"]
    )

# ================================
# VALORES POR DEFECTO PARA COLUMNAS OCULTAS
# ================================
default_values = {
    "ano": 2023,
    "apgar1": 8,
    "apgar2": 9,
    "area_residencia": "Urbana",
    "departamento_residencia": "Antioquia",
    "edad_padre": 30,
    "estado_conyugal_madre": "Soltera",
    "factor_rh": "+",
    "fecha_nacimiento": datetime.now().strftime("%Y-%m-%d"),
    "grupo_edad_madre": "20_34",
    "grupo_sanguineo": "O",
    "localidad": "Medellín",
    "multiplicidad_embarazo": "Único",
    "municipio_residencia": "Medellín",
    "nivel_educativo_padre": "Secundaria",
    "nombre_administradora": "SURA",
    "numero_embarazos": 1,
    "numero_hijos_nacidos_vivos": 0,
    "parto_atendido_por": "Médico",
    "periodo_de_reporte": 1,
    "prematuro": 0,
    "talla_centimetros": 50,
    "ultimo_ano_aprobado_madre": "11"
}

# ================================
# BOTÓN DE PREDICCIÓN
# ================================
if st.button("🔍 Calcular riesgo de bajo peso"):

    # Construcción del payload completo
    payload = [
        {
            # Variables ingresadas por el usuario
            "edad_madre": edad_madre,
            "tiempo_de_gestacion": tiempo_de_gestacion,
            "numero_consultas_prenatales": numero_consultas_prenatales,
            "nivel_educativo_madre": nivel_educativo_madre,
            "sexo": sexo,
            "tipo_parto": tipo_parto,
            "pertenencia_etnica": pertenencia_etnica,
            "regimen_seguridad": regimen_seguridad,
            # Variables ocultas con valores por defecto
            **default_values
        }
    ]

    headers = {
        "Authorization": f"Token {DR_API_KEY}",
        "Content-Type": "application/json"
    }

    # Llamada a DataRobot
    response = requests.post(PREDICTION_URL, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        prediction = response.json()
        result = prediction["data"][0]

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.subheader("Resultado de la predicción")

        # ================================
        # MANEJO UNIVERSAL DE MODELOS
        # ================================

        # Caso 1: Clasificación binaria
        if "predictionProbability" in result:
            prob = result["predictionProbability"]
            if prob >= 0.5:
                st.error(f"⚠️ Riesgo ALTO de bajo peso al nacer: **{prob:.2f}**")
            else:
                st.success(f"🟢 Riesgo BAJO de bajo peso al nacer: **{prob:.2f}**")

        # Caso 2: Clasificación multiclase
        elif "classProbabilities" in result:
            st.info(f"Clase predicha: **{result['prediction']}**")
            st.json(result["classProbabilities"])

        # Caso 3: Regresión
        elif "prediction" in result:
            st.success(f"Valor predicho: **{result['prediction']}**")

        # Caso 4: Respuesta inesperada
        else:
            st.error("Formato de respuesta desconocido.")
            st.json(result)

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error("Error al obtener predicción desde DataRobot.")
        st.write(response.text)
