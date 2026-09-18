"""Ponto de entrada da aplicação: navegação entre os módulos do laboratório."""
import streamlit as st

from modules import conteudo, determinantes, exploracao, home, jogos, matrizes, sistemas, valores_proprios, vetores
from utils.componentes import modo_leve_ativo
from utils.estilo import injetar_css

st.set_page_config(
    page_title="Laboratório Digital de Álgebra Linear",
    page_icon="🧮",
    layout="wide",
)

injetar_css()
modo_leve_ativo()

paginas = [
    st.Page(home.render, title="Início", icon="🏠", url_path="inicio", default=True),
    st.Page(matrizes.render, title="Matrizes", icon="🔢", url_path="matrizes"),
    st.Page(determinantes.render, title="Determinantes / Inversa", icon="➗", url_path="determinantes"),
    st.Page(sistemas.render, title="Sistemas Lineares", icon="📐", url_path="sistemas"),
    st.Page(exploracao.render, title="Exploração Gráfica", icon="🧭", url_path="exploracao"),
    st.Page(vetores.render, title="Vetores", icon="➡️", url_path="vetores"),
    st.Page(valores_proprios.render, title="Valores/Vetores Próprios", icon="🌀", url_path="valores-proprios"),
    st.Page(jogos.render, title="Jogos e Desafios", icon="🎮", url_path="jogos"),
    st.Page(conteudo.render, title="Conteúdo", icon="📖", url_path="conteudo"),
]

st.navigation(paginas).run()
