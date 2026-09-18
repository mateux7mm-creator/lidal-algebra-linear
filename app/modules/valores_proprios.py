"""Módulo Valores/Vetores Próprios: cálculo e visualização da transformação
linear, sobre um número arbitrário de matrizes nomeadas."""
import numpy as np
import sympy as sp
import streamlit as st

from utils import simbolico
from utils.componentes import (
    cabecalho,
    matriz_input,
    modo_leve_da_sessao,
    modo_passo_a_passo_ativo,
    mostrar_passos,
)
from utils.visualizacao import figura_transformacao_parametrizada

VALORES_DEFEITO = {"A": np.array([[2.0, 0.0], [0.0, 3.0]])}


def _inicializar_estado() -> None:
    st.session_state.setdefault("valores_proprios_nomes", ["A"])


def _adicionar_matriz() -> None:
    nomes = st.session_state["valores_proprios_nomes"]
    nomes.append(chr(ord("A") + len(nomes)))


def _remover_ultima_matriz() -> None:
    nomes = st.session_state["valores_proprios_nomes"]
    if len(nomes) > 1:
        nome_removido = nomes.pop()
        for sufixo in ("_dados", "_versao"):
            st.session_state.pop(f"valores_proprios_{nome_removido}{sufixo}", None)


def render() -> None:
    cabecalho("🌀 Valores e Vetores Próprios", "Cálculo e visualização da transformação linear.")
    _inicializar_estado()

    col_add, col_rem = st.columns(2)
    with col_add:
        st.button("➕ Adicionar matriz", width="stretch", on_click=_adicionar_matriz,
                   key="valores_proprios_btn_add")
    with col_rem:
        st.button("➖ Remover última matriz", width="stretch", on_click=_remover_ultima_matriz,
                   disabled=len(st.session_state["valores_proprios_nomes"]) <= 1,
                   key="valores_proprios_btn_rem")

    nomes = st.session_state["valores_proprios_nomes"]
    matrizes: dict[str, np.ndarray] = {}
    for nome in nomes:
        matrizes[nome] = matriz_input(f"valores_proprios_{nome}", titulo=f"Matriz {nome}",
                                       valor_defeito=VALORES_DEFEITO.get(nome), quadrada=True)

    st.divider()
    col_sel, col_toggle = st.columns([2, 1])
    with col_sel:
        nome_a = st.selectbox("Matriz a analisar", nomes, key="valores_proprios_op_nome")
    with col_toggle:
        mostrar_passo_a_passo = modo_passo_a_passo_ativo("valores_proprios")
    a = matrizes[nome_a]

    with st.container(border=True):
        st.markdown("##### 🔎 Matriz escolhida")
        st.caption(f"Matriz {nome_a}")
        st.latex(sp.latex(sp.Matrix(np.round(a, 4).tolist())))

    a_sp = simbolico.para_sympy(a)
    valores, vetores, passos_eigen = simbolico.eigen(a_sp)
    (diagonalizacao, passos_diag) = simbolico.diagonalizar(a_sp)

    with st.container(border=True):
        st.markdown("##### ✅ Resultado")
        st.markdown("**Valores próprios:** " + ", ".join(sp.latex(v) for v in valores))
        if diagonalizacao is not None:
            p, d = diagonalizacao
            st.caption("Diagonalização A = P·D·P⁻¹")
            st.latex(f"P = {sp.latex(p)}, \\quad D = {sp.latex(d)}")

    if mostrar_passo_a_passo:
        mostrar_passos(passos_eigen + passos_diag)

    if a.shape == (2, 2):
        st.divider()
        st.markdown("##### 🔎 Ver a transformação a construir-se")
        valores_np, vetores_np = np.linalg.eig(a)
        direcoes = []
        for i in range(len(valores_np)):
            if abs(valores_np[i].imag) < 1e-9:
                direcoes.append(np.real(vetores_np[:, i]))
        st.caption("Arrasta o slider ou carrega em ▶ Play para ver a transformação a construir-se "
                   "(t: 0 = identidade, 1 = matriz completa).")
        fig = figura_transformacao_parametrizada(
            lambda t: (1 - t) * np.eye(2) + t * a, np.linspace(0, 1, 30), rotulo_parametro="t",
            direcoes_proprias=direcoes or None, modo_leve=modo_leve_da_sessao(),
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("A visualização gráfica 3×3 ficará disponível numa iteração seguinte "
                 "— os valores/vetores próprios acima já estão corretos para 3D.")
