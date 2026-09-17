"""Ecrã inicial: contexto do projeto e instruções de utilização."""
import streamlit as st


def render() -> None:
    st.title("🧮 Laboratório Digital de Álgebra Linear")
    st.markdown(
        """
        Bem-vindo(a)! Este laboratório digital combina representação
        **algébrica, numérica e gráfica** dos principais conteúdos de Álgebra
        Linear, com um modo passo-a-passo para evitar a "caixa preta" —
        cada operação mostra também o método de resolução, não só o
        resultado final.

        ### Módulos disponíveis
        - **Matrizes** — soma, produto escalar, produto matricial, transposição
        - **Determinantes / Inversa** — cálculo e deteção de matrizes singulares
        - **Sistemas Lineares** — resolução e interpretação gráfica
        - **Vetores** — operações e visualização 2D/3D
        - **Valores/Vetores Próprios** — cálculo e visualização da transformação
        - **Jogos e Desafios** — pratica os conteúdos de forma gamificada
        - **Conteúdo** — teoria, exemplos e figuras por tópico (estilo e-book)

        Usa o menu lateral para navegar entre módulos. Em cada módulo
        matemático, ativa o **modo passo-a-passo** para veres como se chega
        ao resultado, e experimenta arrastar o slider ou premir **Play** nos
        gráficos animados para veres o efeito de cada operação em tempo real.
        """
    )
    st.info(
        "💡 Se a app estiver lenta no teu dispositivo ou ligação à internet, "
        "ativa o **Modo leve** na barra lateral."
    )
