"""Módulo Vetores: operações vetoriais e visualização 2D/3D, sobre um número
arbitrário de vetores nomeados (mesmo estilo do módulo Matrizes)."""
import numpy as np  # arrays numéricos: guarda o valor real de cada vetor introduzido
import sympy as sp  # cálculo simbólico: usado aqui só para formatar em LaTeX
import streamlit as st  # framework que desenha todos os widgets desta página

from utils.componentes import (
    cabecalho,  # título da página, sem legenda
    modo_leve_da_sessao,  # lê o estado do toggle "Modo leve" sem recriar o widget
    modo_passo_a_passo_ativo,  # cria/lê o toggle "mostrar passos" de um módulo
    mostrar_passos,  # lista de expanders "Passo 1, 2, ..." com o detalhe pedagógico
    vetor_input,  # editor de células de um vetor nomeado, com pré-visualização simbólica
)
from utils.simbolico import Passo  # dataclass usada para construir os passos pedagógicos deste módulo
from utils.visualizacao import figura_vetor_parametrizado, figura_vetores_2d, figura_vetores_3d  # construtores de gráficos Plotly

# operações que precisam de DOIS vetores escolhidos pelo utilizador
OPERACOES_2_VETORES = ["Soma", "Diferença", "Combinação linear", "Produto interno", "Produto externo",
                        "Teste de ortogonalidade"]
# operações que só precisam de UM vetor
OPERACOES_1_VETOR = ["Multiplicação por escalar", "Norma"]

# paleta de cores usada para distinguir cada vetor no gráfico (ciclada por índice)
CORES = ["#e15759", "#4e79a7", "#59a14f", "#f28e2b", "#b07aa1", "#76b7b2"]
# valores de exemplo pré-carregados nos vetores v e w, para a página nunca abrir vazia
VALORES_DEFEITO = {"v": np.array([2.0, 1.0]), "w": np.array([1.0, 2.0])}


def _inicializar_estado() -> None:
    # lista de nomes de vetores atualmente visíveis (v, w, a, b, ...) — só é
    # criada na primeira execução da sessão; setdefault não sobrescreve o
    # que já lá estiver depois de o utilizador adicionar/remover vetores
    st.session_state.setdefault("vetores_nomes", ["v", "w"])


def _adicionar_vetor() -> None:
    # callback do botão "➕ Adicionar vetor": escolhe a próxima letra minúscula
    # livre do alfabeto, evitando "i", "j", "k" (reservadas por convenção aos
    # versores dos eixos, para não confundir o utilizador)
    nomes = st.session_state["vetores_nomes"]
    letras_usadas = set(nomes)
    for codigo in range(ord("a"), ord("z") + 1):
        letra = chr(codigo)
        if letra not in letras_usadas and letra not in ("i", "j", "k"):
            nomes.append(letra)
            return  # para assim que encontra a primeira letra livre


def _remover_ultimo_vetor() -> None:
    # callback do botão "➖ Remover último vetor": nunca deixa ficar menos de 1 vetor
    nomes = st.session_state["vetores_nomes"]
    if len(nomes) > 1:
        st.session_state["vetores_nomes"].pop()


def render() -> None:
    cabecalho("➡️ Vetores")  # título "➡️ Vetores" no topo da página
    _inicializar_estado()

    col_esquerda, col_direita = st.columns([2, 3])  # 2:3 = coluna de entradas/resultado mais estreita que a do gráfico

    with col_esquerda, st.container(height=650):  # coluna esquerda, com scroll próprio até 650px
        # escolha da dimensão de trabalho: 2D (plano) ou 3D (espaço) — muda os
        # gráficos disponíveis e o número de componentes de cada vetor
        dimensao = st.radio("Dimensão", [2, 3], horizontal=True, format_func=lambda d: f"{d}D")

        # botões para gerir quantos vetores existem, lado a lado
        col_add, col_rem = st.columns(2)
        with col_add:
            st.button("➕ Adicionar vetor", width="stretch", on_click=_adicionar_vetor, key="vetores_btn_add")
        with col_rem:
            st.button("➖ Remover último vetor", width="stretch", on_click=_remover_ultimo_vetor,
                       disabled=len(st.session_state["vetores_nomes"]) <= 1, key="vetores_btn_rem")

        nomes = st.session_state["vetores_nomes"]
        vetores: dict[str, np.ndarray] = {}
        # distribui os editores de vetor em até 3 colunas lado a lado (menos colunas se houver menos vetores)
        colunas = st.columns(min(len(nomes), 3))
        for i, nome in enumerate(nomes):
            with colunas[i % len(colunas)]:  # repartição em "roda" pelas colunas disponíveis
                defeito = VALORES_DEFEITO.get(nome, np.ones(2))  # valor de exemplo, ou vetor de 1s se o nome não tiver um pré-definido
                if len(defeito) != dimensao:
                    # se o utilizador mudou de 2D para 3D (ou vice-versa), o valor de exemplo tem de ser recalculado com o novo nº de componentes
                    defeito = np.ones(dimensao)
                vetores[nome] = vetor_input(f"vetores_{nome}", dimensao=dimensao, titulo=f"Vetor {nome}",
                                             valor_defeito=defeito)

        st.divider()
        # monta a lista de operações disponíveis: as binárias, sem "Produto
        # externo" quando não estamos em 3D (só é definido em R³), mais as unárias
        operacoes = list(OPERACOES_2_VETORES)
        if dimensao != 3:
            operacoes.remove("Produto externo")
        operacoes += OPERACOES_1_VETOR
        operacao = st.selectbox("Escolher operação", operacoes)

        k = c1 = c2 = None  # parâmetros numéricos só usados por algumas operações (inicializados a None para as outras)
        if operacao in OPERACOES_1_VETOR:
            # operações unárias: só é preciso escolher um vetor
            nome_v = st.selectbox("Vetor", nomes, key="vetores_op_nome_unico")
            v, w, nome_w = vetores[nome_v], None, None
            if operacao == "Multiplicação por escalar":
                st.markdown("**Escalar k**")
                # campo numérico para o valor de k (2.0 por omissão, passo de 0.5)
                k = st.number_input("k", value=2.0, step=0.5, label_visibility="collapsed",
                                     key="vetores_k_escalar")
        else:
            # operações binárias precisam de pelo menos 2 vetores definidos
            if len(nomes) < 2:
                st.warning("Esta operação precisa de pelo menos 2 vetores — adiciona outro acima.")
                return
            # seletores para escolher quais dos vetores existentes entram na operação
            col1, col2 = st.columns(2)
            with col1:
                nome_v = st.selectbox("Vetor 1", nomes, index=0, key="vetores_op_nome1")
            with col2:
                nome_w = st.selectbox("Vetor 2", nomes, index=min(1, len(nomes) - 1), key="vetores_op_nome2")
            v, w = vetores[nome_v], vetores[nome_w]
            if operacao == "Combinação linear":
                # campos para os coeficientes c1, c2 da combinação c1·v + c2·w
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    c1 = st.number_input(f"Coeficiente de {nome_v}", value=1.0, step=0.5, key="vetores_c1")
                with col_c2:
                    c2 = st.number_input(f"Coeficiente de {nome_w}", value=1.0, step=0.5, key="vetores_c2")

        # representação em LaTeX de v (e de w, se existir) arredondados a 4 casas
        latex_v = sp.latex(sp.Matrix(np.round(v, 4).tolist()))
        latex_w = sp.latex(sp.Matrix(np.round(w, 4).tolist())) if w is not None else None
        # monta a expressão LaTeX da operação escolhida, com o símbolo apropriado
        if operacao == "Soma":
            simbolo_operacao = f"{latex_v} + {latex_w}"
        elif operacao == "Diferença":
            simbolo_operacao = f"{latex_v} - {latex_w}"
        elif operacao == "Combinação linear":
            simbolo_operacao = (f"{sp.latex(sp.nsimplify(c1))} \\cdot {latex_v} + "
                                 f"{sp.latex(sp.nsimplify(c2))} \\cdot {latex_w}")
        elif operacao == "Multiplicação por escalar":
            simbolo_operacao = f"{sp.latex(sp.nsimplify(k))} \\cdot {latex_v}"
        elif operacao == "Produto interno":
            simbolo_operacao = f"{latex_v} \\cdot {latex_w}"
        elif operacao == "Produto externo":
            simbolo_operacao = f"{latex_v} \\times {latex_w}"
        elif operacao == "Teste de ortogonalidade":
            simbolo_operacao = f"{latex_v} \\cdot {latex_w}"
        else:  # Norma — operação unária, sem segundo operando
            simbolo_operacao = f"\\lVert {latex_v} \\rVert"

        # caixa "🔎 Operandos escolhidos": mostra a expressão completa antes do cálculo
        with st.container(border=True):
            st.markdown("##### 🔎 Operandos escolhidos")
            st.caption(f"Vetor {nome_v}" + (f" e Vetor {nome_w}" if nome_w else ""))
            st.latex(simbolo_operacao)

        passos: list[Passo] = []  # lista de passos pedagógicos, preenchida consoante a operação escolhida abaixo
        with st.container(border=True):
            col_titulo, col_toggle = st.columns([3, 2])
            with col_titulo:
                st.markdown("##### ✅ Resultado")
            with col_toggle:
                # toggle "mostrar passos", desenhado dentro da própria caixa de resultado
                mostrar_passo_a_passo = modo_passo_a_passo_ativo("vetores")
            # cálculo do resultado + passos pedagógicos, um ramo por operação —
            # cada ramo usa NumPy para o valor e monta um Passo por componente/etapa
            if operacao == "Soma":
                resultado = v + w  # soma vetorial componente a componente
                st.latex(f"{simbolo_operacao} = {sp.latex(sp.Matrix(np.round(resultado, 4).tolist()))}")
                passos = [
                    Passo(f"Somar a componente {i + 1}: v_{i + 1} + w_{i + 1}", "",
                          latex=f"{v[i]:g} + {w[i]:g} = {resultado[i]:g}")
                    for i in range(len(v))
                ]
            elif operacao == "Diferença":
                resultado = v - w  # subtração vetorial componente a componente
                st.latex(f"{simbolo_operacao} = {sp.latex(sp.Matrix(np.round(resultado, 4).tolist()))}")
                passos = [
                    Passo(f"Subtrair a componente {i + 1}: v_{i + 1} - w_{i + 1}", "",
                          latex=f"{v[i]:g} - {w[i]:g} = {resultado[i]:g}")
                    for i in range(len(v))
                ]
            elif operacao == "Combinação linear":
                resultado = c1 * v + c2 * w  # combinação linear c1·v + c2·w
                st.latex(f"{simbolo_operacao} = {sp.latex(sp.Matrix(np.round(resultado, 4).tolist()))}")
                passos = [
                    Passo(f"Calcular a componente {i + 1}: {c1:g}·v_{i + 1} + {c2:g}·w_{i + 1}", "",
                          latex=f"({c1:g})({v[i]:g}) + ({c2:g})({w[i]:g}) = {resultado[i]:g}")
                    for i in range(len(v))
                ]
            elif operacao == "Multiplicação por escalar":
                resultado = k * v  # cada componente de v multiplicada por k
                st.latex(f"{simbolo_operacao} = {sp.latex(sp.Matrix(np.round(resultado, 4).tolist()))}")
                passos = [
                    Passo(f"Multiplicar a componente {i + 1} por k", "",
                          latex=f"({k:g})({v[i]:g}) = {resultado[i]:g}")
                    for i in range(len(v))
                ]
            elif operacao == "Produto interno":
                resultado = float(np.dot(v, w))  # produto escalar: soma dos produtos componente a componente
                st.latex(f"{simbolo_operacao} = {resultado:g}")
                termos = " + ".join(f"({v[i]:g})({w[i]:g})" for i in range(len(v)))  # string "(v1)(w1) + (v2)(w2) + ..."
                valores_termos = " + ".join(f"{v[i] * w[i]:g}" for i in range(len(v)))  # os mesmos termos já calculados
                passos = [Passo("Multiplicar cada par de componentes e somar", "",
                                 latex=f"{termos} = {valores_termos} = {resultado:g}")]
            elif operacao == "Produto externo":
                resultado = np.cross(v, w)  # produto vetorial (só definido em R³), NumPy trata do cálculo
                st.latex(f"{simbolo_operacao} = {sp.latex(sp.Matrix(np.round(resultado, 4).tolist()))}")
                # fórmula e índices de cada componente do produto externo (regra determinante 3×3)
                rotulos = [("v_2 w_3 - v_3 w_2", 1, 2, 2, 1), ("v_3 w_1 - v_1 w_3", 2, 0, 0, 2),
                           ("v_1 w_2 - v_2 w_1", 0, 1, 1, 0)]
                passos = [
                    Passo(f"Calcular a componente {i + 1} do produto externo", formula,
                          latex=f"({v[ia]:g})({w[ib]:g}) - ({v[ic]:g})({w[id_]:g}) = {resultado[i]:g}")
                    for i, (formula, ia, ib, ic, id_) in enumerate(rotulos)
                ]
            elif operacao == "Norma":
                resultado = float(np.linalg.norm(v))  # comprimento euclidiano do vetor
                st.latex(f"{simbolo_operacao} = {resultado:g}")
                quadrados = " + ".join(f"({v[i]:g})^2" for i in range(len(v)))  # string "(v1)^2 + (v2)^2 + ..."
                soma_quadrados = float(np.sum(v ** 2))
                passos = [
                    Passo("Elevar cada componente ao quadrado e somar", "",
                          latex=f"{quadrados} = {soma_quadrados:g}"),
                    Passo("Calcular a raiz quadrada da soma", "",
                          latex=f"\\sqrt{{{soma_quadrados:g}}} = {resultado:g}"),
                ]
            else:  # Teste de ortogonalidade — usa o produto interno para decidir se os vetores são perpendiculares
                produto = float(np.dot(v, w))
                ortogonais = abs(produto) < 1e-9  # tolerância numérica, para não falhar por erro de vírgula flutuante
                st.latex(f"{simbolo_operacao} = {produto:.4g}")
                st.markdown("✅ **Ortogonais**" if ortogonais else "❌ **Não ortogonais**")
                termos = " + ".join(f"({v[i]:g})({w[i]:g})" for i in range(len(v)))
                passos = [
                    Passo("Calcular v · w", "", latex=f"{termos} = {produto:.4g}"),
                    Passo("Concluir", f"Como v · w {'=' if ortogonais else '≠'} 0, os vetores "
                                       f"{'são' if ortogonais else 'não são'} ortogonais."),
                ]

            # só mostra os passos pedagógicos se o toggle estiver ligado e houver passos a mostrar
            if mostrar_passo_a_passo and passos:
                st.divider()
                mostrar_passos(passos)

    with col_direita, st.container(height=650):  # coluna direita: visualizações gráficas
        st.markdown("##### 📈 Visualização")
        # lista (nome, valor, cor) de todos os vetores nomeados, para desenhar todos juntos no mesmo gráfico
        vetores_fig = [(nome, vetores[nome], CORES[i % len(CORES)]) for i, nome in enumerate(nomes)]
        # escolhe o construtor de figura 2D ou 3D consoante a dimensão selecionada
        fig = figura_vetores_2d(vetores_fig) if dimensao == 2 else figura_vetores_3d(vetores_fig)
        st.plotly_chart(fig, width="stretch", key="vetores_grafico_principal")  # gráfico principal com todos os vetores

        st.markdown(f"##### 🔎 Ver k·{nome_v}")
        st.caption("Arrasta o slider ou carrega em ▶ Play para ver o vetor a escalar.")
        # gráfico animado: mostra o vetor v (o 1º operando escolhido) a ser escalado por k, de -2 a 2, em 30 fotogramas
        fig_kv = figura_vetor_parametrizado(
            f"k·{nome_v}", lambda k: k * v, np.linspace(-2, 2, 30), dimensao=dimensao,
            cor=CORES[0], rotulo_parametro="k", modo_leve=modo_leve_da_sessao(),
        )
        st.plotly_chart(fig_kv, width="stretch", key="vetores_grafico_kv")  # gráfico animado k·v
