import streamlit as st


def render_html(content: str) -> None:
    """Renderiza HTML de forma robusta entre versiones de Streamlit."""
    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown(content, unsafe_allow_html=True)

st.set_page_config(
    page_title="El Profe Saber — ICFES con IA",
    page_icon="🎓",
    layout="wide",
)

render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;0,9..144,900;1,9..144,300&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --azul:    #0d2d4e;
    --azul-m:  #1a5080;
    --naranja: #e8600a;
    --crema:   #f5f0e8;
    --hueso:   #ede8de;
    --tinta:   #0d1f2d;
    --gris:    #5a7080;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.stApp {
    background: var(--crema);
    font-family: 'DM Sans', sans-serif;
}

/* ── ocultar chrome de streamlit ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ══════════════════════════════════
   HERO
══════════════════════════════════ */
.hero {
    position: relative;
    min-height: 92vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 6rem 8vw 5rem;
    overflow: hidden;
    background: var(--azul);
}

/* textura de ruido sutil */
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    opacity: 0.6;
    pointer-events: none;
}

/* orbe naranja */
.hero::after {
    content: '';
    position: absolute;
    width: 520px; height: 520px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(232,96,10,0.22) 0%, transparent 70%);
    top: -80px; right: -60px;
    pointer-events: none;
}

.hero-badge {
    display: inline-block;
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--naranja);
    border: 1px solid rgba(232,96,10,0.4);
    background: rgba(232,96,10,0.08);
    margin-bottom: 1.8rem;
    animation: fadeUp 0.5s ease both;
}

.hero-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: clamp(3rem, 7vw, 6.5rem);
    font-weight: 900;
    line-height: 1.0;
    color: #fff;
    max-width: 820px;
    animation: fadeUp 0.6s 0.1s ease both;
}

.hero-title em {
    font-style: italic;
    color: var(--naranja);
}

.hero-sub {
    font-size: clamp(1rem, 1.5vw, 1.18rem);
    font-weight: 300;
    color: rgba(255,255,255,0.72);
    max-width: 520px;
    line-height: 1.65;
    margin-top: 1.5rem;
    animation: fadeUp 0.6s 0.2s ease both;
}

.hero-ctas {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 2.5rem;
    animation: fadeUp 0.6s 0.3s ease both;
}

.btn-primary {
    padding: 0.85rem 2rem;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    background: var(--naranja);
    color: #fff;
    border: none;
    transition: transform 0.15s, box-shadow 0.15s;
    box-shadow: 0 6px 20px rgba(232,96,10,0.35);
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(232,96,10,0.45); }

.btn-ghost {
    padding: 0.85rem 2rem;
    border-radius: 8px;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    text-decoration: none;
    background: transparent;
    color: rgba(255,255,255,0.85);
    border: 1px solid rgba(255,255,255,0.28);
    transition: background 0.15s, border-color 0.15s;
}
.btn-ghost:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.5); }

/* stats en hero */
.hero-stats {
    display: flex;
    gap: 2.5rem;
    flex-wrap: wrap;
    margin-top: 4rem;
    padding-top: 2.5rem;
    border-top: 1px solid rgba(255,255,255,0.12);
    animation: fadeUp 0.6s 0.4s ease both;
}

.hero-stat-num {
    font-family: 'Fraunces', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #fff;
    line-height: 1;
}

.hero-stat-txt {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.52);
    margin-top: 0.2rem;
    max-width: 120px;
}

/* ══════════════════════════════════
   FEATURES
══════════════════════════════════ */
.section {
    padding: 6rem 8vw;
}

.section-label {
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--naranja);
    margin-bottom: 0.8rem;
}

.section-title {
    font-family: 'Fraunces', serif;
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 700;
    color: var(--tinta);
    line-height: 1.1;
    max-width: 540px;
}

.section-title em { font-style: italic; color: var(--azul-m); }

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-top: 3.5rem;
}

.feat {
    padding: 2rem;
    border-radius: 16px;
    background: #fff;
    border: 1px solid rgba(13,45,78,0.09);
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}

.feat::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: var(--naranja);
    transform: scaleY(0);
    transform-origin: bottom;
    transition: transform 0.25s ease;
}

.feat:hover { transform: translateY(-4px); box-shadow: 0 16px 40px rgba(13,45,78,0.1); }
.feat:hover::before { transform: scaleY(1); }

.feat-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
    display: block;
}

.feat-title {
    font-family: 'Fraunces', serif;
    font-size: 1.18rem;
    font-weight: 700;
    color: var(--tinta);
    margin-bottom: 0.5rem;
}

.feat-desc {
    font-size: 0.92rem;
    color: var(--gris);
    line-height: 1.6;
}

/* ══════════════════════════════════
   CÓMO FUNCIONA
══════════════════════════════════ */
.how-section {
    padding: 6rem 8vw;
    background: var(--azul);
    position: relative;
    overflow: hidden;
}

.how-section::before {
    content: '';
    position: absolute;
    width: 600px; height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(26,80,128,0.6) 0%, transparent 70%);
    bottom: -200px; left: -100px;
    pointer-events: none;
}

.how-title {
    font-family: 'Fraunces', serif;
    font-size: clamp(2rem, 3.5vw, 2.8rem);
    font-weight: 700;
    color: #fff;
    margin-bottom: 3rem;
}

.steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 2rem;
    position: relative;
    z-index: 1;
}

.step {
    position: relative;
}

.step-num {
    font-family: 'Fraunces', serif;
    font-size: 3.5rem;
    font-weight: 900;
    color: rgba(255,255,255,0.08);
    line-height: 1;
    margin-bottom: 0.5rem;
}

.step-title {
    font-family: 'Fraunces', serif;
    font-size: 1.08rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.4rem;
}

.step-desc {
    font-size: 0.88rem;
    color: rgba(255,255,255,0.55);
    line-height: 1.6;
}

.step-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--naranja);
    margin-bottom: 1rem;
}

/* ══════════════════════════════════
   PLANES
══════════════════════════════════ */
.planes-section {
    padding: 6rem 8vw;
    background: var(--hueso);
}

.planes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.5rem;
    margin-top: 3.5rem;
}

.plan-card {
    padding: 2.2rem;
    border-radius: 18px;
    background: #fff;
    border: 1.5px solid rgba(13,45,78,0.1);
    position: relative;
}

.plan-card.destacado {
    background: var(--azul);
    border-color: var(--azul);
}

.plan-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    background: var(--naranja);
    color: #fff;
    margin-bottom: 1.2rem;
}

.plan-name {
    font-family: 'Fraunces', serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--tinta);
    margin-bottom: 0.3rem;
}

.plan-card.destacado .plan-name { color: #fff; }

.plan-price {
    font-family: 'Fraunces', serif;
    font-size: 2.4rem;
    font-weight: 900;
    color: var(--naranja);
    line-height: 1;
    margin-bottom: 0.2rem;
}

.plan-period {
    font-size: 0.82rem;
    color: var(--gris);
    margin-bottom: 1.5rem;
}

.plan-card.destacado .plan-period { color: rgba(255,255,255,0.55); }

.plan-feat {
    font-size: 0.88rem;
    color: var(--gris);
    padding: 0.45rem 0;
    border-bottom: 1px solid rgba(13,45,78,0.06);
    display: flex;
    gap: 0.5rem;
    align-items: flex-start;
}

.plan-card.destacado .plan-feat {
    color: rgba(255,255,255,0.7);
    border-bottom-color: rgba(255,255,255,0.08);
}

.plan-feat:last-of-type { border-bottom: none; }

/* ══════════════════════════════════
   MATERIAS
══════════════════════════════════ */
.materias-row {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    margin-top: 3rem;
}

.materia-pill {
    padding: 0.5rem 1.2rem;
    border-radius: 999px;
    font-size: 0.88rem;
    font-weight: 500;
    background: #fff;
    color: var(--azul);
    border: 1.5px solid rgba(13,45,78,0.15);
    transition: all 0.15s;
}

.materia-pill:hover {
    background: var(--azul);
    color: #fff;
    border-color: var(--azul);
}

/* ══════════════════════════════════
   CTA FINAL
══════════════════════════════════ */
.cta-section {
    padding: 7rem 8vw;
    text-align: center;
    background: var(--crema);
}

.cta-title {
    font-family: 'Fraunces', serif;
    font-size: clamp(2.2rem, 5vw, 4rem);
    font-weight: 900;
    color: var(--tinta);
    line-height: 1.05;
    margin-bottom: 1.2rem;
}

.cta-title em { font-style: italic; color: var(--naranja); }

.cta-sub {
    font-size: 1rem;
    color: var(--gris);
    max-width: 440px;
    margin: 0 auto 2.5rem;
    line-height: 1.6;
}

/* footer */
.site-footer {
    padding: 2rem 8vw;
    border-top: 1px solid rgba(13,45,78,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.82rem;
    color: var(--gris);
}

/* ══════════════════════════════════
   ANIMACIONES
══════════════════════════════════ */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Ocultar botones nativos de Streamlit en esta página */
.stButton > button {
    background: var(--naranja) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    padding: 0.75rem 1.5rem !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 4px 16px rgba(232,96,10,0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(232,96,10,0.4) !important;
}

@media (max-width: 640px) {
    .hero { padding: 4rem 6vw 3rem; }
    .hero-stats { gap: 1.5rem; }
    .section, .how-section, .planes-section, .cta-section { padding: 4rem 6vw; }
}
</style>""")


# ── HERO ──────────────────────────────────────────────────────────────────────
render_html("""
<section class="hero">
    <span class="hero-badge">Para estudiantes de 10° y 11° · Colombia</span>

    <h1 class="hero-title">
        Tu profe de ICFES.<br>
        Siempre disponible,<br>
        <em>siempre personalizado.</em>
    </h1>

    <p class="hero-sub">
        Diagnóstico adaptativo, tutor socrático con IA y seguimiento familiar
        en una sola plataforma. Aprende más en menos tiempo.
    </p>

    <div class="hero-ctas">
        <a class="btn-primary" href="#planes">Ver planes</a>
        <a class="btn-ghost" href="#flujo">Cómo funciona</a>
    </div>

    <div class="hero-stats">
        <div>
            <div class="hero-stat-num">1 350</div>
            <div class="hero-stat-txt">preguntas diagnósticas únicas</div>
        </div>
        <div>
            <div class="hero-stat-num">5</div>
            <div class="hero-stat-txt">materias Saber 11 cubiertas</div>
        </div>
        <div>
            <div class="hero-stat-num">24/7</div>
            <div class="hero-stat-txt">acceso al tutor sin interrupciones</div>
        </div>
        <div>
            <div class="hero-stat-num">3</div>
            <div class="hero-stat-txt">modelos de IA especializados</div>
        </div>
    </div>
</section>
""")


# ── FEATURES ──────────────────────────────────────────────────────────────────
render_html("""
<section id="features" class="section" style="background:#fff;">
    <div class="section-label">Qué hace diferente a El Profe Saber</div>
    <h2 class="section-title">No te da la respuesta.<br><em>Te enseña a encontrarla.</em></h2>

    <div class="features-grid">
        <div class="feat">
            <span class="feat-icon">🧠</span>
            <div class="feat-title">Método socrático</div>
            <p class="feat-desc">El tutor no resuelve por ti. Formula preguntas que te llevan a descubrir la respuesta — igual que un buen profe en clase.</p>
        </div>
        <div class="feat">
            <span class="feat-icon">📋</span>
            <div class="feat-title">Diagnóstico adaptativo</div>
            <p class="feat-desc">135 competencias mapeadas directamente de exámenes Saber 11 reales. El sistema detecta exactamente dónde estás débil y prioriza eso.</p>
        </div>
        <div class="feat">
            <span class="feat-icon">📸</span>
            <div class="feat-title">Análisis de imágenes</div>
            <p class="feat-desc">Fotografía el ejercicio que no entiendes. El tutor lo lee, lo interpreta y te guía paso a paso desde lo que ya sabes.</p>
        </div>
        <div class="feat">
            <span class="feat-icon">📈</span>
            <div class="feat-title">Seguimiento semanal</div>
            <p class="feat-desc">Cada semana el diagnóstico se renueva. Ves tu evolución por materia, subtema y nivel de dificultad a lo largo del tiempo.</p>
        </div>
        <div class="feat">
            <span class="feat-icon">👨‍👩‍👧</span>
            <div class="feat-title">Panel para padres</div>
            <p class="feat-desc">Leaderboard de progreso, gráfica de evolución semanal y consumo de créditos por hijo. Información real para tomar decisiones.</p>
        </div>
        <div class="feat">
            <span class="feat-icon">📄</span>
            <div class="feat-title">Exportación a PDF</div>
            <p class="feat-desc">Descarga cualquier sesión de estudio en PDF limpio. Ideal para repasar antes del examen o compartir con el profe del colegio.</p>
        </div>
    </div>
</section>
""")


# ── MATERIAS ──────────────────────────────────────────────────────────────────
render_html("""
<section id="materias" class="section" style="padding-top:2rem; padding-bottom:5rem; background:#fff;">
    <div class="section-label">Cobertura académica</div>
    <h2 class="section-title">Las 5 áreas del <em>Saber 11</em></h2>
    <div class="materias-row">
        <span class="materia-pill">📐 Matemáticas</span>
        <span class="materia-pill">📖 Lectura Crítica</span>
        <span class="materia-pill">🌍 Sociales y Ciudadanas</span>
        <span class="materia-pill">🔬 Ciencias Naturales</span>
        <span class="materia-pill">🇬🇧 Inglés</span>
    </div>
    <p style="margin-top:1.5rem; font-size:0.9rem; color:#5a7080; max-width:560px; line-height:1.6;">
        Cada materia tiene su propio modelo de IA especializado y su propio índice vectorial con documentos oficiales del ICFES.
        Grok para análisis crítico, DeepSeek para razonamiento formal, Gemini para imágenes.
    </p>
</section>
""")


# ── CÓMO FUNCIONA ─────────────────────────────────────────────────────────────
render_html("""
<section id="flujo" class="how-section">
    <div class="section-label" style="color:rgba(232,96,10,0.85);">Flujo de uso</div>
    <h2 class="how-title">De cero a estudiar<br>en 3 minutos.</h2>

    <div class="steps">
        <div class="step">
            <div class="step-dot"></div>
            <div class="step-num">01</div>
            <div class="step-title">Regístrate</div>
            <p class="step-desc">El padre crea la cuenta, registra al estudiante y define su PIN. Solo una vez.</p>
        </div>
        <div class="step">
            <div class="step-dot"></div>
            <div class="step-num">02</div>
            <div class="step-title">Haz el diagnóstico</div>
            <p class="step-desc">12 preguntas del banco real de competencias ICFES. El sistema mapea tus fortalezas y brechas por materia y subtema.</p>
        </div>
        <div class="step">
            <div class="step-dot"></div>
            <div class="step-num">03</div>
            <div class="step-title">Estudia con el tutor</div>
            <p class="step-desc">El profe ya sabe dónde fallaste. Te sugiere por dónde empezar y te acompaña con preguntas guiadas hasta que entiendes.</p>
        </div>
        <div class="step">
            <div class="step-dot"></div>
            <div class="step-num">04</div>
            <div class="step-title">Repite cada semana</div>
            <p class="step-desc">El diagnóstico adaptativo se renueva. Primero refuerza lo que fallaste, luego explora nuevos temas. Sin repetir preguntas ya vistas.</p>
        </div>
    </div>
</section>
""")


# ── PLANES ────────────────────────────────────────────────────────────────────
render_html("""
<section id="planes" class="planes-section">
    <div class="section-label">Planes</div>
    <h2 class="section-title">Simple, <em>sin sorpresas.</em></h2>

    <div class="planes-grid">
        <div class="plan-card">
            <div class="plan-name">Básico</div>
            <div class="plan-price">$20.000</div>
            <div class="plan-period">COP / mes · 1 estudiante</div>
            <div class="plan-feat">⚡ 1 000 créditos mensuales</div>
            <div class="plan-feat">📋 Diagnóstico adaptativo semanal</div>
            <div class="plan-feat">💬 Tutor en las 5 materias</div>
            <div class="plan-feat">📄 Exportación a PDF</div>
            <div class="plan-feat">👨‍👩‍👧 Panel del padre</div>
        </div>

        <div class="plan-card destacado">
            <span class="plan-badge">Más popular</span>
            <div class="plan-name">Estándar</div>
            <div class="plan-price">$30.000</div>
            <div class="plan-period">COP / mes · 1 estudiante</div>
            <div class="plan-feat">⚡ 2 000 créditos mensuales</div>
            <div class="plan-feat">📋 Diagnóstico adaptativo semanal</div>
            <div class="plan-feat">💬 Tutor en las 5 materias</div>
            <div class="plan-feat">📄 Exportación a PDF</div>
            <div class="plan-feat">📸 Análisis de imágenes incluido</div>
        </div>

        <div class="plan-card">
            <div class="plan-name">Familia</div>
            <div class="plan-price">$50.000</div>
            <div class="plan-period">COP / mes · hasta 3 estudiantes</div>
            <div class="plan-feat">⚡ 5 000 créditos compartidos</div>
            <div class="plan-feat">📋 Diagnóstico por cada estudiante</div>
            <div class="plan-feat">💬 Tutor en las 5 materias</div>
            <div class="plan-feat">📄 Exportación a PDF</div>
            <div class="plan-feat">📊 Leaderboard familiar</div>
        </div>
    </div>
</section>
""")


# ── CTA FINAL ─────────────────────────────────────────────────────────────────
render_html("""
<section class="cta-section">
    <h2 class="cta-title">El ICFES se prepara<br><em>con método,</em> no con suerte.</h2>
    <p class="cta-sub">
        Empieza hoy. El diagnóstico inicial tarda 10 minutos y ya sabrás exactamente
        en qué enfocar tu estudio.
    </p>
</section>
""")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("📝 Crear cuenta gratis", use_container_width=True):
        st.switch_page("pages/registro.py")
with col2:
    if st.button("🎓 Entrar a estudiar", use_container_width=True):
        st.switch_page("pages/estudiante.py")
with col3:
    if st.button("👨‍👩‍👧 Panel del padre", use_container_width=True):
        st.switch_page("app.py")

# ── FOOTER ───────────────────────────────────────────────────────────────────
render_html("""
<footer class="site-footer">
    <span><strong>El Profe Saber</strong> · Tutor ICFES con IA</span>
    <span>Para estudiantes de 10° y 11° · Colombia</span>
    <span>Desarrollado con ♥ en Medellín</span>
</footer>
""")

























































































