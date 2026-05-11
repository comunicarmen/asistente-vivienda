# 🏠 Asistente IA de Orientación de Vivienda — Víctor

Asistente conversacional que orienta al ciudadano sobre ayudas de vivienda en España según su perfil (edad, CCAA, ingresos, objetivo).

**Stack:** Claude Sonnet 4.6 · LangChain · Chroma RAG · Streamlit

---

## Estructura del proyecto

```
asistente-vivienda/
├── .env.example          → Plantilla para tu API Key (cópiala como .env)
├── requirements.txt      → Dependencias Python
├── app/
│   ├── asistente.py      → Interfaz Streamlit (lo que ve el usuario)
│   └── pipeline.py       → Pipeline RAG (Claude + Chroma + LangChain)
├── scripts/
│   └── indexar_normativa.py  → Crea la base vectorial (ejecutar UNA VEZ)
└── docs/
    ├── normativa_estatal.txt → Ayudas estatales (BOE)
    ├── madrid_vivienda.txt   → Ayudas Comunidad de Madrid
    └── andalucia_vivienda.txt → Ayudas Andalucía
```

---

## Instalación paso a paso

### 1. Requisitos previos
- Python 3.10 o superior instalado
- Cuenta en Anthropic (console.anthropic.com) con API Key

### 2. Configurar la API Key
```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Abre .env con el Bloc de notas y sustituye la clave:
# ANTHROPIC_API_KEY=sk-ant-AQUI-TU-API-KEY
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Indexar la normativa (solo una vez)
```bash
python scripts/indexar_normativa.py
```
Este paso lee los documentos de /docs y crea la base vectorial Chroma.

### 5. Arrancar el asistente
```bash
streamlit run app/asistente.py
```
Se abrirá automáticamente en tu navegador en http://localhost:8501

---

## Deploy en Streamlit Cloud (para la demo)

1. Sube esta carpeta a GitHub (sin el archivo .env)
2. Ve a share.streamlit.io → New app
3. Conecta tu repositorio → selecciona `app/asistente.py`
4. En "Secrets" añade: `ANTHROPIC_API_KEY = "tu-api-key"`
5. Pulsa Deploy → URL pública en 2 minutos

---

## Añadir más normativa

Para añadir normativa de más CCAA:
1. Crea un archivo `.txt` en la carpeta `/docs` con el mismo formato
2. Vuelve a ejecutar `python scripts/indexar_normativa.py`

---

## Pipeline interno

```
Usuario escribe en Streamlit
        ↓
LangChain + Claude extrae el perfil (edad, CCAA, ingresos, objetivo)
        ↓
Chroma busca los chunks de normativa más relevantes
        ↓
Claude sintetiza la respuesta anclada en los documentos
        ↓
Streamlit muestra respuesta con fuentes y disclaimer
```

---

## Coste estimado
- Chroma, LangChain, Streamlit: **0 €**
- Claude Sonnet API: ~0,01 € por consulta completa
- Toda la PoC + demo: **2–5 €** (cubierto por créditos gratuitos de Anthropic)

---

*Datos basados en BOE, Real Decreto 42/2022, RD-ley 1/2025 y webs oficiales de CCAA.*
*Siempre verifica condiciones en el organismo competente.*
