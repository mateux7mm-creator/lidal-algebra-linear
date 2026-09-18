"""Interpretação de equações em texto livre (estilo GeoGebra) para a secção
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
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

_TRANSFORMACOES = standard_transformations + (implicit_multiplication_application, convert_xor)
_X, _Y = sp.symbols("x y")

N_PONTOS_CURVA = 400
N_PONTOS_GRELHA = 300
FATOR_EXTENSAO_DOMINIO = 3  # amostrar bem além da vista inicial, para o pan/zoom não revelar vazio
VALOR_MAXIMO_VISIVEL = 1e5  # acima disto trata-se como assíntota e corta-se a curva (NaN)


class EquacaoInvalida(ValueError):
    """Erro amigável quando uma equação não pode ser interpretada/representada."""


@dataclass
class Curva:
    x: np.ndarray
    y: np.ndarray


@dataclass
class Grelha:
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray


@dataclass
class ResultadoEquacao:
    tipo: str  # "explicita_y", "explicita_x" ou "implicita"
    curvas: list[Curva] = field(default_factory=list)
    grelha: Optional[Grelha] = None


def _avaliar_real(f, valores: np.ndarray) -> np.ndarray:
    """Avalia uma função lambdify sobre `valores`, devolvendo NaN onde o
    resultado é complexo (fora do domínio real), demasiado grande (perto de
    uma assíntota) ou onde a função é constante (broadcast manual)."""
    with np.errstate(all="ignore"):
        resultado = f(valores)
    resultado = np.asarray(resultado)
    if resultado.shape != valores.shape:
        resultado = np.full(valores.shape, complex(resultado) if np.iscomplexobj(resultado) else float(resultado))
    if np.iscomplexobj(resultado):
        parte_real, parte_imag = resultado.real.copy(), resultado.imag
        parte_real[np.abs(parte_imag) > 1e-6] = np.nan
        resultado = parte_real
    resultado = resultado.astype(float)
    resultado[np.abs(resultado) > VALOR_MAXIMO_VISIVEL] = np.nan
    return resultado


def interpretar_e_amostrar(
    texto: str, intervalo: tuple[float, float] = (-10, 10), n_pontos: int = N_PONTOS_CURVA,
) -> ResultadoEquacao:
    """Interpreta `texto` como uma equação em x e/ou y e devolve as curvas já
    amostradas, prontas a desenhar. Lança `EquacaoInvalida` (mensagem em
    português, nunca uma exceção crua do SymPy) se não conseguir."""
    texto = texto.strip()
    if not texto:
        raise EquacaoInvalida("Equação vazia.")
    if "=" not in texto:
        texto = f"y = {texto}"
    lado_esq, lado_dir = texto.split("=", 1)
    mapa = {"x": _X, "y": _Y}
    try:
        expr_esq = parse_expr(lado_esq, local_dict=mapa, transformations=_TRANSFORMACOES)
        expr_dir = parse_expr(lado_dir, local_dict=mapa, transformations=_TRANSFORMACOES)
    except (sp.SympifyError, SyntaxError, TypeError, AttributeError) as erro:
        raise EquacaoInvalida(f"Não consegui interpretar \"{texto}\".") from erro

    diferenca = sp.expand(expr_esq - expr_dir)
    simbolos_usados = diferenca.free_symbols
    if not simbolos_usados <= {_X, _Y}:
        extra = ", ".join(s.name for s in simbolos_usados - {_X, _Y})
        raise EquacaoInvalida(f"Usa apenas as variáveis x e y (encontrei \"{extra}\").")
    if diferenca == 0:
        raise EquacaoInvalida("Essa equação é verdadeira para qualquer x, y — não define uma curva.")

    largura = intervalo[1] - intervalo[0]
    dominio = (intervalo[0] - largura * (FATOR_EXTENSAO_DOMINIO - 1) / 2,
               intervalo[1] + largura * (FATOR_EXTENSAO_DOMINIO - 1) / 2)

    if _Y in simbolos_usados:
        try:
            solucoes_y = sp.solve(sp.Eq(expr_esq, expr_dir), _Y)
        except NotImplementedError:
            solucoes_y = []
        if solucoes_y:
            xs = np.linspace(*dominio, n_pontos)
            curvas = []
            for sol in solucoes_y:
                if sol.free_symbols - {_X}:
                    continue
                f = sp.lambdify(_X, sol, modules=["numpy"])
                curvas.append(Curva(xs, _avaliar_real(f, xs)))
            if curvas:
                return ResultadoEquacao("explicita_y", curvas=curvas)

    if _X in simbolos_usados:
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

    try:
        f = sp.lambdify((_X, _Y), diferenca, modules=["numpy"])
        xs = np.linspace(*dominio, N_PONTOS_GRELHA)
        ys = np.linspace(*dominio, N_PONTOS_GRELHA)
        xx, yy = np.meshgrid(xs, ys)
        with np.errstate(all="ignore"):
            zz = np.asarray(f(xx, yy), dtype=float)
        zz = np.broadcast_to(zz, xx.shape)
    except (TypeError, ValueError) as erro:
        raise EquacaoInvalida("Não consegui representar esta equação.") from erro
    if not np.isfinite(zz).any():
        raise EquacaoInvalida("Não consegui representar esta equação.")
    return ResultadoEquacao("implicita", grelha=Grelha(xs, ys, zz))
