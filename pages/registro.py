# pages/registro.py

import streamlit as st
from core.auth import hashear_pin
from core.database import supabase_admin as supabase, crear_estudiante
import re

st.set_page_config(page_title="Registro — Tutor ICFES", page_icon="📝")

def email_valido(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def telefono_valido(telefono):
    return re.match(r"^[0-9]{10}$", telefono)

# --- ENCABEZADO ---
st.title("📝 Crear cuenta")
st.subheader("¡Bienvenido al proceso de registro del Tutor ICFES!")
st.subheader("El padre, madre o tutor debe realizar el registro.")
st.subheader("Una vez completes el formulario, nos pondremos en contacto contigo para validar tu información y activar tu cuenta.")
st.divider()

# --- PASO 1: DATOS DEL PADRE ---
st.subheader("1. Tus datos")
with st.form("form_registro"):
    nombre = st.text_input("Nombre completo *")
    email = st.text_input("Correo electrónico *")
    telefono = st.text_input("Teléfono (10 dígitos) *")
    pin = st.text_input("PIN de acceso (mínimo 6 dígitos) *", type="password")
    pin_confirmar = st.text_input("Confirmar PIN *", type="password")

    st.divider()

    # --- PASO 2: DATOS DEL ESTUDIANTE ---
    st.subheader("2. Datos del primer estudiante")
    st.caption("Podrás agregar más hijos desde el panel principal una vez la cuenta esté activa.")
    nombre_estudiante = st.text_input("Nombre del estudiante *")
    grado = st.selectbox("Grado *", ["10°", "11°"])
    pin_estudiante = st.text_input("PIN del estudiante (mínimo 4 dígitos) *", type="password")
    pin_estudiante_confirmar = st.text_input("Confirmar PIN del estudiante *", type="password")

    st.divider()

    # --- PASO 3: CONSENTIMIENTO ---
    st.subheader("3. Autorización de datos")
    
    with st.expander("📄 Leer Política de Tratamiento de Datos (obligatorio)", expanded=False):
        st.markdown("""
        **POLÍTICA DE TRATAMIENTO DE DATOS PERSONALES — Tutor ICFES v1.0**

        **Responsable:** Iván Romero | ivanromero714@gmail.com | Medellín, Colombia

        **Datos que recolectamos:** nombre, correo, teléfono, dirección IP del padre/tutor;
        nombre, grado e historial de conversaciones del estudiante.

        **Finalidad:** prestar el servicio de tutoría para preparación al ICFES, gestionar
        la cuenta y medir el progreso académico.

        **Proveedores tecnológicos:** Supabase (base de datos), OpenRouter (modelos de IA),
        Pinecone (búsqueda semántica). No vendemos ni cedemos datos a terceros.

        **Retención:** datos de cuenta: mientras la cuenta esté activa + 6 meses.
        Historial de conversaciones: máximo 12 meses. Métricas anonimizadas: indefinidamente.

        **Derechos:** puede acceder, corregir, suprimir o revocar el consentimiento escribiendo
        a ivanromero714@gmail.com. Tiempo de respuesta: 15 días hábiles.

        **Menores de edad:** el tratamiento de datos del estudiante solo procede con
        autorización expresa del padre, madre o tutor legal, conforme al artículo 7
        de la Ley 1581 de 2012.

        Para la política completa escríbenos al correo indicado.
        """)

    acepto_politica = st.checkbox(
        "He leído y acepto la Política de Tratamiento de Datos Personales (Versión 1.0) *"
    )
    soy_tutor = st.checkbox(
        "Declaro ser padre, madre o tutor legal del estudiante registrado *"
    )

    st.divider()
    submitted = st.form_submit_button("✅ Crear cuenta", use_container_width=True)

# --- VALIDACIONES Y REGISTRO ---
if submitted:
    errores = []

    if not nombre: errores.append("Nombre completo es obligatorio.")
    if not email_valido(email): errores.append("Correo electrónico no válido.")
    if not telefono_valido(telefono): errores.append("Teléfono debe tener 10 dígitos.")
    if len(pin) < 6: errores.append("El PIN debe tener mínimo 6 dígitos.")
    if pin != pin_confirmar: errores.append("Los PINs no coinciden.")
    if not nombre_estudiante: errores.append("Nombre del estudiante es obligatorio.")
    if len(pin_estudiante) < 4: errores.append("El PIN del estudiante debe tener mínimo 4 dígitos.")
    if pin_estudiante != pin_estudiante_confirmar: errores.append("Los PIN del estudiante no coinciden.")
    if not acepto_politica: errores.append("Debes aceptar la política de tratamiento de datos.")
    if not soy_tutor: errores.append("Debes confirmar que eres padre, madre o tutor legal.")

    if errores:
        for e in errores:
            st.error(f"• {e}")
    else:
        try:
            # Verificar si el email ya existe
            existente = supabase.table("padres")\
                .select("id").eq("email", email).execute()
            
            if existente.data:
                st.error("Ya existe una cuenta con ese correo electrónico.")
            else:
                # Crear padre
                pin_hash = hashear_pin(pin)
                res_padre = supabase.table("padres").insert({
                    "nombre": nombre,
                    "email": email,
                    "telefono": telefono,
                    "pin": pin_hash,
                    "plan": "basico",
                    "estado": "pendiente"
                }).execute()

                padre_id = res_padre.data[0]["id"]

                # Crear estudiante
                pin_estudiante_hash = hashear_pin(pin_estudiante)
                res_est = crear_estudiante(
                    padre_id=padre_id,
                    nombre=nombre_estudiante,
                    grado=grado,
                    pin_hash=pin_estudiante_hash,
                )
                est_insertado = (res_est.data[0] if getattr(res_est, "data", None) else None)
                if est_insertado and ("pin_hash" not in est_insertado or not est_insertado.get("pin_hash")):
                    st.warning(
                        "Registro completado, pero el PIN del estudiante no quedó persistido en BD. "
                        "Aplica la migración de `pin_hash` para habilitar entrada del estudiante por PIN."
                    )

                # Registrar consentimiento
                supabase.table("consentimientos").insert({
                    "padre_id": padre_id,
                    "acepto_politica": True,
                    "version_politica": "1.0",
                    "canal": "web_registro"
                }).execute()

                st.success("""
                    ✅ ¡Registro exitoso! 
                    
                    Tu cuenta está siendo revisada. Te notificaremos por correo 
                    cuando esté activa (generalmente en menos de 24 horas).
                """)
                
                st.info("💡 Una vez activa tu cuenta, podrás ingresar con tu correo y PIN.")
                
                if st.button("Ir al login →"):
                    st.switch_page("app.py")

        except Exception as e:
            st.error(f"Error al crear la cuenta: {str(e)}")

st.divider()
st.caption("¿Ya tienes cuenta? [Ir al login](/) ")