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

h1, h2, h3 {{
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
   Boas-vindas na Início (etiqueta pequena acima do título + ilustração)
   -------------------------------------------------------------------- */
.boas-vindas-etiqueta {{
    display: inline-block;
    color: {_PRIMARIA};
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
    margin-bottom: -0.4rem;
}}
.hero-ilustracao {{
    max-width: 340px;
    margin: 0 auto;
}}
.hero-ilustracao svg {{
    width: 100%;
    height: auto;
    display: block;
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

.module-badge {{
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
.badge-indigo {{ background: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE; }}

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
    h1 {{
        font-size: 1.6rem !important;
    }}
    div[data-testid="stMainBlockContainer"] {{
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }}
    div[style*="650px"] {{
        height: 420px !important;
        max-height: 65vh !important;
    }}
    .hero-ilustracao {{
        max-width: 220px;
    }}
    div[class*="st-key-pagina_jogos"] div[data-testid="stVerticalBlockBorderWrapper"] {{
        padding: 0.4rem 0.6rem !important;
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

