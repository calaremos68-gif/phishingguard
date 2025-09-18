import streamlit as st
import re
from textblob import TextBlob
import spacy
import subprocess
import sys
from transformers import pipeline

# --- DESCARGA AUTOMÁTICA DEL MODELO DE SPACY ---
@st.cache_resource
def load_spacy_model():
    try:
        nlp = spacy.load("es_core_news_sm")
        return nlp
    except OSError:
        st.info("📥 Descargando modelo de español 'es_core_news_sm'... Esto puede tomar 1-2 minutos.")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
        nlp = spacy.load("es_core_news_sm")
        st.success("✅ Modelo de español descargado correctamente.")
        return nlp

nlp = load_spacy_model()

# Cargar detector de IA (modelo genérico de Hugging Face)
@st.cache_resource
def load_detector():
    return pipeline("text-classification", model="openai-community/gpt2", truncation=True, max_length=512)

detector_ia = load_detector()

# Función de análisis
def analizar_texto(texto):
    if not texto.strip():
        return {"error": "Por favor ingresa un texto."}

    resultados = {}
    alertas = []

    # 1. URLs sospechosas
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', texto)
    resultados['urls'] = urls
    for url in urls:
        dominio = url.split("//")[-1].split("/")[0]
        if any(ext in dominio.lower() for ext in ["login", "verify", "secure", "update", "account", "bank", "paypal"]) and \
           not any(valid in dominio.lower() for valid in ["google.com", "facebook.com", "amazon.com", "youtube.com", "instagram.com"]):
            alertas.append(f"🚨 URL sospechosa: {url}")

    # 2. Sentimiento (TextBlob)
    blob = TextBlob(texto)
    polaridad = blob.sentiment.polarity
    subjetividad = blob.sentiment.subjectivity
    if polaridad > 0.6 or polaridad < -0.3:
        alertas.append(f"⚠️ Tono extremo: {'Muy positivo' if polaridad > 0.6 else 'Muy negativo'} ({polaridad:.2f})")

    # 3. Palabras de urgencia
    urgencias = ["urgente", "inmediato", "ahora", "24h", "cerrar", "bloquear", "verificar", "confirmar", "sin delay", "sin acción"]
    palabras_urgencia = [p for p in urgencias if p in texto.lower()]
    if len(palabras_urgencia) >= 2:
        alertas.append(f"⚠️ Palabras de urgencia: {', '.join(palabras_urgencia)}")

    # 4. Frases demasiado largas/formales
    doc = nlp(texto)
    frases_largas = len([sent for sent in doc.sents if len(sent) > 20])
    if frases_largas > 1:
        alertas.append("⚠️ Demasiadas frases complejas — poco natural para un humano")

    # 5. Detección de IA
    try:
        ia_pred = detector_ia(texto[:512])
        if ia_pred[0]['label'] == 'LABEL_1' and ia_pred[0]['score'] > 0.7:
            alertas.append("🚨 ALTA PROBABILIDAD DE SER GENERADO POR IA (como WormGPT)")
    except Exception as e:
        alertas.append("ℹ️ No se pudo analizar con IA (texto muy largo o error técnico)")

    # Calcular nivel de riesgo
    score = len(alertas)
    if score >= 4:
        nivel = "🔴 ALTO RIESGO — ¡Es probable phishing generado por IA!"
        color = "red"
    elif score >= 2:
        nivel = "🟡 MODERADO RIESGO — Revisa con cuidado"
        color = "orange"
    else:
        nivel = "🟢 BAJO RIESGO — Parece legítimo"
        color = "green"

    return {
        "nivel": nivel,
        "color": color,
        "alertas": alertas,
        "score": score
    }

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="🛡️ PhishingGuard", page_icon="🛡️", layout="centered")

# --- LOGO ---
st.image("https://i.ibb.co/8YqKJQk/phishingguard-logo.png", width=180)  # Logo público desde ImgBB

st.title("🛡️ PhishingGuard — Detecta mensajes de phishing generados por IA")
st.markdown("""
*¿Recibiste un mensaje extraño? Pégalo aquí y te diremos si fue creado por una IA maliciosa como WormGPT.*  
*(No necesitas ser experto — solo pega y presiona "Analizar")*
""")

# Entrada de texto
texto_input = st.text_area(
    "Pega aquí el mensaje que quieres analizar:",
    height=200,
    placeholder="Ejemplo: 'Estimado cliente, su cuenta será bloqueada en 2 horas. Haga clic aquí: https://secure-bank-login.xyz'"
)

# Botón de análisis
if st.button("🔍 Analizar mensaje"):
    if texto_input.strip():
        with st.spinner("Analizando... Esto puede tomar unos segundos"):
            resultado = analizar_texto(texto_input)
        
        if "error" in resultado:
            st.error(resultado["error"])
        else:
            st.markdown(f"### {resultado['nivel']}")
            st.markdown(f"<span style='color:{resultado['color']}; font-weight:bold;'>{resultado['nivel']}</span>", unsafe_allow_html=True)
            
            if resultado["alertas"]:
                st.subheader("📌 Señales detectadas:")
                for alerta in resultado["alertas"]:
                    st.warning(alerta)
            else:
                st.success("✅ No se encontraron señales de riesgo.")
    else:
        st.warning("Por favor ingresa un texto para analizar.")

# Información adicional
st.markdown("---")
st.markdown("""
### ℹ️ ¿Qué es esto?
PhishingGuard es una herramienta educativa creada para ayudarte a identificar mensajes falsos generados por inteligencia artificial maliciosa (como **WormGPT**).  
**No es 100% perfecta**, pero detecta patrones comunes usados por ciberdelincuentes.

> ❌ Nunca hagas clic en enlaces sospechosos.  
> ✅ Si dudas, contacta directamente a la empresa por su sitio oficial.

### 📚 ¿Quieres aprender más?
- [Curso de Ciberseguridad Cisco (gratis)](https://www.netacad.com/courses/cybersecurity)
- [Hugging Face - Modelos de IA éticos](https://huggingface.co/models)
""")

# Pie de página
st.markdown("<small>🛠️ Hecho con ❤️ usando Python + Streamlit. No al uso malicioso de la IA.</small>", unsafe_allow_html=True)
