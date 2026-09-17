"""Ecrã inicial: contexto do projeto e instruções de utilização."""
import streamlit as st

MODULOS = [
    ("🔢", "Matrizes", "Soma, produto escalar, produto matricial e transposição."),
    ("➗", "Determinantes / Inversa", "Cálculo e deteção de matrizes singulares."),
    ("📐", "Sistemas Lineares", "Resolução e interpretação gráfica."),
    ("➡️", "Vetores", "Operações e visualização 2D/3D."),
    ("🌀", "Valores/Vetores Próprios", "Cálculo e visualização da transformação."),
    ("🎮", "Jogos e Desafios", "Pratica os conteúdos de forma gamificada."),
    ("📖", "Conteúdo", "Teoria, exemplos e figuras por tópico."),
]


def render() -> None:
    st.title("🧮 Laboratório Digital de Álgebra Linear")
    st.caption(
        "Representação algébrica, numérica e gráfica dos principais conteúdos de "
        "Álgebra Linear — sem \"caixa preta\": cada operação mostra também o método "
        "de resolução, não só o resultado final."
    )
    st.divider()

    st.markdown("#### Módulos disponíveis")
    colunas = st.columns(4)
    for i, (icone, nome, descricao) in enumerate(MODULOS):
        with colunas[i % 4]:
            with st.container(border=True):
                st.markdown(f"##### {icone} {nome}")
                st.caption(descricao)

    st.divider()
    st.markdown(
        "Usa o menu lateral para navegar entre módulos. Em cada módulo matemático, "
        "ativa o **modo passo-a-passo** para veres como se chega ao resultado, e "
        "experimenta arrastar o slider ou premir **▶ Play** nos gráficos animados "
        "para veres o efeito de cada operação em tempo real."
    )
    st.info("💡 Se a app estiver lenta no teu dispositivo ou ligação à internet, "
            "ativa o **Modo leve** na barra lateral.")
