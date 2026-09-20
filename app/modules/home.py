"""Ecrã inicial: boas-vindas, contexto do projeto e instruções de utilização."""
import streamlit as st

MODULOS = [
    ("🔢", "Matrizes", "Soma, produto escalar, produto matricial e transposição."),
    ("➗", "Determinantes / Inversa", "Cálculo e deteção de matrizes singulares."),
    ("📐", "Sistemas Lineares", "Resolução e interpretação gráfica."),
    ("🧭", "Exploração Gráfica", "Gráficos de equações livres, estilo GeoGebra."),
    ("➡️", "Vetores", "Operações e visualização 2D/3D."),
    ("🌀", "Valores/Vetores Próprios", "Cálculo e visualização da transformação."),
    ("🎮", "Jogos e Desafios", "Pratica os conteúdos de forma gamificada."),
    ("📖", "Conteúdo", "Teoria, exemplos e figuras por tópico."),
]

# Ilustração decorativa (livros + símbolos matemáticos) desenhada inteiramente
# em SVG inline — sem ficheiro de imagem externo, para a app continuar a
# funcionar offline (incl. no executável desktop) e sem depender de nenhuma
# fonte externa. As cores replicam a paleta já usada nos gráficos (CORES_VETORES
# em visualizacao.py) e o tema em .streamlit/config.toml.
_ILUSTRACAO_SVG = """
<div class="hero-ilustracao">
<svg viewBox="0 0 360 300" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Ilustração de livros e símbolos matemáticos">
  <g transform="translate(40,150)">
    <rect x="0" y="80" width="220" height="34" rx="5" fill="#f28e2b" transform="rotate(-3 110 97)"/>
    <rect x="14" y="50" width="192" height="32" rx="5" fill="#4e79a7" transform="rotate(2 110 66)"/>
    <rect x="10" y="20" width="172" height="32" rx="5" fill="#4F46E5" transform="rotate(-1 96 36)"/>
    <rect x="150" y="6" width="14" height="32" fill="#e15759" transform="rotate(-1 157 22)"/>
  </g>

  <circle cx="70" cy="60" r="26" fill="#ffffff" stroke="#4F46E5" stroke-width="2"/>
  <text x="70" y="70" font-size="26" font-family="Georgia, serif" text-anchor="middle" fill="#4F46E5">&#960;</text>

  <circle cx="152" cy="34" r="22" fill="#4F46E5"/>
  <text x="152" y="43" font-size="22" font-family="Georgia, serif" text-anchor="middle" fill="#ffffff">&#931;</text>

  <circle cx="232" cy="56" r="24" fill="#ffffff" stroke="#59a14f" stroke-width="2"/>
  <text x="232" y="66" font-size="24" font-family="Georgia, serif" text-anchor="middle" fill="#59a14f">&#8730;</text>

  <circle cx="302" cy="104" r="22" fill="#ffffff" stroke="#b07aa1" stroke-width="2"/>
  <text x="302" y="113" font-size="22" font-family="Georgia, serif" text-anchor="middle" fill="#b07aa1">&#8747;</text>

  <defs>
    <marker id="hero-seta" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#4e79a7"/>
    </marker>
  </defs>
  <line x1="178" y1="152" x2="220" y2="112" stroke="#4e79a7" stroke-width="3" marker-end="url(#hero-seta)"/>

  <text x="88" y="148" font-size="46" font-weight="700" fill="#4F46E5">[</text>
  <circle cx="112" cy="124" r="3" fill="#4F46E5"/>
  <circle cx="132" cy="124" r="3" fill="#4F46E5"/>
  <circle cx="112" cy="140" r="3" fill="#4F46E5"/>
  <circle cx="132" cy="140" r="3" fill="#4F46E5"/>
  <text x="140" y="148" font-size="46" font-weight="700" fill="#4F46E5">]</text>
</svg>
</div>
"""


def render() -> None:
    col_texto, col_imagem = st.columns([3, 2])
    with col_texto:
        st.markdown('<p class="boas-vindas-etiqueta">👋 Bem-vindo(a) ao</p>', unsafe_allow_html=True)
        st.title("🧮 Laboratório Digital de Álgebra Linear")
        st.markdown(
            "Explora, calcula e visualiza os principais temas de Álgebra Linear — "
            "sem \"caixa preta\": cada operação mostra também o método de resolução, "
            "não só o resultado final."
        )
    with col_imagem:
        st.markdown(_ILUSTRACAO_SVG, unsafe_allow_html=True)

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
