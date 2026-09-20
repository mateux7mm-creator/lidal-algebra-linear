"""Módulo Exploração Gráfica: uma janela de gráficos maior, estilo GeoGebra,
onde cada equação escrita em texto livre no menu lateral (ex. "y = x^2 - 3",
"x^2 + y^2 = 9", "2x - y = 1") aparece desenhada na vista principal."""
from __future__ import annotations

import numpy as np
import streamlit as st

from utils.componentes import cabecalho
from utils.exploracao_grafica import EquacaoInvalida, detetar_parametros, interpretar_e_amostrar
from utils.visualizacao import (
    CORES_VETORES,
    figura_exploracao_grafica,
    figura_exploracao_grafica_parametrizada,
)

EXEMPLOS = ["y = x^2 - 3", "y = sin(x)", "x^2 + y^2 = 9"]
LIMITE_PARAMETRO = 5.0


def _montar_curvas(
    textos_equacoes: list[str], parametros: dict[str, float], coletar_erros: bool = False,
) -> tuple[list[tuple[str, object, str]], list[str]]:
    """Interpreta cada equação visível com os valores de `parametros` dados,
    devolvendo (curvas, erros) — partilhado entre a vista estática e cada
    frame da vista animada (que chama isto ~30× por parâmetro, por isso os
    erros só se recolhem quando pedido, para não repetir o mesmo aviso)."""
    curvas: list[tuple[str, object, str]] = []
    erros: list[str] = []
    for i, texto in enumerate(textos_equacoes):
        if not st.session_state.get(f"exploracao_eq_mostrar_{i}", True):
            continue
        texto = texto.strip()
        if not texto:
            continue
        cor = st.session_state.get(f"exploracao_eq_cor_{i}", CORES_VETORES[i % len(CORES_VETORES)])
        try:
            resultado = interpretar_e_amostrar(texto, parametros=parametros)
            curvas.append((f"Eq. {i + 1}: {texto}", resultado, cor))
        except EquacaoInvalida as erro:
            if coletar_erros:
                erros.append(f"Equação {i + 1} (\"{texto}\"): {erro}")
    return curvas, erros


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
    cabecalho("🧭 Exploração Gráfica")
    _inicializar_estado()

    col_menu, col_grafico = st.columns([1, 2.2])

    textos_equacoes = [st.session_state.get(f"exploracao_eq_{i}", "")
                        for i in range(st.session_state["exploracao_n_eq"])]
    nomes_parametros = sorted(set().union(*(detetar_parametros(t) for t in textos_equacoes)))

    with col_menu, st.container(height=650):
        st.markdown("##### ✏️ Equações")
        st.caption("Ex.: y = x^2 - 3  ·  x^2 + y^2 = 9  ·  2x - y = 1  ·  sin(x)  ·  y = a·x (com slider para a)")
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

        animar = False
        parametro_animado = None
        if nomes_parametros:
            st.markdown("##### 🎚️ Parâmetros")
            st.caption("Letras usadas nas equações além de x/y viram sliders (estilo GeoGebra).")
            for nome in nomes_parametros:
                st.session_state.setdefault(f"exploracao_param_{nome}", 1.0)
                st.slider(nome, min_value=-LIMITE_PARAMETRO, max_value=LIMITE_PARAMETRO, step=0.1,
                           key=f"exploracao_param_{nome}")

            st.markdown("##### 🎬 Animação")
            animar = st.checkbox("Animar um parâmetro", key="exploracao_animar")
            if animar:
                parametro_animado = st.selectbox("Qual parâmetro animar", nomes_parametros,
                                                  key="exploracao_parametro_animado")

    valores_parametros = {nome: st.session_state.get(f"exploracao_param_{nome}", 1.0)
                           for nome in nomes_parametros}

    with col_grafico, st.container(height=650):
        if animar and parametro_animado:
            def calcular_equacoes(valor, parametro_animado=parametro_animado):
                parametros_quadro = dict(valores_parametros)
                parametros_quadro[parametro_animado] = valor
                curvas_quadro, _ = _montar_curvas(textos_equacoes, parametros_quadro)
                return curvas_quadro

            st.caption("Arrasta o slider ou carrega em ▶ Play para ver a curva a variar.")
            valores_animacao = np.linspace(-LIMITE_PARAMETRO, LIMITE_PARAMETRO, 30)
            fig = figura_exploracao_grafica_parametrizada(
                calcular_equacoes, valores_animacao, rotulo_parametro=parametro_animado,
            )
            _, erros = _montar_curvas(textos_equacoes, valores_parametros, coletar_erros=True)
        else:
            curvas, erros = _montar_curvas(textos_equacoes, valores_parametros, coletar_erros=True)
            fig = figura_exploracao_grafica(curvas)

        st.plotly_chart(fig, width="stretch", key="exploracao_grafico_principal")

        for msg in erros:
            st.warning(msg)
