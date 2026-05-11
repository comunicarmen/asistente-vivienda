"""
FASE 4: Interfaz Streamlit — Lo que ve el usuario (y el tribunal)
=================================================================
Chat conversacional con banner IA, disclaimer, fuentes citadas
y fecha de corte visible.

Uso:
    streamlit run app/asistente.py
"""

import streamlit as st
import sys
from pathlib import Path

# Añadir el directorio raíz al path para importar pipeline
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.pipeline import crear_asistente, consultar

# ─── Configuración de página ───────────────────────────────────────────────
st.set_page_config(
    page_title="Asistente IA de Vivienda — Víctor",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── CSS personalizado para acercar el diseño al visual objetivo ───────────
st.markdown("""
<style>
    /* Fondo general */
    .stApp { background-color: #f8f9fa; }
    
    /* Header principal */
    .header-banner {
        background: linear-gradient(135deg, #1a2a4a 0%, #2a3a6a 100%);
        color: white;
        padding: 2rem 1.5rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    .header-banner h1 { color: white; font-size: 1.6rem; margin: 0 0 0.3rem; }
    .header-banner p { color: #aab8cc; font-size: 0.9rem; margin: 0; }
    .header-banner .badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        color: #fff;
        font-size: 0.7rem;
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 0.8rem;
    }
    
    /* Mensajes del chat */
    .stChatMessage { border-radius: 10px; margin-bottom: 0.5rem; }
    
    /* Disclaimer */
    .disclaimer {
        background: #fff8e1;
        border-left: 4px solid #f0a500;
        padding: 0.6rem 1rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.8rem;
        color: #7a5c00;
        margin-top: 1rem;
    }
    
    /* Botones de acceso rápido */
    .stButton > button {
        background: white;
        border: 1.5px solid #1a2a4a;
        color: #1a2a4a;
        border-radius: 20px;
        font-size: 0.8rem;
        padding: 0.3rem 0.8rem;
    }
    .stButton > button:hover {
        background: #1a2a4a;
        color: white;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        font-size: 0.72rem;
        color: #999;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
    }
    
    /* Ocultar elementos de Streamlit */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <div class="badge">🤖 IA basada en datos reales del BOE · 18 ayudas vigentes</div>
    <h1>🏠 Asistente IA de Vivienda</h1>
    <p>Cuéntame tu situación y te diré exactamente qué ayudas tienes y cómo pedirlas</p>
</div>
""", unsafe_allow_html=True)

# ─── Inicializar sesión ─────────────────────────────────────────────────────
if "historial" not in st.session_state:
    st.session_state.historial = []
    # Mensaje de bienvenida de Víctor
    st.session_state.historial.append({
        "role": "assistant",
        "content": (
            "¡Hola! Soy Víctor, tu asistente de vivienda 🏠\n\n"
            "Conozco todas las ayudas estatales y autonómicas vigentes en España "
            "(datos actualizados a 2025-2026, basados en el BOE y los programas "
            "del Ministerio de Vivienda).\n\n"
            "Cuéntame tu situación: ¿buscas piso de alquiler, quieres comprar "
            "tu primera vivienda, o necesitas ayuda para rehabilitar tu casa?"
        )
    })

if "asistente_listo" not in st.session_state:
    with st.spinner("Cargando base de normativa..."):
        try:
            st.session_state.llm, st.session_state.retriever = crear_asistente()
            st.session_state.asistente_listo = True
        except Exception as e:
            st.error(f"Error al inicializar el asistente: {e}")
            st.info("Asegúrate de haber ejecutado primero: `python scripts/indexar_normativa.py`")
            st.stop()

# ─── Botones de acceso rápido ───────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
acceso_rapido = None
with col1:
    if st.button("🏘️ Busco alquiler asequible"):
        acceso_rapido = "Busco alquiler asequible"
with col2:
    if st.button("🔑 Quiero comprar mi primera vivienda"):
        acceso_rapido = "Quiero comprar mi primera vivienda"
with col3:
    if st.button("🔧 Necesito reformar mi piso"):
        acceso_rapido = "Necesito reformar mi piso"
with col4:
    if st.button("🧭 Soy joven y no sé por dónde empezar"):
        acceso_rapido = "Soy joven y no sé por dónde empezar"

# ─── Mostrar historial de chat ──────────────────────────────────────────────
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["role"], avatar="🏠" if mensaje["role"] == "assistant" else "👤"):
        st.markdown(mensaje["content"])

# ─── Input del usuario ──────────────────────────────────────────────────────
pregunta = st.chat_input("Escribe tu consulta... (ej: Tengo 28 años, vivo en Madrid, ingresos 19.000€, quiero alquilar)")

# Procesar acceso rápido o input directo
entrada = acceso_rapido or pregunta

if entrada:
    # Mostrar mensaje del usuario
    st.session_state.historial.append({"role": "user", "content": entrada})
    with st.chat_message("user", avatar="👤"):
        st.markdown(entrada)

    # Generar respuesta
    with st.chat_message("assistant", avatar="🏠"):
        with st.spinner("Víctor está buscando las mejores ayudas para ti..."):
            try:
                respuesta = consultar(
                    pregunta=entrada,
                    historial=st.session_state.historial[:-1],
                    llm=st.session_state.llm,
                    retriever=st.session_state.retriever
                )
                st.markdown(respuesta)
                st.session_state.historial.append({"role": "assistant", "content": respuesta})
            except Exception as e:
                error_msg = f"❌ Error al consultar: {e}"
                st.error(error_msg)

    st.rerun()

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Datos basados en BOE, Real Decreto 42/2022, RD-ley 1/2025 y webs oficiales de CCAA · 
    Actualizado abril 2026 · 
    <strong>Siempre verifica condiciones en el organismo competente</strong>
</div>
""", unsafe_allow_html=True)
