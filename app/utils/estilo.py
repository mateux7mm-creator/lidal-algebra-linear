"""CSS global injetado em streamlit_app.py para o Laboratório Interativo de Álgebra Linear.
Inclui Google Fonts (Outfit, Plus Jakarta Sans), animações CSS, gradientes dinâmicos,
estilização de cartões em glassmorphism, suporte responsivo e cartões de métricas.
"""
import streamlit as st

_PRIMARIA = "#4F46E5"
_TEXTO = "#0F172A"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* Fontes globais */
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: {_TEXTO};
}}

h1, h2, h3, .hero-title, .gradient-text {{
    font-family: 'Outfit', sans-serif !important;
}}

/* Redução de espaçamentos padrão do Streamlit */
div[data-testid="stMainBlockContainer"],
div[data-testid="stAppViewContainer"] .block-container,
div.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1300px;
}}
div[data-testid="stHeader"] {{
    height: 2.5rem;
    background: transparent !important;
}}
div[data-testid="stVerticalBlock"] {{
    gap: 0.75rem !important;
}}
hr {{
    margin: 1.25rem 0 !important;
    border-color: rgba(99, 102, 241, 0.15) !important;
}}

/* --------------------------------------------------------------------
   Animações Keyframes
   -------------------------------------------------------------------- */
@keyframes fadeInSlideUp {{
    from {{
        opacity: 0;
        transform: translateY(18px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

@keyframes floatAnimation {{
    0% {{ transform: translateY(0px) rotate(0deg); }}
    50% {{ transform: translateY(-8px) rotate(0.5deg); }}
    100% {{ transform: translateY(0px) rotate(0deg); }}
}}

@keyframes glowPulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.35); }}
    70% {{ box-shadow: 0 0 0 12px rgba(79, 70, 229, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }}
}}

@keyframes gradientShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* --------------------------------------------------------------------
   Título "LIDAL" — centrado, animado, acima do hero da Início
   -------------------------------------------------------------------- */
.lidal-titulo {{
    text-align: center;
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 3.2rem;
    letter-spacing: 0.15em;
    margin: 0.2rem 0 0.6rem 0;
    background: linear-gradient(90deg, #4F46E5 0%, #06B6D4 45%, #4F46E5 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 6s ease infinite, fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}}
@media (max-width: 768px) {{
    .lidal-titulo {{
        font-size: 2.1rem;
        letter-spacing: 0.1em;
    }}
}}

/* --------------------------------------------------------------------
   Estilos do Hero & Boas-vindas
   -------------------------------------------------------------------- */
.hero-card {{
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(243,244,246,0.95) 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 20px;
    padding: 2.2rem 2rem;
    box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.15);
    animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
}}

.hero-card::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 6px;
    height: 100%;
    background: linear-gradient(180deg, #4F46E5 0%, #06B6D4 100%);
    border-top-left-radius: 20px;
    border-bottom-left-radius: 20px;
}}

.lab-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.85rem;
    background: linear-gradient(90deg, rgba(79, 70, 229, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
    border: 1px solid rgba(79, 70, 229, 0.25);
    border-radius: 9999px;
    color: #4F46E5;
    font-weight: 700;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}}

.gradient-text {{
    background: linear-gradient(135deg, #1E1B4B 0%, #4F46E5 40%, #06B6D4 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 8s ease infinite;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -0.02em;
}}

.hero-sub {{
    font-size: 1.1rem;
    color: #475569;
    line-height: 1.6;
    margin-top: 0.6rem;
    font-weight: 400;
}}

.hero-img-wrap {{
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(15, 23, 42, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.8);
    transition: transform 0.4s ease, box-shadow 0.4s ease;
    animation: floatAnimation 6s ease-in-out infinite;
}}

.hero-img-wrap:hover {{
    transform: scale(1.02) translateY(-4px);
    box-shadow: 0 22px 45px rgba(79, 70, 229, 0.25);
}}

.hero-img-wrap img {{
    width: 100%;
    height: auto;
    display: block;
    object-fit: cover;
}}

/* Stats Pills - Largura Total Horizontal */
.recursos-container {{
    width: 100%;
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
}}

.stat-pill {{
    display: flex;
    align-items: center;
    gap: 0.85rem;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    padding: 1rem 1.25rem;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    height: 100%;
}}
.stat-pill:hover {{
    transform: translateY(-3px);
    border-color: #818CF8;
    box-shadow: 0 10px 22px rgba(79, 70, 229, 0.12);
}}
.stat-icon {{
    font-size: 1.8rem;
    line-height: 1;
}}
.stat-num {{
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    color: #1E1B4B;
}}
.stat-label {{
    font-size: 0.8rem;
    color: #64748B;
}}

/* --------------------------------------------------------------------
   Cartões dos Módulos (Grid com Mesma Altura - Equal Height Cards)
   -------------------------------------------------------------------- */
div[data-testid="stColumn"] {{
    display: flex;
    flex-direction: column;
}}

div[data-testid="stColumn"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
    height: 100% !important;
    min-height: 175px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 16px !important;
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
    background: #FFFFFF;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    transform: translateY(-4px) scale(1.005) !important;
    box-shadow: 0 16px 32px -8px rgba(79, 70, 229, 0.18) !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
}}

.module-header-box {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.4rem;
}}

.module-badge {{
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
.badge-indigo {{ background: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE; }}
.badge-cyan {{ background: #ECFEFF; color: #0891B2; border: 1px solid #A5F3FC; }}
.badge-emerald {{ background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }}
.badge-amber {{ background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }}

.math-object-img {{
    width: 100%;
    height: 140px;
    object-fit: cover;
    border-radius: 12px;
    margin-bottom: 0.75rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    transition: transform 0.3s ease;
}}
.math-object-img:hover {{
    transform: scale(1.03);
}}

/* --------------------------------------------------------------------
   Botões e Controlos
   -------------------------------------------------------------------- */
div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.2s ease !important;
    border: 1px solid rgba(79, 70, 229, 0.2) !important;
}}

div[data-testid="stButton"] button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.25) !important;
    background-color: #4F46E5 !important;
    color: #FFFFFF !important;
}}

/* Botão Primário no Streamlit */
div[data-testid="stButton"] button[kind="primary"] {{
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
}}

/* --------------------------------------------------------------------
   Caixas de Passos e Expansores
   -------------------------------------------------------------------- */
div[data-testid="stExpander"] {{
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    background: #FAFAFA !important;
    overflow: hidden !important;
}}

div[data-testid="stExpander"] summary {{
    font-weight: 600 !important;
    color: #1E1B4B !important;
}}

/* --------------------------------------------------------------------
   Barra Lateral & Status Badge
   -------------------------------------------------------------------- */
section[data-testid="stSidebar"] {{
    background-color: #F8FAFC !important;
    border-right: 1px solid #E2E8F0 !important;
}}

.sidebar-header-box {{
    padding: 0.6rem 0.2rem;
}}

.lab-status-badge {{
    display: inline-block;
    padding: 0.2rem 0.5rem;
    background: #DCFCE7;
    color: #15803D;
    border: 1px solid #86EFAC;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}}

/* --------------------------------------------------------------------
   Métricas estilizadas
   -------------------------------------------------------------------- */
div[data-testid="stMetric"] {{
    background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%) !important;
    border: 1px solid #C7D2FE !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    border-left: 4px solid #4F46E5 !important;
}}
div[data-testid="stMetricValue"] {{
    color: #4F46E5 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
}}

/* --------------------------------------------------------------------
   Responsividade para Ecrãs Pequenos (Telemóveis / Tablets)
   -------------------------------------------------------------------- */
@media (max-width: 768px) {{
    div[data-testid="stMainBlockContainer"] {{
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }}
    .hero-card {{
        padding: 1.4rem 1.1rem !important;
    }}
    .gradient-text {{
        font-size: 1.8rem !important;
    }}
    .hero-sub {{
        font-size: 0.95rem !important;
    }}
    .math-object-img {{
        height: 110px !important;
    }}
}}
</style>
"""


def injetar_css() -> None:
    """Aplica o CSS global e executa o script de controlo inteligente da barra lateral (Aberta na Home, Fechada nos Módulos)."""
    st.markdown(_CSS, unsafe_allow_html=True)
    st.iframe(
        """
        <script>
        (function() {
            function gerirBarraLateral() {
                try {
                    const parentDoc = window.parent.document;
                    const parentWin = window.parent;
                    const href = parentWin.location.href.toLowerCase();
                    const pathname = parentWin.location.pathname.toLowerCase();
                    const search = parentWin.location.search.toLowerCase();
                    const fullUrl = (href + pathname + search);

                    // Verificar se estamos na página inicial ("Início")
                    const eInicio = fullUrl.endsWith('/inicio') || 
                                   pathname === '/' || 
                                   pathname.endsWith('/inicio') || 
                                   pathname.endsWith('app/') || 
                                   search.includes('inicio') ||
                                   (!fullUrl.includes('matrizes') && 
                                    !fullUrl.includes('determinantes') && 
                                    !fullUrl.includes('sistemas') && 
                                    !fullUrl.includes('exploracao') && 
                                    !fullUrl.includes('vetores') && 
                                    !fullUrl.includes('valores-proprios') && 
                                    !fullUrl.includes('jogos') && 
                                    !fullUrl.includes('conteudo'));

                    const sidebar = parentDoc.querySelector('section[data-testid="stSidebar"]');
                    if (!sidebar) return;

                    const estaExpandida = sidebar.getAttribute('aria-expanded') === 'true';

                    if (eInicio) {
                        // Na página inicial: Garantir que a barra lateral fica ABERTA (Expandida)
                        if (!estaExpandida) {
                            const expandBtn = parentDoc.querySelector('button[data-testid="stSidebarExpandButton"]') || 
                                             parentDoc.querySelector('div[data-testid="stSidebarCollapsedControl"] button') ||
                                             parentDoc.querySelector('[aria-label="Expand sidebar"]') ||
                                             parentDoc.querySelector('[aria-label="Open sidebar"]');
                            if (expandBtn) expandBtn.click();
                        }
                    } else {
                        // Dentro de qualquer módulo (Matrizes, Sistemas, etc.): Garantir que FECHA (Recolhe)
                        if (estaExpandida) {
                            const collapseBtn = parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"]') || 
                                                parentDoc.querySelector('section[data-testid="stSidebar"] button') ||
                                                parentDoc.querySelector('[aria-label="Close sidebar"]') || 
                                                parentDoc.querySelector('[aria-label="Collapse sidebar"]');
                            if (collapseBtn) collapseBtn.click();
                        }
                    }
                } catch (e) {
                    console.log("Gerir barra lateral:", e);
                }
            }

            gerirBarraLateral();
            setTimeout(gerirBarraLateral, 150);
            setTimeout(gerirBarraLateral, 450);
            setTimeout(gerirBarraLateral, 900);
        })();
        </script>
        """,
        height=1,
        width=1,
    )

