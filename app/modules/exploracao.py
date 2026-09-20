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

EXEMPLOS = ["y = x^2 - 3", "y = sin(x)", "2x - y = 1"]
EXEMPLOS_MOSTRAR_DEFEITO = [True, True, False]
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
        st.session_state.setdefault(f"exploracao_eq_mostrar_{i}", EXEMPLOS_MOSTRAR_DEFEITO[i])
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
        st.session_state[f"exploracao_eq_mostrar_{i}"] = EXEMPLOS_MOSTRAR_DEFEITO[i]
        st.session_state[f"exploracao_eq_cor_{i}"] = CORES_VETORES[i % len(CORES_VETORES)]


def _selecionar_animacao(nome_selecionado: str, todos_os_nomes: list[str]) -> None:
    """Callback do botão "🎬" de cada parâmetro — o Plotly só anima uma
    dimensão de cada vez, por isso ligar a animação de um parâmetro desliga a
    dos outros (um grupo tipo "rádio", mas com um botão ao lado de cada
    slider em vez de um seletor à parte)."""
    if st.session_state.get(f"exploracao_animar_{nome_selecionado}"):
        for outro in todos_os_nomes:
            if outro != nome_selecionado:
                st.session_state[f"exploracao_animar_{outro}"] = False


def render() -> None:
    cabecalho("🧭 Exploração Gráfica")
    _inicializar_estado()

    col_menu, col_grafico = st.columns([1, 2.2])

    textos_equacoes = [st.session_state.get(f"exploracao_eq_{i}", "")
                        for i in range(st.session_state["exploracao_n_eq"])]
    nomes_parametros = sorted(set().union(*(detetar_parametros(t) for t in textos_equacoes)))

    with col_menu, st.container(height=650):
        st.markdown("##### ✏️ Equações")
        st.caption("Ex.: y = x^2 - 3  ·  x^2 + y^2 = 9  ·  2x - y = 1  ·  sin(x)  ·  y = a*x (com slider para a)")
        parametros_mostrados: set[str] = set()
        for i in range(st.session_state["exploracao_n_eq"]):
            chave, chave_mostrar = f"exploracao_eq_{i}", f"exploracao_eq_mostrar_{i}"
            chave_cor = f"exploracao_eq_cor_{i}"
            st.session_state.setdefault(chave, "")
            st.session_state.setdefault(chave_mostrar, True)
            st.session_state.setdefault(chave_cor, CORES_VETORES[i % len(CORES_VETORES)])
            st.text_input(f"Equação {i + 1}", key=chave, placeholder="ex.: y = x^2")
            col_cor, col_mostrar = st.columns([1, 3])
            with col_cor:
                st.color_picker("Cor", key=chave_cor, label_visibility="collapsed", width=45)
            with col_mostrar:
                st.checkbox("Mostrar", key=chave_mostrar)

            # o slider (e o botão de animar) de um parâmetro aparecem logo
            # abaixo da PRIMEIRA equação que o usa — não numa secção à parte.
            novos = sorted((detetar_parametros(st.session_state[chave]) & set(nomes_parametros))
                            - parametros_mostrados)
            for nome in novos:
                parametros_mostrados.add(nome)
                st.session_state.setdefault(f"exploracao_param_{nome}", 1.0)
                # o primeiro parâmetro que aparece fica já com o controlo
                # fluido (nativo do Plotly) ligado por omissão — só passa a
                # False se já houver outro ativo (só um pode estar de cada vez).
                ja_ha_algum_ativo = any(st.session_state.get(f"exploracao_animar_{outro}", False)
                                         for outro in nomes_parametros)
                st.session_state.setdefault(f"exploracao_animar_{nome}", not ja_ha_algum_ativo)
                a_animar = st.session_state[f"exploracao_animar_{nome}"]
                col_slider, col_animar = st.columns([4, 1])
                with col_slider:
                    # desativado enquanto anima: nesse modo quem manda no
                    # valor é o slider nativo do Plotly por baixo do gráfico
                    # (a animação percorre sempre o intervalo todo), por isso
                    # arrastar este aqui não mudaria nada — evita a confusão.
                    st.slider(f"Parâmetro {nome}", min_value=-LIMITE_PARAMETRO, max_value=LIMITE_PARAMETRO,
                               step=0.1, key=f"exploracao_param_{nome}", disabled=a_animar)
                with col_animar:
                    st.checkbox("🎬", key=f"exploracao_animar_{nome}", help=f"Animar o parâmetro \"{nome}\"",
                                on_change=_selecionar_animacao, args=(nome, nomes_parametros))
                if a_animar:
                    st.caption("🎬 A animar — usa o slider por baixo do gráfico.")
            st.divider()

        if not nomes_parametros:
            st.caption("💡 Escreve uma letra extra numa equação (ex. \"y = a*x^2\") para "
                       "ganhares um slider fluido desse parâmetro, já pronto a arrastar ou animar.")

        col_add, col_rem = st.columns(2)
        with col_add:
            st.button("➕ Adicionar", width="stretch", on_click=_adicionar_equacao, key="exploracao_btn_add")
        with col_rem:
            st.button("➖ Remover última", width="stretch", on_click=_remover_ultima_equacao,
                       disabled=st.session_state["exploracao_n_eq"] <= 1, key="exploracao_btn_rem")
        st.button("🔄 Repor exemplos", width="stretch", on_click=_repor_exemplos, key="exploracao_btn_reset")

    parametro_animado = next(
        (nome for nome in nomes_parametros if st.session_state.get(f"exploracao_animar_{nome}", False)), None,
    )
    animar = parametro_animado is not None

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
