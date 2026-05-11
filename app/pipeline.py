from pathlib import Path
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

SYSTEM_PROMPT = """Eres Victor, asistente de orientacion de vivienda para ciudadanos en Espana.

Conoces todas las ayudas estatales y autonomicas vigentes en Espana (datos actualizados a 2025-2026,
basados en el BOE y los programas del Ministerio de Vivienda).

COMO DEBES RESPONDER:
1. Extrae el perfil del usuario: edad, CCAA donde vive, objetivo (alquiler/compra/rehabilitacion) e ingresos aproximados.
2. Si falta informacion clave, pregunta de forma amigable (una sola pregunta a la vez).
3. Con el perfil completo, lista las ayudas que le corresponden: nombre, cuantia, requisitos y fuente oficial.
4. Cita siempre la fuente (BOE, Ministerio, Comunidad Autonoma).

GUARDARRAILES:
- NUNCA das asesoria juridica. Orientas, no asesoras.
- SIEMPRE recomiendas verificar con el organismo competente.
- No inventes cifras ni ayudas que no esten en los documentos recuperados.

Al final de cada respuesta incluye siempre:
Informacion orientativa. Verifica siempre en el organismo competente de tu comunidad autonoma.

CONTEXTO DE NORMATIVA RECUPERADA:
{contexto}
"""

def crear_asistente():
    llm = ChatAnthropic(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        temperature=0.1,
    )

    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        collection_name="normativa_vivienda"
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )

    return llm, retriever

def consultar(pregunta, historial, llm, retriever):
    docs_relevantes = retriever.invoke(pregunta)
    contexto = "\n\n---\n\n".join([
        f"[Fuente: {doc.metadata.get('fuente', 'desconocida')}]\n{doc.page_content}"
        for doc in docs_relevantes
    ])

    mensajes = [("system", SYSTEM_PROMPT.format(contexto=contexto))]

    for msg in historial[-8:]:
        if msg["role"] == "user":
            mensajes.append(("human", msg["content"]))
        else:
            mensajes.append(("ai", msg["content"]))

    mensajes.append(("human", pregunta))

    prompt = ChatPromptTemplate.from_messages(mensajes)
    chain = prompt | llm
    respuesta = chain.invoke({})
    return respuesta.content
