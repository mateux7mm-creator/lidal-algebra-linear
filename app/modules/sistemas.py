"""Módulo Sistemas Lineares: resolução e interpretação geométrica.

Estilo "Winplot": as equações escrevem-se em texto livre (ex. "2x + 4y = 6"),
depois de se definirem as incógnitas, e uma barra de menus no topo organiza
as ações (gerir equações, opções de visualização, exportar).
"""
from __future__ import annotations

import numpy as np
import sympy as sp
import streamlit as st

from utils import simbolico
from utils.componentes import (
    barra_menus,
    cabecalho,
    modo_leve_da_sessao,
    mostrar_passos,
)
from utils.visualizacao import figura_retas_2d, figura_retas_2d_parametrizada

EXEMPLO_PADRAO = ["x + y = 3", "x - y = 1"]


def _inicializar_estado() -> None:
    st.session_state.setdefault("sistemas_variaveis", "x, y")
    st.session_state.setdefault("sistemas_n_eq", len(EXEMPLO_PADRAO))
    st.session_state.setdefault("sistemas_passo_a_passo", False)
    st.session_state.setdefault("sistemas_mostrar_exploracao", True)
    for i, eq in enumerate(EXEMPLO_PADRAO):
        st.session_state.setdefault(f"sistemas_eq_{i}", eq)
        st.session_state.setdefault(f"sistemas_eq_mostrar_{i}", True)


def _menu_equacoes() -> None:
    st.caption("Gerir as equações do sistema")
    if st.button("➕ Adicionar equação", key="sistemas_btn_add", width="stretch"):
        i = st.session_state["sistemas_n_eq"]
        st.session_state.setdefault(f"sistemas_eq_{i}", "")
        st.session_state.setdefault(f"sistemas_eq_mostrar_{i}", True)
        st.session_state["sistemas_n_eq"] += 1
    if st.button("➖ Remover última equação", key="sistemas_btn_rem", width="stretch"):
        if st.session_state["sistemas_n_eq"] > 1:
            st.session_state["sistemas_n_eq"] -= 1
    if st.button("🔄 Repor exemplo (2 equações)", key="sistemas_btn_reset", width="stretch"):
        st.session_state["sistemas_variaveis"] = "x, y"
        st.session_state["sistemas_n_eq"] = len(EXEMPLO_PADRAO)
        for i, eq in enumerate(EXEMPLO_PADRAO):
            st.session_state[f"sistemas_eq_{i}"] = eq
            st.session_state[f"sistemas_eq_mostrar_{i}"] = True


def _menu_ver() -> None:
    st.caption("Opções de visualização")
    st.toggle("Mostrar modo passo-a-passo", key="sistemas_passo_a_passo")
    st.toggle("Mostrar exploração animada", key="sistemas_mostrar_exploracao")


def _menu_exportar(a: sp.Matrix, b: sp.Matrix, simbolos: list) -> None:
    st.caption("Copiar o sistema (LaTeX)")
    latex_sistema = f"{sp.latex(a)} {sp.latex(sp.Matrix(simbolos))} = {sp.latex(b)}"
    st.latex(latex_sistema)
    st.code(latex_sistema, language="latex")


def render() -> None:
    cabecalho("📐 Sistemas Lineares", "Escreve as equações em texto — como no papel.")
    _inicializar_estado()

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
            st.text_input(f"Equação {i + 1}", key=chave, placeholder="ex.: 2x + 4y = 6",
                           label_visibility="collapsed")
        with col_mostrar:
            st.checkbox("Mostrar no gráfico", key=chave_mostrar)

    textos_equacoes = [st.session_state[f"sistemas_eq_{i}"] for i in range(st.session_state["sistemas_n_eq"])]

    try:
        a_sp, b_sp, simbolos, passos = simbolico.analisar_equacoes(
            st.session_state["sistemas_variaveis"], textos_equacoes
        )
    except ValueError as erro:
        st.error(str(erro))
        return

    barra_menus({
        "Equações": _menu_equacoes,
        "Ver": _menu_ver,
        "Exportar": lambda: _menu_exportar(a_sp, b_sp, simbolos),
    })

    n_variaveis = len(simbolos)
    a = simbolico.para_numpy(a_sp)
    b = simbolico.para_numpy(b_sp).reshape(-1)
    n_equacoes = a.shape[0]
    sistema_2x2 = (n_equacoes, n_variaveis) == (2, 2)

    solucoes, passos_resolucao = simbolico.resolver_sistema(a_sp, b_sp, simbolos)
    classificacao = simbolico.classificar_sistema(solucoes, simbolos)
    rotulo_classificacao = {
        "determinado": "✅ Sistema possível e determinado — solução única",
        "indeterminado": "♾️ Sistema possível e indeterminado — infinitas soluções",
        "impossivel": "🚫 Sistema impossível — não tem solução",
    }[classificacao]

    with st.container(border=True):
        st.markdown("##### Resultado")
        st.markdown(f"**Classificação:** {rotulo_classificacao}")
        solucao_latex = simbolico.formatar_solucao_sistema(solucoes, simbolos)
        if solucao_latex is not None:
            st.markdown("**Solução:**")
            st.latex(solucao_latex)

    if st.session_state["sistemas_passo_a_passo"]:
        mostrar_passos(passos + passos_resolucao)

    if n_variaveis == 2:
        st.divider()
        st.markdown("##### 📈 Interpretação gráfica")
        equacoes_visiveis = [(a[i, 0], a[i, 1], b[i]) for i in range(n_equacoes)
                              if st.session_state.get(f"sistemas_eq_mostrar_{i}", True)]
        if equacoes_visiveis:
            st.plotly_chart(figura_retas_2d(equacoes_visiveis, modo_leve=modo_leve_da_sessao()), width="stretch",
                             key="sistemas_grafico_principal")
        else:
            st.caption("Nenhuma equação selecionada para mostrar no gráfico — "
                       "marca a caixa \"Mostrar no gráfico\" junto de pelo menos uma equação.")

        if sistema_2x2 and st.session_state["sistemas_mostrar_exploracao"]:
            st.markdown("##### 🔎 Ver a reta e a interseção a variar")
            col_eq, col_coef = st.columns(2)
            with col_eq:
                eq_variavel = st.selectbox("Equação a variar", ["1ª equação", "2ª equação"], index=1)
            indice_eq = 0 if eq_variavel.startswith("1") else 1
            indice_fixa = 1 - indice_eq
            with col_coef:
                coef_variavel = st.selectbox(
                    "Coeficiente a variar",
                    [f"coeficiente de {simbolos[0]}", f"coeficiente de {simbolos[1]}"], index=1,
                )
            indice_coef = 0 if coef_variavel.endswith(str(simbolos[0])) else 1
            valor_atual = float(a[indice_eq, indice_coef])

            def calcular_equacao_variavel(valor, indice_eq=indice_eq, indice_coef=indice_coef):
                linha = [a[indice_eq, 0], a[indice_eq, 1]]
                linha[indice_coef] = valor
                return (linha[0], linha[1], b[indice_eq])

            equacao_fixa = (a[indice_fixa, 0], a[indice_fixa, 1], b[indice_fixa])
            rotulos_equacoes = (f"Eq. {indice_fixa + 1}", f"Eq. {indice_eq + 1}")

            st.caption("Arrasta o slider ou carrega em ▶ Play para ver a reta e a interseção a variar.")
            fig = figura_retas_2d_parametrizada(
                equacao_fixa, calcular_equacao_variavel,
                np.linspace(valor_atual - 3, valor_atual + 3, 30),
                rotulo_parametro=f"coef. de {simbolos[indice_coef]} (eq. {indice_eq + 1})",
                modo_leve=modo_leve_da_sessao(), rotulos_equacoes=rotulos_equacoes,
            )
            st.plotly_chart(fig, width="stretch", key="sistemas_grafico_exploracao")
        elif not sistema_2x2:
            st.caption("A exploração animada da reta só está disponível para sistemas de exatamente "
                       "2 equações e 2 incógnitas.")
    elif n_variaveis == 3:
        st.info("A visualização 3D da interseção de planos ficará disponível numa iteração seguinte "
                 "— a resolução simbólica acima já funciona para 3 variáveis.")
