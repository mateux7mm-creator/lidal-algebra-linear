"""Wrappers Plotly reutilizáveis para os módulos do laboratório.

Cada função devolve uma `go.Figure` já pronta para `st.plotly_chart`, com um
estilo visual inspirado no GeoGebra (grelha cinzenta clara, eixos escurecidos
na origem, escala igual em x/y). Os gráficos são recalculados a cada rerun do
Streamlit — a interatividade em tempo real vem de campos numéricos com
setas +/- em vez de animação, por isso não há frames a gerir aqui.
"""
from __future__ import annotations

from typing import Callable, Optional, Sequence

import numpy as np
import plotly.graph_objects as go

from utils.exploracao_grafica import ResultadoEquacao

GRID_INTERVALO = 2  # malha de -2 a 2 — usada para calcular o domínio inicial da vista
FATOR_EXTENSAO = 4  # a malha/retas desenhadas são FATOR_EXTENSAO× maiores que a vista
                     # inicial, para dar zoom-out não revelar espaço vazio a meio da reta/grelha
GRID_PASSO = 0.5
GRID_PASSO_LEVE = 1.0
N_PONTOS_CIRCULO = 60
N_PONTOS_CIRCULO_LEVE = 24
N_PONTOS_RETA = 200
N_PONTOS_RETA_LEVE = 60
N_FRAMES_MODO_LEVE = 12  # usado só por figura_transformacao_parametrizada (Conteúdo/Jogos)
CORES_VETORES = ["#e15759", "#4e79a7", "#59a14f", "#f28e2b", "#b07aa1"]


# --------------------------------------------------------------------------
# Utilitários internos
# --------------------------------------------------------------------------

def _malha_pontos(modo_leve: bool = False, intervalo_malha: float = GRID_INTERVALO) -> np.ndarray:
    """Grelha de linhas horizontais/verticais como pontos 2D, separadas por NaN.
    Em modo leve, usa um espaçamento maior (menos linhas) — mais rápido de
    desenhar em dispositivos/ligações mais fracas. `intervalo_malha` maior que
    `GRID_INTERVALO` estende a malha para além da vista inicial (mesmo nº de
    linhas, cada uma mais longa), para o zoom-out não a cortar."""
    passo = (GRID_PASSO_LEVE if modo_leve else GRID_PASSO) * (intervalo_malha / GRID_INTERVALO)
    valores = np.arange(-intervalo_malha, intervalo_malha + passo, passo)
    pontos = []
    for v in valores:
        pontos += [(-intervalo_malha, v), (intervalo_malha, v), (np.nan, np.nan)]
    for v in valores:
        pontos += [(v, -intervalo_malha), (v, intervalo_malha), (np.nan, np.nan)]
    return np.array(pontos)


def _circulo_pontos(modo_leve: bool = False) -> np.ndarray:
    n = N_PONTOS_CIRCULO_LEVE if modo_leve else N_PONTOS_CIRCULO
    angulos = np.linspace(0, 2 * np.pi, n)
    return np.column_stack([np.cos(angulos), np.sin(angulos)])


def _dtick_legivel(largura: float, maximo_ticks: int = 10) -> float:
    """Escolhe um espaçamento "redondo" (1, 2, 5, 10, 20, 25, 50, ...) entre
    marcas do eixo, com no máximo `maximo_ticks` marcas dentro de `largura`."""
    bruto = largura / maximo_ticks
    passos_redondos = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000]
    return next((p for p in passos_redondos if p >= bruto), passos_redondos[-1])


def _eixos_geogebra(intervalo: tuple[float, float] = (-6, 6)) -> dict:
    """Layout de eixos/grelha ao estilo GeoGebra: grelha cinzenta clara,
    eixos mais escuros a passar pela origem, fundo branco.

    Os números das marcas são escondidos aqui (`showticklabels=False`) e
    substituídos por anotações próprias em `_anotacoes_eixos`, posicionadas
    junto aos eixos que se cruzam (normalmente perto do meio do gráfico),
    não à margem do gráfico como o Plotly faz por omissão — mais parecido
    com o GeoGebra. `dtick` é fixado ao mesmo valor "redondo" usado para
    gerar essas anotações, para a grelha ficar alinhada com os números.

    A legenda fica horizontal, por cima do gráfico (em vez de vertical à
    direita, que é o omissão do Plotly) — liberta espaço horizontal para a
    área do gráfico em si.
    """
    dtick = _dtick_legivel(intervalo[1] - intervalo[0])
    eixo = dict(range=list(intervalo), showgrid=True, gridcolor="#e3e3e3", gridwidth=1,
                zeroline=True, zerolinecolor="#444444", zerolinewidth=2,
                dtick=dtick, showticklabels=False)
    return dict(
        xaxis={**eixo, "scaleanchor": "y", "scaleratio": 1},
        yaxis=eixo,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#1f2430"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    )


def _anotacoes_eixos(intervalo: tuple[float, float]) -> list[dict]:
    """Etiquetas "x"/"y" na ponta de cada eixo + números das marcas junto aos
    próprios eixos (não à margem do gráfico) — ao estilo GeoGebra.

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

    Cada eixo termina numa seta (estilo GeoGebra), desenhada com o mesmo
    truque de anotação usado nos vetores (`showarrow=True, ax/ay` = cauda,
    `x/y` = ponta). A seta do eixo x também usa `xref="paper"` pela mesma
    razão da etiqueta "x": só a coordenada de papel garante a ponta na
    margem direita real, independentemente do esticamento por `scaleanchor`.
    """
    FATOR_EXTENSAO_MARCAS = 2
    dtick = _dtick_legivel(intervalo[1] - intervalo[0])
    maximo = intervalo[1] * FATOR_EXTENSAO_MARCAS
    cor_eixo = "#444444"

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
        dict(x=0.9, xref="paper", y=0, yref="y", text="x", showarrow=False,
             xanchor="right", yanchor="bottom", yshift=4, font=dict(size=14, color="#1f2430")),
        dict(x=0, xref="x", y=intervalo[1] * 0.82, yref="y", text="y", showarrow=False,
             xanchor="left", yanchor="top", xshift=6, font=dict(size=14, color="#1f2430")),
        dict(x=0, xref="x", y=0, yref="y", text="0", showarrow=False,
             xanchor="right", yanchor="top", xshift=-4, yshift=-4,
             font=dict(size=11, color="#666666")),
    ]
    fonte_numeros = dict(size=11, color="#666666")
    v = dtick
    while v <= maximo:
        rotulo = f"{v:g}"
        anotacoes.append(dict(x=v, xref="x", y=0, yref="y", text=rotulo, showarrow=False,
                               xanchor="center", yanchor="top", yshift=-6, font=fonte_numeros))
        anotacoes.append(dict(x=-v, xref="x", y=0, yref="y", text=f"−{rotulo}", showarrow=False,
                               xanchor="center", yanchor="top", yshift=-6, font=fonte_numeros))
        anotacoes.append(dict(x=0, xref="x", y=v, yref="y", text=rotulo, showarrow=False,
                               xanchor="right", yanchor="middle", xshift=-6, font=fonte_numeros))
        anotacoes.append(dict(x=0, xref="x", y=-v, yref="y", text=f"−{rotulo}", showarrow=False,
                               xanchor="right", yanchor="middle", xshift=-6, font=fonte_numeros))
        v += dtick
    return anotacoes


def _layout_com_slider(valores_parametro: Sequence[float], rotulo_parametro: str) -> dict:
    """Layout partilhado: eixos fixos, botões Play/Pause e slider ligados aos frames."""
    return dict(
        updatemenus=[dict(
            type="buttons",
            direction="left",
            x=0.02, y=-0.12, xanchor="left", yanchor="top",
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None, {"frame": {"duration": 120, "redraw": True},
                                   "fromcurrent": True, "transition": {"duration": 0}}]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}]),
            ],
        )],
        sliders=[dict(
            active=len(valores_parametro) - 1,
            x=0.15, y=-0.12, len=0.8,
            currentvalue={"prefix": f"{rotulo_parametro} = ", "visible": True},
            steps=[dict(method="animate",
                        args=[[str(v)], {"mode": "immediate",
                                          "frame": {"duration": 0, "redraw": True}}],
                        label=f"{v:.2f}")
                   for v in valores_parametro],
        )],
        margin=dict(b=90),
    )


# --------------------------------------------------------------------------
# Vetores
# --------------------------------------------------------------------------

def intervalo_vetores(vetores: list[tuple[str, np.ndarray, str]], minimo: float = 6.0,
                       margem: float = 1.3) -> tuple[float, float]:
    """Domínio automático a partir da maior componente entre os vetores dados
    (público, para os desafios dos Jogos alinharem a camada clicável)."""
    pontos = np.array([v for _, v, _ in vetores]) if vetores else np.zeros((1, 2))
    limite = max(minimo, float(np.abs(pontos).max()) * margem)
    return (-limite, limite)


def figura_vetores_2d(vetores: list[tuple[str, np.ndarray, str]], titulo: str = "") -> go.Figure:
    """vetores: lista de (nome, array 2D, cor)."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=4, color="black"),
                              showlegend=False, hoverinfo="skip"))
    anotacoes = []
    for nome, v, cor in vetores:
        fig.add_trace(go.Scatter(x=[0, v[0]], y=[0, v[1]], mode="lines",
                                  line=dict(color=cor, width=3), name=nome))
        anotacoes.append(dict(x=v[0], y=v[1], ax=0, ay=0, xref="x", yref="y", axref="x", ayref="y",
                               showarrow=True, arrowhead=3, arrowsize=1.5, arrowcolor=cor))
    intervalo = intervalo_vetores(vetores)
    fig.update_layout(title=titulo, annotations=anotacoes + _anotacoes_eixos(intervalo), showlegend=True,
                       **_eixos_geogebra(intervalo))
    return fig


def figura_vetores_3d(vetores: list[tuple[str, np.ndarray, str]], titulo: str = "") -> go.Figure:
    fig = go.Figure()
    for nome, v, cor in vetores:
        fig.add_trace(go.Scatter3d(x=[0, v[0]], y=[0, v[1]], z=[0, v[2]], mode="lines",
                                    line=dict(color=cor, width=6), name=nome))
        fig.add_trace(go.Cone(x=[v[0]], y=[v[1]], z=[v[2]],
                               u=[v[0] * 0.001], v=[v[1] * 0.001], w=[v[2] * 0.001],
                               showscale=False, colorscale=[[0, cor], [1, cor]],
                               sizemode="absolute", sizeref=0.3, showlegend=False))
    eixo3d = dict(gridcolor="#e3e3e3", zerolinecolor="#444444", backgroundcolor="white")
    fig.update_layout(title=titulo, paper_bgcolor="white",
                       font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#1f2430"),
                       scene=dict(aspectmode="cube", xaxis=eixo3d, yaxis=eixo3d, zaxis=eixo3d),
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
        valores_parametro = np.linspace(valores_parametro[0], valores_parametro[-1], N_FRAMES_MODO_LEVE)

    if dimensao == 3:
        def frame_data_3d(p):
            v = calcular_vetor(p)
            return [
                go.Scatter3d(x=[0, v[0]], y=[0, v[1]], z=[0, v[2]], mode="lines",
                             line=dict(color=cor, width=6), name=nome),
                go.Cone(x=[v[0]], y=[v[1]], z=[v[2]], u=[v[0] * 0.001], v=[v[1] * 0.001], w=[v[2] * 0.001],
                        showscale=False, colorscale=[[0, cor], [1, cor]],
                        sizemode="absolute", sizeref=0.3, showlegend=False),
            ]
        fig = go.Figure(
            data=frame_data_3d(valores_parametro[-1]),
            frames=[go.Frame(data=frame_data_3d(p), name=str(p)) for p in valores_parametro],
        )
        eixo3d = dict(gridcolor="#e3e3e3", zerolinecolor="#444444", backgroundcolor="white")
        fig.update_layout(
            paper_bgcolor="white", font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#1f2430"),
            scene=dict(aspectmode="cube", xaxis=eixo3d, yaxis=eixo3d, zaxis=eixo3d),
            legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="center", x=0.5),
            **_layout_com_slider(valores_parametro, rotulo_parametro),
        )
        return fig

    intervalo = intervalo_vetores([(nome, calcular_vetor(p), cor) for p in valores_parametro])

    def seta(p):
        v = calcular_vetor(p)
        return dict(x=v[0], y=v[1], ax=0, ay=0, xref="x", yref="y", axref="x", ayref="y",
                    showarrow=True, arrowhead=3, arrowsize=1.5, arrowcolor=cor)

    def frame_data_2d(p):
        v = calcular_vetor(p)
        return [go.Scatter(x=[0, v[0]], y=[0, v[1]], mode="lines", line=dict(color=cor, width=3), name=nome)]

    fig = go.Figure(
        data=frame_data_2d(valores_parametro[-1]),
        frames=[go.Frame(data=frame_data_2d(p), name=str(p),
                          layout=go.Layout(annotations=[seta(p)] + _anotacoes_eixos(intervalo)))
                for p in valores_parametro],
    )
    fig.update_layout(
        annotations=[seta(valores_parametro[-1])] + _anotacoes_eixos(intervalo),
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
    n = N_PONTOS_RETA_LEVE if modo_leve else N_PONTOS_RETA
    ampliado = (intervalo[0] * FATOR_EXTENSAO, intervalo[1] * FATOR_EXTENSAO)
    xs = np.linspace(*ampliado, n)
    if abs(b) > 1e-9:
        ys = (c - a * xs) / b
    else:
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
            pontos.append((c / a, 0.0))
        if abs(b) > 1e-9:
            pontos.append((0.0, c / b))
    for i, (a1, b1, c1) in enumerate(equacoes):
        for a2, b2, c2 in equacoes[i + 1:]:
            matriz = np.array([[a1, b1], [a2, b2]])
            if abs(np.linalg.det(matriz)) > 1e-9:
                pontos.append(tuple(np.linalg.solve(matriz, [c1, c2])))
    return pontos


def intervalo_retas(equacoes: list[tuple[float, float, float]], minimo: float = 6.0,
                     margem: float = 1.4) -> tuple[float, float]:
    """Domínio automático (público, para os desafios dos Jogos alinharem a
    camada clicável com o mesmo intervalo desta figura): maior valor absoluto
    entre os pontos de interesse das retas, com margem — nunca mais pequeno
    que `minimo`, para nunca cortar conteúdo relevante."""
    pontos = _pontos_interesse_retas(equacoes)
    if not pontos:
        return (-minimo, minimo)
    maior = max(minimo, float(np.abs(np.array(pontos)).max()) * margem)
    return (-maior, maior)


def figura_retas_2d(equacoes: list[tuple[float, float, float]], intervalo: Optional[tuple[float, float]] = None,
                     modo_leve: bool = False) -> go.Figure:
    """equacoes: lista de (a, b, c) representando ax + by = c.
    Se `intervalo` não for indicado, é calculado automaticamente a partir das
    interceções e interseções das retas, para nunca aparecer cortado."""
    if intervalo is None:
        intervalo = intervalo_retas(equacoes)

    fig = go.Figure()
    cores = CORES_VETORES
    for i, (a, b, c) in enumerate(equacoes):
        xs, ys = _pontos_reta(a, b, c, intervalo, modo_leve)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"Eq. {i + 1}",
                                  line=dict(color=cores[i % len(cores)], width=3)))

    for i, (a1, b1, c1) in enumerate(equacoes):
        for j, (a2, b2, c2) in enumerate(equacoes[i + 1:], start=i + 1):
            matriz = np.array([[a1, b1], [a2, b2]])
            if abs(np.linalg.det(matriz)) > 1e-9:
                ponto = np.linalg.solve(matriz, [c1, c2])
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

    intervalo = intervalo_retas([equacao_fixa] + [calcular_equacao_variavel(p) for p in valores_parametro])

    def frame_data(p):
        a2, b2, c2 = calcular_equacao_variavel(p)
        equacoes = [equacao_fixa, (a2, b2, c2)]
        dados = []
        for i, (a, b, c) in enumerate(equacoes):
            xs, ys = _pontos_reta(a, b, c, intervalo, modo_leve)
            dados.append(go.Scatter(x=xs, y=ys, mode="lines", name=rotulos_equacoes[i],
                                     line=dict(color=CORES_VETORES[i % len(CORES_VETORES)], width=3)))
        a1, b1, c1 = equacao_fixa
        matriz = np.array([[a1, b1], [a2, b2]])
        if abs(np.linalg.det(matriz)) > 1e-9:
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
    idx = int(np.argmax(np.abs(coefs)))
    livres = [i for i in range(3) if i != idx]
    g1, g2 = np.meshgrid(np.linspace(*intervalo, n), np.linspace(*intervalo, n))
    grade = [None, None, None]
    grade[livres[0]] = g1
    grade[livres[1]] = g2
    grade[idx] = (d - coefs[livres[0]] * g1 - coefs[livres[1]] * g2) / coefs[idx]
    return grade[0], grade[1], grade[2]


def _interseccao_tripla(equacoes: list[tuple[float, float, float, float]]) -> Optional[np.ndarray]:
    """Ponto de interseção das 3 primeiras equações, se formarem um sistema
    3×3 possível e determinado — None caso contrário (menos/mais equações,
    ou sistema indeterminado/impossível)."""
    if len(equacoes) != 3:
        return None
    matriz = np.array([[a, b, c] for a, b, c, _ in equacoes])
    vetor = np.array([d for _, _, _, d in equacoes])
    if abs(np.linalg.det(matriz)) < 1e-9:
        return None
    return np.linalg.solve(matriz, vetor)


def intervalo_planos(equacoes: list[tuple[float, float, float, float]], minimo: float = 6.0,
                      margem: float = 1.4) -> tuple[float, float]:
    """Domínio automático (cubo simétrico em x/y/z): interceções de cada
    plano com os eixos, mais o ponto de interseção tripla quando existir."""
    pontos = []
    for a, b, c, d in equacoes:
        coefs = [a, b, c]
        for i in range(3):
            if abs(coefs[i]) > 1e-9:
                ponto = [0.0, 0.0, 0.0]
                ponto[i] = d / coefs[i]
                pontos.append(ponto)
    interseccao = _interseccao_tripla(equacoes)
    if interseccao is not None:
        pontos.append(list(interseccao))
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
        x, y, z = _pontos_plano(a, b, c, d, intervalo)
        cor = CORES_VETORES[i % len(CORES_VETORES)]
        fig.add_trace(go.Surface(x=x, y=y, z=z, showscale=False, opacity=0.55,
                                  colorscale=[[0, cor], [1, cor]], name=f"Eq. {i + 1}"))

    interseccao = _interseccao_tripla(equacoes)
    if interseccao is not None:
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
    valores = np.arange(intervalo[0], intervalo[1] + passo, passo)
    xs, ys = np.meshgrid(valores, valores)
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
    malha_t = _malha_pontos(modo_leve, intervalo_malha=GRID_INTERVALO * FATOR_EXTENSAO) @ m.T
    circulo_t = _circulo_pontos(modo_leve) @ m.T
    dados = [
        go.Scatter(x=malha_t[:, 0], y=malha_t[:, 1], mode="lines",
                   line=dict(color="lightgray", width=1), showlegend=False, hoverinfo="skip"),
        go.Scatter(x=circulo_t[:, 0], y=circulo_t[:, 1], mode="lines",
                   line=dict(color=CORES_VETORES[1], width=2), name="Círculo unitário transformado"),
        go.Scatter(x=[0, m[0, 0]], y=[0, m[1, 0]], mode="lines+markers",
                   line=dict(color=CORES_VETORES[0], width=3), marker=dict(size=6), name="M·e1"),
        go.Scatter(x=[0, m[0, 1]], y=[0, m[1, 1]], mode="lines+markers",
                   line=dict(color=CORES_VETORES[2], width=3), marker=dict(size=6), name="M·e2"),
    ]
    if mostrar_area:
        col0, col1 = m[:, 0], m[:, 1]
        poligono = np.array([[0, 0], col0, col0 + col1, col1, [0, 0]])
        dados.append(go.Scatter(x=poligono[:, 0], y=poligono[:, 1], mode="lines",
                                 fill="toself", fillcolor="rgba(240,142,43,0.25)",
                                 line=dict(color=CORES_VETORES[3]), name=f"det = {np.linalg.det(m):.2f}"))
    if direcoes_proprias:
        for i, d in enumerate(direcoes_proprias):
            escala = 3
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
        malha_t = _malha_pontos() @ m.T
        maior = max(maior, float(np.nanmax(np.abs(malha_t))))
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
        return _tracos_transformacao(calcular_matriz(p), mostrar_area, direcoes_proprias)

    intervalo = intervalo_transformacao([calcular_matriz(p) for p in valores_parametro])
    fig = go.Figure(
        data=frame_data(valores_parametro[-1]),
        frames=[go.Frame(data=frame_data(p), name=str(p)) for p in valores_parametro],
    )
    fig.update_layout(annotations=_anotacoes_eixos(intervalo),
                       **_layout_com_slider(valores_parametro, rotulo_parametro), **_eixos_geogebra(intervalo))
    return fig


_ARESTAS_CUBO = [
    (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3),
    (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7),
]
_VERTICES_CUBO = np.array([[x, y, z] for x in (0, 1) for y in (0, 1) for z in (0, 1)], dtype=float)


def intervalo_transformacao_3d(matrizes: list[np.ndarray], minimo: float = 2.0,
                                margem: float = 1.3) -> tuple[float, float]:
    """Maior coordenada (em valor absoluto) do cubo unitário transformado
    por qualquer uma das matrizes dadas, com margem — para o domínio 3D
    abranger sempre toda a transformação (mesma ideia de `intervalo_transformacao`, em 3D)."""
    maior = minimo
    for m in matrizes:
        vertices_t = _VERTICES_CUBO @ m.T
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
    vertices_t = _VERTICES_CUBO @ m.T
    for i, j in _ARESTAS_CUBO:
        p1, p2 = vertices_t[i], vertices_t[j]
        fig.add_trace(go.Scatter3d(x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]], mode="lines",
                                    line=dict(color="lightgray", width=3), showlegend=False, hoverinfo="skip"))

    nomes_base = ["M·e1", "M·e2", "M·e3"]
    for i in range(3):
        v = m[:, i]
        cor = CORES_VETORES[i % len(CORES_VETORES)]
        fig.add_trace(go.Scatter3d(x=[0, v[0]], y=[0, v[1]], z=[0, v[2]], mode="lines",
                                    line=dict(color=cor, width=6), name=nomes_base[i]))
        fig.add_trace(go.Cone(x=[v[0]], y=[v[1]], z=[v[2]], u=[v[0] * 0.001], v=[v[1] * 0.001], w=[v[2] * 0.001],
                               showscale=False, colorscale=[[0, cor], [1, cor]],
                               sizemode="absolute", sizeref=0.3, showlegend=False))

    if direcoes_proprias:
        escala = intervalo[1] * 0.9
        for i, d in enumerate(direcoes_proprias):
            dn = d / (np.linalg.norm(d) + 1e-12)
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
            grelha = resultado.grelha
            tracos.append(go.Contour(
                x=grelha.x, y=grelha.y, z=grelha.z,
                contours=dict(start=0, end=0, size=1, coloring="lines"),
                line=dict(color=cor, width=2.5), showscale=False,
                name=rotulo, hoverinfo="skip",
            ))
        else:
            for i, curva in enumerate(resultado.curvas):
                tracos.append(go.Scatter(x=curva.x, y=curva.y, mode="lines",
                                          line=dict(color=cor, width=2.5),
                                          name=rotulo, legendgroup=rotulo,
                                          showlegend=(i == 0), hoverinfo="skip"))
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
                       height=altura, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
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
        data=_tracos_exploracao(calcular_equacoes(valores_parametro[-1])),
        frames=[go.Frame(data=_tracos_exploracao(calcular_equacoes(p)), name=str(p))
                for p in valores_parametro],
    )
    fig.update_layout(annotations=_anotacoes_eixos(intervalo),
                       **_layout_com_slider(valores_parametro, rotulo_parametro),
                       **_eixos_geogebra(intervalo), height=altura, showlegend=True)
    return fig
