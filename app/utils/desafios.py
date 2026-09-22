"""Geração de desafios/quiz para o módulo "Jogos e Desafios".

Cada `gerar_desafio_*` gera valores aleatórios pequenos e reutiliza as
funções de cálculo já existentes em `simbolico.py` — nunca duplica lógica de
cálculo, só embrulha os valores num enunciado contextualizado (Kwanza,
geografia angolana) para tornar a prática mais próxima da realidade.
"""
from __future__ import annotations  # permite usar tipos como "list[str]" mesmo em versões mais antigas do Python

import random  # números/escolhas aleatórias "puros" do Python (não vetorizados)
from dataclasses import dataclass, field  # cria classes de dados simples (Desafio, DesafioVisual, ...) sem boilerplate
from typing import Literal  # tipo restrito a um conjunto fixo de valores (ex.: "ponto" ou "direcao")

import numpy as np  # arrays e álgebra linear numérica (matrizes/vetores aleatórios, det, eig, ...)
import plotly.graph_objects as go  # tipo de retorno das figuras interativas usadas nos desafios visuais

from utils import simbolico  # funções de cálculo exato (soma, determinante) reaproveitadas aqui, sem duplicar lógica
from utils.visualizacao import (
    camada_clicavel,               # camada Plotly "invisível" usada para capturar o clique do utilizador no gráfico
    figura_retas_2d,                # desenha duas retas (usado no desafio visual de Sistemas)
    figura_transformacao_parametrizada,  # desenha a grelha transformada por uma matriz (Matrizes/Determinantes/Valores Próprios)
    figura_vetores_2d,              # desenha vetores no plano (usado no desafio visual de Vetores)
    intervalo_retas,                # calcula a área/intervalo visível à volta de um conjunto de retas
    intervalo_transformacao,        # calcula a área/intervalo visível à volta de uma transformação
    intervalo_vetores,              # calcula a área/intervalo visível à volta de um conjunto de vetores
)

# cidades angolanas usadas para contextualizar os enunciados dos desafios (torna-os menos abstratos)
CIDADES = ["Luanda", "Huambo", "Lobito", "Benguela", "Lubango", "Malanje"]


@dataclass
class Desafio:
    """Um desafio de escolha múltipla gerado dinamicamente."""

    pergunta: str          # texto do enunciado, já com os valores aleatórios embutidos
    opcoes: list[str]      # lista de respostas possíveis (uma correta + distratores), já baralhada
    indice_correto: int    # posição (em `opcoes`) da resposta correta, após o baralhamento
    explicacao: str = ""   # texto mostrado depois de responder, a explicar o raciocínio


@dataclass
class DesafioVisual:
    """Um desafio resolvido clicando num gráfico Plotly."""

    instrucao: str                       # texto que diz ao utilizador onde/o que clicar no gráfico
    ponto_esperado: tuple[float, float]  # coordenadas (x, y) consideradas a resposta certa
    modo: Literal["ponto", "direcao"] = "ponto"  # "ponto": compara distância; "direcao": compara ângulo da reta
    tolerancia: float = 0.6              # margem de erro aceite (distância ou, em "direcao", diferença angular)
    explicacao: str = ""                 # texto mostrado depois de responder


@dataclass
class DesafioProgressivo:
    """Um desafio em duas fases (em vez de dar logo a resposta): primeiro
    calcular o determinante, só depois decidir se a matriz tem inversa — com
    pista disponível na 1ª fase. Estilo pedido em "Estrutura do Trabalho"
    (secção 9): "solicitar primeiro o cálculo do determinante e, depois,
    fornecer feedback progressivo", em vez de um quiz de resposta direta."""

    matriz: np.ndarray      # a matriz A apresentada ao utilizador
    determinante: float     # det(A), calculado uma única vez e reutilizado nas duas fases
    tem_inversa: bool       # True se det(A) != 0 (dentro de uma tolerância numérica)
    dica: str               # fórmula/método sugerido se o utilizador pedir ajuda na fase 1
    explicacao: str         # texto final, mostrado depois de a fase 2 ser respondida


def _matriz_aleatoria(dim: int = 2, minimo: int = -4, maximo: int = 4) -> np.ndarray:
    # gera uma matriz quadrada dim×dim de inteiros aleatórios (como float, para
    # ser compatível com as funções de cálculo que esperam arrays de vírgula flutuante)
    return np.random.randint(minimo, maximo + 1, size=(dim, dim)).astype(float)


def _vetor_aleatorio(dim: int = 2, minimo: int = -5, maximo: int = 5) -> np.ndarray:
    # gera um vetor de "dim" inteiros aleatórios, também convertido para float
    return np.random.randint(minimo, maximo + 1, size=dim).astype(float)


def _formatar_matriz(m: np.ndarray) -> str:
    # formata uma matriz numpy como texto "[[a, b], [c, d]]" para usar dentro
    # do enunciado ou das opções de resposta (sem casas decimais desnecessárias, graças a "g")
    linhas = ["[" + ", ".join(f"{v:g}" for v in linha) + "]" for linha in m]
    return "[" + ", ".join(linhas) + "]"


def _opcoes_com_perturbacao(correta: np.ndarray, formatar, n_opcoes: int = 4) -> tuple[list[str], int]:
    """Gera n_opcoes-1 alternativas erradas perturbando a resposta correta, e baralha."""
    opcoes = [formatar(correta)]  # a primeira opção é sempre a resposta certa (antes de baralhar)
    tentativas = 0
    # tenta até 20 vezes gerar distratores diferentes da resposta certa e entre si
    while len(opcoes) < n_opcoes and tentativas < 20:
        tentativas += 1
        # perturba a matriz correta com ruído inteiro pequeno, para gerar uma alternativa plausível
        perturbacao = correta + np.random.randint(-3, 4, size=correta.shape)
        texto = formatar(perturbacao)
        if texto not in opcoes:  # evita opções repetidas
            opcoes.append(texto)
    indices = list(range(len(opcoes)))
    random.shuffle(indices)  # baralha a ordem das opções, para a certa não estar sempre em 1º lugar
    opcoes_baralhadas = [opcoes[i] for i in indices]
    indice_correto = opcoes_baralhadas.index(opcoes[0])  # localiza para onde a resposta certa foi parar
    return opcoes_baralhadas, indice_correto


# --------------------------------------------------------------------------
# Desafios de quiz
# --------------------------------------------------------------------------

def gerar_desafio_matrizes() -> Desafio:
    # gera um desafio de escolha múltipla sobre soma de matrizes, com um
    # enunciado sobre vendas em duas mercearias de uma cidade angolana
    cidade = random.choice(CIDADES)
    a = _matriz_aleatoria(2, -3, 3)
    b = _matriz_aleatoria(2, -3, 3)
    a_sp, b_sp = simbolico.para_sympy(a), simbolico.para_sympy(b)
    # reaproveita a função de soma já usada no módulo Matrizes — garante que a
    # resposta do desafio bate sempre certo com o resto da aplicação
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
    # desafio de escolha múltipla sobre o cálculo do determinante de uma matriz 2×2
    cidade = random.choice(CIDADES)
    a = _matriz_aleatoria(2, -4, 4)
    # calcula o determinante exato via SymPy (mesma função usada no módulo Determinantes)
    det_sp, _ = simbolico.determinante(simbolico.para_sympy(a))
    correto = float(det_sp)
    opcoes = [f"{correto:g}"]
    # gera distratores somando pequenos deslocamentos inteiros ao valor correto
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
    # desafio de escolha múltipla sobre a interseção de duas retas (sistema 2×2)
    cidade = random.choice(CIDADES)
    # gera matrizes de coeficientes até encontrar uma não-singular (sistema com solução única)
    while True:
        a = _matriz_aleatoria(2, -3, 3)
        if abs(np.linalg.det(a)) > 1e-6:
            break
    b = _vetor_aleatorio(2, -6, 6)
    # resolve o sistema numericamente (mais rápido que o caminho simbólico, e
    # aqui só interessa o valor final, não os passos pedagógicos)
    ponto = np.linalg.solve(a, b)
    correto = f"({ponto[0]:.2g}, {ponto[1]:.2g})"
    opcoes = [correto]
    # distratores: o ponto correto deslocado por um ruído aleatório contínuo
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
    # desafio de escolha múltipla sobre valores próprios de uma matriz 2×2
    cidade = random.choice(CIDADES)
    # insiste até obter uma matriz simétrica (a[1,0]=a[0,1]) com valores próprios reais,
    # para não ter de lidar com números complexos neste quiz
    while True:
        a = _matriz_aleatoria(2, -3, 3)
        a[1, 0] = a[0, 1]  # força simetria: garante valores próprios sempre reais
        valores = np.linalg.eigvals(a)
        if np.all(np.abs(valores.imag) < 1e-9):  # confirma que a parte imaginária é desprezável
            break
    valores_reais = sorted(float(v.real) for v in valores)
    correto = f"{valores_reais[0]:g} e {valores_reais[1]:g}"
    opcoes = [correto]
    # distratores: cada valor próprio deslocado por um inteiro pequeno, mantendo o par ordenado
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
    # desafio de escolha múltipla sobre produto interno de dois vetores
    cidade_a, cidade_b = random.sample(CIDADES, 2)  # duas cidades diferentes, sem repetição
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
    # desafio visual: identificar para onde o vetor e1 = (1,0) vai depois de
    # aplicar a matriz A (a resposta é sempre a 1ª coluna de A)
    a = _matriz_aleatoria(2, -3, 3)
    while abs(np.linalg.det(a)) < 1e-6:  # evita matrizes singulares, que achatam o plano numa reta
        a = _matriz_aleatoria(2, -3, 3)
    ponto_esperado = (float(a[0, 0]), float(a[1, 0]))  # A aplicada a e1 = 1ª coluna de A
    # desenha a transformação já "parada" no estado final (um único valor de parâmetro = 1.0)
    fig = figura_transformacao_parametrizada(calcular_matriz=lambda t: a, valores_parametro=np.array([1.0]))
    # sobrepõe uma camada transparente e densa de pontos clicáveis, para o
    # Streamlit conseguir capturar as coordenadas exatas onde o utilizador clicou
    fig.add_trace(camada_clicavel(intervalo_transformacao([a])))
    desafio = DesafioVisual(
        instrucao="A grelha já foi transformada pela matriz A. Clica no ponto para onde o "
                  "vetor e1 = (1, 0) foi transformado (a extremidade da linha vermelha M·e1).",
        ponto_esperado=ponto_esperado,
        modo="ponto",
        explicacao=f"A·e1 é sempre a 1ª coluna de A: ({ponto_esperado[0]:g}, {ponto_esperado[1]:g}).",
    )
    return desafio, fig


def gerar_desafio_visual_determinantes() -> tuple[DesafioVisual, go.Figure]:
    # desafio visual: identificar o vértice oposto à origem do paralelogramo
    # formado pelas colunas de A (esse vértice é a soma das duas colunas)
    a = _matriz_aleatoria(2, -3, 3)
    while abs(np.linalg.det(a)) < 1e-6:
        a = _matriz_aleatoria(2, -3, 3)
    vertice = (float(a[0, 0] + a[0, 1]), float(a[1, 0] + a[1, 1]))  # soma das duas colunas
    # aqui também se pede a área sombreada (mostrar_area=True), que é o próprio
    # significado geométrico do determinante em valor absoluto
    fig = figura_transformacao_parametrizada(calcular_matriz=lambda t: a, valores_parametro=np.array([1.0]),
                                              mostrar_area=True)
    fig.add_trace(camada_clicavel(intervalo_transformacao([a])))
    desafio = DesafioVisual(
        instrucao="O paralelogramo formado pelas colunas de A está sombreado. Clica no vértice "
                  "oposto à origem (soma das duas colunas de A).",
        ponto_esperado=vertice,
        modo="ponto",
        explicacao=f"Esse vértice é a soma das colunas de A: ({vertice[0]:g}, {vertice[1]:g}).",
    )
    return desafio, fig


def gerar_desafio_visual_vetores() -> tuple[DesafioVisual, go.Figure]:
    # desafio visual: identificar a extremidade do vetor soma v + w
    v = _vetor_aleatorio(2, -4, 4)
    w = _vetor_aleatorio(2, -4, 4)
    soma = v + w
    vetores_fig = [("v", v, "#e15759"), ("w", w, "#4e79a7")]  # (nome, vetor, cor) de cada seta desenhada
    fig = figura_vetores_2d(vetores_fig)
    fig.add_trace(camada_clicavel(intervalo_vetores(vetores_fig)))
    desafio = DesafioVisual(
        instrucao="Clica no ponto onde estaria a extremidade do vetor soma v + w.",
        ponto_esperado=(float(soma[0]), float(soma[1])),
        modo="ponto",
        tolerancia=0.8,  # tolerância maior aqui: é mais difícil apontar com precisão a soma visualmente
        explicacao=f"v + w = ({soma[0]:g}, {soma[1]:g}).",
    )
    return desafio, fig


def gerar_desafio_visual_sistemas() -> tuple[DesafioVisual, go.Figure]:
    # desafio visual: identificar o ponto de interseção de duas retas
    while True:
        a = _matriz_aleatoria(2, -3, 3)
        if abs(np.linalg.det(a)) > 1e-6:  # garante que as duas retas não são paralelas (solução única)
            break
    b = _vetor_aleatorio(2, -6, 6)
    ponto = np.linalg.solve(a, b)
    equacoes = [(a[0, 0], a[0, 1], b[0]), (a[1, 0], a[1, 1], b[1])]  # forma (coef_x, coef_y, termo independente)
    fig = figura_retas_2d(equacoes)
    fig.add_trace(camada_clicavel(intervalo_retas(equacoes)))
    desafio = DesafioVisual(
        instrucao="Clica no gráfico, no ponto onde as duas retas se cruzam (o ponto de interseção do sistema).",
        ponto_esperado=(float(ponto[0]), float(ponto[1])),
        modo="ponto",
        explicacao=f"A interseção é a solução do sistema: x = {ponto[0]:.2f}, y = {ponto[1]:.2f}.",
    )
    return desafio, fig


def gerar_desafio_visual_valores_proprios() -> tuple[DesafioVisual, go.Figure]:
    # desafio visual: identificar a direção própria associada ao MAIOR valor próprio (em módulo)
    while True:
        a = _matriz_aleatoria(2, -3, 3)
        a[1, 0] = a[0, 1]  # simétrica: garante valores/vetores próprios reais
        valores, vetores = np.linalg.eig(a)
        # exige valores próprios reais e distintos (senão as duas direções coincidem/confundem-se)
        if np.all(np.abs(valores.imag) < 1e-9) and not np.isclose(valores[0], valores[1]):
            break
    indice_maior = int(np.argmax(np.abs(valores)))  # posição do valor próprio de maior valor absoluto
    direcao = np.real(vetores[:, indice_maior])  # o vetor próprio correspondente (colunas de `vetores`)
    fig = figura_transformacao_parametrizada(
        calcular_matriz=lambda t: a,
        valores_parametro=np.array([1.0]),
        direcoes_proprias=[np.real(vetores[:, i]) for i in range(2)],  # desenha as DUAS direções tracejadas
    )
    fig.add_trace(camada_clicavel(intervalo_transformacao([a])))
    desafio = DesafioVisual(
        instrucao="Clica num ponto sobre a linha tracejada que corresponde à direção própria "
                  "do MAIOR valor próprio (em valor absoluto).",
        ponto_esperado=(float(direcao[0]), float(direcao[1])),
        modo="direcao",  # aqui compara-se o ÂNGULO da reta, não a distância a um ponto exato
        tolerancia=0.35,
        explicacao=f"O maior valor próprio (em módulo) é λ = {valores[indice_maior]:.2f}, "
                    f"com direção própria ≈ ({direcao[0]:.2f}, {direcao[1]:.2f}).",
    )
    return desafio, fig


# --------------------------------------------------------------------------
# Desafios progressivos (pistas por fases, em vez da resposta direta)
# --------------------------------------------------------------------------

def gerar_desafio_progressivo_inversa(dim: int = 2) -> DesafioProgressivo:
    """Fase 1: calcular det(A). Fase 2: decidir se A tem inversa. Gera
    metade das vezes uma matriz singular e metade não-singular, para o
    "tem inversa?" não ser sempre a mesma resposta."""
    singular = random.random() < 0.5  # decide, com 50% de probabilidade, se A vai ser singular
    if singular:
        # constrói uma matriz DELIBERADAMENTE singular: a 2ª linha é um múltiplo da 1ª
        while True:
            a = _matriz_aleatoria(dim, -4, 4)
            if not np.allclose(a[0], 0):  # evita partir de uma 1ª linha toda a zeros (múltiplo trivial)
                break
        fator = random.choice([-2, -1, 2, 3])
        a[1] = fator * a[0]  # força a linha 2 a ser combinação linear da linha 1 → det(A) = 0
        if dim == 3:
            a[2] = _matriz_aleatoria(1, -4, 4)[0]  # a 3ª linha (se existir) pode ser qualquer coisa
    else:
        # insiste até obter uma matriz com determinante claramente não-nulo
        while True:
            a = _matriz_aleatoria(dim, -4, 4)
            if abs(np.linalg.det(a)) > 1e-6:
                break

    det = float(np.linalg.det(a))
    tem_inversa = abs(det) > 1e-6  # tolerância para erros de arredondamento em vírgula flutuante
    # a dica muda consoante a dimensão: fórmula direta em 2×2, regra de Sarrus em 3×3
    if dim == 2:
        dica = "Para uma matriz 2×2 [[a, b], [c, d]], det(A) = a·d − b·c."
    else:
        dica = ("Usa a regra de Sarrus: soma o produto das 3 diagonais descendentes e subtrai "
                "o produto das 3 diagonais ascendentes.")
    explicacao = (f"det(A) = {det:g}. Como det(A) {'≠' if tem_inversa else '='} 0, "
                  f"a matriz {'tem' if tem_inversa else 'não tem'} inversa.")
    return DesafioProgressivo(a, det, tem_inversa, dica, explicacao)


def verificar_resposta_visual(desafio: DesafioVisual, ponto_clicado: tuple[float, float]) -> bool:
    # compara o ponto onde o utilizador clicou com o ponto esperado do desafio,
    # usando o critério (distância ou ângulo) definido em `desafio.modo`
    clicado = np.array(ponto_clicado, dtype=float)
    if desafio.modo == "ponto":
        # distância euclidiana entre o clique e o ponto esperado, dentro da tolerância
        return float(np.linalg.norm(clicado - np.array(desafio.ponto_esperado))) < desafio.tolerancia
    # modo "direcao": compara o ângulo da linha (mod π, já que uma direção própria é uma reta)
    if np.linalg.norm(clicado) < 1e-9:  # clique praticamente na origem: sem direção definida, falha
        return False
    angulo_clicado = np.arctan2(clicado[1], clicado[0]) % np.pi
    angulo_esperado = np.arctan2(desafio.ponto_esperado[1], desafio.ponto_esperado[0]) % np.pi
    # a menor diferença angular entre as duas retas (uma reta e o seu oposto têm o mesmo ângulo mod π)
    diferenca = min(abs(angulo_clicado - angulo_esperado), np.pi - abs(angulo_clicado - angulo_esperado))
    return diferenca < desafio.tolerancia
