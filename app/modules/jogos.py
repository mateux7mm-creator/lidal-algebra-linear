"""Módulo Jogos e Desafios: gamificação da aprendizagem dos 5 tópicos.

Cada tópico tem um desafio de quiz (escolha múltipla, gerado aleatoriamente e
contextualizado) e um desafio visual (clicar no gráfico Plotly certo). O
"modo turma" é opcional: com um código de turma e um nome, cada resposta
correta é registada em `utils.pontuacao` e aparece num ranking partilhado.
"""
from __future__ import annotations

import time

import streamlit as st

from utils import desafios, pontuacao
from utils.componentes import cabecalho

TOPICOS = ["Matrizes", "Determinantes", "Sistemas Lineares", "Vetores", "Valores Próprios"]

GERADORES_QUIZ = {
    "Matrizes": desafios.gerar_desafio_matrizes,
    "Determinantes": desafios.gerar_desafio_determinantes,
    "Sistemas Lineares": desafios.gerar_desafio_sistemas,
    "Vetores": desafios.gerar_desafio_vetores,
    "Valores Próprios": desafios.gerar_desafio_valores_proprios,
}
GERADORES_VISUAL = {
    "Matrizes": desafios.gerar_desafio_visual_matrizes,
    "Determinantes": desafios.gerar_desafio_visual_determinantes,
    "Sistemas Lineares": desafios.gerar_desafio_visual_sistemas,
    "Vetores": desafios.gerar_desafio_visual_vetores,
    "Valores Próprios": desafios.gerar_desafio_visual_valores_proprios,
}


def _pontuacao_sessao() -> dict:
    if "jogos_pontuacao" not in st.session_state:
        st.session_state["jogos_pontuacao"] = {t: 0 for t in TOPICOS}
    return st.session_state["jogos_pontuacao"]


def _registar_pontos(topico: str, pontos: int) -> None:
    _pontuacao_sessao()[topico] += pontos
    codigo_turma = st.session_state.get("jogos_codigo_turma", "").strip()
    nome = st.session_state.get("jogos_nome_jogador", "").strip()
    if codigo_turma and nome and pontos > 0:
        pontuacao.registar_pontuacao(codigo_turma, nome, topico, pontos)


def _pontos_por_tempo(inicio: float) -> int:
    segundos = time.time() - inicio
    return max(0, 100 - int(segundos))


def render() -> None:
    cabecalho("🎮 Jogos e Desafios", "Pratica os conteúdos de forma gamificada, sozinho ou em turma.")

    with st.sidebar:
        st.divider()
        st.markdown("**🏫 Modo turma** (opcional)")
        st.text_input("Código de turma", key="jogos_codigo_turma")
        st.text_input("O teu nome", key="jogos_nome_jogador")

    pontuacoes = _pontuacao_sessao()
    with st.container(border=True):
        st.caption("Pontuação da sessão")
        st.markdown(" · ".join(f"**{t}**: {p}" for t, p in pontuacoes.items()))

    col_topico, col_botao = st.columns([3, 1])
    with col_topico:
        topico = st.selectbox("Escolhe o tópico", TOPICOS)
    with col_botao:
        st.write("")
        if st.button("🔄 Novo desafio", width="stretch"):
            st.session_state.pop(f"jogos_quiz_{topico}", None)
            st.session_state.pop(f"jogos_visual_{topico}", None)

    st.divider()
    _render_quiz(topico)
    st.divider()
    _render_visual(topico)

    codigo_turma = st.session_state.get("jogos_codigo_turma", "").strip()
    if codigo_turma:
        st.divider()
        st.markdown(f"##### 🏆 Ranking da turma '{codigo_turma}' — {topico}")
        ranking = pontuacao.obter_ranking(codigo_turma, topico=topico)
        if ranking:
            st.table(ranking)
        else:
            st.caption("Ainda sem pontuações registadas para este tópico.")


def _render_quiz(topico: str) -> None:
    st.markdown("##### ⚡ Quiz rápido")
    chave = f"jogos_quiz_{topico}"
    if chave not in st.session_state:
        st.session_state[chave] = {"desafio": GERADORES_QUIZ[topico](), "inicio": time.time(), "respondido": False}
    estado = st.session_state[chave]
    desafio = estado["desafio"]

    with st.container(border=True):
        st.write(desafio.pergunta)
        escolha = st.radio("Escolhe a resposta:", desafio.opcoes, key=f"jogos_quiz_radio_{topico}")

    if not estado["respondido"] and st.button("Responder", key=f"jogos_quiz_responder_{topico}"):
        estado["respondido"] = True
        estado["correto"] = desafio.opcoes.index(escolha) == desafio.indice_correto
        estado["pontos"] = _pontos_por_tempo(estado["inicio"]) if estado["correto"] else 0
        if estado["correto"]:
            _registar_pontos(topico, estado["pontos"])

    if estado["respondido"]:
        if estado["correto"]:
            st.success(f"✅ Correto! +{estado['pontos']} pontos. {desafio.explicacao}")
        else:
            st.error(f"❌ Não é essa. {desafio.explicacao}")


def _render_visual(topico: str) -> None:
    st.markdown("##### 🎯 Desafio visual")
    chave = f"jogos_visual_{topico}"
    if chave not in st.session_state:
        desafio, fig = GERADORES_VISUAL[topico]()
        st.session_state[chave] = {"desafio": desafio, "figura": fig, "inicio": time.time(), "respondido": False}
    estado = st.session_state[chave]
    desafio = estado["desafio"]

    st.write(desafio.instrucao)
    chave_grafico = f"jogos_grafico_{topico}"
    st.plotly_chart(estado["figura"], width="stretch", on_select="rerun", key=chave_grafico)

    evento = st.session_state.get(chave_grafico)
    pontos_clicados = evento["selection"]["points"] if evento and evento.get("selection") else []

    if pontos_clicados and not estado["respondido"]:
        ponto = pontos_clicados[0]
        xy = (ponto.get("x", 0.0), ponto.get("y", 0.0))
        estado["respondido"] = True
        estado["correto"] = desafios.verificar_resposta_visual(desafio, xy)
        estado["pontos"] = _pontos_por_tempo(estado["inicio"]) if estado["correto"] else 0
        if estado["correto"]:
            _registar_pontos(topico, estado["pontos"])

    if estado["respondido"]:
        if estado["correto"]:
            st.success(f"✅ Correto! +{estado['pontos']} pontos. {desafio.explicacao}")
        else:
            st.error(f"❌ Não foi bem esse ponto. {desafio.explicacao}")
