"""CSS global injetado uma única vez em streamlit_app.py, para dar um
acabamento visual mais consistente além do que o tema nativo do Streamlit
(.streamlit/config.toml) já cobre — cartões com sombra/hover, botões e
caixas de passos mais arredondados, etc. As cores usadas aqui replicam as
de config.toml (mantê-las sincronizadas se o tema mudar)."""
import streamlit as st

_PRIMARIA = "#4F46E5"
_TEXTO = "#1F2430"

_CSS = f"""
<style>
/* Reduz o espaço vazio entre a barra de ferramentas do Streamlit (ícone de
   "Deploy", menu ☰) e o título de cada página — o Streamlit reserva por
   omissão um padding grande no topo (e no fundo) do bloco principal, para
   nunca ficar tapado por essa barra. !important porque o Streamlit injeta
   o seu próprio CSS depois deste, com a mesma especificidade. */
div[data-testid="stMainBlockContainer"],
div[data-testid="stAppViewContainer"] .block-container,
div.block-container {{
    padding-top: 3rem !important;
    padding-bottom: 2rem !important;
}}
div[data-testid="stHeader"] {{
    height: 3rem;
}}

/* Reduz o espaçamento vertical entre elementos dentro do conteúdo (títulos,
   inputs, divisores, gráficos, ...) — o Streamlit usa por omissão um
   espaçamento generoso pensado para páginas mais simples que as deste
   laboratório, com várias secções empilhadas por módulo. */
div[data-testid="stVerticalBlock"] {{
    gap: 0.6rem !important;
}}
hr {{
    margin: 0.75rem 0 !important;
}}

/* Cartões (st.container(border=True)) — usados nos cabeçalhos de módulo,
   nos blocos "Resultado"/"Operandos escolhidos" e nos cartões da Início. */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 14px !important;
    box-shadow: 0 1px 3px rgba(31, 36, 48, 0.08);
    transition: box-shadow 0.15s ease, transform 0.15s ease;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    box-shadow: 0 4px 14px rgba(31, 36, 48, 0.12);
}}

/* Botões (➕ Adicionar, ➖ Remover, 🔄 Repor, etc.) */
div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {{
    border-radius: 8px;
    transition: transform 0.1s ease, box-shadow 0.1s ease;
}}
div[data-testid="stButton"] button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25);
}}

/* Caixas de passos pedagógicos ("Como se chega ao resultado") */
div[data-testid="stExpander"] {{
    border-radius: 10px;
    border: 1px solid #e3e3e3;
    overflow: hidden;
}}

/* Menu de popover (barra_menus, estilo Winplot) */
div[data-testid="stPopoverBody"] {{
    border-radius: 10px;
}}

/* Barra lateral */
section[data-testid="stSidebar"] {{
    border-right: 1px solid #e8e8ef;
}}

/* Título principal de cada página */
h1 {{
    font-weight: 700;
    color: {_TEXTO};
}}

/* Métricas (ex. "Determinante" em Determinantes) */
div[data-testid="stMetric"] {{
    background: rgba(79, 70, 229, 0.06);
    border-radius: 10px;
    padding: 0.6rem 0.8rem;
}}
div[data-testid="stMetricValue"] {{
    color: {_PRIMARIA};
}}

/* Cartões mais compactos só no módulo Jogos e Desafios (st.container(
   key="pagina_jogos")) — os cartões e métricas do jogo (pergunta,
   pontuação, nível, resumo) ficam menores do que o resto da app. */
div[class*="st-key-pagina_jogos"] div[data-testid="stVerticalBlockBorderWrapper"] {{
    padding: 0.5rem 0.75rem !important;
}}
div[class*="st-key-pagina_jogos"] div[data-testid="stMetric"] {{
    padding: 0.35rem 0.5rem !important;
}}
div[class*="st-key-pagina_jogos"] div[data-testid="stMetricValue"] {{
    font-size: 1.3rem !important;
}}
div[class*="st-key-pagina_jogos"] div[data-testid="stMetricLabel"] p {{
    font-size: 0.75rem !important;
}}

/* Seletor de cor de cada equação (Exploração Gráfica) — o retângulo clicável
   (stColorPickerBlock) vem grande por omissão; o "width=" do widget só
   ajusta o contentor à volta, não este bloco em si. */
div[data-testid="stColorPickerBlock"] {{
    width: 22px !important;
    height: 22px !important;
    min-width: 22px !important;
    min-height: 22px !important;
    padding: 0 !important;
    border-radius: 4px !important;
}}
div[data-testid="stColorPicker"] {{
    width: fit-content !important;
}}

/* Boas-vindas na Início (etiqueta pequena acima do título + ilustração) */
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
   Responsividade — o Streamlit já empilha st.columns sozinho em ecrãs
   estreitos; aqui só se ajusta densidade/tamanho para esse caso: texto
   maior não cabe, e as caixas com altura fixa (650px, usadas no layout
   de 2 colunas de cada módulo) ficam mais baixas para não obrigar a
   tanto scroll dentro de um ecrã já pequeno.
   -------------------------------------------------------------------- */
@media (max-width: 768px) {{
    h1 {{
        font-size: 1.6rem !important;
    }}
    div[data-testid="stMainBlockContainer"] {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
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
    """Aplica o CSS partilhado por toda a app — chamar uma única vez, em
    streamlit_app.py (o markdown fica invisível, só define estilos)."""
    st.markdown(_CSS, unsafe_allow_html=True)
