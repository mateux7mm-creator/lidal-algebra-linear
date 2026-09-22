"""Wrappers Plotly reutilizáveis para os módulos do laboratório.

Cada função devolve uma `go.Figure` já pronta para `st.plotly_chart`, com um
estilo visual inspirado no Gráfico (grelha cinzenta clara, eixos escurecidos
na origem, escala igual em x/y). Os gráficos são recalculados a cada rerun do
Streamlit — a interatividade em tempo real vem de campos numéricos com
setas +/- em vez de animação, por isso não há frames a gerir aqui.
"""
from __future__ import annotations  # permite anotações de tipo modernas (ex. "list[int]") em qualquer versão do Python

from typing import Callable, Optional, Sequence  # tipos usados nas assinaturas das funções abaixo

import numpy as np  # arrays e álgebra linear numérica (malhas, produtos matriciais, resolução de sistemas)
import plotly.graph_objects as go  # biblioteca de gráficos interativos (figuras, traços, animações)

from utils.exploracao_grafica import ResultadoEquacao  # tipo devolvido pela interpretação de equações em texto livre

GRID_INTERVALO = 2  # malha de -2 a 2 — usada para calcular o domínio inicial da vista
FATOR_EXTENSAO = 4  # a malha/retas desenhadas são FATOR_EXTENSAO× maiores que a vista
                     # inicial, para dar zoom-out não revelar espaço vazio a meio da reta/grelha
GRID_PASSO = 0.5  # espaçamento entre linhas da grelha, em modo normal
GRID_PASSO_LEVE = 1.0  # espaçamento maior (menos linhas) em modo leve
N_PONTOS_CIRCULO = 60  # nº de pontos usados para desenhar um círculo, em modo normal
N_PONTOS_CIRCULO_LEVE = 24  # nº de pontos do círculo em modo leve (mais rápido de desenhar)
N_PONTOS_RETA = 200  # nº de pontos usados para desenhar uma reta, em modo normal
N_PONTOS_RETA_LEVE = 60  # nº de pontos da reta em modo leve
N_FRAMES_MODO_LEVE = 12  # usado só por figura_transformacao_parametrizada (Conteúdo/Jogos)
CORES_VETORES = ["#e15759", "#4e79a7", "#59a14f", "#f28e2b", "#b07aa1"]  # paleta de cores usada em vetores/retas/planos, por ordem


# --------------------------------------------------------------------------
# Utilitários internos
# --------------------------------------------------------------------------

def _malha_pontos(modo_leve: bool = False, intervalo_malha: float = GRID_INTERVALO) -> np.ndarray:
    """Grelha de linhas horizontais/verticais como pontos 2D, separadas por NaN.
    Em modo leve, usa um espaçamento maior (menos linhas) — mais rápido de
    desenhar em dispositivos/ligações mais fracas. `intervalo_malha` maior que
    `GRID_INTERVALO` estende a malha para além da vista inicial (mesmo nº de
    linhas, cada uma mais longa), para o zoom-out não a cortar."""
    # espaçamento entre linhas, escalado proporcionalmente se intervalo_malha for maior que o normal
    passo = (GRID_PASSO_LEVE if modo_leve else GRID_PASSO) * (intervalo_malha / GRID_INTERVALO)
    valores = np.arange(-intervalo_malha, intervalo_malha + passo, passo)  # posições de cada linha da grelha
    pontos = []
    for v in valores:
        # uma linha HORIZONTAL completa (de x=-intervalo a x=+intervalo, a altura y=v),
        # seguida de (NaN, NaN) para o Plotly "levantar a caneta" e não ligar esta linha à seguinte
        pontos += [(-intervalo_malha, v), (intervalo_malha, v), (np.nan, np.nan)]
    for v in valores:
        # o mesmo, mas para as linhas VERTICAIS (x=v fixo, y a variar)
        pontos += [(v, -intervalo_malha), (v, intervalo_malha), (np.nan, np.nan)]
    return np.array(pontos)  # array Nx2 com todos os pontos da grelha completa


def _circulo_pontos(modo_leve: bool = False) -> np.ndarray:
    n = N_PONTOS_CIRCULO_LEVE if modo_leve else N_PONTOS_CIRCULO  # menos pontos em modo leve
    angulos = np.linspace(0, 2 * np.pi, n)  # n ângulos igualmente espaçados entre 0 e 2π (volta completa)
    return np.column_stack([np.cos(angulos), np.sin(angulos)])  # (cos, sin) de cada ângulo = pontos do círculo unitário


def _dtick_legivel(largura: float, maximo_ticks: int = 10) -> float:
    """Escolhe um espaçamento "redondo" (1, 2, 5, 10, 20, 25, 50, ...) entre
    marcas do eixo, com no máximo `maximo_ticks` marcas dentro de `largura`."""
    bruto = largura / maximo_ticks  # espaçamento mínimo necessário para não ultrapassar o nº máximo de marcas
    passos_redondos = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000]  # candidatos, em ordem crescente
    # devolve o primeiro valor "redondo" que seja grande o suficiente; se nenhum bastar, usa o maior disponível
    return next((p for p in passos_redondos if p >= bruto), passos_redondos[-1])


def _eixos_geogebra(intervalo: tuple[float, float] = (-6, 6)) -> dict:
    """Layout de eixos/grelha ao estilo Gráfico: grelha cinzenta clara,
    eixos mais escuros a passar pela origem, fundo branco.

    Os números das marcas são escondidos aqui (`showticklabels=False`) e
    substituídos por anotações próprias em `_anotacoes_eixos`, posicionadas
    junto aos eixos que se cruzam (normalmente perto do meio do gráfico),
    não à margem do gráfico como o Plotly faz por omissão — mais parecido
    com o Gráfico. `dtick` é fixado ao mesmo valor "redondo" usado para
    gerar essas anotações, para a grelha ficar alinhada com os números.

    A legenda fica horizontal, por cima do gráfico (em vez de vertical à
    direita, que é o omissão do Plotly) — liberta espaço horizontal para a
    área do gráfico em si.
    """
    dtick = _dtick_legivel(intervalo[1] - intervalo[0])  # espaçamento "redondo" entre marcas, calculado a partir da largura da vista
    # definição comum aos eixos x e y: intervalo visível, grelha cinzenta, linha zero mais escura,
    # espaçamento das marcas, e números escondidos (são desenhados à parte, em _anotacoes_eixos)
    eixo = dict(range=list(intervalo), showgrid=True, gridcolor="#e3e3e3", gridwidth=1,
                zeroline=True, zerolinecolor="#444444", zerolinewidth=2,
                dtick=dtick, showticklabels=False)
    return dict(
        xaxis={**eixo, "scaleanchor": "y", "scaleratio": 1},  # eixo x igual ao y, com escala 1:1 (círculos ficam redondos, não elípticos)
        yaxis=eixo,
        plot_bgcolor="white",  # fundo da área do gráfico
        paper_bgcolor="white",  # fundo de toda a figura (incluindo margens)
        font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#1f2430"),  # tipo de letra geral do gráfico
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),  # legenda horizontal, centrada, por cima do gráfico
    )


def _anotacoes_eixos(intervalo: tuple[float, float]) -> list[dict]:
    """Etiquetas "x"/"y" na ponta de cada eixo + números das marcas junto aos
    próprios eixos (não à margem do gráfico) — ao estilo Gráfico.

    A etiqueta "x" usa `xref="paper"` (sempre a margem direita real do
    gráfico) em vez de `xref="x"` (dados): como `scaleanchor`/`scaleratio`
    (escala igual x/y) pode esticar o eixo x muito além de `intervalo` para
    caber no aspeto do contentor, uma posição em coordenadas de dados como
    `x=intervalo[1]` deixaria de estar junto à margem, ficando perto do
    centro. O eixo y não estica (é a referência de `scaleanchor`), por isso
    a etiqueta "y" e os números das marcas podem usar coordenadas de dados.

    Os números estendem-se até FATOR_EXTENSAO_MARCAS× o intervalo pedido
    (menos que o FATOR_EXTENSAO das retas/malha, para não gerar demasiadas
    anotações), para continuarem a aparecer num zoom-out moderado.

    Cada eixo termina numa seta (estilo Gráfico), desenhada com o mesmo
    truque de anotação usado nos vetores (`showarrow=True, ax/ay` = cauda,
    `x/y` = ponta). A seta do eixo x também usa `xref="paper"` pela mesma
    razão da etiqueta "x": só a coordenada de papel garante a ponta na
    margem direita real, independentemente do esticamento por `scaleanchor`.
    """
    FATOR_EXTENSAO_MARCAS = 2  # até onde os números das marcas se estendem, em múltiplos do intervalo pedido
    dtick = _dtick_legivel(intervalo[1] - intervalo[0])  # espaçamento entre números, igual ao da grelha
    maximo = intervalo[1] * FATOR_EXTENSAO_MARCAS  # limite superior até onde gerar números
    cor_eixo = "#444444"  # cor usada nas setas dos eixos

    anotacoes = [
        # seta na ponta do eixo x (margem direita real; "x domain" é o único
        # valor de axref que suporta uma referência tipo "paper", pois axref
        # não aceita "paper" diretamente — só xref, que é usado na etiqueta "x")
        dict(x=0.995, xref="x domain", ax=0.93, axref="x domain", y=0, yref="y", ay=0, ayref="y",
             text="", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.6, arrowcolor=cor_eixo),
        # seta na ponta do eixo y (o eixo y não estica, coordenadas de dados são fiáveis)
        dict(x=0, xref="x", y=intervalo[1] * 0.99, yref="y",
             ax=0, axref="x", ay=intervalo[1] * 0.82, ayref="y",
             text="", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.6, arrowcolor=cor_eixo),
        # etiqueta "x" junto à ponta do eixo x
        dict(x=0.9, xref="paper", y=0, yref="y", text="x", showarrow=False,
             xanchor="right", yanchor="bottom", yshift=4, font=dict(size=14, color="#1f2430")),
        # etiqueta "y" junto à ponta do eixo y
        dict(x=0, xref="x", y=intervalo[1] * 0.82, yref="y", text="y", showarrow=False,
             xanchor="left", yanchor="top", xshift=6, font=dict(size=14, color="#1f2430")),
        # o "0" na origem, onde os dois eixos se cruzam
        dict(x=0, xref="x", y=0, yref="y", text="0", showarrow=False,
             xanchor="right", yanchor="top", xshift=-4, yshift=-4,
             font=dict(size=11, color="#666666")),
    ]
    fonte_numeros = dict(size=11, color="#666666")  # tipo de letra mais pequeno/cinzento usado nos números das marcas
    v = dtick
    while v <= maximo:  # gera pares de números (positivo e negativo) em cada eixo, espaçados de dtick em dtick
        rotulo = f"{v:g}"
        # número positivo no eixo x
        anotacoes.append(dict(x=v, xref="x", y=0, yref="y", text=rotulo, showarrow=False,
                               xanchor="center", yanchor="top", yshift=-6, font=fonte_numeros))
        # número negativo no eixo x
        anotacoes.append(dict(x=-v, xref="x", y=0, yref="y", text=f"−{rotulo}", showarrow=False,
                               xanchor="center", yanchor="top", yshift=-6, font=fonte_numeros))
        # número positivo no eixo y
        anotacoes.append(dict(x=0, xref="x", y=v, yref="y", text=rotulo, showarrow=False,
                               xanchor="right", yanchor="middle", xshift=-6, font=fonte_numeros))
        # número negativo no eixo y
        anotacoes.append(dict(x=0, xref="x", y=-v, yref="y", text=f"−{rotulo}", showarrow=False,
                               xanchor="right", yanchor="middle", xshift=-6, font=fonte_numeros))
        v += dtick
    return anotacoes


def _layout_com_slider(valores_parametro: Sequence[float], rotulo_parametro: str) -> dict:
    """Layout partilhado: eixos fixos, botões Play/Pause e slider ligados aos frames."""
    return dict(
        # menu de botões "▶ Play"/"⏸ Pause" que controlam a animação dos frames da figura
        updatemenus=[dict(
            type="buttons",
            direction="left",
            x=0.02, y=-0.12, xanchor="left", yanchor="top",  # posição do menu, por baixo do gráfico
            buttons=[
                # "Play": anima a partir do frame atual (fromcurrent=True), 120ms por frame, sem transição extra
                dict(label="▶ Play", method="animate",
                     args=[None, {"frame": {"duration": 120, "redraw": True},
                                   "fromcurrent": True, "transition": {"duration": 0}}]),
                # "Pause": para a animação imediatamente, sem avançar frame
                dict(label="⏸ Pause", method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]),
            ],
        )],
        # slider que mostra/controla manualmente em que frame (valor do parâmetro) a figura está
        sliders=[dict(
            active=len(valores_parametro) - 1,  # começa no último frame (valor final do parâmetro)
            x=0.15, y=-0.12, len=0.8,  # posição e largura do slider, por baixo do gráfico
            currentvalue={"prefix": f"{rotulo_parametro} = ", "visible": True},  # mostra "nome_do_parametro = valor_atual"
            # um "step" do slider por cada valor do parâmetro, ligado a saltar diretamente para esse frame
            steps=[dict(method="animate",
                        args=[[str(v)], {"mode": "immediate",
                                          "frame": {"duration": 0, "redraw": True}}],
                        label=f"{v:.2f}")
                   for v in valores_parametro],
        )],
        margin=dict(b=90),  # margem inferior extra, para dar espaço aos botões/slider sem sobrepor o gráfico
    )


# --------------------------------------------------------------------------
# Vetores
# --------------------------------------------------------------------------

def intervalo_vetores(vetores: list[tuple[str, np.ndarray, str]], minimo: float = 6.0,
                       margem: float = 1.3) -> tuple[float, float]:
    """Domínio automático a partir da maior componente entre os vetores dados
    (público, para os desafios dos Jogos alinharem a camada clicável)."""
    # junta todos os vetores num único array; se a lista estiver vazia, usa um vetor nulo para não rebentar
    pontos = np.array([v for _, v, _ in vetores]) if vetores else np.zeros((1, 2))
    # maior componente em valor absoluto, multiplicada pela margem, mas nunca menor que "minimo"
    limite = max(minimo, float(np.abs(pontos).max()) * margem)
    return (-limite, limite)  # domínio simétrico à volta da origem


def figura_vetores_2d(vetores: list[tuple[str, np.ndarray, str]], titulo: str = "") -> go.Figure:
    """vetores: lista de (nome, array 2D, cor)."""
    fig = go.Figure()
    # ponto preto na origem, só decorativo (sem hover nem entrada na legenda)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=4, color="black"),
                              showlegend=False, hoverinfo="skip"))
    anotacoes = []
    for nome, v, cor in vetores:
        # linha da origem até à ponta do vetor (a "haste" — a ponta em si vem da anotação de seta abaixo)
        fig.add_trace(go.Scatter(x=[0, v[0]], y=[0, v[1]], mode="lines",
                                  line=dict(color=cor, width=3), name=nome))
        # seta desenhada como anotação, da origem (ax,ay) até à ponta do vetor (x,y)
        anotacoes.append(dict(x=v[0], y=v[1], ax=0, ay=0, xref="x", yref="y", axref="x", ayref="y",
                               showarrow=True, arrowhead=3, arrowsize=1.5, arrowcolor=cor))
    intervalo = intervalo_vetores(vetores)  # domínio calculado a partir dos vetores dados
    # junta as setas dos vetores com as anotações fixas dos eixos (números, etiquetas x/y)
    fig.update_layout(title=titulo, annotations=anotacoes + _anotacoes_eixos(intervalo), showlegend=True,
                       **_eixos_geogebra(intervalo))
    return fig


def figura_vetores_3d(vetores: list[tuple[str, np.ndarray, str]], titulo: str = "") -> go.Figure:
    fig = go.Figure()
    for nome, v, cor in vetores:
        # linha 3D da origem até à ponta do vetor
        fig.add_trace(go.Scatter3d(x=[0, v[0]], y=[0, v[1]], z=[0, v[2]], mode="lines",
                                    line=dict(color=cor, width=6), name=nome))
        # cone pequeno na ponta do vetor, a simular a cabeça da seta em 3D
        # (u/v/w são a direção do cone, escalada para ser mínima — só define a orientação, o tamanho vem de sizeref)
        fig.add_trace(go.Cone(x=[v[0]], y=[v[1]], z=[v[2]],
                               u=[v[0] * 0.001], v=[v[1] * 0.001], w=[v[2] * 0.001],
                               showscale=False, colorscale=[[0, cor], [1, cor]],
                               sizemode="absolute", sizeref=0.3, showlegend=False))
    eixo3d = dict(gridcolor="#e3e3e3", zerolinecolor="#444444", backgroundcolor="white")  # estilo comum aos 3 eixos 3D
    fig.update_layout(title=titulo, paper_bgcolor="white",
                       font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#1f2430"),
                       scene=dict(aspectmode="cube", xaxis=eixo3d, yaxis=eixo3d, zaxis=eixo3d),  # "cube": os 3 eixos com a mesma escala visual
                       legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="center", x=0.5))
    return fig


def figura_vetor_parametrizado(
    nome: str, calcular_vetor: Callable[[float], np.ndarray], valores_parametro: np.ndarray,
    dimensao: int, cor: str = CORES_VETORES[0], rotulo_parametro: str = "k", modo_leve: bool = False,
) -> go.Figure:
    """Anima um único vetor nome = calcular_vetor(parametro) ao longo de
    valores_parametro, em 2D ou 3D — usado pela exploração "k·v" do módulo
    Vetores. Em 2D a seta é uma anotação (como em `figura_vetores_2d`), por
    isso animada através do `layout` de cada frame; em 3D é um `go.Cone`
    (uma trace normal), que anima como os outros dados."""
    if modo_leve:
        # reduz o número de frames (fotogramas) da animação, mantendo o mesmo intervalo de valores
        valores_parametro = np.linspace(valores_parametro[0], valores_parametro[-1], N_FRAMES_MODO_LEVE)

    if dimensao == 3:
        def frame_data_3d(p):
            v = calcular_vetor(p)  # vetor correspondente a este valor do parâmetro
            return [
                go.Scatter3d(x=[0, v[0]], y=[0, v[1]], z=[0, v[2]], mode="lines",
                             line=dict(color=cor, width=6), name=nome),
                go.Cone(x=[v[0]], y=[v[1]], z=[v[2]], u=[v[0] * 0.001], v=[v[1] * 0.001], w=[v[2] * 0.001],
                        showscale=False, colorscale=[[0, cor], [1, cor]],
                        sizemode="absolute", sizeref=0.3, showlegend=False),
            ]
        fig = go.Figure(
            data=frame_data_3d(valores_parametro[-1]),  # estado inicial: último valor do parâmetro
            frames=[go.Frame(data=frame_data_3d(p), name=str(p)) for p in valores_parametro],  # um frame por valor
        )
        eixo3d = dict(gridcolor="#e3e3e3", zerolinecolor="#444444", backgroundcolor="white")
        fig.update_layout(
            paper_bgcolor="white", font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#1f2430"),
            scene=dict(aspectmode="cube", xaxis=eixo3d, yaxis=eixo3d, zaxis=eixo3d),
            legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="center", x=0.5),
            **_layout_com_slider(valores_parametro, rotulo_parametro),  # acrescenta os botões Play/Pause + slider
        )
        return fig

    # caso 2D: calcula o domínio a partir de todas as posições que o vetor vai tomar ao longo da animação
    intervalo = intervalo_vetores([(nome, calcular_vetor(p), cor) for p in valores_parametro])

    def seta(p):
        v = calcular_vetor(p)
        # anotação de seta (usada no layout de cada frame, porque anotações não animam como "data")
        return dict(x=v[0], y=v[1], ax=0, ay=0, xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True, arrowhead=3, arrowsize=1.5, arrowcolor=cor)

    def frame_data_2d(p):
        v = calcular_vetor(p)
        return [go.Scatter(x=[0, v[0]], y=[0, v[1]], mode="lines", line=dict(color=cor, width=3), name=nome)]

    fig = go.Figure(
        data=frame_data_2d(valores_parametro[-1]),
        # cada frame tem os seus próprios dados (a linha do vetor) E o seu próprio layout
        # (a anotação da seta + eixos), porque anotações fazem parte do layout, não do "data"
        frames=[go.Frame(data=frame_data_2d(p), name=str(p),
                          layout=go.Layout(annotations=[seta(p)] + _anotacoes_eixos(intervalo)))
                for p in valores_parametro],
    )
    fig.update_layout(
        annotations=[seta(valores_parametro[-1])] + _anotacoes_eixos(intervalo),  # estado inicial (último valor)
        **_layout_com_slider(valores_parametro, rotulo_parametro), **_eixos_geogebra(intervalo),
    )
    return fig


# --------------------------------------------------------------------------
# Sistemas Lineares
# --------------------------------------------------------------------------

def _pontos_reta(a: float, b: float, c: float, intervalo=(-10, 10),
                  modo_leve: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """Pontos (x, y) da reta ax + by = c, gerados num intervalo FATOR_EXTENSAO×
    maior que `intervalo` (a vista inicial) — para que, ao dar zoom-out, a
    reta continue visível em vez de acabar exatamente na margem da vista."""
    n = N_PONTOS_RETA_LEVE if modo_leve else N_PONTOS_RETA  # menos pontos em modo leve
    ampliado = (intervalo[0] * FATOR_EXTENSAO, intervalo[1] * FATOR_EXTENSAO)  # intervalo estendido, além da vista inicial
    xs = np.linspace(*ampliado, n)  # n valores de x, igualmente espaçados no intervalo ampliado
    if abs(b) > 1e-9:
        # caso normal: resolve y em função de x (reta não vertical)
        ys = (c - a * xs) / b
    else:
        # reta vertical (b=0): x é constante = c/a, e é y que varia
        xs = np.full(n, c / a) if abs(a) > 1e-9 else xs
        ys = np.linspace(*ampliado, n)
    return xs, ys


def _pontos_interesse_retas(equacoes: list[tuple[float, float, float]]) -> list[tuple[float, float]]:
    """Interceções com os eixos e pontos de interseção entre cada par de
    retas — usados para calcular automaticamente um domínio que mostre tudo
    o que é relevante, em vez de um intervalo fixo que pode cortar a reta."""
    pontos = []
    for a, b, c in equacoes:
        if abs(a) > 1e-9:
            pontos.append((c / a, 0.0))  # interceção com o eixo x (onde y=0)
        if abs(b) > 1e-9:
            pontos.append((0.0, c / b))  # interceção com o eixo y (onde x=0)
    for i, (a1, b1, c1) in enumerate(equacoes):
        for a2, b2, c2 in equacoes[i + 1:]:  # cada par de retas distintas, sem repetir combinações
            matriz = np.array([[a1, b1], [a2, b2]])
            if abs(np.linalg.det(matriz)) > 1e-9:  # só resolve se as retas não forem paralelas (determinante não nulo)
                pontos.append(tuple(np.linalg.solve(matriz, [c1, c2])))  # ponto de interseção das duas retas
    return pontos


def intervalo_retas(equacoes: list[tuple[float, float, float]], minimo: float = 6.0,
                     margem: float = 1.4) -> tuple[float, float]:
    """Domínio automático (público, para os desafios dos Jogos alinharem a
    camada clicável com o mesmo intervalo desta figura): maior valor absoluto
    entre os pontos de interesse das retas, com margem — nunca mais pequeno
    que `minimo`, para nunca cortar conteúdo relevante."""
    pontos = _pontos_interesse_retas(equacoes)
    if not pontos:  # sem pontos de interesse (ex. só uma reta, sem interceções calculáveis): usa o domínio mínimo
        return (-minimo, minimo)
    maior = max(minimo, float(np.abs(np.array(pontos)).max()) * margem)
    return (-maior, maior)


def figura_retas_2d(equacoes: list[tuple[float, float, float]], intervalo: Optional[tuple[float, float]] = None,
                     modo_leve: bool = False) -> go.Figure:
    """equacoes: lista de (a, b, c) representando ax + by = c.
    Se `intervalo` não for indicado, é calculado automaticamente a partir das
    interceções e interseções das retas, para nunca aparecer cortado."""
    if intervalo is None:
        intervalo = intervalo_retas(equacoes)  # calcula o domínio automaticamente, se não foi dado

    fig = go.Figure()
    cores = CORES_VETORES
    for i, (a, b, c) in enumerate(equacoes):
        xs, ys = _pontos_reta(a, b, c, intervalo, modo_leve)  # pontos da reta i
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"Eq. {i + 1}",
                                  line=dict(color=cores[i % len(cores)], width=3)))  # cor cíclica, se houver mais retas que cores

    for i, (a1, b1, c1) in enumerate(equacoes):
        for j, (a2, b2, c2) in enumerate(equacoes[i + 1:], start=i + 1):  # cada par (i, j) de retas distintas
            matriz = np.array([[a1, b1], [a2, b2]])
            if abs(np.linalg.det(matriz)) > 1e-9:  # retas não paralelas: têm um único ponto de interseção
                ponto = np.linalg.solve(matriz, [c1, c2])
                # marca o ponto de interseção com um círculo preto, com as coordenadas escritas ao lado
                fig.add_trace(go.Scatter(x=[ponto[0]], y=[ponto[1]], mode="markers+text",
                                          marker=dict(size=10, color="black", symbol="circle"),
                                          text=[f"({ponto[0]:.2f}, {ponto[1]:.2f})"], textposition="top center",
                                          name=f"Interseção Eq.{i + 1}/Eq.{j + 1}"))
    fig.update_layout(annotations=_anotacoes_eixos(intervalo), **_eixos_geogebra(intervalo))
    return fig


def figura_retas_2d_parametrizada(
    equacao_fixa: tuple[float, float, float],
    calcular_equacao_variavel: Callable[[float], tuple[float, float, float]],
    valores_parametro: np.ndarray,
    rotulo_parametro: str = "t",
    modo_leve: bool = False,
    rotulos_equacoes: tuple[str, str] = ("Eq. 1", "Eq. 2"),
) -> go.Figure:
    """Anima a 2ª reta (calcular_equacao_variavel(parametro)) e a sua
    interseção com a 1ª reta fixa, ao longo de valores_parametro — usado
    pela exploração de Sistemas Lineares (só sistemas 2×2). `rotulos_equacoes`
    nomeia a legenda de (equacao_fixa, equação variável) nessa ordem — para a
    legenda continuar a mostrar o número real da equação mesmo quando é a 1ª
    equação do sistema (e não a 2ª) que está a variar."""
    if modo_leve:
        valores_parametro = np.linspace(valores_parametro[0], valores_parametro[-1], N_FRAMES_MODO_LEVE)

    # calcula o domínio considerando a reta fixa E todas as posições que a reta variável vai tomar
    intervalo = intervalo_retas([equacao_fixa] + [calcular_equacao_variavel(p) for p in valores_parametro])

    def frame_data(p):
        a2, b2, c2 = calcular_equacao_variavel(p)  # coeficientes da 2ª reta, para este valor do parâmetro
        equacoes = [equacao_fixa, (a2, b2, c2)]
        dados = []
        for i, (a, b, c) in enumerate(equacoes):
            xs, ys = _pontos_reta(a, b, c, intervalo, modo_leve)
            dados.append(go.Scatter(x=xs, y=ys, mode="lines", name=rotulos_equacoes[i],
                                     line=dict(color=CORES_VETORES[i % len(CORES_VETORES)], width=3)))
        a1, b1, c1 = equacao_fixa
        matriz = np.array([[a1, b1], [a2, b2]])
        if abs(np.linalg.det(matriz)) > 1e-9:  # só desenha o ponto de interseção quando as retas não são paralelas
            ponto = np.linalg.solve(matriz, [c1, c2])
            dados.append(go.Scatter(x=[ponto[0]], y=[ponto[1]], mode="markers+text",
                                     marker=dict(size=10, color="black", symbol="circle"),
                                     text=[f"({ponto[0]:.2f}, {ponto[1]:.2f})"], textposition="top center",
                                     name="Interseção"))
        return dados

    fig = go.Figure(
        data=frame_data(valores_parametro[-1]),
        frames=[go.Frame(data=frame_data(p), name=str(p)) for p in valores_parametro],
    )
    fig.update_layout(annotations=_anotacoes_eixos(intervalo),
                       **_layout_com_slider(valores_parametro, rotulo_parametro), **_eixos_geogebra(intervalo))
    return fig


def _pontos_plano(a: float, b: float, c: float, d: float,
                   intervalo: tuple[float, float], n: int = 15) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Malha (X, Y, Z) do plano ax + by + cz = d, resolvendo para a variável
    com o maior coeficiente em valor absoluto (mais estável numericamente —
    evita dividir por um coeficiente perto de zero)."""
    coefs = np.array([a, b, c], dtype=float)
    idx = int(np.argmax(np.abs(coefs)))  # índice da variável com maior coeficiente — é essa que se isola
    livres = [i for i in range(3) if i != idx]  # as outras duas variáveis, tratadas como "livres" (formam a grelha)
    g1, g2 = np.meshgrid(np.linspace(*intervalo, n), np.linspace(*intervalo, n))  # grelha 2D das variáveis livres
    grade = [None, None, None]
    grade[livres[0]] = g1
    grade[livres[1]] = g2
    grade[idx] = (d - coefs[livres[0]] * g1 - coefs[livres[1]] * g2) / coefs[idx]  # resolve a equação para a variável isolada
    return grade[0], grade[1], grade[2]  # (X, Y, Z) prontos para go.Surface


def _interseccao_tripla(equacoes: list[tuple[float, float, float, float]]) -> Optional[np.ndarray]:
    """Ponto de interseção das 3 primeiras equações, se formarem um sistema
    3×3 possível e determinado — None caso contrário (menos/mais equações,
    ou sistema indeterminado/impossível)."""
    if len(equacoes) != 3:  # só faz sentido calcular uma interseção "tripla" com exatamente 3 planos
        return None
    matriz = np.array([[a, b, c] for a, b, c, _ in equacoes])  # matriz dos coeficientes (3×3)
    vetor = np.array([d for _, _, _, d in equacoes])  # vetor dos termos independentes
    if abs(np.linalg.det(matriz)) < 1e-9:  # sistema singular: sem solução única
        return None
    return np.linalg.solve(matriz, vetor)  # ponto único de interseção dos 3 planos


def intervalo_planos(equacoes: list[tuple[float, float, float, float]], minimo: float = 6.0,
                      margem: float = 1.4) -> tuple[float, float]:
    """Domínio automático (cubo simétrico em x/y/z): interceções de cada
    plano com os eixos, mais o ponto de interseção tripla quando existir."""
    pontos = []
    for a, b, c, d in equacoes:
        coefs = [a, b, c]
        for i in range(3):
            if abs(coefs[i]) > 1e-9:
                # interceção do plano com o eixo i (as outras duas coordenadas ficam a zero)
                ponto = [0.0, 0.0, 0.0]
                ponto[i] = d / coefs[i]
                pontos.append(ponto)
    interseccao = _interseccao_tripla(equacoes)
    if interseccao is not None:
        pontos.append(list(interseccao))  # inclui o ponto de interseção tripla, se existir, no cálculo do domínio
    if not pontos:
        return (-minimo, minimo)
    maior = max(minimo, float(np.abs(np.array(pontos)).max()) * margem)
    return (-maior, maior)


def figura_planos_3d(equacoes: list[tuple[float, float, float, float]],
                      intervalo: Optional[tuple[float, float]] = None) -> go.Figure:
    """equacoes: lista de (a, b, c, d) representando ax + by + cz = d —
    usado pela interpretação gráfica de Sistemas Lineares com 3 incógnitas.
    Se `intervalo` não for indicado, é calculado automaticamente."""
    if intervalo is None:
        intervalo = intervalo_planos(equacoes)

    fig = go.Figure()
    for i, (a, b, c, d) in enumerate(equacoes):
        x, y, z = _pontos_plano(a, b, c, d, intervalo)  # malha 3D do plano i
        cor = CORES_VETORES[i % len(CORES_VETORES)]
        # superfície semitransparente (opacity=0.55) para se conseguir ver planos sobrepostos
        fig.add_trace(go.Surface(x=x, y=y, z=z, showscale=False, opacity=0.55,
                                  colorscale=[[0, cor], [1, cor]], name=f"Eq. {i + 1}"))

    interseccao = _interseccao_tripla(equacoes)
    if interseccao is not None:
        # marca o ponto onde os 3 planos se cruzam, se existir um único
        fig.add_trace(go.Scatter3d(
            x=[interseccao[0]], y=[interseccao[1]], z=[interseccao[2]], mode="markers",
            marker=dict(size=5, color="black"), name="Interseção",
        ))

    eixo3d = dict(gridcolor="#e3e3e3", zerolinecolor="#444444", backgroundcolor="white", range=list(intervalo))
    fig.update_layout(
        paper_bgcolor="white", font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#1f2430"),
        scene=dict(aspectmode="cube", xaxis=eixo3d, yaxis=eixo3d, zaxis=eixo3d),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="center", x=0.5),
    )
    return fig


# --------------------------------------------------------------------------
# Transformação linear (Matrizes / Determinantes / Valores Próprios)
# --------------------------------------------------------------------------

def camada_clicavel(intervalo: tuple[float, float] = (-6, 6), passo: float = 0.3) -> go.Scatter:
    """Grelha densa de marcadores quase invisíveis: dá ao clique do utilizador (nos desafios
    visuais dos Jogos) um ponto de dados próximo em qualquer zona do gráfico, já que o Plotly
    só reporta cliques sobre pontos existentes."""
    valores = np.arange(intervalo[0], intervalo[1] + passo, passo)  # posições da grelha densa de marcadores
    xs, ys = np.meshgrid(valores, valores)  # todas as combinações (x, y) dessa grelha
    # marcadores praticamente transparentes (alpha=0.001) mas grandes o suficiente (size=14) para captar o clique
    return go.Scatter(x=xs.ravel(), y=ys.ravel(), mode="markers",
                       marker=dict(size=14, color="rgba(0,0,0,0.001)"),
                       hoverinfo="skip", showlegend=False, name="_alvo_clique")


def _tracos_transformacao(
    m: np.ndarray, mostrar_area: bool = False, direcoes_proprias: Optional[list[np.ndarray]] = None,
    modo_leve: bool = False,
) -> list[go.Scatter]:
    """Traços de uma grelha 2D + círculo unitário transformados pela matriz M
    — partilhado entre a versão estática (`figura_transformacao`) e a
    animada (`figura_transformacao_parametrizada`). A malha usa
    `intervalo_malha` estendido (FATOR_EXTENSAO×) para o zoom-out não a
    cortar; o círculo unitário não precisa disso, é uma curva fechada."""
    # aplica a matriz M a cada ponto da grelha/círculo (multiplicação matricial: pontos @ M^T)
    malha_t = _malha_pontos(modo_leve, intervalo_malha=GRID_INTERVALO * FATOR_EXTENSAO) @ m.T
    circulo_t = _circulo_pontos(modo_leve) @ m.T
    dados = [
        # grelha transformada, em cinzento claro, sem entrada na legenda nem hover (é só referência visual)
        go.Scatter(x=malha_t[:, 0], y=malha_t[:, 1], mode="lines",
                   line=dict(color="lightgray", width=1), showlegend=False, hoverinfo="skip"),
        # círculo unitário transformado (torna-se uma elipse, em geral)
        go.Scatter(x=circulo_t[:, 0], y=circulo_t[:, 1], mode="lines",
                   line=dict(color=CORES_VETORES[1], width=2), name="Círculo unitário transformado"),
        # imagem do primeiro vetor da base (e1 = (1,0)) pela transformação: é a 1ª coluna de M
        go.Scatter(x=[0, m[0, 0]], y=[0, m[1, 0]], mode="lines+markers",
                   line=dict(color=CORES_VETORES[0], width=3), marker=dict(size=6), name="M·e1"),
        # imagem do segundo vetor da base (e2 = (0,1)): é a 2ª coluna de M
        go.Scatter(x=[0, m[0, 1]], y=[0, m[1, 1]], mode="lines+markers",
                   line=dict(color=CORES_VETORES[2], width=3), marker=dict(size=6), name="M·e2"),
    ]
    if mostrar_area:
        # paralelogramo formado pelas duas colunas de M (M·e1 e M·e2); a sua área = |det(M)|
        col0, col1 = m[:, 0], m[:, 1]
        poligono = np.array([[0, 0], col0, col0 + col1, col1, [0, 0]])  # 4 vértices do paralelogramo, fechando no início
        dados.append(go.Scatter(x=poligono[:, 0], y=poligono[:, 1], mode="lines",
                                 fill="toself", fillcolor="rgba(240,142,43,0.25)",
                                 line=dict(color=CORES_VETORES[3]), name=f"det = {np.linalg.det(m):.2f}"))
    if direcoes_proprias:
        for i, d in enumerate(direcoes_proprias):
            escala = 3  # comprimento da reta desenhada, em ambos os sentidos a partir da origem
            # reta tracejada a passar pela origem, na direção do vetor próprio d
            dados.append(go.Scatter(x=[-escala * d[0], escala * d[0]], y=[-escala * d[1], escala * d[1]],
                                     mode="lines", line=dict(color="black", width=1, dash="dash"),
                                     name=f"Direção própria {i + 1}"))
    return dados


def intervalo_transformacao(matrizes: list[np.ndarray], minimo: float = 6.0, margem: float = 1.2) -> tuple[float, float]:
    """Maior coordenada (em valor absoluto) da grelha transformada por
    qualquer uma das matrizes dadas, com margem — para o domínio abranger
    sempre toda a transformação, nunca a cortar."""
    maior = minimo
    for m in matrizes:
        malha_t = _malha_pontos() @ m.T  # grelha padrão transformada por esta matriz
        maior = max(maior, float(np.nanmax(np.abs(malha_t))))  # nanmax ignora os NaN usados para separar as linhas da grelha
    return (-maior * margem, maior * margem)


def figura_transformacao(
    m: np.ndarray, mostrar_area: bool = False, direcoes_proprias: Optional[list[np.ndarray]] = None,
    intervalo: Optional[tuple[float, float]] = None, modo_leve: bool = False,
) -> go.Figure:
    """Versão estática (sem slider/animação) da grelha 2D + círculo unitário
    transformados por M — para uso com controlo por número/setas +/- em vez
    de slider: cada rerun do Streamlit recalcula esta figura para o valor
    atual do parâmetro. Em modo leve, a grelha e o círculo usam menos pontos.
    Se `intervalo` não for indicado, é calculado automaticamente a partir de M."""
    if intervalo is None:
        intervalo = intervalo_transformacao([m])
    fig = go.Figure(data=_tracos_transformacao(m, mostrar_area, direcoes_proprias, modo_leve))
    fig.update_layout(annotations=_anotacoes_eixos(intervalo), **_eixos_geogebra(intervalo))
    return fig


def figura_transformacao_parametrizada(
    calcular_matriz: Callable[[float], np.ndarray],
    valores_parametro: np.ndarray,
    rotulo_parametro: str = "t",
    mostrar_area: bool = False,
    direcoes_proprias: Optional[list[np.ndarray]] = None,
    modo_leve: bool = False,
) -> go.Figure:
    """Anima uma grelha 2D + círculo unitário sob a matriz M(parametro).

    Se mostrar_area=True, desenha também o paralelogramo formado pelas colunas
    de M e anota det(M) — usado por Determinantes para visualizar a matriz a
    tornar-se singular.
    """
    if modo_leve:
        valores_parametro = np.linspace(valores_parametro[0], valores_parametro[-1], N_FRAMES_MODO_LEVE)

    def frame_data(p):
        # matriz correspondente a este valor do parâmetro, convertida nos traços da grelha/círculo/vetores
        return _tracos_transformacao(calcular_matriz(p), mostrar_area, direcoes_proprias)

    # calcula o domínio considerando TODAS as matrizes que a animação vai percorrer, não só a inicial/final
    intervalo = intervalo_transformacao([calcular_matriz(p) for p in valores_parametro])
    fig = go.Figure(
        data=frame_data(valores_parametro[-1]),
        frames=[go.Frame(data=frame_data(p), name=str(p)) for p in valores_parametro],
    )
    fig.update_layout(annotations=_anotacoes_eixos(intervalo),
                       **_layout_com_slider(valores_parametro, rotulo_parametro), **_eixos_geogebra(intervalo))
    return fig


# lista de pares de índices (vértice inicial, vértice final) que formam cada uma das 12 arestas do cubo unitário
_ARESTAS_CUBO = [
    (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3),
    (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7),
]
# os 8 vértices do cubo unitário: todas as combinações de 0/1 em (x, y, z)
_VERTICES_CUBO = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], dtype=float)


def intervalo_transformacao_3d(matrizes: list[np.ndarray], minimo: float = 2.0,
                                margem: float = 1.3) -> tuple[float, float]:
    """Maior coordenada (em valor absoluto) do cubo unitário transformado
    por qualquer uma das matrizes dadas, com margem — para o domínio 3D
    abranger sempre toda a transformação (mesma ideia de `intervalo_transformacao`, em 3D)."""
    maior = minimo
    for m in matrizes:
        vertices_t = _VERTICES_CUBO @ m.T  # vértices do cubo transformados por esta matriz
        maior = max(maior, float(np.abs(vertices_t).max()))
    return (-maior * margem, maior * margem)


def figura_transformacao_3d(
    m: np.ndarray, direcoes_proprias: Optional[list[np.ndarray]] = None,
    intervalo: Optional[tuple[float, float]] = None,
) -> go.Figure:
    """Versão 3D de `figura_transformacao`: o cubo unitário (arestas) e os 3
    vetores da base transformados por M (matriz 3×3) — usado por Valores
    Próprios quando a matriz escolhida é 3×3. `direcoes_proprias`, se dadas,
    desenham-se como retas tracejadas a passar pela origem (a mesma direção
    própria estende-se nos dois sentidos)."""
    if intervalo is None:
        intervalo = intervalo_transformacao_3d([m])

    fig = go.Figure()
    vertices_t = _VERTICES_CUBO @ m.T  # os 8 vértices do cubo, transformados pela matriz M
    for i, j in _ARESTAS_CUBO:
        p1, p2 = vertices_t[i], vertices_t[j]
        # uma linha por cada aresta do cubo transformado, em cinzento claro
        fig.add_trace(go.Scatter3d(x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]], mode="lines",
                                    line=dict(color="lightgray", width=3), showlegend=False, hoverinfo="skip"))

    nomes_base = ["M·e1", "M·e2", "M·e3"]
    for i in range(3):
        v = m[:, i]  # a i-ésima coluna de M = imagem do i-ésimo vetor da base canónica
        cor = CORES_VETORES[i % len(CORES_VETORES)]
        fig.add_trace(go.Scatter3d(x=[0, v[0]], y=[0, v[1]], z=[0, v[2]], mode="lines",
                                    line=dict(color=cor, width=6), name=nomes_base[i]))
        # cone na ponta de cada vetor, tal como em figura_vetores_3d
        fig.add_trace(go.Cone(x=[v[0]], y=[v[1]], z=[v[2]], u=[v[0] * 0.001], v=[v[1] * 0.001], w=[v[2] * 0.001],
                               showscale=False, colorscale=[[0, cor], [1, cor]],
                               sizemode="absolute", sizeref=0.3, showlegend=False))

    if direcoes_proprias:
        escala = intervalo[1] * 0.9  # comprimento das retas das direções próprias, proporcional ao domínio da vista
        for i, d in enumerate(direcoes_proprias):
            dn = d / (np.linalg.norm(d) + 1e-12)  # normaliza o vetor (o +1e-12 evita divisão por zero)
            fig.add_trace(go.Scatter3d(
                x=[-escala * dn[0], escala * dn[0]], y=[-escala * dn[1], escala * dn[1]],
                z=[-escala * dn[2], escala * dn[2]], mode="lines",
                line=dict(color="black", width=2, dash="dash"), name=f"Direção própria {i + 1}",
            ))

    eixo3d = dict(gridcolor="#e3e3e3", zerolinecolor="#444444", backgroundcolor="white", range=list(intervalo))
    fig.update_layout(
        paper_bgcolor="white", font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#1f2430"),
        scene=dict(aspectmode="cube", xaxis=eixo3d, yaxis=eixo3d, zaxis=eixo3d),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="center", x=0.5),
    )
    return fig


# --------------------------------------------------------------------------
# Exploração Gráfica (equações em texto livre, estilo GeoGebra)
# --------------------------------------------------------------------------

def _tracos_exploracao(equacoes: list[tuple[str, ResultadoEquacao, str]]) -> list[go.Scatter | go.Contour]:
    """Traços (sem layout) de uma lista de equações já interpretadas —
    partilhado entre a versão estática e a animada de `figura_exploracao_grafica`.

    Uma equação pode dar mais que um traço (ex. um círculo resolve para
    y = ±√(...), duas curvas) — usa `legendgroup` e só mostra o rótulo na
    legenda uma vez por equação, para não aparecer repetido."""
    tracos = []
    for rotulo, resultado, cor in equacoes:
        if resultado.tipo == "implicita":
            # equação implícita (ex. x²+y²=9): desenha como contorno de nível 0 de uma grelha (X, Y, Z)
            grelha = resultado.grelha
            tracos.append(go.Contour(
                x=grelha.x, y=grelha.y, z=grelha.z,
                contours=dict(start=0, end=0, size=1, coloring="lines"),  # só desenha a linha onde z=0 (a curva da equação)
                line=dict(color=cor, width=2.5), showscale=False,
                name=rotulo, hoverinfo="skip",
            ))
        else:
            # equação explícita/paramétrica: já vem como uma ou mais curvas de pontos (x, y) prontas a desenhar
            for i, curva in enumerate(resultado.curvas):
                tracos.append(go.Scatter(x=curva.x, y=curva.y, mode="lines",
                                          line=dict(color=cor, width=2.5),
                                          name=rotulo, legendgroup=rotulo,
                                          showlegend=(i == 0), hoverinfo="skip"))  # só a 1ª curva desta equação aparece na legenda
    return tracos


def figura_exploracao_grafica(
    equacoes: list[tuple[str, ResultadoEquacao, str]], intervalo: tuple[float, float] = (-10, 10),
    altura: int = 650,
) -> go.Figure:
    """equacoes: lista de (rótulo, resultado já interpretado, cor). Desenha
    cada curva explícita como uma linha e cada resultado implícito como um
    contorno de nível 0 — com uma janela maior (altura fixa em pixels) e
    margens reduzidas, para a Exploração Gráfica ocupar o espaço disponível
    como uma vista GeoGebra. A legenda (rótulo de cada equação) fica visível,
    horizontal, por cima do gráfico — mesmo estilo dos outros módulos."""
    fig = go.Figure(data=_tracos_exploracao(equacoes))
    fig.update_layout(annotations=_anotacoes_eixos(intervalo), **_eixos_geogebra(intervalo),
                       height=altura, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)  # margens mínimas, para aproveitar o espaço
    return fig


def figura_exploracao_grafica_parametrizada(
    calcular_equacoes: Callable[[float], list[tuple[str, ResultadoEquacao, str]]],
    valores_parametro: np.ndarray,
    rotulo_parametro: str = "t",
    intervalo: tuple[float, float] = (-10, 10),
    altura: int = 650,
) -> go.Figure:
    """Versão animada de `figura_exploracao_grafica`: anima UM parâmetro (os
    restantes ficam fixos — o chamador é quem decide isso dentro de
    `calcular_equacoes`, tal como em `figura_transformacao_parametrizada`),
    reaproveitando o slider + ▶ Play/⏸ Pause nativo do Plotly."""
    fig = go.Figure(
        data=_tracos_exploracao(calcular_equacoes(valores_parametro[-1])),  # estado inicial: último valor do parâmetro
        frames=[go.Frame(data=_tracos_exploracao(calcular_equacoes(p)), name=str(p))
                for p in valores_parametro],  # um frame por valor do parâmetro, cada um com as suas próprias curvas
    )
    fig.update_layout(annotations=_anotacoes_eixos(intervalo),
                       **_layout_com_slider(valores_parametro, rotulo_parametro),
                       **_eixos_geogebra(intervalo), height=altura, showlegend=True)
    return fig
