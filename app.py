import streamlit as st
import re
from textblob import TextBlob

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="🛡️ PhishingGuard", page_icon="🛡️", layout="centered")

# --- LOGO ---
st.image("https://i.ibb.co/8YqKJQk/phishingguard-logo.png", width=180)

# --- TÍTULO ---
st.title("🛡️ PhishingGuard — Detecta mensajes de phishing")
st.markdown("""
*¿Recibiste un mensaje extraño? Pégalo aquí y te diremos si es sospechoso.*
""")

# --- ENTRADA DE TEXTO ---
texto = st.text_area(
    "Pega el mensaje aquí:",
    height=150,
    placeholder="Ejemplo: 'Estimado cliente, su cuenta será bloqueada en 2 horas. Haga clic aquí: https://secure-bank-login.xyz'"
)

# --- BOTÓN ---
if st.button("🔍 Analizar"):
    if not texto.strip():
        st.warning("Por favor ingresa un texto.")
    else:
        # 1. URLs sospechosas
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', texto)
        alertas = []
        for url in urls:
            dominio = url.split("//")[-1].split("/")[0]
            if any(ext in dominio.lower() for ext in ["login", "verify", "secure", "update", "account", "bank"]) and \
               not any(valid in dominio.lower() for valid in ["google.com", "facebook.com", "amazon.com"]):
                alertas.append(f"🚨 URL sospechosa: {url}")

        # 2. Sentimiento extremo
        blob = TextBlob(texto)
        polaridad = blob.sentiment.polarity
        if polaridad > 0.7 or polaridad < -0.4:
            alertas.append(f"⚠️ Tono extremo: {'Muy positivo' if polaridad > 0.7 else 'Muy negativo'} ({polaridad:.2f})")

        # 3. Palabras de urgencia
        urgencias = ["urgente", "inmediato", "ahora", "24h", "cerrar", "bloquear"]
        palabras_urgencia = [p for p in urgencias if p in texto.lower()]
        if len(palabras_urgencia) >= 2:
            alertas.append(f"⚠️ Palabras de urgencia: {', '.join(palabras_urgencia)}")

        # 4. Frases largas
        oraciones = [s.strip() for s in texto.split('.') if s.strip()]
        frases_largas = sum(1 for oracion in oraciones if len(oracion.split()) > 15)
        if frases_largas > 1:
            alertas.append("⚠️ Demasiadas frases largas — poco natural")

        # 5. Exceso de signos
        if texto.count('!') >= 3 or texto.count('?') >= 2:
            alertas.append("⚠️ Exceso de signos de exclamación")

        # --- CLASIFICACIÓN ---
        score = len(alertas)
        if score >= 4:
            nivel = "🔴 ALTO RIESGO"
            color = "red"
        elif score >= 2:
            nivel = "🟡 MODERADO RIESGO"
            color = "orange"
        else:
            nivel = "🟢 BAJO RIESGO"
            color = "green"

        # --- RESULTADOS ---
        st.markdown(f"### {nivel}")
        st.markdown(f"<span style='color:{color}; font-weight:bold;'>{nivel}</span>", unsafe_allow_html=True)
        
        if alertas:
            st.subheader("📌 Señales detectadas:")
            for a in alertas:
                st.warning(a)
        else:
            st.success("✅ No se encontraron señales de riesgo.")

# --- PIE ---
st.markdown("---")
st.markdown("<small>🛠️ Hecho con ❤️ para proteger a personas de estafas digitales.</small>", unsafe_allow_html=True)
