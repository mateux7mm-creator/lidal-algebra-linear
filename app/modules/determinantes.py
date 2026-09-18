"""Módulo Determinantes / Inversa: cálculo e deteção de matrizes singulares,
sobre um número arbitrário de matrizes nomeadas (mesmo estilo do módulo Matrizes)."""
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
from utils.visualizacao import figura_transformacao

VALORES_DEFEITO = {"A": np.array([[2.0, 1.0], [1.0, 3.0]])}


def _inicializar_estado() -> None:
    st.session_state.setdefault("determinantes_nomes", ["A"])


def _adicionar_matriz() -> None:
    nomes = st.session_state["determinantes_nomes"]
    nomes.append(chr(ord("A") + len(nomes)))


def _remover_ultima_matriz() -> None:
    nomes = st.session_state["determinantes_nomes"]
    if len(nomes) > 1:
        nome_removido = nomes.pop()
        for sufixo in ("_dados", "_versao"):
            st.session_state.pop(f"determinantes_{nome_removido}{sufixo}", None)


def render() -> None:
    cabecalho("➗ Determinantes e Matriz Inversa", "Cálculo e deteção de matrizes singulares.")
    _inicializar_estado()

    col_add, col_rem = st.columns(2)
    with col_add:
        st.button("➕ Adicionar matriz", width="stretch", on_click=_adicionar_matriz, key="determinantes_btn_add")
    with col_rem:
        st.button("➖ Remover última matriz", width="stretch", on_click=_remover_ultima_matriz,
                   disabled=len(st.session_state["determinantes_nomes"]) <= 1, key="determinantes_btn_rem")

    nomes = st.session_state["determinantes_nomes"]
    matrizes: dict[str, np.ndarray] = {}
    for nome in nomes:
        matrizes[nome] = matriz_input(f"determinantes_{nome}", titulo=f"Matriz {nome}",
                                       valor_defeito=VALORES_DEFEITO.get(nome), quadrada=True)

    st.divider()
    col_sel, col_toggle = st.columns([2, 1])
    with col_sel:
        nome_a = st.selectbox("Matriz a analisar", nomes, key="determinantes_op_nome")
    with col_toggle:
        mostrar_passo_a_passo = modo_passo_a_passo_ativo("determinantes")
    a = matrizes[nome_a]

    with st.container(border=True):
        st.markdown("##### 🔎 Matriz escolhida")
        st.caption(f"Matriz {nome_a}")
        st.latex(sp.latex(sp.Matrix(np.round(a, 4).tolist())))

    a_sp = simbolico.para_sympy(a)
    det_sp, passos_det = simbolico.determinante(a_sp)
    inversa_sp, passos_inv = simbolico.inversa(a_sp)

    with st.container(border=True):
        st.markdown("##### ✅ Resultado")
        col_det, col_inv = st.columns(2)
        with col_det:
            st.metric("Determinante", f"{float(det_sp):.4g}")
        with col_inv:
            if inversa_sp is None:
                st.warning("Matriz singular — não tem inversa.")
            else:
                st.caption("Matriz inversa")
                st.latex(sp.latex(inversa_sp))

    if mostrar_passo_a_passo:
        mostrar_passos(passos_det + passos_inv)

    if a.shape == (2, 2):
        st.divider()
        st.markdown("##### 🔎 Ver a matriz a tornar-se singular")
        posicoes = {"a11": (0, 0), "a12": (0, 1), "a21": (1, 0), "a22": (1, 1)}
        col_entrada, col_valor = st.columns(2)
        with col_entrada:
            rotulo_entrada = st.selectbox("Entrada a variar", list(posicoes.keys()), index=3)
        posicao = posicoes[rotulo_entrada]
        with col_valor:
            valor_entrada = st.number_input(f"Valor de {rotulo_entrada}", value=float(a[posicao]), step=0.5)
        matriz_variada = simbolico.matriz_com_entrada_variavel(a, posicao, valor_entrada)
        st.plotly_chart(figura_transformacao(matriz_variada, mostrar_area=True,
                                              modo_leve=modo_leve_da_sessao()), width="stretch")
