"""Módulo Conteúdo: e-book por tópico (teoria + exemplo resolvido + figura).

O texto teórico vive em `app/content/*.md`, separado do código, para poder
ser editado pelo grupo sem tocar em Python. O exemplo resolvido e a figura
reutilizam sempre as mesmas funções de `simbolico.py`/`visualizacao.py` já
usadas nos módulos de cálculo — zero lógica nova.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import sympy as sp
import streamlit as st

from utils import simbolico
from utils.componentes import cabecalho, mostrar_passos
from utils.visualizacao import figura_retas_2d, figura_transformacao_parametrizada, figura_vetores_2d

PASTA_CONTEUDO = Path(__file__).resolve().parent.parent / "content"

TOPICOS = {
    "Matrizes": "matrizes",
    "Determinantes e Matriz Inversa": "determinantes",
    "Sistemas Lineares": "sistemas",
    "Vetores": "vetores",
    "Valores e Vetores Próprios": "valores_proprios",
}


def _exemplo_matrizes() -> None:
    a = np.array([[2.0, 1.0], [1.0, 3.0]])
    b = np.array([[1.0, 0.0], [0.0, 1.0]])
    resultado, passos = simbolico.somar_matrizes(simbolico.para_sympy(a), simbolico.para_sympy(b))
    st.latex(f"A + B = {sp.latex(resultado)}")
    mostrar_passos(passos)
    fig = figura_transformacao_parametrizada(lambda k: k * a, np.linspace(-2, 2, 20), rotulo_parametro="k")
    st.plotly_chart(fig, width="stretch")


def _exemplo_determinantes() -> None:
    a = np.array([[2.0, 1.0], [1.0, 3.0]])
    det_sp, passos = simbolico.determinante(simbolico.para_sympy(a))
    st.latex(f"\\det(A) = {sp.latex(det_sp)}")
    mostrar_passos(passos)
    fig = figura_transformacao_parametrizada(
        lambda x: simbolico.matriz_com_entrada_variavel(a, (1, 1), x),
        np.linspace(-3, 3, 20), mostrar_area=True,
    )
    st.plotly_chart(fig, width="stretch")


def _exemplo_sistemas() -> None:
    a = np.array([[1.0, 1.0], [1.0, -1.0]])
    b = np.array([3.0, 1.0])
    simbolos = list(sp.symbols(f"x1:{a.shape[1] + 1}"))
    solucoes, passos = simbolico.resolver_sistema(
        simbolico.para_sympy(a), simbolico.para_sympy(b.reshape(-1, 1)), simbolos
    )
    solucao_latex = simbolico.formatar_solucao_sistema(solucoes, simbolos)
    if solucao_latex is not None:
        st.latex(solucao_latex)
    mostrar_passos(passos)
    fig = figura_retas_2d([(a[0, 0], a[0, 1], b[0]), (a[1, 0], a[1, 1], b[1])])
    st.plotly_chart(fig, width="stretch")


def _exemplo_vetores() -> None:
    v, w = np.array([2.0, 1.0]), np.array([1.0, 2.0])
    st.write(f"v · w = {float(np.dot(v, w)):g}")
    fig = figura_vetores_2d([("v", v, "#e15759"), ("w", w, "#4e79a7")])
    st.plotly_chart(fig, width="stretch")


def _exemplo_valores_proprios() -> None:
    a = np.array([[2.0, 0.0], [0.0, 3.0]])
    valores, _vetores, passos = simbolico.eigen(simbolico.para_sympy(a))
    st.write("Valores próprios: " + ", ".join(sp.latex(v) for v in valores))
    mostrar_passos(passos)
    fig = figura_transformacao_parametrizada(lambda t: (1 - t) * np.eye(2) + t * a, np.linspace(0, 1, 20))
    st.plotly_chart(fig, width="stretch")


EXEMPLOS = {
    "matrizes": _exemplo_matrizes,
    "determinantes": _exemplo_determinantes,
    "sistemas": _exemplo_sistemas,
    "vetores": _exemplo_vetores,
    "valores_proprios": _exemplo_valores_proprios,
}


def render() -> None:
    cabecalho("📖 Conteúdo")
    nome_topico = st.selectbox("Tópico", list(TOPICOS.keys()))
    slug = TOPICOS[nome_topico]

    texto = (PASTA_CONTEUDO / f"{slug}.md").read_text(encoding="utf-8")
    marcador = f"<!-- exemplo:{slug} -->"
    antes, _separador, depois = texto.partition(marcador)

    st.divider()
    st.markdown(antes)
    with st.container(border=True):
        st.markdown("##### 📝 Exemplo resolvido")
        EXEMPLOS[slug]()
    st.markdown(depois)
