"""Módulo Jogos e Desafios: gamificação da aprendizagem dos 5 tópicos.

Dois modos, escolhidos num submenu no topo da página:
- "Jogo Cronometrado": perguntas de escolha múltipla contra o relógio, com
  nível a subir a cada N perguntas (o tempo por pergunta encurta a cada
  nível), pontos acumulados por velocidade de resposta, e um resumo final.
- "Modo Livre": o quiz + desafio visual por tópico já existente, sem
  cronómetro, com botão "Novo desafio" manual.

Em ambos os modos, o "modo turma" é opcional: com um código de turma e um
nome (na barra lateral), cada resposta correta é registada em
`utils.pontuacao` e aparece num ranking partilhado.
"""
from __future__ import annotations

import random
import time

import streamlit as st

from utils import desafios, pontuacao
from utils.componentes import cabecalho

TOPICOS = ["Matrizes", "Determinantes", "Sistemas Lineares", "Vetores", "Valores Próprios"]
TOPICOS_CRONOMETRADO = ["🔀 Todos os tópicos (aleatório)"] + TOPICOS

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

PERGUNTAS_POR_NIVEL = 3
TEMPO_INICIAL_S = 25
TEMPO_MINIMO_S = 8
DECREMENTO_POR_NIVEL_S = 3
PONTOS_BASE = 100
PONTOS_MINIMOS_ACERTO = 10

MODOS = ["🕒 Jogo Cronometrado", "📝 Modo Livre (por tópico)"]


def _pontuacao_sessao() -> dict:
    if "jogos_pontuacao" not in st.session_state:
        st.session_state["jogos_pontuacao"] = {t: 0 for t in TOPICOS}
    return st.session_state["jogos_pontuacao"]


def _registar_pontos(topico: str, pontos: int, nome: str | None = None) -> None:
    """`nome` substitui o campo da barra lateral quando indicado — usado pelo
    Jogo Cronometrado, que tem o seu próprio campo de nome e não pode escrever
    em `st.session_state["jogos_nome_jogador"]` depois desse widget da
    barra lateral já ter sido instanciado nesta execução."""
    _pontuacao_sessao()[topico] += pontos
    codigo_turma = st.session_state.get("jogos_codigo_turma", "").strip()
    nome_final = (nome if nome is not None else st.session_state.get("jogos_nome_jogador", "")).strip()
    if codigo_turma and nome_final and pontos > 0:
        pontuacao.registar_pontuacao(codigo_turma, nome_final, topico, pontos)


def _pontos_por_tempo(inicio: float) -> int:
    segundos = time.time() - inicio
    return max(0, 100 - int(segundos))


def render() -> None:
    cabecalho("🎮 Jogos e Desafios")

    with st.sidebar:
        st.divider()
        st.markdown("**🏫 Modo turma** (opcional)")
        st.text_input("Código de turma", key="jogos_codigo_turma")
        st.text_input("O teu nome", key="jogos_nome_jogador")

    modo = st.radio("Escolhe o modo", MODOS, horizontal=True, key="jogos_modo_escolhido")
    st.divider()

    with st.container(key="pagina_jogos"):
        if modo == MODOS[0]:
            _render_cronometrado()
        else:
            _render_modo_livre()


# --------------------------------------------------------------------------
# Modo Livre (quiz + desafio visual por tópico, sem cronómetro)
# --------------------------------------------------------------------------

def _mostrar_resultado(resultado: tuple[bool, str]) -> None:
    correto, mensagem = resultado
    if correto:
        st.success(mensagem)
    else:
        st.error(mensagem)


def _render_modo_livre() -> None:
    col_esquerda, col_direita = st.columns([3, 2])

    with col_esquerda, st.container(height=650):
        col_topico, col_botao = st.columns([3, 1])
        with col_topico:
            topico = st.selectbox("Escolhe o tópico", TOPICOS)
        with col_botao:
            st.write("")
            if st.button("🔄 Novo desafio", width="stretch"):
                st.session_state.pop(f"jogos_quiz_{topico}", None)
                st.session_state.pop(f"jogos_visual_{topico}", None)

        st.divider()
        resultado_quiz = _render_quiz(topico)
        st.divider()
        resultado_visual = _render_visual(topico)

    with col_direita, st.container(height=650):
        st.markdown("##### 📊 Pontuação e resultados")
        pontuacoes = _pontuacao_sessao()
        with st.container(border=True):
            st.caption("Pontuação da sessão")
            st.markdown(" · ".join(f"**{t}**: {p}" for t, p in pontuacoes.items()))

        if resultado_quiz is not None:
            _mostrar_resultado(resultado_quiz)
        if resultado_visual is not None:
            _mostrar_resultado(resultado_visual)

        codigo_turma = st.session_state.get("jogos_codigo_turma", "").strip()
        if codigo_turma:
            st.markdown(f"##### 🏆 Ranking da turma '{codigo_turma}' — {topico}")
            ranking = pontuacao.obter_ranking(codigo_turma, topico=topico)
            if ranking:
                st.table(ranking)
            else:
                st.caption("Ainda sem pontuações registadas para este tópico.")


def _render_quiz(topico: str) -> tuple[bool, str] | None:
    """Desenha a pergunta + escolha (coluna principal) e devolve o resultado
    (correto, mensagem) para a coluna de pontuação, ou None se ainda por responder."""
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

    if not estado["respondido"]:
        return None
    if estado["correto"]:
        return True, f"⚡ Quiz — ✅ Correto! +{estado['pontos']} pontos. {desafio.explicacao}"
    return False, f"⚡ Quiz — ❌ Não é essa. {desafio.explicacao}"


def _render_visual(topico: str) -> tuple[bool, str] | None:
    """Desenha o desafio visual (coluna principal) e devolve o resultado
    (correto, mensagem) para a coluna de pontuação, ou None se ainda por responder."""
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

    if not estado["respondido"]:
        return None
    if estado["correto"]:
        return True, f"🎯 Visual — ✅ Correto! +{estado['pontos']} pontos. {desafio.explicacao}"
    return False, f"🎯 Visual — ❌ Não foi bem esse ponto. {desafio.explicacao}"


# --------------------------------------------------------------------------
# Jogo Cronometrado
# --------------------------------------------------------------------------

def _tempo_limite_para_nivel(nivel: int) -> int:
    return max(TEMPO_MINIMO_S, TEMPO_INICIAL_S - (nivel - 1) * DECREMENTO_POR_NIVEL_S)


def _estado_cronometrado() -> dict:
    return st.session_state.setdefault("jogos_cron", {
        "ativo": False,
        "nome": "",
        "topico": TOPICOS_CRONOMETRADO[0],
        "topico_pergunta": "",
        "nivel": 1,
        "pontos": 0,
        "n_perguntas": 0,
        "n_corretas": 0,
        "perguntas_no_nivel": 0,
        "pergunta_atual": None,
        "inicio_pergunta": 0.0,
        "tempo_limite": TEMPO_INICIAL_S,
        "respondida": False,
        "correta": False,
        "expirado": False,
        "pontos_pergunta": 0,
    })


def _gerar_pergunta_cronometrado(estado: dict) -> None:
    topico_pergunta = estado["topico"]
    if topico_pergunta == TOPICOS_CRONOMETRADO[0]:
        topico_pergunta = random.choice(TOPICOS)
    estado["topico_pergunta"] = topico_pergunta
    estado["pergunta_atual"] = GERADORES_QUIZ[topico_pergunta]()
    estado["inicio_pergunta"] = time.time()
    estado["tempo_limite"] = _tempo_limite_para_nivel(estado["nivel"])
    estado["respondida"] = False
    estado["correta"] = False
    estado["expirado"] = False
    estado["pontos_pergunta"] = 0


def _verificar_subida_nivel(estado: dict) -> None:
    if estado["perguntas_no_nivel"] >= PERGUNTAS_POR_NIVEL:
        estado["nivel"] += 1
        estado["perguntas_no_nivel"] = 0
        st.toast(f"🎉 Subiste para o nível {estado['nivel']}!")


def _responder_cronometrado(estado: dict, escolha: str) -> None:
    desafio = estado["pergunta_atual"]
    estado["respondida"] = True
    estado["n_perguntas"] += 1
    estado["perguntas_no_nivel"] += 1
    correta = desafio.opcoes.index(escolha) == desafio.indice_correto
    estado["correta"] = correta
    if correta:
        decorrido = time.time() - estado["inicio_pergunta"]
        restante = max(0.0, estado["tempo_limite"] - decorrido)
        pontos = max(PONTOS_MINIMOS_ACERTO, int(PONTOS_BASE * (restante / estado["tempo_limite"])))
        estado["pontos_pergunta"] = pontos
        estado["pontos"] += pontos
        estado["n_corretas"] += 1
        _registar_pontos(estado["topico_pergunta"], pontos, nome=estado["nome"])
    else:
        estado["pontos_pergunta"] = 0
    _verificar_subida_nivel(estado)


@st.fragment(run_every=1)
def _cronometro_pergunta() -> None:
    """Fragmento independente: atualiza a barra de progresso a cada segundo
    sem voltar a correr a página toda — só quando o tempo esgota é que força
    um rerun completo, para a pergunta seguinte reagir imediatamente."""
    estado = st.session_state["jogos_cron"]
    if estado["respondida"]:
        st.progress(0.0 if estado["expirado"] else 1.0,
                    text="⏰ Tempo esgotado" if estado["expirado"] else "✅ Respondido")
        return
    decorrido = time.time() - estado["inicio_pergunta"]
    restante = max(0.0, estado["tempo_limite"] - decorrido)
    st.progress(restante / estado["tempo_limite"], text=f"⏱️ {int(restante) + 1}s restantes")
    if restante <= 0:
        estado["respondida"] = True
        estado["correta"] = False
        estado["expirado"] = True
        estado["n_perguntas"] += 1
        estado["perguntas_no_nivel"] += 1
        _verificar_subida_nivel(estado)
        st.rerun()


def _render_resumo_cronometrado(estado: dict) -> None:
    st.markdown(f"##### 🏁 Resumo de {estado['nome']}")
    taxa = (estado["n_corretas"] / estado["n_perguntas"] * 100) if estado["n_perguntas"] else 0.0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nível alcançado", estado["nivel"])
    col2.metric("Perguntas respondidas", estado["n_perguntas"])
    col3.metric("Pontos totais", estado["pontos"])
    col4.metric("Taxa de acerto", f"{taxa:.0f}%")


def _render_cronometrado_config() -> None:
    estado = _estado_cronometrado()
    if estado["n_perguntas"] > 0:
        _render_resumo_cronometrado(estado)
        st.divider()

    st.caption(
        f"Responde a perguntas de escolha múltipla contra o relógio — o nível sobe a cada "
        f"{PERGUNTAS_POR_NIVEL} perguntas, e o tempo por pergunta encurta a cada nível "
        f"(começa em {TEMPO_INICIAL_S}s, nunca menos de {TEMPO_MINIMO_S}s)."
    )
    nome_defeito = estado["nome"] or st.session_state.get("jogos_nome_jogador", "")
    nome = st.text_input("O teu nome", value=nome_defeito, key="jogos_cron_nome_input")
    topico = st.selectbox("Tópico", TOPICOS_CRONOMETRADO, key="jogos_cron_topico_input")

    if st.button("▶ Começar", key="jogos_cron_comecar", width="stretch", type="primary"):
        if not nome.strip():
            st.warning("Escreve o teu nome antes de começar.")
            return
        estado.update({
            "ativo": True, "nome": nome.strip(), "topico": topico, "nivel": 1, "pontos": 0,
            "n_perguntas": 0, "n_corretas": 0, "perguntas_no_nivel": 0, "pergunta_atual": None,
        })
        st.rerun()


def _render_cronometrado_jogo() -> None:
    estado = _estado_cronometrado()
    if estado["pergunta_atual"] is None:
        _gerar_pergunta_cronometrado(estado)
    desafio = estado["pergunta_atual"]

    col_esquerda, col_direita = st.columns([3, 2])

    with col_esquerda, st.container(height=650):
        _cronometro_pergunta()

        with st.container(border=True):
            st.caption(f"Tópico: {estado['topico_pergunta']} · Jogador: {estado['nome']}")
            st.write(desafio.pergunta)
            escolha = st.radio("Escolhe a resposta:", desafio.opcoes, key="jogos_cron_radio",
                                disabled=estado["respondida"])

        if not estado["respondida"]:
            col_responder, col_fim = st.columns([3, 1])
            with col_responder:
                if st.button("Responder", key="jogos_cron_responder", width="stretch", type="primary"):
                    _responder_cronometrado(estado, escolha)
                    st.rerun()
            with col_fim:
                if st.button("🏁 Terminar", key="jogos_cron_terminar", width="stretch"):
                    estado["ativo"] = False
                    st.rerun()
        else:
            col_prox, col_fim = st.columns(2)
            with col_prox:
                if st.button("➡️ Próxima pergunta", key="jogos_cron_proxima", width="stretch", type="primary"):
                    _gerar_pergunta_cronometrado(estado)
                    st.rerun()
            with col_fim:
                if st.button("🏁 Terminar e ver resumo", key="jogos_cron_terminar", width="stretch"):
                    estado["ativo"] = False
                    st.rerun()

    with col_direita, st.container(height=650):
        st.markdown("##### 📊 Pontuação")
        col_nivel, col_perg = st.columns(2)
        col_nivel.metric("Nível", estado["nivel"])
        col_perg.metric("Pergunta", estado["n_perguntas"] + 1)
        col_pontos, col_acerto = st.columns(2)
        col_pontos.metric("Pontos", estado["pontos"])
        taxa = (estado["n_corretas"] / estado["n_perguntas"] * 100) if estado["n_perguntas"] else 0.0
        col_acerto.metric("Acerto", f"{taxa:.0f}%")

        if estado["respondida"]:
            st.markdown("##### 📝 Resultado")
            if estado["expirado"]:
                st.error(f"⏰ Tempo esgotado! {desafio.explicacao}")
            elif estado["correta"]:
                st.success(f"✅ Correto! +{estado['pontos_pergunta']} pontos. {desafio.explicacao}")
            else:
                st.error(f"❌ Não é essa. {desafio.explicacao}")


def _render_cronometrado() -> None:
    estado = _estado_cronometrado()
    if estado["ativo"]:
        _render_cronometrado_jogo()
    else:
        _render_cronometrado_config()
