"""Módulo Vetores: operações vetoriais e visualização 2D/3D, sobre um número
arbitrário de vetores nomeados (mesmo estilo do módulo Matrizes)."""
import numpy as np
import sympy as sp
import streamlit as st

from utils.componentes import (
    cabecalho,
    modo_passo_a_passo_ativo,
    mostrar_passos,
    vetor_input,
)
from utils.simbolico import Passo
from utils.visualizacao import figura_vetores_2d, figura_vetores_3d

OPERACOES_2_VETORES = ["Soma", "Produto interno", "Produto externo", "Teste de ortogonalidade"]
OPERACOES_1_VETOR = ["Norma"]

CORES = ["#e15759", "#4e79a7", "#59a14f", "#f28e2b", "#b07aa1", "#76b7b2"]
VALORES_DEFEITO = {"v": np.array([2.0, 1.0]), "w": np.array([1.0, 2.0])}


def _inicializar_estado() -> None:
    st.session_state.setdefault("vetores_nomes", ["v", "w"])


def _adicionar_vetor() -> None:
    nomes = st.session_state["vetores_nomes"]
    letras_usadas = set(nomes)
    for codigo in range(ord("a"), ord("z") + 1):
        letra = chr(codigo)
        if letra not in letras_usadas and letra not in ("i", "j", "k"):
            nomes.append(letra)
            return


def _remover_ultimo_vetor() -> None:
    nomes = st.session_state["vetores_nomes"]
    if len(nomes) > 1:
        st.session_state["vetores_nomes"].pop()


def render() -> None:
    cabecalho("➡️ Vetores", "Operações vetoriais e visualização 2D/3D.")
    _inicializar_estado()

    col_dim, col_toggle = st.columns([2, 1])
    with col_dim:
        dimensao = st.radio("Dimensão", [2, 3], horizontal=True, format_func=lambda d: f"{d}D")
    with col_toggle:
        mostrar_passo_a_passo = modo_passo_a_passo_ativo("vetores")

    col_add, col_rem = st.columns(2)
    with col_add:
        st.button("➕ Adicionar vetor", width="stretch", on_click=_adicionar_vetor, key="vetores_btn_add")
    with col_rem:
        st.button("➖ Remover último vetor", width="stretch", on_click=_remover_ultimo_vetor,
                   disabled=len(st.session_state["vetores_nomes"]) <= 1, key="vetores_btn_rem")

    nomes = st.session_state["vetores_nomes"]
    vetores: dict[str, np.ndarray] = {}
    colunas = st.columns(min(len(nomes), 3))
    for i, nome in enumerate(nomes):
        with colunas[i % len(colunas)]:
            defeito = VALORES_DEFEITO.get(nome, np.ones(2))
            if len(defeito) != dimensao:
                defeito = np.ones(dimensao)
            vetores[nome] = vetor_input(f"vetores_{nome}", dimensao=dimensao, titulo=f"Vetor {nome}",
                                         valor_defeito=defeito)

    st.divider()
    operacoes = list(OPERACOES_2_VETORES)
    if dimensao != 3:
        operacoes.remove("Produto externo")
    operacoes += OPERACOES_1_VETOR
    operacao = st.selectbox("Escolher operação", operacoes)

    if operacao in OPERACOES_1_VETOR:
        nome_v = st.selectbox("Vetor", nomes, key="vetores_op_nome_unico")
        v, w, nome_w = vetores[nome_v], None, None
    else:
        if len(nomes) < 2:
            st.warning("Esta operação precisa de pelo menos 2 vetores — adiciona outro acima.")
            return
        col1, col2 = st.columns(2)
        with col1:
            nome_v = st.selectbox("Vetor 1", nomes, index=0, key="vetores_op_nome1")
        with col2:
            nome_w = st.selectbox("Vetor 2", nomes, index=min(1, len(nomes) - 1), key="vetores_op_nome2")
        v, w = vetores[nome_v], vetores[nome_w]

    latex_v = sp.latex(sp.Matrix(np.round(v, 4).tolist()))
    latex_w = sp.latex(sp.Matrix(np.round(w, 4).tolist())) if w is not None else None
    simbolo_operacao = {
        "Soma": f"{latex_v} + {latex_w}",
        "Produto interno": f"{latex_v} \\cdot {latex_w}",
        "Produto externo": f"{latex_v} \\times {latex_w}",
        "Teste de ortogonalidade": f"{latex_v} \\cdot {latex_w}",
        "Norma": f"\\lVert {latex_v} \\rVert",
    }[operacao]

    with st.container(border=True):
        st.markdown("##### 🔎 Operandos escolhidos")
        st.caption(f"Vetor {nome_v}" + (f" e Vetor {nome_w}" if nome_w else ""))
        st.latex(simbolo_operacao)

    passos: list[Passo] = []
    with st.container(border=True):
        st.markdown("##### ✅ Resultado")
        if operacao == "Soma":
            resultado = v + w
            st.latex(f"{simbolo_operacao} = {sp.latex(sp.Matrix(np.round(resultado, 4).tolist()))}")
            passos = [
                Passo(f"Somar a componente {i + 1}: v_{i + 1} + w_{i + 1}", "",
                      latex=f"{v[i]:g} + {w[i]:g} = {resultado[i]:g}")
                for i in range(len(v))
            ]
        elif operacao == "Produto interno":
            resultado = float(np.dot(v, w))
            st.latex(f"{simbolo_operacao} = {resultado:g}")
            termos = " + ".join(f"({v[i]:g})({w[i]:g})" for i in range(len(v)))
            valores_termos = " + ".join(f"{v[i] * w[i]:g}" for i in range(len(v)))
            passos = [Passo("Multiplicar cada par de componentes e somar", "",
                             latex=f"{termos} = {valores_termos} = {resultado:g}")]
        elif operacao == "Produto externo":
            resultado = np.cross(v, w)
            st.latex(f"{simbolo_operacao} = {sp.latex(sp.Matrix(np.round(resultado, 4).tolist()))}")
            rotulos = [("v_2 w_3 - v_3 w_2", 1, 2, 2, 1), ("v_3 w_1 - v_1 w_3", 2, 0, 0, 2),
                       ("v_1 w_2 - v_2 w_1", 0, 1, 1, 0)]
            passos = [
                Passo(f"Calcular a componente {i + 1} do produto externo", formula,
                      latex=f"({v[ia]:g})({w[ib]:g}) - ({v[ic]:g})({w[id_]:g}) = {resultado[i]:g}")
                for i, (formula, ia, ib, ic, id_) in enumerate(rotulos)
            ]
        elif operacao == "Norma":
            resultado = float(np.linalg.norm(v))
            st.latex(f"{simbolo_operacao} = {resultado:g}")
            quadrados = " + ".join(f"({v[i]:g})^2" for i in range(len(v)))
            soma_quadrados = float(np.sum(v ** 2))
            passos = [
                Passo("Elevar cada componente ao quadrado e somar", "",
                      latex=f"{quadrados} = {soma_quadrados:g}"),
                Passo("Calcular a raiz quadrada da soma", "",
                      latex=f"\\sqrt{{{soma_quadrados:g}}} = {resultado:g}"),
            ]
        else:  # Teste de ortogonalidade
            produto = float(np.dot(v, w))
            ortogonais = abs(produto) < 1e-9
            st.latex(f"{simbolo_operacao} = {produto:.4g}")
            st.markdown("✅ **Ortogonais**" if ortogonais else "❌ **Não ortogonais**")
            termos = " + ".join(f"({v[i]:g})({w[i]:g})" for i in range(len(v)))
            passos = [
                Passo("Calcular v · w", "", latex=f"{termos} = {produto:.4g}"),
                Passo("Concluir", f"Como v · w {'=' if ortogonais else '≠'} 0, os vetores "
                                   f"{'são' if ortogonais else 'não são'} ortogonais."),
            ]

    if mostrar_passo_a_passo and passos:
        mostrar_passos(passos)

    st.divider()
    st.markdown("##### 📈 Visualização")
    vetores_fig = [(nome, vetores[nome], CORES[i % len(CORES)]) for i, nome in enumerate(nomes)]
    fig = figura_vetores_2d(vetores_fig) if dimensao == 2 else figura_vetores_3d(vetores_fig)
    st.plotly_chart(fig, width="stretch", key="vetores_grafico_principal")

    st.markdown(f"##### 🔎 Ver k·{nome_v}")
    k_exploracao = st.number_input(f"k (escalar aplicado a {nome_v})", value=1.0, step=0.5,
                                    key="vetores_k_explorar")
    nome_kv = f"{k_exploracao:g}·{nome_v}"
    fig_kv = figura_vetores_2d([(nome_kv, k_exploracao * v, CORES[0])]) if dimensao == 2 \
        else figura_vetores_3d([(nome_kv, k_exploracao * v, CORES[0])])
    st.plotly_chart(fig_kv, width="stretch", key="vetores_grafico_kv")
