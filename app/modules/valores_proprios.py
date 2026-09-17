"""Módulo Valores/Vetores Próprios: cálculo e visualização da transformação linear."""
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
    st.header("🌀 Valores e Vetores Próprios")
    mostrar_passo_a_passo = modo_passo_a_passo_ativo("valores_proprios")

    dimensao = st.radio("Dimensão da matriz", [2, 3], horizontal=True)
    a = matriz_input("valores_proprios_A", linhas=dimensao, colunas=dimensao, titulo="Matriz A",
                      valor_defeito=np.array([[2.0, 0.0], [0.0, 3.0]]) if dimensao == 2
                      else np.array([[2.0, 0.0, 0.0], [0.0, 3.0, 0.0], [0.0, 0.0, 1.0]]))

    a_sp = simbolico.para_sympy(a)
    valores, vetores, passos_eigen = simbolico.eigen(a_sp)
    (diagonalizacao, passos_diag) = simbolico.diagonalizar(a_sp)

    st.markdown("**Valores próprios:** " + ", ".join(sp.latex(v) for v in valores))
    if diagonalizacao is not None:
        p, d = diagonalizacao
        st.markdown("**Diagonalização A = P·D·P⁻¹**")
        st.latex(f"P = {sp.latex(p)}, \\quad D = {sp.latex(d)}")

    if mostrar_passo_a_passo:
        mostrar_passos(passos_eigen + passos_diag)

    if dimensao == 2:
        st.subheader("Ver a transformação a construir-se em tempo real")
        valores_np, vetores_np = np.linalg.eig(a)
        direcoes = []
        for i in range(len(valores_np)):
            if abs(valores_np[i].imag) < 1e-9:
                direcoes.append(np.real(vetores_np[:, i]))
        valores_t = np.linspace(0, 1, n_frames(modo_leve_da_sessao()))
        fig = figura_transformacao_parametrizada(
            calcular_matriz=lambda t: (1 - t) * np.eye(2) + t * a,
            valores_parametro=valores_t,
            rotulo_parametro="t",
            direcoes_proprias=direcoes or None,
            modo_leve=modo_leve_da_sessao(),
        )
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("A visualização gráfica 3×3 ficará disponível numa iteração seguinte "
                 "— os valores/vetores próprios acima já estão corretos para 3D.")
