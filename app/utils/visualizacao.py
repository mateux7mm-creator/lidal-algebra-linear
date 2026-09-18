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


def _eixos_geogebra(intervalo: tuple[float, float] = (-6, 6)) -> dict:
    """Layout de eixos/grelha ao estilo GeoGebra: grelha cinzenta clara,
    eixos mais escuros a passar pela origem, fundo branco, texto horizontal.

    Usa `nticks` (não `dtick`) porque `scaleanchor`/`scaleratio` (escala igual
    em x/y) pode expandir o eixo x muito além de `intervalo` para caber no
    aspeto do contentor — um `dtick` fixo calculado a partir de `intervalo`
    ficaria sobrelotado nesse caso; `nticks` deixa o Plotly escolher um
    espaçamento "redondo" já a partir do intervalo final, seja ele qual for.
    """
    eixo = dict(range=list(intervalo), showgrid=True, gridcolor="#e3e3e3", gridwidth=1,
                zeroline=True, zerolinecolor="#444444", zerolinewidth=2,
                nticks=13, tickangle=0)
    return dict(
        xaxis={**eixo, "scaleanchor": "y", "scaleratio": 1},
        yaxis=eixo,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#1f2430"),
    )


def _anotacoes_eixos(intervalo: tuple[float, float]) -> list[dict]:
    """Pequenas etiquetas "x"/"y" perto da ponta positiva de cada eixo, ao
    estilo GeoGebra — usa anotações (não `xaxis.title`/`yaxis.title`, que ao
    ficarem centradas ao longo do eixo sobrepunham-se ao valor "0" da grelha
    em gráficos pequenos).

    A etiqueta "x" usa `xref="paper"` (sempre a margem direita real do
    gráfico) em vez de `xref="x"` (dados): como `scaleanchor`/`scaleratio`
    (escala igual x/y) pode esticar o eixo x muito além de `intervalo` para
    caber no aspeto do contentor, uma posição em coordenadas de dados como
    `x=intervalo[1]` deixaria de estar junto à margem, ficando perto do
    centro. O eixo y não estica (é a referência de `scaleanchor`), por isso
    a etiqueta "y" pode usar coordenadas de dados em ambos os eixos.
    """
    return [
        dict(x=0.99, xref="paper", y=0, yref="y", text="x", showarrow=False,
             xanchor="right", yanchor="bottom", yshift=4, font=dict(size=14, color="#1f2430")),
        dict(x=0, xref="x", y=intervalo[1], yref="y", text="y", showarrow=False,
             xanchor="left", yanchor="top", xshift=6, font=dict(size=14, color="#1f2430")),
    ]


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
                       scene=dict(aspectmode="cube", xaxis=eixo3d, yaxis=eixo3d, zaxis=eixo3d))
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
