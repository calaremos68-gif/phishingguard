import streamlit as st
import re
from textblob import TextBlob

# --- LOGO ---
st.image("https://i.ibb.co/8YqKJQk/phishingguard-logo.png", width=180)

# --- TÍTULO ---
st.title("🛡️ PhishingGuard — Detecta mensajes de phishing generados por IA")
st.markdown("""
*¿Recibiste un mensaje extraño? Pégalo aquí y te diremos si fue creado por una IA maliciosa como WormGPT.*  
*(No necesitas ser experto — solo pega y presiona "Analizar")*
""")

# --- ENTRADA DE TEXTO ---
texto_input = st.text_area(
    "Pega aquí el mensaje que quieres analizar:",
    height=200,
    placeholder="Ejemplo: 'Estimado cliente, su cuenta será bloqueada en 2 horas. Haga clic aquí: https://secure-bank-login.xyz'"
)

# --- BOTÓN DE ANÁLISIS ---
if st.button("🔍 Analizar mensaje"):
    if not texto_input.strip():
        st.warning("Por favor ingresa un texto para analizar.")
    else:
        with st.spinner("Analizando..."):
            alertas = []
            
            # 1. URLs sospechosas
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', texto_input)
            for url in urls:
                dominio = url.split("//")[-1].split("/")[0]
                if any(ext in dominio.lower() for ext in ["login", "verify", "secure", "update", "account", "bank", "paypal"]) and \
                   not any(valid in dominio.lower() for valid in ["google.com", "facebook.com", "amazon.com", "youtube.com", "instagram.com"]):
                    alertas.append(f"🚨 URL sospechosa: {url}")

            # 2. Sentimiento extremo (TextBlob)
            blob = TextBlob(texto_input)
            polaridad = blob.sentiment.polarity
            subjetividad = blob.sentiment.subjectivity
            if polaridad > 0.7 or polaridad < -0.4:
                alertas.append(f"⚠️ Tono extremo: {'Muy positivo' if polaridad > 0.7 else 'Muy negativo'} ({polaridad:.2f})")

            # 3. Palabras de urgencia
            urgencias = [
                "urgente", "inmediato", "ahora", "24h", "cerrar", "bloquear", 
                "verificar", "confirmar", "sin delay", "sin acción", "antes de",
                "por favor actúa", "limítate", "última oportunidad", "cierre inminente"
            ]
            palabras_urgencia = [p for p in urgencias if p in texto_input.lower()]
            if len(palabras_urgencia) >= 2:
                alertas.append(f"⚠️ Palabras de urgencia: {', '.join(palabras_urgencia)}")

            # 4. Frases demasiado largas o formales
            oraciones = [s.strip() for s in texto_input.split('.') if s.strip()]
            frases_largas = sum(1 for oracion in oraciones if len(oracion.split()) > 15)
            if frases_largas > 1:
                alertas.append("⚠️ Demasiadas frases largas y formales — poco natural para un humano")

            # 5. Uso excesivo de mayúsculas o signos de exclamación
            if texto_input.count('!') >= 3 or texto_input.count('?') >= 2:
                alertas.append("⚠️ Exceso de signos de exclamación o interrogación — típico en estafas")

            # 6. Ausencia de nombre personalizado
            if "estimado cliente" in texto_input.lower() or "estimado usuario" in texto_input.lower():
                alertas.append("⚠️ Saludo genérico ('Estimado cliente') — común en phishing de IA")

            # 7. Firma falsa de empresa
            if any(x in texto_input.lower() for x in ["equipo de seguridad", "servicio al cliente", "departamento de cuentas"]) and \
               not any(x in texto_input.lower() for x in ["gmail", "hotmail", "outlook", "yahoo"]):
                alertas.append("⚠️ Firma corporativa falsa — sin correo oficial ni contacto real")

            # --- CLASIFICACIÓN FINAL ---
            score = len(alertas)
            if score >= 5:
                nivel = "🔴 ALTO RIESGO — ¡Es probable phishing generado por IA!"
                color = "red"
            elif score >= 3:
                nivel = "🟡 MODERADO RIESGO — Revisa con cuidado"
                color = "orange"
            else:
                nivel = "🟢 BAJO RIESGO — Parece legítimo"
                color = "green"

            # --- RESULTADOS ---
            st.markdown(f"### {nivel}")
            st.markdown(f"<span style='color:{color}; font-weight:bold;'>{nivel}</span>", unsafe_allow_html=True)

            if alertas:
                st.subheader("📌 Señales detectadas:")
                for alerta in alertas:
                    st.warning(alerta)
            else:
                st.success("✅ No se encontraron señales de riesgo.")

# --- INFORMACIÓN ADICIONAL ---
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

# --- PIE DE PÁGINA ---
st.markdown("<small>🛠️ Hecho con ❤️ usando Python + Streamlit. No al uso malicioso de la IA.</small>", unsafe_allow_html=True)
