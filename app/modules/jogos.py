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
from __future__ import annotations  # permite anotações de tipo modernas (ex. "str | None") em qualquer versão

import random  # escolhe o tópico aleatório no Jogo Cronometrado
import time  # mede o tempo decorrido, para pontuação por velocidade e para o cronómetro

import sympy as sp  # formata a matriz do Desafio com Pistas em LaTeX
import streamlit as st  # widgets desta página

from utils import desafios, pontuacao  # geradores de perguntas/desafios + persistência do ranking (SQLite)
from utils.componentes import cabecalho  # título da página

# Os 5 tópicos que o jogo cobre, na mesma ordem usada nos outros módulos.
TOPICOS = ["Matrizes", "Determinantes", "Sistemas Lineares", "Vetores", "Valores Próprios"]
# Lista usada no seletor de tópico do Jogo Cronometrado: acrescenta a opção "aleatório" à frente.
TOPICOS_CRONOMETRADO = ["🔀 Todos os tópicos (aleatório)"] + TOPICOS

# Dicionário tópico -> função geradora do quiz de escolha múltipla desse tópico
# (cada uma devolve um objeto Desafio de utils/desafios.py).
GERADORES_QUIZ = {
    "Matrizes": desafios.gerar_desafio_matrizes,
    "Determinantes": desafios.gerar_desafio_determinantes,
    "Sistemas Lineares": desafios.gerar_desafio_sistemas,
    "Vetores": desafios.gerar_desafio_vetores,
    "Valores Próprios": desafios.gerar_desafio_valores_proprios,
}
# Dicionário tópico -> função geradora do desafio visual (clicar no gráfico) desse tópico
# (cada uma devolve um par (DesafioVisual, figura Plotly)).
GERADORES_VISUAL = {
    "Matrizes": desafios.gerar_desafio_visual_matrizes,
    "Determinantes": desafios.gerar_desafio_visual_determinantes,
    "Sistemas Lineares": desafios.gerar_desafio_visual_sistemas,
    "Vetores": desafios.gerar_desafio_visual_vetores,
    "Valores Próprios": desafios.gerar_desafio_visual_valores_proprios,
}

# Parâmetros de progressão/pontuação do Jogo Cronometrado.
PERGUNTAS_POR_NIVEL = 3  # quantas perguntas por nível até subir
TEMPO_INICIAL_S = 25  # tempo limite (segundos) no nível 1
TEMPO_MINIMO_S = 8  # o tempo nunca encurta abaixo disto
DECREMENTO_POR_NIVEL_S = 3  # quantos segundos a menos por cada nível acima do 1º
PONTOS_BASE = 100  # pontuação máxima possível numa resposta certa instantânea
PONTOS_MINIMOS_ACERTO = 10  # pontuação mínima garantida numa resposta certa (mesmo no limite do tempo)

# As 3 entradas do submenu "Escolhe o modo", no topo da página.
MODOS = ["🕒 Jogo Cronometrado", "📝 Modo Livre (por tópico)", "🧩 Desafio com Pistas"]

# Pontuação do modo "Desafio com Pistas" (ver _render_desafio_progressivo).
PONTOS_FASE1_PRIMEIRA_TENTATIVA = 50  # acertar o determinante à primeira, sem pedir pista
PONTOS_FASE1_COM_PISTA = 20  # acertar depois de errar e/ou pedir a pista
PONTOS_FASE2 = 50  # acertar se a matriz tem ou não inversa


def _pontuacao_sessao() -> dict:
    # dicionário tópico -> pontos acumulados NESTA sessão (Modo Livre),
    # criado a zeros na primeira chamada e reutilizado depois
    if "jogos_pontuacao" not in st.session_state:
        st.session_state["jogos_pontuacao"] = {t: 0 for t in TOPICOS}
    return st.session_state["jogos_pontuacao"]


def _registar_pontos(topico: str, pontos: int, nome: str | None = None) -> None:
    """`nome` substitui o campo da barra lateral quando indicado — usado pelo
    Jogo Cronometrado, que tem o seu próprio campo de nome e não pode escrever
    em `st.session_state["jogos_nome_jogador"]` depois desse widget da
    barra lateral já ter sido instanciado nesta execução."""
    _pontuacao_sessao()[topico] += pontos  # soma sempre à pontuação da sessão (mesmo sem modo turma)
    codigo_turma = st.session_state.get("jogos_codigo_turma", "").strip()
    # usa o nome explícito, se dado; senão lê o campo da barra lateral
    nome_final = (nome if nome is not None else st.session_state.get("jogos_nome_jogador", "")).strip()
    if codigo_turma and nome_final and pontos > 0:
        # só grava no ranking partilhado (SQLite) se houver turma + nome preenchidos e pontos a somar
        pontuacao.registar_pontuacao(codigo_turma, nome_final, topico, pontos)


def _pontos_por_tempo(inicio: float) -> int:
    # quanto mais rápido responder, mais pontos (até 100), nunca abaixo de 0
    segundos = time.time() - inicio
    return max(0, 100 - int(segundos))


def render() -> None:
    cabecalho("🎮 Jogos e Desafios")  # título no topo da página

    with st.sidebar:
        st.divider()
        st.markdown("**🏫 Modo turma** (opcional)")
        # campos opcionais: se preenchidos, as pontuações ficam guardadas num ranking partilhado
        st.text_input("Código de turma", key="jogos_codigo_turma")
        st.text_input("O teu nome", key="jogos_nome_jogador")

    # Enquanto uma pergunta cronometrada está ativa, esconde o seletor de modo
    # (o jogador não deve trocar de modo a meio de uma pergunta contra o
    # relógio) — reaparece assim que a sessão termina, ou sempre no Modo Livre.
    estado_cron = st.session_state.get("jogos_cron", {})
    modo_anterior = st.session_state.get("jogos_modo_escolhido", MODOS[0])
    a_jogar_cronometrado = estado_cron.get("ativo", False) and modo_anterior == MODOS[0]

    if a_jogar_cronometrado:
        # jogo a decorrer: mantém o modo anterior sem desenhar o seletor
        modo = modo_anterior
    else:
        # fora de jogo: mostra o seletor normalmente
        modo = st.radio("Escolhe o modo", MODOS, horizontal=True, key="jogos_modo_escolhido")
        st.divider()

    with st.container(key="pagina_jogos"):  # container com CSS próprio (cartões mais compactos neste módulo)
        # despacha para a função de desenho do modo escolhido
        if modo == MODOS[0]:
            _render_cronometrado()
        elif modo == MODOS[1]:
            _render_modo_livre()
        else:
            _render_desafio_progressivo()


# --------------------------------------------------------------------------
# Modo Livre (quiz + desafio visual por tópico, sem cronómetro)
# --------------------------------------------------------------------------

def _mostrar_resultado(resultado: tuple[bool, str]) -> None:
    # mostra a mensagem de resultado a verde (correto) ou vermelho (errado)
    correto, mensagem = resultado
    if correto:
        st.success(mensagem)
    else:
        st.error(mensagem)


def _render_modo_livre() -> None:
    col_esquerda, col_direita = st.columns([3, 2])  # pergunta/desafio à esquerda, pontuação à direita

    with col_esquerda, st.container(height=650):
        col_topico, col_botao = st.columns([3, 1])
        with col_topico:
            # escolha do tópico a praticar
            topico = st.selectbox("Escolhe o tópico", TOPICOS)
        with col_botao:
            st.write("")  # espaçador vertical, para alinhar o botão com o selectbox
            if st.button("🔄 Novo desafio", width="stretch"):
                # apaga o estado guardado do quiz/visual deste tópico — na
                # próxima execução são gerados um quiz e um visual novos
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
            # mostra a pontuação de todos os tópicos numa só linha, tipo "Matrizes: 40 · Determinantes: 0 · ..."
            st.markdown(" · ".join(f"**{t}**: {p}" for t, p in pontuacoes.items()))

        if resultado_quiz is not None:
            _mostrar_resultado(resultado_quiz)
        if resultado_visual is not None:
            _mostrar_resultado(resultado_visual)

        codigo_turma = st.session_state.get("jogos_codigo_turma", "").strip()
        if codigo_turma:
            # se o "modo turma" estiver ativo, mostra o ranking partilhado deste tópico
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
        # 1ª vez que se vê este tópico (ou depois de "Novo desafio"): gera uma pergunta nova
        st.session_state[chave] = {"desafio": GERADORES_QUIZ[topico](), "inicio": time.time(), "respondido": False}
    estado = st.session_state[chave]
    desafio = estado["desafio"]

    with st.container(border=True):
        st.write(desafio.pergunta)
        # escolha múltipla entre as opções do desafio (uma delas é a correta)
        escolha = st.radio("Escolhe a resposta:", desafio.opcoes, key=f"jogos_quiz_radio_{topico}")

    if not estado["respondido"] and st.button("Responder", key=f"jogos_quiz_responder_{topico}"):
        estado["respondido"] = True
        # compara o índice da opção escolhida com o índice da opção correta
        estado["correto"] = desafio.opcoes.index(escolha) == desafio.indice_correto
        # pontos por velocidade, só se acertou (0 se errou)
        estado["pontos"] = _pontos_por_tempo(estado["inicio"]) if estado["correto"] else 0
        if estado["correto"]:
            _registar_pontos(topico, estado["pontos"])

    if not estado["respondido"]:
        return None  # ainda não há resultado a mostrar
    if estado["correto"]:
        return True, f"⚡ Quiz — ✅ Correto! +{estado['pontos']} pontos. {desafio.explicacao}"
    return False, f"⚡ Quiz — ❌ Não é essa. {desafio.explicacao}"


def _render_visual(topico: str) -> tuple[bool, str] | None:
    """Desenha o desafio visual (coluna principal) e devolve o resultado
    (correto, mensagem) para a coluna de pontuação, ou None se ainda por responder."""
    st.markdown("##### 🎯 Desafio visual")
    chave = f"jogos_visual_{topico}"
    if chave not in st.session_state:
        # gera um desafio visual novo (com a figura Plotly já pronta) e guarda-o em sessão
        desafio, fig = GERADORES_VISUAL[topico]()
        st.session_state[chave] = {"desafio": desafio, "figura": fig, "inicio": time.time(), "respondido": False}
    estado = st.session_state[chave]
    desafio = estado["desafio"]

    st.write(desafio.instrucao)
    chave_grafico = f"jogos_grafico_{topico}"
    # desenha o gráfico interativo; on_select="rerun" faz a página re-executar
    # assim que o utilizador clicar num ponto do gráfico
    st.plotly_chart(estado["figura"], width="stretch", on_select="rerun", key=chave_grafico)

    # lê o evento de clique guardado pelo Streamlit no session_state, sob a mesma key do gráfico
    evento = st.session_state.get(chave_grafico)
    pontos_clicados = evento["selection"]["points"] if evento and evento.get("selection") else []

    if pontos_clicados and not estado["respondido"]:
        # o utilizador acabou de clicar num ponto do gráfico pela primeira vez
        ponto = pontos_clicados[0]
        xy = (ponto.get("x", 0.0), ponto.get("y", 0.0))
        estado["respondido"] = True
        # verifica se o ponto clicado está suficientemente perto da resposta esperada
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
    # tempo por pergunta encurta 3s por cada nível acima do 1º, nunca abaixo do mínimo
    return max(TEMPO_MINIMO_S, TEMPO_INICIAL_S - (nivel - 1) * DECREMENTO_POR_NIVEL_S)


def _estado_cronometrado() -> dict:
    # estrutura de estado completa do Jogo Cronometrado, criada uma única vez
    # por sessão (setdefault) — cada campo documentado junto do seu uso:
    return st.session_state.setdefault("jogos_cron", {
        "ativo": False,  # True enquanto o jogo está a decorrer (falso = ecrã de configuração/resumo)
        "nome": "",  # nome do jogador, escolhido no ecrã de configuração
        "topico": TOPICOS_CRONOMETRADO[0],  # tópico escolhido (pode ser "aleatório")
        "topico_pergunta": "",  # tópico realmente sorteado para a pergunta atual
        "nivel": 1,  # nível atual (sobe a cada PERGUNTAS_POR_NIVEL perguntas)
        "pontos": 0,  # pontuação total acumulada nesta partida
        "n_perguntas": 0,  # nº total de perguntas já respondidas/expiradas
        "n_corretas": 0,  # nº de respostas corretas, para a taxa de acerto
        "perguntas_no_nivel": 0,  # contador que reinicia a cada subida de nível
        "pergunta_atual": None,  # objeto Desafio da pergunta em curso
        "inicio_pergunta": 0.0,  # timestamp de quando a pergunta atual foi gerada
        "tempo_limite": TEMPO_INICIAL_S,  # tempo limite (s) da pergunta atual
        "respondida": False,  # True assim que o jogador responde ou o tempo esgota
        "correta": False,  # se a última resposta foi correta
        "expirado": False,  # True se o tempo esgotou antes de responder
        "pontos_pergunta": 0,  # pontos ganhos na última pergunta
    })


def _gerar_pergunta_cronometrado(estado: dict) -> None:
    # sorteia (se necessário) o tópico e gera uma pergunta nova, reiniciando
    # o cronómetro e todos os indicadores de resposta desta pergunta
    topico_pergunta = estado["topico"]
    if topico_pergunta == TOPICOS_CRONOMETRADO[0]:
        # opção "aleatório": sorteia um dos 5 tópicos reais
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
    # ao atingir o nº de perguntas necessário, sobe de nível e reinicia o
    # contador, avisando o jogador com um toast temporário
    if estado["perguntas_no_nivel"] >= PERGUNTAS_POR_NIVEL:
        estado["nivel"] += 1
        estado["perguntas_no_nivel"] = 0
        st.toast(f"🎉 Subiste para o nível {estado['nivel']}!")


def _responder_cronometrado(estado: dict, escolha: str) -> None:
    # regista a resposta escolhida, calcula pontos (se correta, proporcionais
    # ao tempo que ainda restava) e verifica se há subida de nível
    desafio = estado["pergunta_atual"]
    estado["respondida"] = True
    estado["n_perguntas"] += 1
    estado["perguntas_no_nivel"] += 1
    correta = desafio.opcoes.index(escolha) == desafio.indice_correto
    estado["correta"] = correta
    if correta:
        decorrido = time.time() - estado["inicio_pergunta"]
        restante = max(0.0, estado["tempo_limite"] - decorrido)
        # quanto mais tempo restante, mais pontos — nunca menos que o mínimo garantido
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
        # já respondeu (ou o tempo já tinha esgotado antes): barra parada, sem contagem
        st.progress(0.0 if estado["expirado"] else 1.0,
                    text="⏰ Tempo esgotado" if estado["expirado"] else "✅ Respondido")
        return
    decorrido = time.time() - estado["inicio_pergunta"]
    restante = max(0.0, estado["tempo_limite"] - decorrido)
    # barra de progresso proporcional ao tempo restante, com a contagem decrescente em segundos
    st.progress(restante / estado["tempo_limite"], text=f"⏱️ {int(restante) + 1}s restantes")
    if restante <= 0:
        # tempo esgotado sem resposta: marca como respondida/errada/expirada e força um rerun completo
        estado["respondida"] = True
        estado["correta"] = False
        estado["expirado"] = True
        estado["n_perguntas"] += 1
        estado["perguntas_no_nivel"] += 1
        _verificar_subida_nivel(estado)
        st.rerun()


def _render_resumo_cronometrado(estado: dict) -> None:
    # painel de resumo mostrado no ecrã de configuração depois de terminar uma partida
    st.markdown(f"##### 🏁 Resumo de {estado['nome']}")
    taxa = (estado["n_corretas"] / estado["n_perguntas"] * 100) if estado["n_perguntas"] else 0.0
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nível alcançado", estado["nivel"])
    col2.metric("Perguntas respondidas", estado["n_perguntas"])
    col3.metric("Pontos totais", estado["pontos"])
    col4.metric("Taxa de acerto", f"{taxa:.0f}%")


def _render_cronometrado_config() -> None:
    # ecrã antes de começar (ou depois de terminar) uma partida: mostra o
    # resumo da partida anterior (se houve), nome do jogador e tópico
    estado = _estado_cronometrado()
    if estado["n_perguntas"] > 0:
        _render_resumo_cronometrado(estado)
        st.divider()

    st.caption(
        f"Responde a perguntas de escolha múltipla contra o relógio — o nível sobe a cada "
        f"{PERGUNTAS_POR_NIVEL} perguntas, e o tempo por pergunta encurta a cada nível "
        f"(começa em {TEMPO_INICIAL_S}s, nunca menos de {TEMPO_MINIMO_S}s)."
    )
    # pré-preenche o nome com o já usado (se houver) ou com o da barra lateral
    nome_defeito = estado["nome"] or st.session_state.get("jogos_nome_jogador", "")
    nome = st.text_input("O teu nome", value=nome_defeito, key="jogos_cron_nome_input")
    topico = st.selectbox("Tópico", TOPICOS_CRONOMETRADO, key="jogos_cron_topico_input")

    if st.button("▶ Começar", key="jogos_cron_comecar", width="stretch", type="primary"):
        if not nome.strip():
            # exige um nome antes de deixar começar (usado no registo de pontos)
            st.warning("Escreve o teu nome antes de começar.")
            return
        # reinicia todo o estado da partida com as escolhas feitas agora
        estado.update({
            "ativo": True, "nome": nome.strip(), "topico": topico, "nivel": 1, "pontos": 0,
            "n_perguntas": 0, "n_corretas": 0, "perguntas_no_nivel": 0, "pergunta_atual": None,
        })
        st.rerun()


def _render_cronometrado_jogo() -> None:
    estado = _estado_cronometrado()
    if estado["pergunta_atual"] is None:
        # primeira pergunta da partida: ainda não foi gerada
        _gerar_pergunta_cronometrado(estado)
    desafio = estado["pergunta_atual"]

    col_esquerda, col_direita = st.columns([3, 2])  # pergunta à esquerda, pontuação/resultado à direita

    with col_esquerda, st.container(height=650):
        _cronometro_pergunta()  # barra de progresso do tempo restante (fragmento independente)

        with st.container(border=True):
            st.caption(f"Tópico: {estado['topico_pergunta']} · Jogador: {estado['nome']}")
            st.write(desafio.pergunta)
            # escolha múltipla; fica bloqueada assim que já houver resposta
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
                    # termina a partida a meio, sem responder à pergunta atual
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
            # mostra o resultado da última pergunta: tempo esgotado, correto ou errado
            st.markdown("##### 📝 Resultado")
            if estado["expirado"]:
                st.error(f"⏰ Tempo esgotado! {desafio.explicacao}")
            elif estado["correta"]:
                st.success(f"✅ Correto! +{estado['pontos_pergunta']} pontos. {desafio.explicacao}")
            else:
                st.error(f"❌ Não é essa. {desafio.explicacao}")


def _render_cronometrado() -> None:
    # despacha entre o ecrã de jogo (partida em curso) e o de configuração/resumo
    estado = _estado_cronometrado()
    if estado["ativo"]:
        _render_cronometrado_jogo()
    else:
        _render_cronometrado_config()


# --------------------------------------------------------------------------
# Desafio com Pistas — em vez de dar logo a resposta, pede primeiro o cálculo
# do determinante (com pista disponível) e só depois se decide se a matriz
# tem inversa, com feedback explicado. Ver "Estrutura do Trabalho" secção 9.
# --------------------------------------------------------------------------

def _estado_progressivo() -> dict:
    # estado completo deste modo, criado uma única vez por sessão:
    return st.session_state.setdefault("jogos_prog", {
        "desafio": None,  # objeto DesafioProgressivo (matriz, determinante, dica, ...) em curso
        "fase": 1,  # 1 = a adivinhar o determinante, 2 = a decidir se tem inversa
        "tentativas_fase1": 0,  # quantas vezes já errou o determinante neste desafio
        "mostrar_dica": False,  # se o jogador já pediu a pista
        "erro_fase1": False,  # se a última tentativa da fase 1 foi errada (para mostrar o aviso)
        "resposta_fase2": None,  # None = ainda não respondeu; True/False = respondeu Sim/Não
        "pontos": 0,  # pontuação total acumulada neste modo
        "n_desafios": 0,  # nº de desafios já gerados (contador exibido)
        "n_fase2_respondidas": 0,  # nº de vezes que chegou a responder à fase 2 (para a taxa de acerto)
        "n_corretos_fase2": 0,  # nº de respostas corretas na fase 2
    })


def _novo_desafio_progressivo(estado: dict) -> None:
    # gera uma matriz 2×2 nova e reinicia todo o estado por-desafio (fase,
    # tentativas, dica, resposta) — mantém a pontuação/contadores acumulados
    estado["desafio"] = desafios.gerar_desafio_progressivo_inversa(dim=2)
    estado["fase"] = 1
    estado["tentativas_fase1"] = 0
    estado["mostrar_dica"] = False
    estado["erro_fase1"] = False
    estado["resposta_fase2"] = None
    estado["n_desafios"] += 1


def _responder_fase2(estado: dict, resposta: bool) -> None:
    # regista a resposta "tem inversa?" e soma pontos se estiver correta
    estado["resposta_fase2"] = resposta
    estado["n_fase2_respondidas"] += 1
    if resposta == estado["desafio"].tem_inversa:
        estado["pontos"] += PONTOS_FASE2
        estado["n_corretos_fase2"] += 1
        _registar_pontos("Determinantes", PONTOS_FASE2)


def _render_desafio_progressivo() -> None:
    estado = _estado_progressivo()
    if estado["desafio"] is None:
        # primeira vez neste modo: gera o primeiro desafio
        _novo_desafio_progressivo(estado)
    desafio = estado["desafio"]

    col_esquerda, col_direita = st.columns([3, 2])  # desafio à esquerda, pontuação à direita

    with col_esquerda, st.container(height=650):
        st.caption(f"Desafio {estado['n_desafios']} · Fase {estado['fase']} de 2")
        with st.container(border=True):
            st.write("Considera a matriz A:")
            # mostra a matriz em notação matemática (LaTeX)
            st.latex(f"A = {sp.latex(sp.Matrix(desafio.matriz.tolist()))}")

        if estado["fase"] == 1:
            # FASE 1: pede o valor do determinante, com pista opcional
            st.markdown("##### 1️⃣ Qual é o determinante de A?")
            resposta = st.number_input("det(A) =", value=0.0, step=1.0, key="jogos_prog_det_input")
            col_responder, col_dica = st.columns(2)
            with col_responder:
                if st.button("Responder", key="jogos_prog_responder_fase1", width="stretch", type="primary"):
                    if abs(resposta - desafio.determinante) < 1e-6:
                        # resposta certa: pontuação depende de ter sido à
                        # primeira tentativa e sem pista, ou não
                        pontos_fase1 = (
                            PONTOS_FASE1_PRIMEIRA_TENTATIVA
                            if estado["tentativas_fase1"] == 0 and not estado["mostrar_dica"]
                            else PONTOS_FASE1_COM_PISTA
                        )
                        estado["pontos"] += pontos_fase1
                        estado["fase"] = 2  # avança para a pergunta "tem inversa?"
                        estado["erro_fase1"] = False
                        st.rerun()
                    else:
                        # resposta errada: conta a tentativa e mostra o aviso
                        estado["tentativas_fase1"] += 1
                        estado["erro_fase1"] = True
            with col_dica:
                if st.button("💡 Pista", key="jogos_prog_pista", width="stretch"):
                    estado["mostrar_dica"] = True

            if estado["erro_fase1"]:
                st.error("Ainda não é esse valor — tenta de novo.")
            if estado["mostrar_dica"] or estado["tentativas_fase1"] >= 2:
                # mostra a pista se foi pedida OU automaticamente ao fim de 2 erros
                st.info(f"💡 {desafio.dica}")
        else:
            # FASE 2: já sabe o determinante — decide se a matriz tem inversa
            st.success(f"✅ det(A) = {desafio.determinante:g}. Boa!")
            st.markdown("##### 2️⃣ A matriz A tem inversa?")
            col_sim, col_nao = st.columns(2)
            respondido_fase2 = estado["resposta_fase2"] is not None
            with col_sim:
                if st.button("Sim", key="jogos_prog_sim", width="stretch", disabled=respondido_fase2):
                    _responder_fase2(estado, True)
                    st.rerun()
            with col_nao:
                if st.button("Não", key="jogos_prog_nao", width="stretch", disabled=respondido_fase2):
                    _responder_fase2(estado, False)
                    st.rerun()

            if respondido_fase2:
                if estado["resposta_fase2"] == desafio.tem_inversa:
                    st.success(f"✅ Certo! {desafio.explicacao}")
                else:
                    st.error(f"❌ Não é bem assim. {desafio.explicacao}")
                if st.button("➡️ Novo desafio", key="jogos_prog_novo", width="stretch", type="primary"):
                    _novo_desafio_progressivo(estado)
                    st.rerun()

    with col_direita, st.container(height=650):
        st.markdown("##### 📊 Pontuação")
        col_desafios, col_pontos = st.columns(2)
        col_desafios.metric("Desafios", estado["n_desafios"])
        col_pontos.metric("Pontos", estado["pontos"])
        taxa = (estado["n_corretos_fase2"] / estado["n_fase2_respondidas"] * 100) if estado["n_fase2_respondidas"] else 0.0
        st.metric("Acerto (fase 2)", f"{taxa:.0f}%")

        st.divider()
        st.caption(
            "Em vez de perguntar logo se a matriz tem inversa, o desafio pede primeiro o "
            "determinante (com pista, se precisares) — só depois é que decides."
        )
