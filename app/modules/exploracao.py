"""Módulo Exploração Gráfica: uma janela de gráficos maior, estilo GeoGebra,
onde cada equação escrita em texto livre no menu lateral (ex. "y = x^2 - 3",
"x^2 + y^2 = 9", "2x - y = 1") aparece desenhada na vista principal."""
from __future__ import annotations

import streamlit as st

from utils.componentes import cabecalho
from utils.exploracao_grafica import EquacaoInvalida, interpretar_e_amostrar
from utils.visualizacao import CORES_VETORES, figura_exploracao_grafica

EXEMPLOS = ["y = x^2 - 3", "y = sin(x)", "x^2 + y^2 = 9"]


def _inicializar_estado() -> None:
    st.session_state.setdefault("exploracao_n_eq", len(EXEMPLOS))
    for i, eq in enumerate(EXEMPLOS):
        st.session_state.setdefault(f"exploracao_eq_{i}", eq)
        st.session_state.setdefault(f"exploracao_eq_mostrar_{i}", True)
        st.session_state.setdefault(f"exploracao_eq_cor_{i}", CORES_VETORES[i % len(CORES_VETORES)])


def _adicionar_equacao() -> None:
    i = st.session_state["exploracao_n_eq"]
    st.session_state.setdefault(f"exploracao_eq_{i}", "")
    st.session_state.setdefault(f"exploracao_eq_mostrar_{i}", True)
    st.session_state.setdefault(f"exploracao_eq_cor_{i}", CORES_VETORES[i % len(CORES_VETORES)])
    st.session_state["exploracao_n_eq"] += 1


def _remover_ultima_equacao() -> None:
    if st.session_state["exploracao_n_eq"] > 1:
        st.session_state["exploracao_n_eq"] -= 1


def _repor_exemplos() -> None:
    st.session_state["exploracao_n_eq"] = len(EXEMPLOS)
    for i, eq in enumerate(EXEMPLOS):
        st.session_state[f"exploracao_eq_{i}"] = eq
        st.session_state[f"exploracao_eq_mostrar_{i}"] = True
        st.session_state[f"exploracao_eq_cor_{i}"] = CORES_VETORES[i % len(CORES_VETORES)]


def render() -> None:
    cabecalho("🧭 Exploração Gráfica", "Escreve equações em x e y — como no GeoGebra — e vê o gráfico ao vivo.")
    _inicializar_estado()

    col_menu, col_grafico = st.columns([1, 2.2])

    with col_menu:
        st.markdown("##### ✏️ Equações")
        st.caption("Ex.: y = x^2 - 3  ·  x^2 + y^2 = 9  ·  2x - y = 1  ·  sin(x)")
        for i in range(st.session_state["exploracao_n_eq"]):
            chave, chave_mostrar = f"exploracao_eq_{i}", f"exploracao_eq_mostrar_{i}"
            chave_cor = f"exploracao_eq_cor_{i}"
            st.session_state.setdefault(chave, "")
            st.session_state.setdefault(chave_mostrar, True)
            st.session_state.setdefault(chave_cor, CORES_VETORES[i % len(CORES_VETORES)])
            st.text_input(f"Equação {i + 1}", key=chave, placeholder="ex.: y = x^2")
            col_cor, col_mostrar = st.columns([1, 2])
            with col_cor:
                st.color_picker("Cor", key=chave_cor, label_visibility="collapsed")
            with col_mostrar:
                st.checkbox("Mostrar", key=chave_mostrar)
            st.divider()

        col_add, col_rem = st.columns(2)
        with col_add:
            st.button("➕ Adicionar", width="stretch", on_click=_adicionar_equacao, key="exploracao_btn_add")
        with col_rem:
            st.button("➖ Remover última", width="stretch", on_click=_remover_ultima_equacao,
                       disabled=st.session_state["exploracao_n_eq"] <= 1, key="exploracao_btn_rem")
        st.button("🔄 Repor exemplos", width="stretch", on_click=_repor_exemplos, key="exploracao_btn_reset")

    with col_grafico:
        curvas, erros = [], []
        for i in range(st.session_state["exploracao_n_eq"]):
            if not st.session_state.get(f"exploracao_eq_mostrar_{i}", True):
                continue
            texto = st.session_state.get(f"exploracao_eq_{i}", "").strip()
            if not texto:
                continue
            cor = st.session_state.get(f"exploracao_eq_cor_{i}", CORES_VETORES[i % len(CORES_VETORES)])
            try:
                resultado = interpretar_e_amostrar(texto)
                curvas.append((f"Eq. {i + 1}: {texto}", resultado, cor))
            except EquacaoInvalida as erro:
                erros.append(f"Equação {i + 1} (\"{texto}\"): {erro}")

        st.plotly_chart(figura_exploracao_grafica(curvas), width="stretch", key="exploracao_grafico_principal")

        for msg in erros:
            st.warning(msg)
