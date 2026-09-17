"""Módulo Vetores: operações vetoriais e visualização 2D/3D."""
import numpy as np
import streamlit as st

from utils.componentes import (
    modo_leve_da_sessao,
    modo_passo_a_passo_ativo,
    mostrar_passos,
    vetor_input,
)
from utils.simbolico import Passo
from utils.visualizacao import figura_vetor_escalado, figura_vetores_2d, figura_vetores_3d, n_frames

CORES = ["#e15759", "#4e79a7"]


def render() -> None:
    st.header("➡️ Vetores")
    mostrar_passo_a_passo = modo_passo_a_passo_ativo("vetores")
    dimensao = st.radio("Dimensão", [2, 3], horizontal=True, format_func=lambda d: f"{d}D")

    col_a, col_b = st.columns(2)
    with col_a:
        v = vetor_input("vetores_v", dimensao=dimensao, titulo="Vetor v",
                         valor_defeito=np.array([2.0, 1.0] if dimensao == 2 else [2.0, 1.0, 0.0]))
    with col_b:
        w = vetor_input("vetores_w", dimensao=dimensao, titulo="Vetor w",
                         valor_defeito=np.array([1.0, 2.0] if dimensao == 2 else [0.0, 1.0, 2.0]))

    operacoes = ["Soma", "Produto interno", "Norma", "Teste de ortogonalidade"]
    if dimensao == 3:
        operacoes.insert(2, "Produto externo")
    operacao = st.selectbox("Operação", operacoes)

    passos: list[Passo] = []
    if operacao == "Soma":
        st.write("v + w =", v + w)
        passos = [Passo("Somar componente a componente", "(v + w)_i = v_i + w_i")]
    elif operacao == "Produto interno":
        st.write("v · w =", float(np.dot(v, w)))
        passos = [Passo("Somar os produtos das componentes", "v · w = Σ v_i · w_i")]
    elif operacao == "Produto externo":
        st.write("v × w =", np.cross(v, w))
        passos = [Passo("Calcular o produto vetorial", "v × w é perpendicular a v e a w (só definido em 3D)")]
    elif operacao == "Norma":
        st.write("‖v‖ =", float(np.linalg.norm(v)))
        passos = [Passo("Raiz quadrada da soma dos quadrados", "‖v‖ = √(Σ v_i²)")]
    else:  # Teste de ortogonalidade
        produto = float(np.dot(v, w))
        ortogonais = abs(produto) < 1e-9
        st.write(f"v · w = {produto:.4g} → {'✅ ortogonais' if ortogonais else '❌ não ortogonais'}")
        passos = [Passo("Calcular v · w", "Se v · w = 0, os vetores são ortogonais.")]

    if mostrar_passo_a_passo and passos:
        mostrar_passos(passos)

    st.subheader("Visualização")
    if dimensao == 2:
        fig = figura_vetores_2d([("v", v, CORES[0]), ("w", w, CORES[1])])
    else:
        fig = figura_vetores_3d([("v", v, CORES[0]), ("w", w, CORES[1])])
    st.plotly_chart(fig, width="stretch")

    st.subheader("Ver k·v em tempo real")
    valores_k = np.linspace(-2, 2, n_frames(modo_leve_da_sessao()))
    fig_anim = figura_vetor_escalado(v, valores_k, modo_leve=modo_leve_da_sessao())
    st.plotly_chart(fig_anim, width="stretch")
