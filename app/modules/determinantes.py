"""Módulo Determinantes / Inversa: cálculo e deteção de matrizes singulares,
sobre um número arbitrário de matrizes nomeadas (mesmo estilo do módulo Matrizes)."""
import numpy as np  # arrays numéricos usados para guardar/manipular as matrizes
import sympy as sp  # cálculo simbólico (determinante exato, inversa exata, LaTeX)
import streamlit as st  # widgets de interface (botões, colunas, gráficos, etc.)

from utils import simbolico  # funções puras de cálculo (sem UI): determinante, inversa, conversões
from utils.componentes import (
    cabecalho,               # título da página
    matriz_input,             # editor de células para uma matriz + pré-visualização simbólica
    modo_leve_da_sessao,      # lê o estado do toggle "Modo leve" já criado noutro sítio
    modo_passo_a_passo_ativo,  # cria o toggle "mostrar passos" e devolve o seu estado
    mostrar_passos,           # desenha a lista de passos pedagógicos
)
from utils.visualizacao import figura_transformacao_parametrizada  # gráfico animado da transformação linear

# matriz 2×2 pré-preenchida por omissão para a matriz "A", para a página já
# nascer com um exemplo válido em vez de tudo a zeros
VALORES_DEFEITO = {"A": np.array([[2.0, 1.0], [1.0, 3.0]])}


def _inicializar_estado() -> None:
    # garante que existe pelo menos a matriz "A" na primeira visita a esta página
    st.session_state.setdefault("determinantes_nomes", ["A"])


def _adicionar_matriz() -> None:
    nomes = st.session_state["determinantes_nomes"]
    # gera o próximo nome em sequência alfabética (A, B, C, ...) a partir do número já existente
    nomes.append(chr(ord("A") + len(nomes)))


def _remover_ultima_matriz() -> None:
    nomes = st.session_state["determinantes_nomes"]
    if len(nomes) > 1:  # nunca remove a última matriz que resta
        nome_removido = nomes.pop()
        # limpa também os dados/estado do editor dessa matriz, para não ficarem "fantasmas" na sessão
        for sufixo in ("_dados", "_versao"):
            st.session_state.pop(f"determinantes_{nome_removido}{sufixo}", None)


def render() -> None:
    cabecalho("➗ Determinantes e Matriz Inversa")  # título no topo da página
    _inicializar_estado()

    # layout em 2 colunas: entradas/resultado à esquerda, gráfico à direita
    col_esquerda, col_direita = st.columns([2, 3])

    with col_esquerda, st.container(height=650):  # coluna esquerda, com scroll próprio até 650px
        col_add, col_rem = st.columns(2)
        with col_add:
            # botão para acrescentar mais uma matriz nomeada
            st.button("➕ Adicionar matriz", width="stretch", on_click=_adicionar_matriz,
                       key="determinantes_btn_add")
        with col_rem:
            # botão para remover a última matriz; desativado se só sobrar uma
            st.button("➖ Remover última matriz", width="stretch", on_click=_remover_ultima_matriz,
                       disabled=len(st.session_state["determinantes_nomes"]) <= 1, key="determinantes_btn_rem")

        nomes = st.session_state["determinantes_nomes"]
        matrizes: dict[str, np.ndarray] = {}
        for nome in nomes:
            # desenha um editor de matriz por cada nome existente e guarda o valor introduzido
            matrizes[nome] = matriz_input(f"determinantes_{nome}", titulo=f"Matriz {nome}",
                                           valor_defeito=VALORES_DEFEITO.get(nome), quadrada=True)

        st.divider()
        # escolha de qual das matrizes nomeadas vai ser analisada
        nome_a = st.selectbox("Matriz a analisar", nomes, key="determinantes_op_nome")
        a = matrizes[nome_a]

        with st.container(border=True):
            st.markdown("##### 🔎 Matriz escolhida")
            st.caption(f"Matriz {nome_a}")
            # mostra a matriz escolhida em notação matemática (LaTeX), arredondada a 4 casas decimais
            st.latex(sp.latex(sp.Matrix(np.round(a, 4).tolist())))

        a_sp = simbolico.para_sympy(a)  # converte o array numpy numa matriz SymPy (permite cálculo exato/simbólico)
        det_sp, passos_det = simbolico.determinante(a_sp)  # determinante exato + passos pedagógicos
        inversa_sp, passos_inv = simbolico.inversa(a_sp)  # inversa exata (ou None se singular) + passos

        with st.container(border=True):
            col_titulo, col_toggle = st.columns([3, 2])
            with col_titulo:
                st.markdown("##### ✅ Resultado")
            with col_toggle:
                # toggle "mostrar passos", desenhado dentro da própria caixa de resultado
                mostrar_passo_a_passo = modo_passo_a_passo_ativo("determinantes")
            col_det, col_inv = st.columns(2)
            with col_det:
                # mostra o determinante como número, com 4 algarismos significativos
                st.metric("Determinante", f"{float(det_sp):.4g}")
            with col_inv:
                if inversa_sp is None:
                    # determinante nulo: a matriz não tem inversa
                    st.warning("Matriz singular — não tem inversa.")
                else:
                    st.caption("Matriz inversa")
                    st.latex(sp.latex(inversa_sp))  # inversa em notação matemática
            if mostrar_passo_a_passo:
                st.divider()
                # junta os passos do determinante com os da inversa, numa só lista ordenada
                mostrar_passos(passos_det + passos_inv)

    with col_direita, st.container(height=650):  # coluna direita: visualização gráfica
        if a.shape == (2, 2):  # a animação só está definida para matrizes 2×2
            st.markdown("##### 🔎 Ver a matriz a tornar-se singular")
            # posições possíveis (linha, coluna) de cada entrada de uma matriz 2×2
            posicoes = {"a11": (0, 0), "a12": (0, 1), "a21": (1, 0), "a22": (1, 1)}
            # escolha de qual entrada da matriz vai variar na animação (a22 pré-selecionada)
            rotulo_entrada = st.selectbox("Entrada a variar", list(posicoes.keys()), index=3)
            posicao = posicoes[rotulo_entrada]
            st.caption("Arrasta o slider ou carrega em ▶ Play para ver o paralelogramo a degenerar.")
            # constrói a figura animada: para cada valor do parâmetro, substitui a
            # entrada escolhida por esse valor e recalcula a transformação/área
            fig = figura_transformacao_parametrizada(
                lambda valor: simbolico.matriz_com_entrada_variavel(a, posicao, valor),
                np.linspace(-3, 3, 30), rotulo_parametro=rotulo_entrada, mostrar_area=True,
                modo_leve=modo_leve_da_sessao(),
            )
            st.plotly_chart(fig, width="stretch")  # desenha o gráfico Plotly interativo, a ocupar toda a largura
        else:
            # matrizes maiores que 2×2 não têm a visualização geométrica implementada
            st.caption("A visualização gráfica só está disponível para matrizes 2×2.")
