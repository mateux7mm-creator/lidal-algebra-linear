"""Wrappers Plotly reutilizáveis para os módulos do laboratório.

Cada função devolve uma `go.Figure` já pronta para `st.plotly_chart`. As
figuras "animadas" (transformação, sistema, vetor escalado) constroem todos
os frames de uma vez no servidor; a animação em si (slider + botão Play)
corre inteiramente no browser, sem pedidos adicionais ao Streamlit.
"""
from __future__ import annotations

from typing import Callable, Optional, Sequence

import numpy as np
import plotly.graph_objects as go

GRID_INTERVALO = 2  # malha de -2 a 2
GRID_PASSO = 0.5
N_PONTOS_CIRCULO = 60
N_FRAMES_NORMAL = 30
N_FRAMES_MODO_LEVE = 12
CORES_VETORES = ["#e15759", "#4e79a7", "#59a14f", "#f28e2b", "#b07aa1"]


# --------------------------------------------------------------------------
# Utilitários internos
# --------------------------------------------------------------------------

def _malha_pontos() -> np.ndarray:
    """Grelha de linhas horizontais/verticais como pontos 2D, separadas por NaN."""
    valores = np.arange(-GRID_INTERVALO, GRID_INTERVALO + GRID_PASSO, GRID_PASSO)
    pontos = []
    for v in valores:
        pontos += [(-GRID_INTERVALO, v), (GRID_INTERVALO, v), (np.nan, np.nan)]
    for v in valores:
        pontos += [(v, -GRID_INTERVALO), (v, GRID_INTERVALO), (np.nan, np.nan)]
    return np.array(pontos)


def _circulo_pontos() -> np.ndarray:
    angulos = np.linspace(0, 2 * np.pi, N_PONTOS_CIRCULO)
    return np.column_stack([np.cos(angulos), np.sin(angulos)])


def n_frames(modo_leve: bool) -> int:
    return N_FRAMES_MODO_LEVE if modo_leve else N_FRAMES_NORMAL


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
    fig.update_layout(title=titulo, annotations=anotacoes,
                       xaxis=dict(zeroline=True, scaleanchor="y", scaleratio=1),
                       yaxis=dict(zeroline=True), showlegend=True)
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
    fig.update_layout(title=titulo, scene=dict(aspectmode="cube"))
    return fig


def figura_vetor_escalado(v: np.ndarray, valores_k: np.ndarray, modo_leve: bool = False) -> go.Figure:
    """Anima k·v ao longo de valores_k. Suporta v 2D ou 3D."""
    if modo_leve:
        valores_k = np.linspace(valores_k[0], valores_k[-1], N_FRAMES_MODO_LEVE)

    if len(v) == 2:
        def frame_data(k):
            kv = k * v
            return [go.Scatter(x=[0, kv[0]], y=[0, kv[1]], mode="lines",
                                line=dict(color=CORES_VETORES[0], width=3), name="k·v")]

        def frame_layout(k):
            kv = k * v
            return go.Layout(annotations=[dict(
                x=kv[0], y=kv[1], ax=0, ay=0, xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1.5, arrowcolor=CORES_VETORES[0],
            )])

        fig = go.Figure(
            data=frame_data(valores_k[-1]),
            frames=[go.Frame(data=frame_data(k), layout=frame_layout(k), name=str(k)) for k in valores_k],
        )
        fig.update_layout(**_layout_com_slider(valores_k, "k"),
                           xaxis=dict(range=[-6, 6], zeroline=True, scaleanchor="y", scaleratio=1),
                           yaxis=dict(range=[-6, 6], zeroline=True))
        fig.update_layout(annotations=frame_layout(valores_k[-1]).annotations)
        return fig

    def frame_data_3d(k):
        kv = k * v
        return [
            go.Scatter3d(x=[0, kv[0]], y=[0, kv[1]], z=[0, kv[2]], mode="lines",
                         line=dict(color=CORES_VETORES[0], width=6), name="k·v"),
            go.Cone(x=[kv[0]], y=[kv[1]], z=[kv[2]],
                    u=[kv[0] * 0.001], v=[kv[1] * 0.001], w=[kv[2] * 0.001],
                    showscale=False, colorscale=[[0, CORES_VETORES[0]], [1, CORES_VETORES[0]]],
                    sizemode="absolute", sizeref=0.3, showlegend=False),
        ]

    fig = go.Figure(
        data=frame_data_3d(valores_k[-1]),
        frames=[go.Frame(data=frame_data_3d(k), name=str(k)) for k in valores_k],
    )
    fig.update_layout(**_layout_com_slider(valores_k, "k"),
                       scene=dict(aspectmode="cube",
                                  xaxis=dict(range=[-6, 6]), yaxis=dict(range=[-6, 6]), zaxis=dict(range=[-6, 6])))
    return fig


# --------------------------------------------------------------------------
# Sistemas Lineares
# --------------------------------------------------------------------------

def _pontos_reta(a: float, b: float, c: float, intervalo=(-10, 10)) -> tuple[np.ndarray, np.ndarray]:
    """Pontos (x, y) da reta ax + by = c dentro do intervalo dado."""
    xs = np.linspace(*intervalo, 200)
    if abs(b) > 1e-9:
        ys = (c - a * xs) / b
    else:
        xs = np.full(200, c / a) if abs(a) > 1e-9 else xs
        ys = np.linspace(*intervalo, 200)
    return xs, ys


def figura_retas_2d(equacoes: list[tuple[float, float, float]], intervalo=(-10, 10)) -> go.Figure:
    """equacoes: lista de (a, b, c) representando ax + by = c."""
    fig = go.Figure()
    cores = CORES_VETORES
    for i, (a, b, c) in enumerate(equacoes):
        xs, ys = _pontos_reta(a, b, c, intervalo)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"Eq. {i + 1}",
                                  line=dict(color=cores[i % len(cores)], width=3)))

    if len(equacoes) == 2:
        a1, b1, c1 = equacoes[0]
        a2, b2, c2 = equacoes[1]
        matriz = np.array([[a1, b1], [a2, b2]])
        if abs(np.linalg.det(matriz)) > 1e-9:
            ponto = np.linalg.solve(matriz, [c1, c2])
            fig.add_trace(go.Scatter(x=[ponto[0]], y=[ponto[1]], mode="markers+text",
                                      marker=dict(size=12, color="black", symbol="x"),
                                      text=[f"({ponto[0]:.2f}, {ponto[1]:.2f})"], textposition="top center",
                                      name="Interseção"))
    fig.update_layout(xaxis=dict(range=list(intervalo), zeroline=True, scaleanchor="y", scaleratio=1),
                       yaxis=dict(range=list(intervalo), zeroline=True))
    return fig


def figura_sistema_2d_animado(
    equacao_fixa: tuple[float, float, float],
    calcular_equacao_variavel: Callable[[float], tuple[float, float, float]],
    valores_parametro: np.ndarray,
    intervalo=(-10, 10),
    modo_leve: bool = False,
) -> go.Figure:
    """Anima a 2ª reta (dada por calcular_equacao_variavel(parametro)) e o ponto de interseção
    com a 1ª reta, fixa."""
    if modo_leve:
        valores_parametro = np.linspace(valores_parametro[0], valores_parametro[-1], N_FRAMES_MODO_LEVE)

    a1, b1, c1 = equacao_fixa
    xs_fixa, ys_fixa = _pontos_reta(a1, b1, c1, intervalo)

    def frame_data(p):
        a2, b2, c2 = calcular_equacao_variavel(p)
        xs_var, ys_var = _pontos_reta(a2, b2, c2, intervalo)
        dados = [
            go.Scatter(x=xs_fixa, y=ys_fixa, mode="lines", name="Eq. 1",
                       line=dict(color=CORES_VETORES[0], width=3)),
            go.Scatter(x=xs_var, y=ys_var, mode="lines", name="Eq. 2",
                       line=dict(color=CORES_VETORES[1], width=3)),
        ]
        matriz = np.array([[a1, b1], [a2, b2]])
        if abs(np.linalg.det(matriz)) > 1e-9:
            ponto = np.linalg.solve(matriz, [c1, c2])
            dados.append(go.Scatter(x=[ponto[0]], y=[ponto[1]], mode="markers",
                                     marker=dict(size=12, color="black", symbol="x"), name="Interseção"))
        else:
            dados.append(go.Scatter(x=[], y=[], mode="markers", name="Interseção"))
        return dados

    fig = go.Figure(
        data=frame_data(valores_parametro[-1]),
        frames=[go.Frame(data=frame_data(p), name=str(p)) for p in valores_parametro],
    )
    fig.update_layout(**_layout_com_slider(valores_parametro, "coef."),
                       xaxis=dict(range=list(intervalo), zeroline=True, scaleanchor="y", scaleratio=1),
                       yaxis=dict(range=list(intervalo), zeroline=True))
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

    malha = _malha_pontos()
    circulo = _circulo_pontos()

    def frame_data(p):
        m = calcular_matriz(p)
        malha_t = malha @ m.T
        circulo_t = circulo @ m.T
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

    fig = go.Figure(
        data=frame_data(valores_parametro[-1]),
        frames=[go.Frame(data=frame_data(p), name=str(p)) for p in valores_parametro],
    )
    fig.update_layout(**_layout_com_slider(valores_parametro, rotulo_parametro),
                       xaxis=dict(range=[-6, 6], zeroline=True, scaleanchor="y", scaleratio=1),
                       yaxis=dict(range=[-6, 6], zeroline=True))
    return fig
