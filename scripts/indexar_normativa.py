import glob
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma

load_dotenv()

DOCS_DIR = Path(__file__).parent.parent / "docs"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

def cargar_texto(archivo):
    with open(archivo, encoding="utf-8") as f:
        return f.read()

def trocear(texto, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(texto):
        end = start + chunk_size
        chunks.append(texto[start:end])
        start = end - overlap
    return chunks

def indexar():
    print("Leyendo documentos de normativa...")
    archivos = glob.glob(str(DOCS_DIR / "*.txt"))

    if not archivos:
        print(f"No se encontraron archivos .txt en {DOCS_DIR}")
        return

    from langchain_core.documents import Document

    documentos = []
    for archivo in archivos:
        nombre = Path(archivo).name
        print(f"  Cargando: {nombre}")
        texto = cargar_texto(archivo)
        chunks = trocear(texto)
        for chunk in chunks:
            documentos.append(Document(
                page_content=chunk,
                metadata={"fuente": nombre}
            ))

    print(f"\n{len(documentos)} chunks generados")
    print("Guardando en Chroma (embeddings por defecto)...")

    vectorstore = Chroma.from_documents(
        documents=documentos,
        persist_directory=str(CHROMA_DIR),
        collection_name="normativa_vivienda"
    )

    print(f"\nBase vectorial creada en: {CHROMA_DIR}")
    print(f"   {len(documentos)} chunks indexados y listos")

if __name__ == "__main__":
    indexar()
