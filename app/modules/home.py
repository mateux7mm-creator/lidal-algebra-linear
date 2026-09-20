"""Ecrã inicial do Laboratório Interativo de Álgebra Linear:
Boas-vindas, recursos em largura total horizontal, módulos principais e secção extra (jogos, exploração, conteúdo).
"""
from pathlib import Path
import streamlit as st

_ASSETS_DIR = Path(__file__).parent.parent / "assets"

MODULOS_PRINCIPAIS = [
    (
        "🔢",
        "Matrizes",
        "Soma, produto escalar, produto matricial, transposição e propriedades das operações.",
        "badge-indigo",
        "Base Linear",
    ),
    (
        "➗",
        "Determinantes / Inversa",
        "Cálculo de determinantes de ordem 2x2 a 5x5, cofatores e verificação da matriz inversa.",
        "badge-cyan",
        "Simbólico",
    ),
    (
        "📐",
        "Sistemas Lineares",
        "Resolução completa por Eliminação de Gauss, Regra de Cramer e interpretação gráfica.",
        "badge-emerald",
        "Passo a Passo",
    ),
    (
        "➡️",
        "Vetores",
        "Operações vetoriais em 2D/3D, produto interno, externo e projeções com gráficos em Plotly.",
        "badge-indigo",
        "Visual 3D",
    ),
    (
        "🌀",
        "Valores/Vetores Próprios",
        "Cálculo de autovalores, autovetores e animação interativa de transformação no espaço.",
        "badge-cyan",
        "Avançado 3D",
    ),
]

MODULOS_EXTRAS = [
    (
        "🧭",
        "Exploração Gráfica",
        "Gráficos interativos de equações no plano cartesiano, interseções e exploração estilo GeoGebra.",
        "badge-amber",
        "GeoGebra 2D",
    ),
    (
        "🎮",
        "Jogos e Desafios",
        "Pratica os conceitos de forma gamificada com níveis de dificuldade e registo de pontuação.",
        "badge-emerald",
        "Gamificado",
    ),
    (
        "📖",
        "Conteúdo",
        "Biblioteca pedagógica com fundamentação teórica, definições, fórmulas e exemplos guiados.",
        "badge-amber",
        "Teoria & Fórmulas",
    ),
]


def _obter_caminho_asset(nome_ficheiro: str) -> str | None:
    caminho = _ASSETS_DIR / nome_ficheiro
    return str(caminho) if caminho.exists() else None


def render() -> None:
    # ------------------------------------------------------------------
    # BANNER HERO PRINCIPAL (LARGURA TOTAL)
    # ------------------------------------------------------------------
    st.markdown(
        """
        <div class="hero-card">
            <div class="lab-badge">
                <span>🔬 LABORATÓRIO INTERATIVO VIRTUAL</span>
            </div>
            <h1 class="gradient-text" style="font-size: 2.6rem; margin-bottom: 0.2rem;">
                Laboratório Interativo de Álgebra Linear
            </h1>
            <p style="font-size: 0.9rem; color: #4F46E5; font-weight: 700; margin-bottom: 0.7rem; letter-spacing: 0.01em;">
                Álgebra Linear Educativa · Desenvolvido pelo Grupo 8 / UC: Tecnologias Educativas Aplicadas ao Ensino da Matemática - ISCED - Huíla/2026
            </p>
            <p class="hero-sub" style="margin-top: 0.2rem;">
                Calcula, visualiza e compreende os conceitos de Álgebra Linear sem "caixa preta" — 
                resoluções passo-a-passo detalhadas e animações interativas 2D/3D em tempo real.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # RECURSOS DO LABORATÓRIO (PREENCHE O ECRÃ INTEIRO NA HORIZONTAL)
    # ------------------------------------------------------------------
    st.markdown(
        """
        <h3 style="color: #1E1B4B; font-weight: 700; margin-bottom: 0.8rem;">
            ⚡ Recursos do Laboratório
        </h3>
        """,
        unsafe_allow_html=True,
    )

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.markdown(
            """
            <div class="stat-pill">
                <span class="stat-icon">🧮</span>
                <div>
                    <div class="stat-num">Módulos de Cálculo</div>
                    <div class="stat-label">Cálculo & Exploração</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r2:
        st.markdown(
            """
            <div class="stat-pill">
                <span class="stat-icon">🔍</span>
                <div>
                    <div class="stat-num">Passo a Passo</div>
                    <div class="stat-label">Resoluções Detalhadas</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r3:
        st.markdown(
            """
            <div class="stat-pill">
                <span class="stat-icon">🧭</span>
                <div>
                    <div class="stat-num">Gráficos 2D / 3D</div>
                    <div class="stat-label">Animações em Tempo Real</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with r4:
        st.markdown(
            """
            <div class="stat-pill">
                <span class="stat-icon">🎮</span>
                <div>
                    <div class="stat-num">Modo Desafio</div>
                    <div class="stat-label">Prática Gamificada</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ------------------------------------------------------------------
    # VITRINE DE OBJETOS MATEMÁTICOS EM 3D
    # ------------------------------------------------------------------
    st.markdown(
        """
        <h3 style="color: #1E1B4B; font-weight: 700; text-align: center; margin-bottom: 0.2rem;">
            📐 Exploração de Objetos Matemáticos em 3D
        </h3>
        <p style="text-align: center; color: #64748B; font-size: 0.95rem; margin-bottom: 1.5rem;">
            Visualização dos conceitos geométricos e vetoriais em tempo real
        </p>
        """,
        unsafe_allow_html=True,
    )

    obj_col1, obj_col2, obj_col3 = st.columns(3)

    with obj_col1:
        with st.container(border=True):
            img_p1 = _obter_caminho_asset("matrix_object_3d.jpg")
            if img_p1:
                st.image(img_p1, width="stretch")
            st.markdown(
                """
                <h5 style="color: #1E1B4B; font-weight: 700; margin-top: 0.4rem;">Matrizes & Espaço Vetorial</h5>
                <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 0;">
                    Representação de transformações lineares, espaços nulos e imagem de matrizes.
                </p>
                """,
                unsafe_allow_html=True,
            )

    with obj_col2:
        with st.container(border=True):
            img_p2 = _obter_caminho_asset("vector_space_3d.jpg")
            if img_p2:
                st.image(img_p2, width="stretch")
            st.markdown(
                """
                <h5 style="color: #1E1B4B; font-weight: 700; margin-top: 0.4rem;">Vetores & Geometria 3D</h5>
                <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 0;">
                    Operações vetoriais com gráficos rotativos em 3D, produto vetorial e projeções.
                </p>
                """,
                unsafe_allow_html=True,
            )

    with obj_col3:
        with st.container(border=True):
            img_p3 = _obter_caminho_asset("eigen_sphere_3d.jpg")
            if img_p3:
                st.image(img_p3, width="stretch")
            st.markdown(
                """
                <h5 style="color: #1E1B4B; font-weight: 700; margin-top: 0.4rem;">Autovalores & Autovetores</h5>
                <p style="color: #64748B; font-size: 0.85rem; margin-bottom: 0;">
                    Deformação de superfícies esféricas e direções invariantes sob transformação.
                </p>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # ------------------------------------------------------------------
    # 1. MÓDULOS INTERATIVOS DISPONÍVEIS (PRINCIPAIS DE CÁLCULO)
    # ------------------------------------------------------------------
    st.markdown(
        """
        <h3 style="color: #1E1B4B; font-weight: 700; margin-bottom: 0.2rem;">
            🚀 Módulos Interativos Disponíveis
        </h3>
        <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 1.2rem;">
            Ferramentas de cálculo e análise de Álgebra Linear
        </p>
        """,
        unsafe_allow_html=True,
    )

    # 3 cartões na primeira linha, 2 cartões na segunda linha (com mesma altura)
    linha1_cols = st.columns(3)
    for idx, (icone, nome, descricao, classe_badge, texto_badge) in enumerate(MODULOS_PRINCIPAIS[:3]):
        with linha1_cols[idx]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div>
                        <div class="module-header-box">
                            <span style="font-size: 1.6rem;">{icone}</span>
                            <span class="module-badge {classe_badge}">{texto_badge}</span>
                        </div>
                        <h4 style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.1rem; color: #1E1B4B; margin-bottom: 0.4rem;">
                            {nome}
                        </h4>
                        <p style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 0;">
                            {descricao}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<div style='margin-top: 0.6rem;'></div>", unsafe_allow_html=True)

    linha2_cols = st.columns(3)
    for idx, (icone, nome, descricao, classe_badge, texto_badge) in enumerate(MODULOS_PRINCIPAIS[3:]):
        with linha2_cols[idx]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div>
                        <div class="module-header-box">
                            <span style="font-size: 1.6rem;">{icone}</span>
                            <span class="module-badge {classe_badge}">{texto_badge}</span>
                        </div>
                        <h4 style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.1rem; color: #1E1B4B; margin-bottom: 0.4rem;">
                            {nome}
                        </h4>
                        <p style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 0;">
                            {descricao}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()

    # ------------------------------------------------------------------
    # 2. SECÇÃO EXTRA: FERRAMENTAS COMPLEMENTARES, JOGOS E CONTEÚDO
    # ------------------------------------------------------------------
    st.markdown(
        """
        <h3 style="color: #1E1B4B; font-weight: 700; margin-bottom: 0.2rem;">
            ⭐ Secção Extra: Ferramentas Complementares, Jogos e Conteúdo
        </h3>
        <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 1.2rem;">
            Visualização gráfica livre, prática gamificada e biblioteca teórica
        </p>
        """,
        unsafe_allow_html=True,
    )

    extra_cols = st.columns(3)
    for idx, (icone, nome, descricao, classe_badge, texto_badge) in enumerate(MODULOS_EXTRAS):
        with extra_cols[idx]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div>
                        <div class="module-header-box">
                            <span style="font-size: 1.6rem;">{icone}</span>
                            <span class="module-badge {classe_badge}">{texto_badge}</span>
                        </div>
                        <h4 style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.1rem; color: #1E1B4B; margin-bottom: 0.4rem;">
                            {nome}
                        </h4>
                        <p style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 0;">
                            {descricao}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()

    # ------------------------------------------------------------------
    # DICA E GUIA DE UTILIZAÇÃO
    # ------------------------------------------------------------------
    st.info(
        "💡 **Como navegar no Laboratório:** Usa o menu lateral esquerdo para alternar entre os módulos. "
        "Dentro de cada módulo, podes ativar o **Modo Passo-a-passo** para veres as resoluções detalhadas "
        "ou ajustar parâmetros nos gráficos interativos."
    )

    st.markdown(
        """
        <div style="text-align: center; padding: 1.2rem; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; margin-top: 1rem;">
            <p style="font-size: 0.85rem; color: #475569; font-weight: 600; margin-bottom: 0.2rem;">
                🎓 <b>Laboratório Interativo de Álgebra Linear Educativa</b>
            </p>
            <p style="font-size: 0.78rem; color: #64748B; margin-bottom: 0;">
                Desenvolvido pelo Grupo 8 / UC: Tecnologias Educativas Aplicadas ao Ensino da Matemática - ISCED - Huíla/2026
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


