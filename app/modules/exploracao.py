"""Módulo Exploração Gráfica: uma janela de gráficos maior,
onde cada equação escrita em texto livre no menu lateral (ex. "y = x^2 - 3",
"x^2 + y^2 = 9", "2x - y = 1") aparece desenhada na vista principal."""
from __future__ import annotations  # permite anotações de tipo como "list[str]" independentemente da versão do Python

import numpy as np  # gera os valores do parâmetro animado (np.linspace)
import streamlit as st  # widgets desta página (inputs de equação, sliders, gráfico)

from utils.componentes import cabecalho  # título da página
from utils.exploracao_grafica import EquacaoInvalida, detetar_parametros, interpretar_e_amostrar  # motor de interpretação de equações
from utils.visualizacao import (
    CORES_VETORES,  # paleta de cores partilhada, usada para dar uma cor diferente a cada equação
    figura_exploracao_grafica,  # desenha o gráfico estático (sem parâmetro a animar)
    figura_exploracao_grafica_parametrizada,  # desenha o gráfico animado (com slider/Play do Plotly)
)

# As 3 equações de exemplo com que a página abre por omissão.
EXEMPLOS = ["y = x^2 - 3", "y = a*x + 2", "2x - y = 1"]
# Se cada equação de EXEMPLOS começa "visível" (marcada no gráfico) ou não —
# a 3ª (a reta) começa escondida, para o gráfico inicial não ficar sobrecarregado.
EXEMPLOS_MOSTRAR_DEFEITO = [True, True, False]
LIMITE_PARAMETRO = 5.0  # intervalo [-5, 5] usado tanto no slider manual como na animação


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
            # equação desmarcada ("Mostrar" desligado) — não entra no gráfico
            continue
        texto = texto.strip()
        if not texto:
            # caixa de equação vazia — nada a desenhar
            continue
        # cor atribuída a esta equação (ou a cor por omissão baseada na posição, se ainda não escolhida)
        cor = st.session_state.get(f"exploracao_eq_cor_{i}", CORES_VETORES[i % len(CORES_VETORES)])
        try:
            # interpreta o texto (com os parâmetros atuais) e obtém as curvas já amostradas
            resultado = interpretar_e_amostrar(texto, parametros=parametros)
            curvas.append((f"Eq. {i + 1}: {texto}", resultado, cor))
        except EquacaoInvalida as erro:
            if coletar_erros:
                # só regista o erro quando pedido (evita repetir o mesmo aviso ~30× durante a animação)
                erros.append(f"Equação {i + 1} (\"{texto}\"): {erro}")
    return curvas, erros


def _inicializar_estado() -> None:
    # nº de equações atualmente mostradas no menu — arranca com as 3 de EXEMPLOS
    st.session_state.setdefault("exploracao_n_eq", len(EXEMPLOS))
    for i, eq in enumerate(EXEMPLOS):
        # texto de cada equação, se ainda mostrar no gráfico e a sua cor —
        # `setdefault` só define na primeira visita, sem apagar o que o
        # utilizador já tenha escrito numa sessão em curso
        st.session_state.setdefault(f"exploracao_eq_{i}", eq)
        st.session_state.setdefault(f"exploracao_eq_mostrar_{i}", EXEMPLOS_MOSTRAR_DEFEITO[i])
        st.session_state.setdefault(f"exploracao_eq_cor_{i}", CORES_VETORES[i % len(CORES_VETORES)])


def _adicionar_equacao() -> None:
    # callback do botão "➕ Adicionar": cria uma nova caixa de equação vazia,
    # visível por omissão, com a próxima cor da paleta
    i = st.session_state["exploracao_n_eq"]
    st.session_state.setdefault(f"exploracao_eq_{i}", "")
    st.session_state.setdefault(f"exploracao_eq_mostrar_{i}", True)
    st.session_state.setdefault(f"exploracao_eq_cor_{i}", CORES_VETORES[i % len(CORES_VETORES)])
    st.session_state["exploracao_n_eq"] += 1


def _remover_ultima_equacao() -> None:
    # callback do botão "➖ Remover última": nunca deixa ficar com 0 equações
    if st.session_state["exploracao_n_eq"] > 1:
        st.session_state["exploracao_n_eq"] -= 1


def _repor_exemplos() -> None:
    # callback do botão "🔄 Repor exemplos": volta ao estado inicial de EXEMPLOS,
    # sobrescrevendo (não só "setdefault") o que o utilizador tiver escrito
    st.session_state["exploracao_n_eq"] = len(EXEMPLOS)
    for i, eq in enumerate(EXEMPLOS):
        st.session_state[f"exploracao_eq_{i}"] = eq
        st.session_state[f"exploracao_eq_mostrar_{i}"] = EXEMPLOS_MOSTRAR_DEFEITO[i]
        st.session_state[f"exploracao_eq_cor_{i}"] = CORES_VETORES[i % len(CORES_VETORES)]
    # Limpar estados de animação para os sliders ficarem ativos por defeito
    for chave in list(st.session_state.keys()):
        if chave.startswith("exploracao_animar_"):
            st.session_state[chave] = False


def _selecionar_animacao(nome_selecionado: str, todos_os_nomes: list[str]) -> None:
    """Callback do botão "🎬" de cada parâmetro — o Plotly só anima uma
    dimensão de cada vez, por isso ligar a animação de um parâmetro desliga a
    dos outros (um grupo tipo "rádio", mas com um botão ao lado de cada
    slider em vez de um seletor à parte)."""
    if st.session_state.get(f"exploracao_animar_{nome_selecionado}"):
        # este parâmetro acabou de ser ligado: desliga todos os outros,
        # garantindo que só um está animado de cada vez
        for outro in todos_os_nomes:
            if outro != nome_selecionado:
                st.session_state[f"exploracao_animar_{outro}"] = False


def render() -> None:
    cabecalho("🧭 Exploração Gráfica")  # título no topo da página
    _inicializar_estado()

    col_menu, col_grafico = st.columns([1, 2.2])  # menu de equações estreito, gráfico ocupa o resto

    # texto atual de cada equação (lista, uma entrada por caixa existente)
    textos_equacoes = [st.session_state.get(f"exploracao_eq_{i}", "")
                        for i in range(st.session_state["exploracao_n_eq"])]
    # conjunto de todos os nomes de parâmetros (letras extra) usados em
    # qualquer uma das equações, já ordenado alfabeticamente
    nomes_parametros = sorted(set().union(*(detetar_parametros(t) for t in textos_equacoes)))

    with col_menu, st.container(height=650):  # coluna do menu, com scroll próprio
        st.markdown("##### ✏️ Equações")
        st.caption("Ex.: y = x^2 - 3  ·  x^2 + y^2 = 9  ·  2x - y = 1  ·  y = a*x + 2 (com slider para a)")
        parametros_mostrados: set[str] = set()  # parâmetros cujo slider já foi desenhado nesta execução
        for i in range(st.session_state["exploracao_n_eq"]):
            chave, chave_mostrar = f"exploracao_eq_{i}", f"exploracao_eq_mostrar_{i}"
            chave_cor = f"exploracao_eq_cor_{i}"
            st.session_state.setdefault(chave, "")
            st.session_state.setdefault(chave_mostrar, True)
            st.session_state.setdefault(chave_cor, CORES_VETORES[i % len(CORES_VETORES)])
            # caixa de texto onde o utilizador escreve a equação
            st.text_input(f"Equação {i + 1}", key=chave, placeholder="ex.: y = x^2")
            col_cor, col_mostrar = st.columns([1, 3])
            with col_cor:
                # seletor de cor desta equação (sem rótulo visível, para poupar espaço)
                st.color_picker("Cor", key=chave_cor, label_visibility="collapsed", width=45)
            with col_mostrar:
                # caixa para ligar/desligar esta equação no gráfico
                st.checkbox("Mostrar", key=chave_mostrar)

            # o slider (e o botão de animar) de um parâmetro aparecem logo
            # abaixo da PRIMEIRA equação que o usa — não numa secção à parte.
            novos = sorted((detetar_parametros(st.session_state[chave]) & set(nomes_parametros))
                            - parametros_mostrados)
            for nome in novos:
                parametros_mostrados.add(nome)
                # valor inicial do parâmetro (1.0) — só define se ainda não existir
                st.session_state.setdefault(f"exploracao_param_{nome}", 1.0)
                # Por defeito, a animação fica DESLIGADA (False) para que o slider esteja ativo e movimentável
                st.session_state.setdefault(f"exploracao_animar_{nome}", False)
                a_animar = st.session_state.get(f"exploracao_animar_{nome}", False)

                col_slider, col_animar = st.columns([3.2, 1.8])
                with col_slider:
                    # slider manual do parâmetro — fica desativado enquanto a
                    # animação estiver ligada (nesse modo o valor é controlado
                    # pelo slider nativo do Plotly, por baixo do gráfico)
                    st.slider(
                        f"Parâmetro {nome}",
                        min_value=-LIMITE_PARAMETRO,
                        max_value=LIMITE_PARAMETRO,
                        step=0.1,
                        key=f"exploracao_param_{nome}",
                        disabled=a_animar,
                        help=f"Arrasta para alterar o valor de {nome} em tempo real",
                    )
                with col_animar:
                    # caixa para ligar a animação automática deste parâmetro;
                    # o on_change chama _selecionar_animacao para desligar os outros
                    st.checkbox(
                        "Animar",
                        key=f"exploracao_animar_{nome}",
                        help=f"Ativar/Desativar animação automática para {nome}",
                        on_change=_selecionar_animacao,
                        args=(nome, nomes_parametros),
                    )
                if a_animar:
                    # aviso de que o slider aqui está desativado por estar em modo animação
                    st.caption("🎬 Modo Animação ativo — usa os controlos ▶ Play no gráfico.")
            st.divider()

        if not nomes_parametros:
            # nenhuma equação usa ainda uma letra extra — dica de como ganhar um parâmetro
            st.caption("💡 Escreve uma letra extra numa equação (ex. \"y = a*x^2\") para "
                       "ganhares um slider fluido desse parâmetro, já pronto a arrastar ou animar.")

        col_add, col_rem = st.columns(2)
        with col_add:
            st.button("➕ Adicionar", width="stretch", on_click=_adicionar_equacao, key="exploracao_btn_add")
        with col_rem:
            st.button("➖ Remover última", width="stretch", on_click=_remover_ultima_equacao,
                       disabled=st.session_state["exploracao_n_eq"] <= 1, key="exploracao_btn_rem")
        st.button("🔄 Repor exemplos", width="stretch", on_click=_repor_exemplos, key="exploracao_btn_reset")

    # procura, entre todos os parâmetros, qual (no máximo um) está com a animação ligada
    parametro_animado = next(
        (nome for nome in nomes_parametros if st.session_state.get(f"exploracao_animar_{nome}", False)), None,
    )
    animar = parametro_animado is not None

    # valor atual (do slider) de cada parâmetro — usado quando NÃO se está a animar
    valores_parametros = {nome: st.session_state.get(f"exploracao_param_{nome}", 1.0)
                           for nome in nomes_parametros}

    with col_grafico, st.container(height=650):  # coluna do gráfico, com scroll próprio
        if animar and parametro_animado:
            def calcular_equacoes(valor, parametro_animado=parametro_animado):
                # função chamada uma vez por cada frame da animação: recalcula
                # todas as curvas com o parâmetro animado fixado em `valor`
                parametros_quadro = dict(valores_parametros)
                parametros_quadro[parametro_animado] = valor
                curvas_quadro, _ = _montar_curvas(textos_equacoes, parametros_quadro)
                return curvas_quadro

            st.caption("Arrasta o slider ou carrega em ▶ Play para ver a curva a variar.")
            # 30 valores igualmente espaçados no intervalo do parâmetro — um frame por valor
            valores_animacao = np.linspace(-LIMITE_PARAMETRO, LIMITE_PARAMETRO, 30)
            fig = figura_exploracao_grafica_parametrizada(
                calcular_equacoes, valores_animacao, rotulo_parametro=parametro_animado,
            )
            # recalcula também a versão "estática" (valores atuais dos sliders) só para recolher eventuais erros a mostrar
            _, erros = _montar_curvas(textos_equacoes, valores_parametros, coletar_erros=True)
        else:
            # sem animação: desenha o gráfico normal com os valores atuais dos parâmetros
            curvas, erros = _montar_curvas(textos_equacoes, valores_parametros, coletar_erros=True)
            fig = figura_exploracao_grafica(curvas)

        st.plotly_chart(fig, width="stretch", key="exploracao_grafico_principal")

        for msg in erros:
            # mostra um aviso por cada equação que não foi possível interpretar/desenhar
            st.warning(msg)
