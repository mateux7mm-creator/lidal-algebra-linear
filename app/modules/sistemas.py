"""Módulo Sistemas Lineares: resolução e interpretação geométrica.

Estilo "Winplot": as equações escrevem-se em texto livre (ex. "2x + 4y = 6"),
depois de se definirem as incógnitas, e uma barra de menus no topo organiza
as ações (gerir equações, opções de visualização, exportar).
"""
from __future__ import annotations  # permite anotações de tipo mais modernas em qualquer versão do Python

import numpy as np  # conversão para arrays numéricos (coeficientes/termos independentes)
import sympy as sp  # álgebra simbólica: resolução exata do sistema e formatação LaTeX
import streamlit as st  # widgets desta página

from utils import simbolico  # análise das equações, resolução do sistema e classificação
from utils.componentes import (
    barra_menus,  # menu horizontal estilo desktop, com popovers (Equações/Ver/Exportar)
    cabecalho,  # título da página
    modo_leve_da_sessao,  # lê o estado do "Modo leve" (reduz detalhe dos gráficos)
    modo_passo_a_passo_ativo,  # cria/lê o toggle "mostrar passos"
    mostrar_passos,  # lista de passos pedagógicos
)
from utils.visualizacao import figura_planos_3d, figura_retas_2d, figura_retas_2d_parametrizada  # gráficos 2D/3D das equações

# Sistema de exemplo (2 equações, 2 incógnitas) com que a página abre por omissão.
EXEMPLO_PADRAO = ["x + y = 3", "x - y = 1"]


def _inicializar_estado() -> None:
    # nomes das incógnitas (texto livre, separado por vírgulas)
    st.session_state.setdefault("sistemas_variaveis", "x, y")
    # nº de equações atualmente no sistema
    st.session_state.setdefault("sistemas_n_eq", len(EXEMPLO_PADRAO))
    # toggle "mostrar passos" desligado por omissão
    st.session_state.setdefault("sistemas_passo_a_passo", False)
    # a exploração animada (reta/interseção a variar) começa ligada por omissão
    st.session_state.setdefault("sistemas_mostrar_exploracao", True)
    for i, eq in enumerate(EXEMPLO_PADRAO):
        # texto de cada equação de exemplo e se aparece marcada no gráfico
        st.session_state.setdefault(f"sistemas_eq_{i}", eq)
        st.session_state.setdefault(f"sistemas_eq_mostrar_{i}", True)


def _menu_equacoes() -> None:
    """Os st.rerun() são necessários porque este menu (dentro de um popover
    de barra_menus) só é desenhado DEPOIS do ciclo que mostra as caixas de
    equação — sem forçar já aqui outra execução, o clique só ficaria visível
    na interação seguinte, não de imediato."""
    st.caption("Gerir as equações do sistema")
    if st.button("➕ Adicionar equação", key="sistemas_btn_add", width="stretch"):
        # cria uma nova equação vazia, visível por omissão, e força um rerun imediato
        i = st.session_state["sistemas_n_eq"]
        st.session_state.setdefault(f"sistemas_eq_{i}", "")
        st.session_state.setdefault(f"sistemas_eq_mostrar_{i}", True)
        st.session_state["sistemas_n_eq"] += 1
        st.rerun()
    if st.button("➖ Remover última equação", key="sistemas_btn_rem", width="stretch"):
        if st.session_state["sistemas_n_eq"] > 1:  # nunca remove a última equação que resta
            st.session_state["sistemas_n_eq"] -= 1
            st.rerun()
    if st.button("🔄 Repor exemplo (2 equações)", key="sistemas_btn_reset", width="stretch"):
        # repõe o sistema de exemplo original, sobrescrevendo o que o utilizador tiver escrito
        st.session_state["sistemas_variaveis"] = "x, y"
        st.session_state["sistemas_n_eq"] = len(EXEMPLO_PADRAO)
        for i, eq in enumerate(EXEMPLO_PADRAO):
            st.session_state[f"sistemas_eq_{i}"] = eq
            st.session_state[f"sistemas_eq_mostrar_{i}"] = True
        st.rerun()


def _menu_ver() -> None:
    # popover "Ver": único item, o toggle que liga/desliga a exploração animada
    st.caption("Opções de visualização")
    st.toggle("Mostrar exploração animada", key="sistemas_mostrar_exploracao")


def _menu_exportar(a: sp.Matrix, b: sp.Matrix, simbolos: list) -> None:
    # popover "Exportar": mostra o sistema em forma matricial (A·x = b) como
    # LaTeX renderizado e como texto copiável (st.code)
    st.caption("Copiar o sistema (LaTeX)")
    latex_sistema = f"{sp.latex(a)} {sp.latex(sp.Matrix(simbolos))} = {sp.latex(b)}"
    st.latex(latex_sistema)
    st.code(latex_sistema, language="latex")


def render() -> None:
    cabecalho("📐 Sistemas Lineares")  # título no topo da página
    _inicializar_estado()

    col_esquerda, col_direita = st.columns([2, 3])  # entradas/resultado à esquerda, gráfico à direita (maior)

    with col_esquerda, st.container(height=650):  # coluna esquerda, com scroll próprio
        # campo de texto com os nomes das incógnitas (ex. "x, y" ou "x, y, z")
        st.text_input("Incógnitas (separadas por vírgula)", key="sistemas_variaveis",
                       placeholder="ex.: x, y")

        st.markdown("**Equações**")
        for i in range(st.session_state["sistemas_n_eq"]):
            chave = f"sistemas_eq_{i}"
            chave_mostrar = f"sistemas_eq_mostrar_{i}"
            st.session_state.setdefault(chave, "")
            st.session_state.setdefault(chave_mostrar, True)
            col_eq, col_mostrar = st.columns([4, 1])
            with col_eq:
                # caixa de texto onde se escreve a equação (sem rótulo visível, para poupar espaço)
                st.text_input(f"Equação {i + 1}", key=chave, placeholder="ex.: 2x + 4y = 6",
                               label_visibility="collapsed")
            with col_mostrar:
                # liga/desliga esta equação no gráfico (interpretação gráfica)
                st.checkbox("Mostrar no gráfico", key=chave_mostrar)

        # texto atual de todas as equações, na ordem em que aparecem
        textos_equacoes = [st.session_state[f"sistemas_eq_{i}"]
                            for i in range(st.session_state["sistemas_n_eq"])]

        try:
            # interpreta as equações e devolve: matriz de coeficientes A, vetor
            # de termos independentes b, lista de símbolos das incógnitas e os
            # passos pedagógicos de como o sistema foi montado
            a_sp, b_sp, simbolos, passos = simbolico.analisar_equacoes(
                st.session_state["sistemas_variaveis"], textos_equacoes
            )
        except ValueError as erro:
            # equação mal escrita, incógnita desconhecida, etc. — mostra o erro e para aqui
            st.error(str(erro))
            return

        # barra de menus horizontal, estilo desktop, com 3 popovers
        barra_menus({
            "Equações": _menu_equacoes,
            "Ver": _menu_ver,
            "Exportar": lambda: _menu_exportar(a_sp, b_sp, simbolos),
        })

        n_variaveis = len(simbolos)
        a = simbolico.para_numpy(a_sp)  # matriz de coeficientes, em NumPy (para o gráfico)
        b = simbolico.para_numpy(b_sp).reshape(-1)  # termos independentes, como vetor 1D
        n_equacoes = a.shape[0]
        sistema_2x2 = (n_equacoes, n_variaveis) == (2, 2)  # só sistemas 2×2 têm a exploração animada

        # resolve o sistema (solução exata) e classifica-o (determinado/indeterminado/impossível)
        solucoes, passos_resolucao = simbolico.resolver_sistema(a_sp, b_sp, simbolos)
        classificacao = simbolico.classificar_sistema(solucoes, simbolos)
        # rótulo em português + emoji para cada uma das 3 classificações possíveis
        rotulo_classificacao = {
            "determinado": "✅ Sistema possível e determinado — solução única",
            "indeterminado": "♾️ Sistema possível e indeterminado — infinitas soluções",
            "impossivel": "🚫 Sistema impossível — não tem solução",
        }[classificacao]

        with st.container(border=True):
            col_titulo, col_toggle = st.columns([3, 2])
            with col_titulo:
                st.markdown("##### Resultado")
            with col_toggle:
                # toggle "mostrar passos", dentro da própria caixa de resultado
                mostrar_passo_a_passo = modo_passo_a_passo_ativo("sistemas")
            st.markdown(f"**Classificação:** {rotulo_classificacao}")
            # formata a solução (se existir uma forma fechada a mostrar) como LaTeX
            solucao_latex = simbolico.formatar_solucao_sistema(solucoes, simbolos)
            if solucao_latex is not None:
                st.markdown("<p style='text-align:center'><strong>Solução:</strong></p>",
                            unsafe_allow_html=True)
                st.latex(solucao_latex)
            if mostrar_passo_a_passo:
                st.divider()
                # junta os passos de montagem do sistema com os da resolução
                mostrar_passos(passos + passos_resolucao)

    with col_direita, st.container(height=650):  # coluna direita: visualização gráfica
        if n_variaveis == 2:
            st.markdown("##### 📈 Interpretação gráfica")
            # lista (a, b, c) de cada equação "a·x + b·y = c" que está marcada para aparecer
            equacoes_visiveis = [(a[i, 0], a[i, 1], b[i]) for i in range(n_equacoes)
                                  if st.session_state.get(f"sistemas_eq_mostrar_{i}", True)]
            if equacoes_visiveis:
                # desenha as retas 2D e o(s) ponto(s) de interseção
                st.plotly_chart(figura_retas_2d(equacoes_visiveis, modo_leve=modo_leve_da_sessao()),
                                 width="stretch", key="sistemas_grafico_principal")
            else:
                st.caption("Nenhuma equação selecionada para mostrar no gráfico — "
                           "marca a caixa \"Mostrar no gráfico\" junto de pelo menos uma equação.")

            if sistema_2x2 and st.session_state["sistemas_mostrar_exploracao"]:
                st.markdown("##### 🔎 Ver a reta e a interseção a variar")
                col_eq, col_coef = st.columns(2)
                with col_eq:
                    # escolha de qual das 2 equações vai ter um coeficiente animado
                    eq_variavel = st.selectbox("Equação a variar", ["1ª equação", "2ª equação"], index=1)
                indice_eq = 0 if eq_variavel.startswith("1") else 1
                indice_fixa = 1 - indice_eq  # a outra equação fica fixa, como referência
                with col_coef:
                    # escolha de qual dos 2 coeficientes dessa equação vai variar
                    coef_variavel = st.selectbox(
                        "Coeficiente a variar",
                        [f"coeficiente de {simbolos[0]}", f"coeficiente de {simbolos[1]}"], index=1,
                    )
                indice_coef = 0 if coef_variavel.endswith(str(simbolos[0])) else 1
                valor_atual = float(a[indice_eq, indice_coef])

                def calcular_equacao_variavel(valor, indice_eq=indice_eq, indice_coef=indice_coef):
                    # dado um valor do parâmetro, devolve a equação (a, b, c) da
                    # reta variável, com esse coeficiente substituído
                    linha = [a[indice_eq, 0], a[indice_eq, 1]]
                    linha[indice_coef] = valor
                    return (linha[0], linha[1], b[indice_eq])

                # a equação fixa (não anima) e os rótulos de cada uma, para a legenda do gráfico
                equacao_fixa = (a[indice_fixa, 0], a[indice_fixa, 1], b[indice_fixa])
                rotulos_equacoes = (f"Eq. {indice_fixa + 1}", f"Eq. {indice_eq + 1}")

                st.caption("Arrasta o slider ou carrega em ▶ Play para ver a reta e a interseção a variar.")
                # gráfico animado: a reta variável desloca-se ao longo de 30 valores
                # do coeficiente escolhido, à volta do valor atual (±3)
                fig = figura_retas_2d_parametrizada(
                    equacao_fixa, calcular_equacao_variavel,
                    np.linspace(valor_atual - 3, valor_atual + 3, 30),
                    rotulo_parametro=f"coef. de {simbolos[indice_coef]} (eq. {indice_eq + 1})",
                    modo_leve=modo_leve_da_sessao(), rotulos_equacoes=rotulos_equacoes,
                )
                st.plotly_chart(fig, width="stretch", key="sistemas_grafico_exploracao")
            elif not sistema_2x2:
                # a exploração animada só está implementada para o caso 2 equações × 2 incógnitas
                st.caption("A exploração animada da reta só está disponível para sistemas de exatamente "
                           "2 equações e 2 incógnitas.")
        elif n_variaveis == 3:
            st.markdown("##### 📈 Interpretação gráfica (3D)")
            # lista (a, b, c, d) de cada plano "a·x + b·y + c·z = d" marcado para aparecer
            equacoes_visiveis_3d = [(a[i, 0], a[i, 1], a[i, 2], b[i]) for i in range(n_equacoes)
                                     if st.session_state.get(f"sistemas_eq_mostrar_{i}", True)]
            if equacoes_visiveis_3d:
                st.caption("Arrasta para rodar a vista — cada plano é uma equação; "
                           "o ponto preto é a interseção, quando existe uma única.")
                # desenha os planos 3D (um por equação) e o ponto de interseção, se único
                st.plotly_chart(figura_planos_3d(equacoes_visiveis_3d), width="stretch",
                                 key="sistemas_grafico_3d")
            else:
                st.caption("Nenhuma equação selecionada para mostrar no gráfico — "
                           "marca a caixa \"Mostrar no gráfico\" junto de pelo menos uma equação.")
        # sistemas com 1 ou mais de 3 incógnitas não têm visualização gráfica implementada
        # (fica apenas a resolução simbólica/numérica na coluna esquerda)
