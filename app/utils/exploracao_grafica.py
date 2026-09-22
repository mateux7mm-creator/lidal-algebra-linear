"""Interpretação de equações em texto livre (estilo Gráfico) para a secção
de Exploração Gráfica: cada equação escrita pelo utilizador (ex. "y = x^2 - 3",
"x^2 + y^2 = 9", "2x - y = 1", ou apenas "sin(x)") é convertida num conjunto
de curvas amostradas, tentando por esta ordem:

1. Resolver explicitamente para y em função de x (o caso mais comum) e
   amostrar y = f(x) sobre x — cobre também equações com várias soluções em
   y (ex. x² + y² = 9 dá y = ±√(9 − x²), duas curvas que juntas formam o
   círculo completo).
2. Se não depender de y (ou não for possível resolver para y), tentar
   resolver para x em função de y (cobre retas verticais e parábolas
   "deitadas", ex. x = y²).
3. Por último, um contorno implícito: avalia lhs − rhs numa grelha (x, y) e
   desenha a curva de nível 0 — cobre qualquer equação que as duas
   tentativas anteriores não conseguiram isolar.
"""
from __future__ import annotations  # permite usar tipos como "list[Curva]" em Python mais antigo

from dataclasses import dataclass, field  # cria classes de dados simples (Curva, Grelha, ResultadoEquacao)
from typing import Optional  # anotação de tipo para campos que podem ser None

import numpy as np  # arrays/amostragem numérica das curvas
import sympy as sp  # resolução simbólica das equações (sp.solve, lambdify, símbolos)
from sympy.parsing.sympy_parser import (
    convert_xor,  # permite escrever "^" como potência (em vez do XOR do Python)
    implicit_multiplication_application,  # permite escrever "2x" em vez de "2*x"
    parse_expr,  # converte o texto da equação numa expressão SymPy
    standard_transformations,  # conjunto de transformações padrão do parser do SymPy
)

# Transformações aplicadas ao interpretar cada equação: as padrão do SymPy,
# mais as duas acima, para aceitar a notação matemática informal que um
# aluno escreveria à mão (potência com "^", multiplicação implícita).
_TRANSFORMACOES = standard_transformations + (implicit_multiplication_application, convert_xor)
# Os dois únicos símbolos que uma equação pode usar como variáveis (x, y) —
# qualquer outra letra livre é tratada como parâmetro (ver detetar_parametros).
_X, _Y = sp.symbols("x y")

N_PONTOS_CURVA = 400  # nº de pontos amostrados ao longo de uma curva explícita (y=f(x) ou x=f(y))
N_PONTOS_GRELHA = 300  # resolução da grelha (por eixo) usada no caso implícito
FATOR_EXTENSAO_DOMINIO = 3  # amostrar bem além da vista inicial, para o pan/zoom não revelar vazio
VALOR_MAXIMO_VISIVEL = 1e5  # acima disto trata-se como assíntota e corta-se a curva (NaN)


class EquacaoInvalida(ValueError):
    """Erro amigável quando uma equação não pode ser interpretada/representada."""


@dataclass
class Curva:
    # Par de arrays x/y já amostrados, prontos a desenhar como uma linha.
    x: np.ndarray
    y: np.ndarray


@dataclass
class Grelha:
    # Grelha 2D (meshgrid) usada para desenhar um contorno implícito: x e y
    # são os vetores dos eixos, z é o valor de (lado_esq - lado_dir) em cada ponto.
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray


@dataclass
class ResultadoEquacao:
    tipo: str  # "explicita_y", "explicita_x" ou "implicita"
    curvas: list[Curva] = field(default_factory=list)  # lista de curvas explícitas (vazia no caso implícito)
    grelha: Optional[Grelha] = None  # só preenchido no caso implícito


def _avaliar_real(f, valores: np.ndarray) -> np.ndarray:
    """Avalia uma função lambdify sobre `valores`, devolvendo NaN onde o
    resultado é complexo (fora do domínio real), demasiado grande (perto de
    uma assíntota) ou onde a função é constante (broadcast manual)."""
    with np.errstate(all="ignore"):  # evita avisos do NumPy em divisões por zero, raízes negativas, etc.
        resultado = f(valores)
    resultado = np.asarray(resultado)
    if resultado.shape != valores.shape:
        # a função pode devolver um escalar constante (ex. "y = 3") em vez de
        # um array — expande manualmente para o mesmo formato de `valores`
        resultado = np.full(valores.shape, complex(resultado) if np.iscomplexobj(resultado) else float(resultado))
    if np.iscomplexobj(resultado):
        # fora do domínio real o SymPy devolve números complexos — guarda só
        # a parte real e marca como inválido (NaN) onde a parte imaginária não é desprezável
        parte_real, parte_imag = resultado.real.copy(), resultado.imag
        parte_real[np.abs(parte_imag) > 1e-6] = np.nan
        resultado = parte_real
    resultado = resultado.astype(float)
    resultado[np.abs(resultado) > VALOR_MAXIMO_VISIVEL] = np.nan  # corta perto de assíntotas
    return resultado


def _analisar_lados(texto: str) -> tuple[sp.Expr, sp.Expr]:
    """Faz só o parsing de "lado_esq = lado_dir" (aceitando o atalho sem "="),
    sem qualquer substituição de parâmetros — usado tanto por
    `interpretar_e_amostrar` como por `detetar_parametros`."""
    texto = texto.strip()
    if not texto:
        raise EquacaoInvalida("Equação vazia.")
    if "=" not in texto:
        # atalho: "x^2 - 3" sem "=" é interpretado como "y = x^2 - 3"
        texto = f"y = {texto}"
    lado_esq, lado_dir = texto.split("=", 1)  # divide só no primeiro "=", para não partir "==" ou "<="
    mapa = {"x": _X, "y": _Y}  # garante que "x"/"y" no texto mapeiam para os símbolos fixos _X/_Y
    try:
        # interpreta cada lado da equação como uma expressão SymPy
        expr_esq = parse_expr(lado_esq, local_dict=mapa, transformations=_TRANSFORMACOES)
        expr_dir = parse_expr(lado_dir, local_dict=mapa, transformations=_TRANSFORMACOES)
    except (sp.SympifyError, SyntaxError, TypeError, AttributeError) as erro:
        # qualquer erro de parsing do SymPy é traduzido numa mensagem em português
        raise EquacaoInvalida(f"Não consegui interpretar \"{texto}\".") from erro
    return expr_esq, expr_dir


def detetar_parametros(texto: str) -> set[str]:
    """Nomes de símbolos livres na equação que não sejam x/y — tratados como
    parâmetros com slider (estilo Gráfico), ex. "a" em "y = a*x^2". Devolve
    um conjunto vazio se a equação ainda não for interpretável (o utilizador
    pode estar a meio de a escrever)."""
    try:
        expr_esq, expr_dir = _analisar_lados(texto)
    except EquacaoInvalida:
        # equação incompleta/inválida enquanto o utilizador ainda a escreve — sem parâmetros por agora
        return set()
    # símbolos livres em qualquer um dos dois lados, excluindo x e y
    livres = (expr_esq.free_symbols | expr_dir.free_symbols) - {_X, _Y}
    return {s.name for s in livres}


def interpretar_e_amostrar(
    texto: str, intervalo: tuple[float, float] = (-10, 10), n_pontos: int = N_PONTOS_CURVA,
    parametros: Optional[dict[str, float]] = None,
) -> ResultadoEquacao:
    """Interpreta `texto` como uma equação em x e/ou y e devolve as curvas já
    amostradas, prontas a desenhar. Lança `EquacaoInvalida` (mensagem em
    português, nunca uma exceção crua do SymPy) se não conseguir.

    `parametros` substitui, antes de mais nada, quaisquer letras extra por um
    valor numérico (ex. {"a": 2.0} em "y = a*x^2" dá "y = 2*x^2") — os
    valores vêm dos sliders geridos por `detetar_parametros`."""
    expr_esq, expr_dir = _analisar_lados(texto)

    if parametros:
        # substitui cada parâmetro (ex. "a") pelo respetivo valor numérico do slider
        substituicoes = {sp.Symbol(nome): valor for nome, valor in parametros.items()}
        expr_esq = expr_esq.subs(substituicoes)
        expr_dir = expr_dir.subs(substituicoes)

    diferenca = sp.expand(expr_esq - expr_dir)  # equação reescrita como "diferenca(x, y) = 0"
    simbolos_usados = diferenca.free_symbols
    if not simbolos_usados <= {_X, _Y}:
        # sobrou algum parâmetro sem valor atribuído (ou uma letra desconhecida) — erro amigável
        extra = ", ".join(s.name for s in simbolos_usados - {_X, _Y})
        raise EquacaoInvalida(f"Usa apenas as variáveis x e y (encontrei \"{extra}\").")
    if diferenca == 0:
        # ex. "x = x": verdadeiro para todo o plano, não define nenhuma curva
        raise EquacaoInvalida("Essa equação é verdadeira para qualquer x, y — não define uma curva.")

    largura = intervalo[1] - intervalo[0]
    # domínio de amostragem alargado (FATOR_EXTENSAO_DOMINIO×) além do intervalo
    # visível, para que arrastar/fazer zoom-out não mostre espaço vazio de repente
    dominio = (intervalo[0] - largura * (FATOR_EXTENSAO_DOMINIO - 1) / 2,
               intervalo[1] + largura * (FATOR_EXTENSAO_DOMINIO - 1) / 2)

    if _Y in simbolos_usados:
        # tentativa 1: resolver explicitamente para y = f(x)
        try:
            solucoes_y = sp.solve(sp.Eq(expr_esq, expr_dir), _Y)
        except NotImplementedError:
            solucoes_y = []  # o SymPy não conseguiu resolver esta equação para y
        if solucoes_y:
            xs = np.linspace(*dominio, n_pontos)
            curvas = []
            for sol in solucoes_y:
                if sol.free_symbols - {_X}:
                    # a solução ainda depende de outra coisa além de x (não deveria acontecer aqui) — ignora
                    continue
                # transforma a expressão simbólica numa função Python rápida sobre arrays NumPy
                f = sp.lambdify(_X, sol, modules=["numpy"])
                curvas.append(Curva(xs, _avaliar_real(f, xs)))
            if curvas:
                return ResultadoEquacao("explicita_y", curvas=curvas)

    if _X in simbolos_usados:
        # tentativa 2: se não deu para resolver por y, tentar resolver para x = f(y)
        try:
            solucoes_x = sp.solve(sp.Eq(expr_esq, expr_dir), _X)
        except NotImplementedError:
            solucoes_x = []
        if solucoes_x:
            ys = np.linspace(*dominio, n_pontos)
            curvas = []
            for sol in solucoes_x:
                if sol.free_symbols - {_Y}:
                    continue
                f = sp.lambdify(_Y, sol, modules=["numpy"])
                curvas.append(Curva(_avaliar_real(f, ys), ys))
            if curvas:
                return ResultadoEquacao("explicita_x", curvas=curvas)

    # tentativa 3 (fallback): contorno implícito — avalia a diferença numa
    # grelha 2D e a curva fica onde essa diferença passa por zero
    try:
        f = sp.lambdify((_X, _Y), diferenca, modules=["numpy"])
        xs = np.linspace(*dominio, N_PONTOS_GRELHA)
        ys = np.linspace(*dominio, N_PONTOS_GRELHA)
        xx, yy = np.meshgrid(xs, ys)  # grelha 2D de coordenadas (x, y)
        with np.errstate(all="ignore"):
            zz = np.asarray(f(xx, yy), dtype=float)  # valor da diferença em cada ponto da grelha
        zz = np.broadcast_to(zz, xx.shape)  # garante a forma certa mesmo se f(x,y) não depender de um dos dois
    except (TypeError, ValueError) as erro:
        raise EquacaoInvalida("Não consegui representar esta equação.") from erro
    if not np.isfinite(zz).any():
        # nenhum valor finito na grelha inteira — não há nada para desenhar
        raise EquacaoInvalida("Não consegui representar esta equação.")
    return ResultadoEquacao("implicita", grelha=Grelha(xs, ys, zz))
