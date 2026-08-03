import sys
import os
import pandas as pd
import streamlit as st

# Añadir la raíz del proyecto al sys.path para poder importar módulos propios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.models import DatabaseManager
from core.cv_parser import CVParser
from core.matcher import JobMatcher
from core.ai_analyzer import AIJobAnalyzer

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Job Hunter AI | Dashboard",
    page_icon="💼",
    layout="wide"
)

st.title("💼 Job Hunter AI - Panel de Control")
st.caption("Sistema inteligente de búsqueda, análisis y priorización de vacantes de QA & Automation.")


# Inicializar Base de Datos, Matcher y AI Analyzer
@st.cache_resource
def get_db():
    return DatabaseManager(db_path="jobs.db")


db = get_db()


@st.cache_resource
def get_ai_analyzer():
    return AIJobAnalyzer()


ai_analyzer = get_ai_analyzer()

# Cargar CV si existe
user_skills = ["python", "selenium", "pytest", "sql", "git", "postman", "jira"]
cv_file = "tu_cv.pdf"
if os.path.exists(cv_file):
    parser = CVParser(cv_path=cv_file)
    user_skills = parser.parse()["skills"]

matcher = JobMatcher(user_skills=user_skills)

# Cargar vacantes desde SQLite
jobs = db.get_all_jobs()

if not jobs:
    st.warning(
        "⚠️ No hay vacantes registradas en la base de datos. Ejecuta `python main.py` primero para extraer ofertas.")
    st.stop()

# Convertir a DataFrame de Pandas
data = [j.to_dict() for j in jobs]
df = pd.DataFrame(data)

# Sidebar: Filtros
st.sidebar.header("🔍 Filtros de Búsqueda")

search_term = st.sidebar.text_input("Buscar por puesto o empresa", "")
min_compat = st.sidebar.slider("Mínimo % de Compatibilidad", 0, 100, 40)

fuentes = ["Todas"] + list(df["fuente"].unique())
selected_fuente = st.sidebar.selectbox("Fuente de empleo", fuentes)

estados = ["Todos"] + list(df["estado"].unique())
selected_estado = st.sidebar.selectbox("Estado de postulación", estados)

# Aplicar Filtros
filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[
        filtered_df["puesto"].str.contains(search_term, case=False, na=False) |
        filtered_df["empresa"].str.contains(search_term, case=False, na=False)
        ]

filtered_df = filtered_df[filtered_df["compatibilidad"] >= min_compat]

if selected_fuente != "Todas":
    filtered_df = filtered_df[filtered_df["fuente"] == selected_fuente]

if selected_estado != "Todos":
    filtered_df = filtered_df[filtered_df["estado"] == selected_estado]

# Ordenar por compatibilidad descendente
filtered_df = filtered_df.sort_values(by="compatibilidad", ascending=False)

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Vacantes Registradas", len(df))
col2.metric("Vacantes Filtradas", len(filtered_df))
col3.metric("Promedio Compatibilidad",
            f"{round(filtered_df['compatibilidad'].mean(), 1) if not filtered_df.empty else 0}%")
col4.metric("Alta Coincidencia (>80%)", len(df[df['compatibilidad'] >= 80]))

st.divider()

# Layout Principal: Listado y Detalle
st.subheader("📋 Vacantes Encontradas")

for idx, row in filtered_df.iterrows():
    match_info = matcher.match(row["puesto"], row["descripcion"])

    # Renderizado en tarjeta expandible
    with st.expander(f"**[{row['compatibilidad']}%] {row['empresa']} — {row['puesto']}** ({row['modalidad']})"):
        c1, c2 = st.columns([3, 1])

        with c1:
            st.markdown(
                f"**Fuente:** `{row['fuente']}` | **Ubicación:** `{row['ubicacion']}` | **Salario:** `{row['salario']}`")
            st.markdown(f"**Coincidencias ({len(match_info['matches'])}):** " + ", ".join(
                [f"`{m}`" for m in match_info['matches']]))
            if match_info['missing']:
                st.markdown(f"**Faltantes ({len(match_info['missing'])}):** " + ", ".join(
                    [f"`{m}`" for m in match_info['missing']]))

            st.text_area("Descripción de la vacante", row["descripcion"], height=150, key=f"desc_{row['id']}")
            st.markdown(f"[🔗 Abrir oferta de empleo original]({row['url']})")

            st.divider()

            # Pestañas de Integración con IA
            tab1, tab2 = st.tabs(["📄 Análisis de IA", "✍️ Carta de Presentación"])

            with tab1:
                if st.button("Analizar con IA 🤖", key=f"ai_btn_{row['id']}"):
                    with st.spinner("Analizando vacante con IA..."):
                        analysis = ai_analyzer.analyze_job(row['puesto'], row['empresa'], row['descripcion'],
                                                           user_skills)
                        st.success("Análisis generado:")
                        st.write("**Resumen:**", analysis.get("resumen"))
                        st.write("**Por qué encajas:**", analysis.get("por_que_encajas"))
                        st.write("**Requisitos clave:**")
                        for req in analysis.get("requisitos_clave", []):
                            st.write(f"- {req}")

            with tab2:
                if st.button("Generar Carta de Presentación ✍️", key=f"cl_btn_{row['id']}"):
                    with st.spinner("Redactando propuesta personalizada..."):
                        letter = ai_analyzer.generate_cover_letter_draft(row['puesto'], row['empresa'],
                                                                         row['descripcion'], user_skills)
                        st.text_area("Borrador listo para copiar:", letter, height=180, key=f"cl_txt_{row['id']}")

        with c2:
            st.write("**Estado actual:**", row["estado"])

            # Cambiar estado desde la UI
            nuevo_estado = st.selectbox(
                "Cambiar estado:",
                ["Pendiente", "Aplicada", "Descartada"],
                index=["Pendiente", "Aplicada", "Descartada"].index(row["estado"]),
                key=f"status_{row['id']}"
            )

            if st.button("Guardar Estado", key=f"btn_{row['id']}"):
                db.update_job_compatibility(row["id"], row["compatibilidad"], status=nuevo_estado)
                st.success("¡Estado actualizado!")
                st.rerun()