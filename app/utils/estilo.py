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
</style>
"""


def injetar_css() -> None:
    """Aplica o CSS partilhado por toda a app — chamar uma única vez, em
    streamlit_app.py (o markdown fica invisível, só define estilos)."""
    st.markdown(_CSS, unsafe_allow_html=True)
