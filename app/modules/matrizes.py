"""Módulo Matrizes: soma, produto escalar, produto matricial, transposição."""
import numpy as np
import sympy as sp
import streamlit as st

from utils import simbolico
from utils.componentes import (
    matriz_input,
    modo_leve_da_sessao,
    modo_passo_a_passo_ativo,
    mostrar_passos,
    mostrar_resultado,
)
from utils.visualizacao import figura_transformacao_parametrizada, n_frames

OPERACOES = ["Soma", "Produto escalar", "Produto matricial", "Transposição"]


def render() -> None:
    st.header("🔢 Matrizes")
    mostrar_passo_a_passo = modo_passo_a_passo_ativo("matrizes")
    operacao = st.selectbox("Operação", OPERACOES)

    col_a, col_b = st.columns(2)
    with col_a:
        a = matriz_input("matrizes_A", titulo="Matriz A",
                          valor_defeito=np.array([[1.0, 2.0], [3.0, 4.0]]))
    b = None
    k = 1.0
    if operacao in ("Soma", "Produto matricial"):
        with col_b:
            b = matriz_input("matrizes_B", titulo="Matriz B",
                              valor_defeito=np.array([[0.0, 1.0], [1.0, 0.0]]))
    elif operacao == "Produto escalar":
        with col_b:
            k = st.number_input("Escalar k", value=2.0, step=0.5)

    a_sp = simbolico.para_sympy(a)

    try:
        if operacao == "Soma":
            resultado_sp, passos = simbolico.somar_matrizes(a_sp, simbolico.para_sympy(b))
        elif operacao == "Produto escalar":
            resultado_sp, passos = simbolico.multiplicar_escalar(k, a_sp)
        elif operacao == "Produto matricial":
            resultado_sp, passos = simbolico.multiplicar_matrizes(a_sp, simbolico.para_sympy(b))
        else:  # Transposição
            resultado_sp, passos = simbolico.transpor(a_sp)
    except ValueError as erro:
        st.error(str(erro))
        return

    mostrar_resultado(numerico=simbolico.para_numpy(resultado_sp), simbolico_latex=sp.latex(resultado_sp))
    if mostrar_passo_a_passo:
        mostrar_passos(passos)

    if operacao == "Produto escalar" and a.shape == (2, 2):
        st.subheader("Ver o efeito de k·A em tempo real")
        valores_k = np.linspace(-2, 2, n_frames(modo_leve_da_sessao()))
        fig = figura_transformacao_parametrizada(
            calcular_matriz=lambda t: t * a,
            valores_parametro=valores_k,
            rotulo_parametro="k",
            modo_leve=modo_leve_da_sessao(),
        )
        st.plotly_chart(fig, width="stretch")
