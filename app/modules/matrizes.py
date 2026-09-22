"""Módulo Matrizes: soma, produto escalar, produto matricial, transposição,
escalonamento e inversa — sobre um número arbitrário de matrizes nomeadas."""
import numpy as np  # arrays numéricos: guarda o valor real de cada matriz introduzida
import sympy as sp  # álgebra simbólica: usado aqui só para formatar em LaTeX (sp.latex/sp.Matrix)
import streamlit as st  # framework que desenha todos os widgets desta página

from utils import simbolico  # funções de cálculo (soma, produto, inversa, ...) com passos pedagógicos
from utils.componentes import (
    cabecalho,  # título da página, sem legenda
    matriz_input,  # editor de células de uma matriz nomeada, com pré-visualização simbólica
    modo_leve_da_sessao,  # lê o estado do toggle "Modo leve" sem recriar o widget
    modo_passo_a_passo_ativo,  # cria/lê o toggle "mostrar passos" de um módulo
    mostrar_passos,  # lista de expanders "Passo 1, 2, ..." com o detalhe pedagógico
    mostrar_resultado,  # caixa "Resultado" com o valor numérico e simbólico lado a lado
)
from utils.visualizacao import figura_transformacao_parametrizada  # gráfico animado k·A (grelha a transformar-se)

# As duas operações que precisam de DUAS matrizes escolhidas pelo utilizador.
OPERACOES_2_MATRIZES = ["Soma", "Produto matricial"]
# As operações que só precisam de UMA matriz (mais, no caso do produto escalar, o escalar k).
OPERACOES_1_MATRIZ = ["Produto escalar", "Transposição", "Escalonamento", "Inversa"]
# Lista completa mostrada no seletor de operação — a ordem das duas listas acima define a ordem no menu.
TODAS_OPERACOES = OPERACOES_2_MATRIZES + OPERACOES_1_MATRIZ

# Valores de exemplo pré-carregados nas matrizes A e B, para a página nunca abrir vazia.
VALORES_DEFEITO = {
    "A": np.array([[1.0, 2.0], [3.0, 4.0]]),
    "B": np.array([[0.0, 1.0], [1.0, 0.0]]),
}


def _inicializar_estado() -> None:
    # Lista de nomes de matrizes atualmente visíveis (A, B, C, ...) — só é
    # criada na primeira execução da sessão; `setdefault` não sobrescreve
    # o que já lá estiver depois de o utilizador adicionar/remover matrizes.
    st.session_state.setdefault("matrizes_nomes", ["A", "B"])


def _adicionar_matriz() -> None:
    # Callback do botão "➕ Adicionar matriz": dá o próximo nome do alfabeto
    # (A, B, C, ...) à nova matriz, calculado a partir de quantas já existem.
    nomes = st.session_state["matrizes_nomes"]
    nomes.append(chr(ord("A") + len(nomes)))


def _remover_ultima_matriz() -> None:
    # Callback do botão "➖ Remover última matriz": nunca deixa ficar menos
    # de 1 matriz, e limpa também o estado guardado dessa matriz (dados da
    # tabela + contador de versão do editor), para não sobrar lixo em sessão.
    nomes = st.session_state["matrizes_nomes"]
    if len(nomes) > 1:
        nome_removido = nomes.pop()
        for sufixo in ("_dados", "_versao"):
            st.session_state.pop(f"matrizes_{nome_removido}{sufixo}", None)


def render() -> None:
    cabecalho("🔢 Matrizes")  # título "🔢 Matrizes" no topo da página
    _inicializar_estado()

    # Ao contrário dos outros módulos, aqui só uma operação (Produto escalar,
    # matriz 2×2) tem gráfico — a coluna do conteúdo fica maior.
    col_esquerda, col_direita = st.columns([3, 2])  # 3:2 = conteúdo maior que o gráfico

    with col_esquerda, st.container(height=650):  # coluna esquerda, com scroll próprio até 650px
        # Botões para gerir quantas matrizes existem, lado a lado.
        col_add, col_rem = st.columns(2)
        with col_add:
            st.button("➕ Adicionar matriz", width="stretch", on_click=_adicionar_matriz)
        with col_rem:
            st.button("➖ Remover última matriz", width="stretch", on_click=_remover_ultima_matriz,
                       disabled=len(st.session_state["matrizes_nomes"]) <= 1)  # não deixa remover a última que resta

        nomes = st.session_state["matrizes_nomes"]
        matrizes: dict[str, np.ndarray] = {}
        # Desenha um editor de células por cada matriz nomeada e guarda o
        # valor lido de cada uma num dicionário nome -> np.ndarray.
        for nome in nomes:
            matrizes[nome] = matriz_input(f"matrizes_{nome}", titulo=f"Matriz {nome}",
                                           valor_defeito=VALORES_DEFEITO.get(nome))

        st.divider()
        # Seletor da operação a realizar, entre as combinadas em TODAS_OPERACOES.
        operacao = st.selectbox("Escolher operação", TODAS_OPERACOES)

        k = None  # escalar k, só usado no "Produto escalar"
        if operacao in OPERACOES_2_MATRIZES:
            # Operações binárias precisam de pelo menos 2 matrizes definidas.
            if len(nomes) < 2:
                st.warning("Esta operação precisa de pelo menos 2 matrizes — adiciona outra acima.")
                return
            # Seletores para escolher QUAIS das matrizes existentes entram na operação.
            col1, col2 = st.columns(2)
            with col1:
                nome_a = st.selectbox("Matriz 1", nomes, index=0, key="matrizes_op_nome1")
            with col2:
                nome_b = st.selectbox("Matriz 2", nomes, index=min(1, len(nomes) - 1), key="matrizes_op_nome2")
            a, b = matrizes[nome_a], matrizes[nome_b]
        else:
            # Operações unárias só precisam de escolher uma matriz.
            nome_a = st.selectbox("Matriz", nomes, key="matrizes_op_nome_unica")
            a, b = matrizes[nome_a], None
            if operacao == "Produto escalar":
                st.markdown("**Escalar k**")
                # Campo numérico para o valor de k (2.0 por omissão, passo de 0.5).
                k = st.number_input("k", value=2.0, step=0.5, label_visibility="collapsed")

        # Representação em LaTeX de A (e de B, se existir) arredondadas a 4 casas,
        # para mostrar os "Operandos escolhidos" de forma legível antes do resultado.
        latex_a = sp.latex(sp.Matrix(np.round(a, 4).tolist()))
        latex_b = sp.latex(sp.Matrix(np.round(b, 4).tolist())) if b is not None else None
        # Monta a expressão LaTeX da operação escolhida, combinando os operandos
        # com o símbolo apropriado (+, ×, escalar·A, transposta, inversa, ...).
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

        # Caixa "🔎 Operandos escolhidos": mostra a expressão completa antes do cálculo.
        with st.container(border=True):
            st.markdown("##### 🔎 Operandos escolhidos")
            st.caption(f"Matriz {nome_a}" + (f" e Matriz {nome_b}" if b is not None else ""))
            st.latex(latex_operandos)

    # Converte a matriz A (NumPy) para SymPy, formato usado por todas as
    # funções de cálculo em `simbolico`, que devolvem sempre (resultado, passos).
    a_sp = simbolico.para_sympy(a)
    try:
        # Despacha para a função de simbolico.py correspondente à operação escolhida.
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
    except ValueError as erro:
        # Ex.: dimensões incompatíveis na soma/produto — mostra o erro na
        # coluna direita (o layout normal ainda nem foi desenhado aí) e sai.
        with col_direita, st.container(height=650):
            st.error(str(erro))
        return

    with col_direita, st.container(height=650):
        if resultado_sp is None:
            # Caso especial da Inversa: matriz singular (det = 0) não tem
            # inversa — mostra o aviso e, se pedido, os passos até essa
            # conclusão, dentro da mesma caixa que o toggle "passo-a-passo".
            with st.container(border=True):
                col_titulo, col_toggle = st.columns([3, 2])
                with col_titulo:
                    st.warning("A matriz é singular (det = 0) — não tem inversa.")
                with col_toggle:
                    mostrar_passo_a_passo = modo_passo_a_passo_ativo("matrizes")
                if mostrar_passo_a_passo:
                    st.divider()
                    mostrar_passos(passos)
            return

        # Caso normal: mostra o resultado (numérico + simbólico) e, dentro da
        # mesma caixa, o toggle de passos e os passos quando ligado.
        mostrar_resultado(numerico=simbolico.para_numpy(resultado_sp), simbolico_latex=sp.latex(resultado_sp),
                           chave_pagina="matrizes", passos=passos)

        # Só no Produto escalar com matriz 2×2 há gráfico: anima k·A a variar
        # k de -2 a 2, mostrando a grelha 2D a transformar-se em tempo real.
        if operacao == "Produto escalar" and a.shape == (2, 2):
            st.divider()
            st.markdown("##### 🔎 Ver o efeito de k·A")
            st.caption("Arrasta o slider ou carrega em ▶ Play para ver a grelha a transformar-se.")
            fig = figura_transformacao_parametrizada(
                lambda valor_k: valor_k * a, np.linspace(-2, 2, 30), rotulo_parametro="k",
                modo_leve=modo_leve_da_sessao(),
            )
            st.plotly_chart(fig, width="stretch")
