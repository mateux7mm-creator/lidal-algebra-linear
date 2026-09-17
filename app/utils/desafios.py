"""Geração de desafios/quiz para o módulo "Jogos e Desafios".

Cada `gerar_desafio_*` gera valores aleatórios pequenos e reutiliza as
funções de cálculo já existentes em `simbolico.py` — nunca duplica lógica de
cálculo, só embrulha os valores num enunciado contextualizado (Kwanza,
geografia angolana) para tornar a prática mais próxima da realidade.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import plotly.graph_objects as go

from utils import simbolico
from utils.visualizacao import camada_clicavel, figura_retas_2d, figura_transformacao_parametrizada, figura_vetores_2d

CIDADES = ["Luanda", "Huambo", "Lobito", "Benguela", "Lubango", "Malanje"]


@dataclass
class Desafio:
    """Um desafio de escolha múltipla gerado dinamicamente."""

    pergunta: str
    opcoes: list[str]
    indice_correto: int
    explicacao: str = ""


@dataclass
class DesafioVisual:
    """Um desafio resolvido clicando num gráfico Plotly."""

    instrucao: str
    ponto_esperado: tuple[float, float]
    modo: Literal["ponto", "direcao"] = "ponto"
    tolerancia: float = 0.6
    explicacao: str = ""


def _matriz_aleatoria(dim: int = 2, minimo: int = -4, maximo: int = 4) -> np.ndarray:
    return np.random.randint(minimo, maximo + 1, size=(dim, dim)).astype(float)


def _vetor_aleatorio(dim: int = 2, minimo: int = -5, maximo: int = 5) -> np.ndarray:
    return np.random.randint(minimo, maximo + 1, size=dim).astype(float)


def _formatar_matriz(m: np.ndarray) -> str:
    linhas = ["[" + ", ".join(f"{v:g}" for v in linha) + "]" for linha in m]
    return "[" + ", ".join(linhas) + "]"


def _opcoes_com_perturbacao(correta: np.ndarray, formatar, n_opcoes: int = 4) -> tuple[list[str], int]:
    """Gera n_opcoes-1 alternativas erradas perturbando a resposta correta, e baralha."""
    opcoes = [formatar(correta)]
    tentativas = 0
    while len(opcoes) < n_opcoes and tentativas < 20:
        tentativas += 1
        perturbacao = correta + np.random.randint(-3, 4, size=correta.shape)
        texto = formatar(perturbacao)
        if texto not in opcoes:
            opcoes.append(texto)
    indices = list(range(len(opcoes)))
    random.shuffle(indices)
    opcoes_baralhadas = [opcoes[i] for i in indices]
    indice_correto = opcoes_baralhadas.index(opcoes[0])
    return opcoes_baralhadas, indice_correto


# --------------------------------------------------------------------------
# Desafios de quiz
# --------------------------------------------------------------------------

def gerar_desafio_matrizes() -> Desafio:
    cidade = random.choice(CIDADES)
    a = _matriz_aleatoria(2, -3, 3)
    b = _matriz_aleatoria(2, -3, 3)
    a_sp, b_sp = simbolico.para_sympy(a), simbolico.para_sympy(b)
    resultado_sp, _ = simbolico.somar_matrizes(a_sp, b_sp)
    resultado = simbolico.para_numpy(resultado_sp)
    opcoes, indice = _opcoes_com_perturbacao(resultado, _formatar_matriz)
    pergunta = (
        f"Duas mercearias em {cidade} registaram, em duas semanas, as quantidades vendidas "
        f"(em dezenas de unidades) de dois produtos nas matrizes A = {_formatar_matriz(a)} "
        f"e B = {_formatar_matriz(b)}. Qual é a matriz A + B (total vendido nas duas semanas)?"
    )
    return Desafio(pergunta, opcoes, indice,
                    explicacao="Basta somar as entradas na mesma posição: (A+B)_ij = a_ij + b_ij.")


def gerar_desafio_determinantes() -> Desafio:
    cidade = random.choice(CIDADES)
    a = _matriz_aleatoria(2, -4, 4)
    det_sp, _ = simbolico.determinante(simbolico.para_sympy(a))
    correto = float(det_sp)
    opcoes = [f"{correto:g}"]
    while len(opcoes) < 4:
        candidato = correto + random.choice([-4, -2, -1, 1, 2, 3, 4, 5])
        texto = f"{candidato:g}"
        if texto not in opcoes:
            opcoes.append(texto)
    random.shuffle(opcoes)
    indice = opcoes.index(f"{correto:g}")
    pergunta = (
        f"Uma cooperativa agrícola perto de {cidade} representa os preços (Kz) de dois tipos de "
        f"sementes em duas épocas pela matriz A = {_formatar_matriz(a)}. Qual é det(A)?"
    )
    return Desafio(pergunta, opcoes, indice,
                    explicacao="Para uma matriz 2×2 [[a,b],[c,d]], det(A) = a·d − b·c.")


def gerar_desafio_sistemas() -> Desafio:
    cidade = random.choice(CIDADES)
    while True:
        a = _matriz_aleatoria(2, -3, 3)
        if abs(np.linalg.det(a)) > 1e-6:
            break
    b = _vetor_aleatorio(2, -6, 6)
    ponto = np.linalg.solve(a, b)
    correto = f"({ponto[0]:.2g}, {ponto[1]:.2g})"
    opcoes = [correto]
    while len(opcoes) < 4:
        perturbado = ponto + np.random.uniform(-3, 3, size=2)
        texto = f"({perturbado[0]:.2g}, {perturbado[1]:.2g})"
        if texto not in opcoes:
            opcoes.append(texto)
    random.shuffle(opcoes)
    indice = opcoes.index(correto)
    pergunta = (
        f"Duas rotas de distribuição em {cidade} cruzam-se onde "
        f"{a[0,0]:g}x + {a[0,1]:g}y = {b[0]:g} e {a[1,0]:g}x + {a[1,1]:g}y = {b[1]:g}. "
        f"Qual é o ponto de interseção (x, y)?"
    )
    return Desafio(pergunta, opcoes, indice,
                    explicacao="Resolve o sistema 2×2 por eliminação de Gauss ou regra de Cramer.")


def gerar_desafio_valores_proprios() -> Desafio:
    cidade = random.choice(CIDADES)
    while True:
        a = _matriz_aleatoria(2, -3, 3)
        a[1, 0] = a[0, 1]
        valores = np.linalg.eigvals(a)
        if np.all(np.abs(valores.imag) < 1e-9):
            break
    valores_reais = sorted(float(v.real) for v in valores)
    correto = f"{valores_reais[0]:g} e {valores_reais[1]:g}"
    opcoes = [correto]
    while len(opcoes) < 4:
        perturbados = sorted(v + random.choice([-3, -2, -1, 1, 2, 3]) for v in valores_reais)
        texto = f"{perturbados[0]:g} e {perturbados[1]:g}"
        if texto not in opcoes:
            opcoes.append(texto)
    random.shuffle(opcoes)
    indice = opcoes.index(correto)
    pergunta = (
        f"Uma transformação aplicada a um terreno em {cidade} é representada pela matriz "
        f"A = {_formatar_matriz(a)}. Quais são os valores próprios de A?"
    )
    return Desafio(pergunta, opcoes, indice,
                    explicacao="Resolve det(A − λI) = 0 para encontrar os valores próprios λ.")


def gerar_desafio_vetores() -> Desafio:
    cidade_a, cidade_b = random.sample(CIDADES, 2)
    v = _vetor_aleatorio(2, -5, 5)
    w = _vetor_aleatorio(2, -5, 5)
    correto = float(np.dot(v, w))
    opcoes = [f"{correto:g}"]
    while len(opcoes) < 4:
        candidato = correto + random.choice([-6, -3, -2, 2, 3, 6])
        texto = f"{candidato:g}"
        if texto not in opcoes:
            opcoes.append(texto)
    random.shuffle(opcoes)
    indice = opcoes.index(f"{correto:g}")
    pergunta = (
        f"Um camião viaja de {cidade_a} representado pelo vetor de deslocamento "
        f"v = ({v[0]:g}, {v[1]:g}) (em centenas de km) e outro parte de {cidade_b} com "
        f"w = ({w[0]:g}, {w[1]:g}). Qual é o produto interno v · w?"
    )
    return Desafio(pergunta, opcoes, indice,
                    explicacao="v · w = v₁w₁ + v₂w₂.")


# --------------------------------------------------------------------------
# Desafios visuais (clicar no gráfico)
# --------------------------------------------------------------------------

def gerar_desafio_visual_matrizes() -> tuple[DesafioVisual, go.Figure]:
    a = _matriz_aleatoria(2, -3, 3)
    while abs(np.linalg.det(a)) < 1e-6:
        a = _matriz_aleatoria(2, -3, 3)
    ponto_esperado = (float(a[0, 0]), float(a[1, 0]))  # A aplicada a e1 = 1ª coluna de A
    fig = figura_transformacao_parametrizada(calcular_matriz=lambda t: a, valores_parametro=np.array([1.0]))
    fig.add_trace(camada_clicavel())
    desafio = DesafioVisual(
        instrucao="A grelha já foi transformada pela matriz A. Clica no ponto para onde o "
                  "vetor e1 = (1, 0) foi transformado (a extremidade da linha vermelha M·e1).",
        ponto_esperado=ponto_esperado,
        modo="ponto",
        explicacao=f"A·e1 é sempre a 1ª coluna de A: ({ponto_esperado[0]:g}, {ponto_esperado[1]:g}).",
    )
    return desafio, fig


def gerar_desafio_visual_determinantes() -> tuple[DesafioVisual, go.Figure]:
    a = _matriz_aleatoria(2, -3, 3)
    while abs(np.linalg.det(a)) < 1e-6:
        a = _matriz_aleatoria(2, -3, 3)
    vertice = (float(a[0, 0] + a[0, 1]), float(a[1, 0] + a[1, 1]))  # soma das duas colunas
    fig = figura_transformacao_parametrizada(calcular_matriz=lambda t: a, valores_parametro=np.array([1.0]),
                                              mostrar_area=True)
    fig.add_trace(camada_clicavel())
    desafio = DesafioVisual(
        instrucao="O paralelogramo formado pelas colunas de A está sombreado. Clica no vértice "
                  "oposto à origem (soma das duas colunas de A).",
        ponto_esperado=vertice,
        modo="ponto",
        explicacao=f"Esse vértice é a soma das colunas de A: ({vertice[0]:g}, {vertice[1]:g}).",
    )
    return desafio, fig


def gerar_desafio_visual_vetores() -> tuple[DesafioVisual, go.Figure]:
    v = _vetor_aleatorio(2, -4, 4)
    w = _vetor_aleatorio(2, -4, 4)
    soma = v + w
    fig = figura_vetores_2d([("v", v, "#e15759"), ("w", w, "#4e79a7")])
    fig.add_trace(camada_clicavel())
    desafio = DesafioVisual(
        instrucao="Clica no ponto onde estaria a extremidade do vetor soma v + w.",
        ponto_esperado=(float(soma[0]), float(soma[1])),
        modo="ponto",
        tolerancia=0.8,
        explicacao=f"v + w = ({soma[0]:g}, {soma[1]:g}).",
    )
    return desafio, fig


def gerar_desafio_visual_sistemas() -> tuple[DesafioVisual, go.Figure]:
    while True:
        a = _matriz_aleatoria(2, -3, 3)
        if abs(np.linalg.det(a)) > 1e-6:
            break
    b = _vetor_aleatorio(2, -6, 6)
    ponto = np.linalg.solve(a, b)
    fig = figura_retas_2d([(a[0, 0], a[0, 1], b[0]), (a[1, 0], a[1, 1], b[1])])
    fig.add_trace(camada_clicavel())
    desafio = DesafioVisual(
        instrucao="Clica no gráfico, no ponto onde as duas retas se cruzam (o ponto de interseção do sistema).",
        ponto_esperado=(float(ponto[0]), float(ponto[1])),
        modo="ponto",
        explicacao=f"A interseção é a solução do sistema: x = {ponto[0]:.2f}, y = {ponto[1]:.2f}.",
    )
    return desafio, fig


def gerar_desafio_visual_valores_proprios() -> tuple[DesafioVisual, go.Figure]:
    while True:
        a = _matriz_aleatoria(2, -3, 3)
        a[1, 0] = a[0, 1]  # simétrica: garante valores/vetores próprios reais
        valores, vetores = np.linalg.eig(a)
        if np.all(np.abs(valores.imag) < 1e-9) and not np.isclose(valores[0], valores[1]):
            break
    indice_maior = int(np.argmax(np.abs(valores)))
    direcao = np.real(vetores[:, indice_maior])
    fig = figura_transformacao_parametrizada(
        calcular_matriz=lambda t: a,
        valores_parametro=np.array([1.0]),
        direcoes_proprias=[np.real(vetores[:, i]) for i in range(2)],
    )
    fig.add_trace(camada_clicavel())
    desafio = DesafioVisual(
        instrucao="Clica num ponto sobre a linha tracejada que corresponde à direção própria "
                  "do MAIOR valor próprio (em valor absoluto).",
        ponto_esperado=(float(direcao[0]), float(direcao[1])),
        modo="direcao",
        tolerancia=0.35,
        explicacao=f"O maior valor próprio (em módulo) é λ = {valores[indice_maior]:.2f}, "
                    f"com direção própria ≈ ({direcao[0]:.2f}, {direcao[1]:.2f}).",
    )
    return desafio, fig


def verificar_resposta_visual(desafio: DesafioVisual, ponto_clicado: tuple[float, float]) -> bool:
    clicado = np.array(ponto_clicado, dtype=float)
    if desafio.modo == "ponto":
        return float(np.linalg.norm(clicado - np.array(desafio.ponto_esperado))) < desafio.tolerancia
    # modo "direcao": compara o ângulo da linha (mod π, já que uma direção própria é uma reta)
    if np.linalg.norm(clicado) < 1e-9:
        return False
    angulo_clicado = np.arctan2(clicado[1], clicado[0]) % np.pi
    angulo_esperado = np.arctan2(desafio.ponto_esperado[1], desafio.ponto_esperado[0]) % np.pi
    diferenca = min(abs(angulo_clicado - angulo_esperado), np.pi - abs(angulo_clicado - angulo_esperado))
    return diferenca < desafio.tolerancia
