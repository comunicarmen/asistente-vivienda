import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app.pipeline import crear_asistente, consultar

st.title("Asistente de Vivienda - Victor")

if "historial" not in st.session_state:
    st.session_state.historial = []
    st.session_state.historial.append({
        "role": "assistant",
        "content": "Hola! Soy Victor, tu asistente de vivienda. Cuentame tu situacion: edad, comunidad autonoma, si quieres alquilar o comprar, e ingresos aproximados."
    })

if "listo" not in st.session_state:
    with st.spinner("Cargando..."):
        st.session_state.llm, st.session_state.retriever = crear_asistente()
        st.session_state.listo = True

for msg in st.session_state.historial:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

pregunta = st.chat_input("Escribe tu consulta aqui...")

if pregunta:
    st.session_state.historial.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.write(pregunta)
    with st.chat_message("assistant"):
        with st.spinner("Buscando ayudas..."):
            respuesta = consultar(
                pregunta=pregunta,
                historial=st.session_state.historial[:-1],
                llm=st.session_state.llm,
                retriever=st.session_state.retriever
            )
            st.write(respuesta)
    st.session_state.historial.append({"role": "assistant", "content": respuesta})
    st.rerun()
