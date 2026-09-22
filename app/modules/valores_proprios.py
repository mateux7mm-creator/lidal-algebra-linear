"""Módulo Valores/Vetores Próprios: cálculo e visualização da transformação
linear, sobre um número arbitrário de matrizes nomeadas."""
import numpy as np  # arrays numéricos e np.linalg.eig (valores/vetores próprios numéricos, para o gráfico)
import sympy as sp  # cálculo simbólico exato (eigen, diagonalização) e formatação LaTeX
import streamlit as st  # widgets de interface

from utils import simbolico  # funções de cálculo com passos pedagógicos
from utils.componentes import (
    cabecalho,               # título da página
    matriz_input,             # editor de células de uma matriz nomeada
    modo_leve_da_sessao,      # lê o estado do "Modo leve" já criado na barra lateral
    modo_passo_a_passo_ativo,  # cria/lê o toggle "mostrar passos"
    mostrar_passos,           # desenha a lista de passos pedagógicos
)
from utils.visualizacao import figura_transformacao_3d, figura_transformacao_parametrizada  # gráficos animados 2D e 3D

# matriz 2×2 diagonal por omissão (valores próprios óbvios: 2 e 3), para a página nunca abrir vazia
VALORES_DEFEITO = {"A": np.array([[2.0, 0.0], [0.0, 3.0]])}


def _inicializar_estado() -> None:
    # garante que existe pelo menos a matriz "A" na primeira visita a esta página
    st.session_state.setdefault("valores_proprios_nomes", ["A"])


def _adicionar_matriz() -> None:
    nomes = st.session_state["valores_proprios_nomes"]
    # próximo nome em sequência alfabética (A, B, C, ...)
    nomes.append(chr(ord("A") + len(nomes)))


def _remover_ultima_matriz() -> None:
    nomes = st.session_state["valores_proprios_nomes"]
    if len(nomes) > 1:  # nunca remove a última matriz
        nome_removido = nomes.pop()
        # limpa o estado guardado dessa matriz (dados da tabela + versão do editor)
        for sufixo in ("_dados", "_versao"):
            st.session_state.pop(f"valores_proprios_{nome_removido}{sufixo}", None)


def render() -> None:
    cabecalho("🌀 Valores e Vetores Próprios")
    _inicializar_estado()

    # layout em 2 colunas: entradas/resultado à esquerda, gráfico à direita
    col_esquerda, col_direita = st.columns([2, 3])

    with col_esquerda, st.container(height=650):
        col_add, col_rem = st.columns(2)
        with col_add:
            # botão para acrescentar mais uma matriz nomeada
            st.button("➕ Adicionar matriz", width="stretch", on_click=_adicionar_matriz,
                       key="valores_proprios_btn_add")
        with col_rem:
            # botão para remover a última matriz; desativado se só sobrar uma
            st.button("➖ Remover última matriz", width="stretch", on_click=_remover_ultima_matriz,
                       disabled=len(st.session_state["valores_proprios_nomes"]) <= 1,
                       key="valores_proprios_btn_rem")

        nomes = st.session_state["valores_proprios_nomes"]
        matrizes: dict[str, np.ndarray] = {}
        for nome in nomes:
            # desenha um editor por cada matriz nomeada; "quadrada=True" porque
            # valores/vetores próprios só fazem sentido para matrizes quadradas
            matrizes[nome] = matriz_input(f"valores_proprios_{nome}", titulo=f"Matriz {nome}",
                                           valor_defeito=VALORES_DEFEITO.get(nome), quadrada=True)

        st.divider()
        # escolha de qual das matrizes nomeadas vai ser analisada
        nome_a = st.selectbox("Matriz a analisar", nomes, key="valores_proprios_op_nome")
        a = matrizes[nome_a]

        with st.container(border=True):
            st.markdown("##### 🔎 Matriz escolhida")
            st.caption(f"Matriz {nome_a}")
            # mostra a matriz escolhida em notação matemática
            st.latex(sp.latex(sp.Matrix(np.round(a, 4).tolist())))

        a_sp = simbolico.para_sympy(a)  # converte para SymPy, formato exigido pelas funções de simbolico.py
        valores, vetores, passos_eigen = simbolico.eigen(a_sp)  # valores/vetores próprios exatos + passos
        (diagonalizacao, passos_diag) = simbolico.diagonalizar(a_sp)  # decomposição A = P·D·P⁻¹, se possível

        with st.container(border=True):
            col_titulo, col_toggle = st.columns([3, 2])
            with col_titulo:
                st.markdown("##### ✅ Resultado")
            with col_toggle:
                # toggle "mostrar passos", dentro da própria caixa de resultado
                mostrar_passo_a_passo = modo_passo_a_passo_ativo("valores_proprios")
            # lista os valores próprios encontrados, separados por vírgulas, em notação matemática
            st.markdown("**Valores próprios:** " + ", ".join(sp.latex(v) for v in valores))
            if diagonalizacao is not None:
                # só mostra a diagonalização se a matriz for diagonalizável (P invertível)
                p, d = diagonalizacao
                st.caption("Diagonalização A = P·D·P⁻¹")
                st.latex(f"P = {sp.latex(p)}, \\quad D = {sp.latex(d)}")
            if mostrar_passo_a_passo:
                st.divider()
                # junta os passos do cálculo dos valores próprios com os da diagonalização
                mostrar_passos(passos_eigen + passos_diag)

    with col_direita, st.container(height=650):  # coluna direita: visualização gráfica
        if a.shape == (2, 2):  # caso 2×2: animação da transformação a "construir-se"
            st.markdown("##### 🔎 Ver a transformação a construir-se")
            valores_np, vetores_np = np.linalg.eig(a)  # versão numérica rápida (para desenhar, não precisa de ser exata)
            direcoes = []
            for i in range(len(valores_np)):
                # só guarda direções próprias REAIS (ignora valores próprios complexos,
                # que não têm uma seta 2D correspondente no gráfico)
                if abs(valores_np[i].imag) < 1e-9:
                    direcoes.append(np.real(vetores_np[:, i]))
            st.caption("Arrasta o slider ou carrega em ▶ Play para ver a transformação a construir-se "
                       "(t: 0 = identidade, 1 = matriz completa).")
            # anima a matriz M(t) = (1-t)·I + t·A, entre t=0 (identidade) e t=1 (matriz completa)
            fig = figura_transformacao_parametrizada(
                lambda t: (1 - t) * np.eye(2) + t * a, np.linspace(0, 1, 30), rotulo_parametro="t",
                direcoes_proprias=direcoes or None, modo_leve=modo_leve_da_sessao(),
            )
            st.plotly_chart(fig, width="stretch")
        elif a.shape == (3, 3):  # caso 3×3: visualização estática em 3D (sem animação)
            st.markdown("##### 🔎 Ver a transformação em 3D")
            valores_np, vetores_np = np.linalg.eig(a)
            direcoes = []
            for i in range(len(valores_np)):
                if abs(valores_np[i].imag) < 1e-9:  # mesma filtragem: só direções próprias reais
                    direcoes.append(np.real(vetores_np[:, i]))
            st.caption("Arrasta para rodar a vista — o cubo unitário e os vetores M·e1/e2/e3 "
                       "mostram a transformação; as retas tracejadas são as direções próprias reais.")
            # gráfico 3D interativo: cubo unitário antes/depois da transformação + direções próprias
            fig = figura_transformacao_3d(a, direcoes_proprias=direcoes or None)
            st.plotly_chart(fig, width="stretch")
        else:
            # matrizes de outras dimensões (1×1, 4×4, ...) não têm visualização geométrica implementada
            st.info("A visualização gráfica só está disponível para matrizes 2×2 e 3×3.")
