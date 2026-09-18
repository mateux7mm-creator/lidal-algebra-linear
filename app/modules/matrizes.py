"""Módulo Matrizes: soma, produto escalar, produto matricial, transposição,
escalonamento e inversa — sobre um número arbitrário de matrizes nomeadas."""
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
    mostrar_resultado,
)
from utils.visualizacao import figura_transformacao

OPERACOES_2_MATRIZES = ["Soma", "Produto matricial"]
OPERACOES_1_MATRIZ = ["Produto escalar", "Transposição", "Escalonamento", "Inversa"]
TODAS_OPERACOES = OPERACOES_2_MATRIZES + OPERACOES_1_MATRIZ

VALORES_DEFEITO = {
    "A": np.array([[1.0, 2.0], [3.0, 4.0]]),
    "B": np.array([[0.0, 1.0], [1.0, 0.0]]),
}


def _inicializar_estado() -> None:
    st.session_state.setdefault("matrizes_nomes", ["A", "B"])


def _adicionar_matriz() -> None:
    nomes = st.session_state["matrizes_nomes"]
    nomes.append(chr(ord("A") + len(nomes)))


def _remover_ultima_matriz() -> None:
    nomes = st.session_state["matrizes_nomes"]
    if len(nomes) > 1:
        nome_removido = nomes.pop()
        for sufixo in ("_dados", "_versao"):
            st.session_state.pop(f"matrizes_{nome_removido}{sufixo}", None)


def render() -> None:
    cabecalho("🔢 Matrizes",
              "Soma, produto escalar, produto matricial, transposição, escalonamento e inversa.")
    _inicializar_estado()

    col_add, col_rem = st.columns(2)
    with col_add:
        st.button("➕ Adicionar matriz", width="stretch", on_click=_adicionar_matriz)
    with col_rem:
        st.button("➖ Remover última matriz", width="stretch", on_click=_remover_ultima_matriz,
                   disabled=len(st.session_state["matrizes_nomes"]) <= 1)

    nomes = st.session_state["matrizes_nomes"]
    matrizes: dict[str, np.ndarray] = {}
    for nome in nomes:
        matrizes[nome] = matriz_input(f"matrizes_{nome}", titulo=f"Matriz {nome}",
                                       valor_defeito=VALORES_DEFEITO.get(nome))

    st.divider()
    col_operacao, col_toggle = st.columns([2, 1])
    with col_operacao:
        operacao = st.selectbox("Escolher operação", TODAS_OPERACOES)
    with col_toggle:
        mostrar_passo_a_passo = modo_passo_a_passo_ativo("matrizes")

    k = None
    if operacao in OPERACOES_2_MATRIZES:
        if len(nomes) < 2:
            st.warning("Esta operação precisa de pelo menos 2 matrizes — adiciona outra acima.")
            return
        col1, col2 = st.columns(2)
        with col1:
            nome_a = st.selectbox("Matriz 1", nomes, index=0, key="matrizes_op_nome1")
        with col2:
            nome_b = st.selectbox("Matriz 2", nomes, index=min(1, len(nomes) - 1), key="matrizes_op_nome2")
        a, b = matrizes[nome_a], matrizes[nome_b]
    else:
        nome_a = st.selectbox("Matriz", nomes, key="matrizes_op_nome_unica")
        a, b = matrizes[nome_a], None
        if operacao == "Produto escalar":
            st.markdown("**Escalar k**")
            k = st.number_input("k", value=2.0, step=0.5, label_visibility="collapsed")

    latex_a = sp.latex(sp.Matrix(np.round(a, 4).tolist()))
    latex_b = sp.latex(sp.Matrix(np.round(b, 4).tolist())) if b is not None else None
    if operacao == "Soma":
        latex_operandos = f"{latex_a} + {latex_b}"
    elif operacao == "Produto matricial":
        latex_operandos = f"{latex_a} \\times {latex_b}"
    elif operacao == "Produto escalar":
        latex_operandos = f"{sp.latex(sp.nsimplify(k))} \\cdot {latex_a}"
    elif operacao == "Transposição":
        latex_operandos = f"{latex_a}^T"
    elif operacao == "Inversa":
        latex_operandos = f"{latex_a}^{{-1}}"
    else:  # Escalonamento — não é uma expressão binária, só a matriz de partida
        latex_operandos = latex_a

    with st.container(border=True):
        st.markdown("##### 🔎 Operandos escolhidos")
        st.caption(f"Matriz {nome_a}" + (f" e Matriz {nome_b}" if b is not None else ""))
        st.latex(latex_operandos)

    a_sp = simbolico.para_sympy(a)
    try:
        if operacao == "Soma":
            resultado_sp, passos = simbolico.somar_matrizes(a_sp, simbolico.para_sympy(b))
        elif operacao == "Produto matricial":
            resultado_sp, passos = simbolico.multiplicar_matrizes(a_sp, simbolico.para_sympy(b))
        elif operacao == "Produto escalar":
            resultado_sp, passos = simbolico.multiplicar_escalar(k, a_sp)
        elif operacao == "Transposição":
            resultado_sp, passos = simbolico.transpor(a_sp)
        elif operacao == "Escalonamento":
            resultado_sp, passos = simbolico.escalonar(a_sp)
        else:  # Inversa
            resultado_sp, passos = simbolico.inversa(a_sp)
            if resultado_sp is None:
                st.warning("A matriz é singular (det = 0) — não tem inversa.")
                if mostrar_passo_a_passo:
                    mostrar_passos(passos)
                return
    except ValueError as erro:
        st.error(str(erro))
        return

    mostrar_resultado(numerico=simbolico.para_numpy(resultado_sp), simbolico_latex=sp.latex(resultado_sp))
    if mostrar_passo_a_passo:
        mostrar_passos(passos)

    if operacao == "Produto escalar" and a.shape == (2, 2):
        st.divider()
        st.markdown("##### 🔎 Ver o efeito de k·A")
        st.caption("Usa as setas do campo \"Escalar k\" acima para ver a grelha a transformar-se.")
        st.plotly_chart(figura_transformacao(k * a, modo_leve=modo_leve_da_sessao()), width="stretch")
