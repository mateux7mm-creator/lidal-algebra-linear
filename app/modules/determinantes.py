"""Módulo Determinantes / Inversa: cálculo e deteção de matrizes singulares."""
import numpy as np
import sympy as sp
import streamlit as st

from utils import simbolico
from utils.componentes import (
    matriz_input,
    modo_leve_da_sessao,
    modo_passo_a_passo_ativo,
    mostrar_passos,
)
from utils.visualizacao import figura_transformacao_parametrizada, n_frames


def render() -> None:
    st.header("➗ Determinantes e Matriz Inversa")
    mostrar_passo_a_passo = modo_passo_a_passo_ativo("determinantes")

    dimensao = st.radio("Dimensão da matriz", [2, 3], horizontal=True)
    a = matriz_input("determinantes_A", linhas=dimensao, colunas=dimensao, titulo="Matriz A",
                      valor_defeito=np.array([[2.0, 1.0], [1.0, 3.0]]) if dimensao == 2
                      else np.array([[2.0, 1.0, 0.0], [1.0, 3.0, 1.0], [0.0, 1.0, 2.0]]))

    a_sp = simbolico.para_sympy(a)
    det_sp, passos_det = simbolico.determinante(a_sp)
    inversa_sp, passos_inv = simbolico.inversa(a_sp)

    st.metric("Determinante", f"{float(det_sp):.4g}")
    if inversa_sp is None:
        st.warning("A matriz é singular (det = 0) — não tem inversa.")
    else:
        st.markdown("**Matriz inversa**")
        st.latex(sp.latex(inversa_sp))

    if mostrar_passo_a_passo:
        mostrar_passos(passos_det + passos_inv)

    if dimensao == 2:
        st.subheader("Ver a matriz a tornar-se singular, em tempo real")
        posicoes = {"a11": (0, 0), "a12": (0, 1), "a21": (1, 0), "a22": (1, 1)}
        rotulo_entrada = st.selectbox("Entrada a variar", list(posicoes.keys()), index=3)
        posicao = posicoes[rotulo_entrada]
        valores = np.linspace(-3, 3, n_frames(modo_leve_da_sessao()))
        fig = figura_transformacao_parametrizada(
            calcular_matriz=lambda x: simbolico.matriz_com_entrada_variavel(a, posicao, x),
            valores_parametro=valores,
            rotulo_parametro=rotulo_entrada,
            mostrar_area=True,
            modo_leve=modo_leve_da_sessao(),
        )
        st.plotly_chart(fig, width="stretch")
