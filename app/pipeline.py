from pathlib import Path
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
load_dotenv()

FAISS_DIR = Path(__file__).parent.parent / "faiss_db"
DOCS_DIR = Path(__file__).parent.parent / "docs"

URLS_OFICIALES = {
    "andalucia_vivienda":  "https://www.juntadeandalucia.es/fomentoinfraestructurasyordenaciondelterritorio/vivienda",
    "madrid_vivienda":     "https://www.comunidad.madrid/servicios/vivienda",
    "normativa_estatal":   "https://www.mivau.gob.es/vivienda/ayudas-y-financiacion",
    "cataluna_vivienda":   "https://habitatge.gencat.cat/ca/inici",
    "pais_vasco_vivienda": "https://www.etxebide.euskadi.eus",
    "valencia_vivienda":   "https://habitatge.gva.es/es",
}

def obtener_url(nombre_archivo):
    nombre = nombre_archivo.lower()
    for clave, url in URLS_OFICIALES.items():
        if clave in nombre:
            return url
    return "https://www.mivau.gob.es/vivienda/ayudas-y-financiacion"

SYSTEM_PROMPT = """Eres Victor, asistente de orientacion de vivienda para ciudadanos en Espana.
Conoces todas las ayudas estatales y autonomicas vigentes en Espana (datos actualizados a 2025-2026,
basados en el BOE y los programas del Ministerio de Vivienda).

COMO DEBES RESPONDER:
1. Extrae el perfil del usuario: edad, CCAA donde vive, objetivo (alquiler/compra/rehabilitacion) e ingresos aproximados.
2. Si falta informacion clave, pregunta de forma amigable (una sola pregunta a la vez).
3. Con el perfil completo, lista las ayudas que le corresponden: nombre, cuantia, requisitos y fuente oficial.
4. Para cada ayuda incluye un link clicable: [Ver informacion oficial](URL)

GUARDARRAILES:
- NUNCA das asesoria juridica. Orientas, no asesoras.
- SIEMPRE recomiendas verificar con el organismo competente.
- No inventes cifras ni ayudas que no esten en los documentos recuperados.
- No inventes URLs. Usa solo las que aparecen en el contexto recuperado.

Al final de cada respuesta incluye siempre:
⚠️ *Informacion orientativa. Verifica siempre en el organismo competente de tu comunidad autonoma.*

CONTEXTO DE NORMATIVA RECUPERADA:
{contexto}
"""

def construir_base():
    import glob
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    archivos = glob.glob(str(DOCS_DIR / "*.txt"))
    documentos = []
    for archivo in archivos:
        nombre = Path(archivo).name
        url = obtener_url(nombre)
        with open(archivo, encoding="utf-8") as f:
            texto = f.read()
        start = 0
        while start < len(texto):
            end = start + 800
            chunk = texto[start:end]
            documentos.append(Document(
                page_content=chunk,
                metadata={"fuente": nombre, "url": url}
            ))
            start = end - 100
    vectorstore = FAISS.from_documents(documentos, embeddings)
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(FAISS_DIR))
    return vectorstore

def crear_asistente():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
    llm = ChatAnthropic(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        temperature=0.1,
    )
    if not FAISS_DIR.exists():
        vectorstore = construir_base()
    else:
        vectorstore = FAISS.load_local(
            str(FAISS_DIR),
            embeddings,
            allow_dangerous_deserialization=True
        )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
    return llm, retriever

def consultar(pregunta, historial, llm, retriever):
    docs_relevantes = retriever.invoke(pregunta)
    contexto = "\n\n---\n\n".join([
        f"[Fuente: {doc.metadata.get('fuente', 'desconocida')} | URL: {doc.metadata.get('url', '')}]\n{doc.page_content}"
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