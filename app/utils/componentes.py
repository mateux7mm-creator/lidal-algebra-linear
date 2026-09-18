"""Widgets Streamlit partilhados por todos os módulos.

Centralizar aqui o input de matrizes/vetores e a apresentação de
resultados/passos garante que os 5 módulos matemáticos têm sempre o mesmo
aspeto e comportamento, e que uma melhoria futura (ex. à forma como os passos
são mostrados) só precisa de ser feita num sítio.
"""
from __future__ import annotations

from typing import Callable

import numpy as np
import sympy as sp
import streamlit as st

from utils.simbolico import Passo


def barra_menus(menus: dict[str, Callable[[], None]]) -> None:
    """Barra de menus estilo desktop (ex. Winplot): cada entrada é um rótulo
    de menu (ex. "Equações") associado a uma função que desenha o conteúdo do
    popover quando o utilizador o abre. Os itens dentro de cada popover são
    controlos Streamlit normais (botões, toggles) — o menu só organiza o
    acesso, a ação real fica na função de callback.

    Uso:
        barra_menus({
            "Equações": _menu_equacoes,
            "Ver": _menu_ver,
            "Exportar": _menu_exportar,
        })
    """
    colunas = st.columns(len(menus))
    for coluna, (rotulo, desenhar_conteudo) in zip(colunas, menus.items()):
        with coluna:
            with st.popover(f"{rotulo} ▾", width="stretch"):
                desenhar_conteudo()


def cabecalho(icone_titulo: str, descricao: str) -> None:
    """Título da página + uma frase curta a explicar o que o módulo faz.
    Uso: cabecalho("🔢 Matrizes", "Soma, produto escalar, produto matricial e transposição.")"""
    st.title(icone_titulo)
    st.caption(descricao)


def _config_colunas_numericas(n_colunas: int) -> dict:
    return {str(i): st.column_config.NumberColumn(label=f"col. {i + 1}", format="%.2f", width="small")
            for i in range(n_colunas)}


def matriz_input(chave: str, linhas: int = 2, colunas: int = 2, titulo: str = "Matriz",
                  valor_defeito: np.ndarray | None = None) -> np.ndarray:
    """Editor de células para uma matriz linhas×colunas, devolvendo um numpy.ndarray."""
    if valor_defeito is None or valor_defeito.shape != (linhas, colunas):
        valor_defeito = np.eye(max(linhas, colunas))[:linhas, :colunas]
    with st.container(border=True):
        st.markdown(f"**{titulo}** · {linhas}×{colunas}")
        editado = st.data_editor(
            valor_defeito,
            key=f"{chave}_{linhas}x{colunas}",
            num_rows="fixed",
            hide_index=True,
            column_config=_config_colunas_numericas(colunas),
        )
    return np.array(editado, dtype=float)


def vetor_input(chave: str, dimensao: int = 2, titulo: str = "Vetor",
                 valor_defeito: np.ndarray | None = None) -> np.ndarray:
    """Editor de células para um vetor de `dimensao` componentes."""
    if valor_defeito is None or len(valor_defeito) != dimensao:
        valor_defeito = np.ones(dimensao)
    with st.container(border=True):
        st.markdown(f"**{titulo}** · {dimensao}D")
        editado = st.data_editor(
            valor_defeito.reshape(1, -1),
            key=f"{chave}_{dimensao}d",
            num_rows="fixed",
            hide_index=True,
            column_config=_config_colunas_numericas(dimensao),
        )
    return np.array(editado, dtype=float).reshape(-1)


def modo_passo_a_passo_ativo(chave_pagina: str) -> bool:
    """Toggle único, igual em todos os módulos, ligado por omissão."""
    return st.toggle("🔍 Mostrar modo passo-a-passo", value=True, key=f"{chave_pagina}_passo_a_passo")


def modo_leve_ativo() -> bool:
    """Cria o toggle de modo leve na sidebar. Chamar UMA ÚNICA VEZ, em streamlit_app.py
    (o widget fica disponível em todas as páginas porque o script de entrada corre sempre).
    Dentro de cada módulo, usar `modo_leve_da_sessao()` para ler o valor sem recriar o widget."""
    st.sidebar.markdown("### 🧮 Laboratório de Álgebra Linear")
    st.sidebar.caption("Mestrado em Ensino da Matemática")
    st.sidebar.divider()
    return st.sidebar.toggle(
        "🐢 Modo leve",
        value=False,
        key="modo_leve",
        help="Reduz a densidade das malhas e o número de frames das animações — "
             "para ligações ou dispositivos mais fracos.",
    )


def modo_leve_da_sessao() -> bool:
    """Lê o estado atual do modo leve, sem criar um novo widget."""
    return bool(st.session_state.get("modo_leve", False))


def mostrar_passos(passos: list[Passo]) -> None:
    """Renderização uniforme da lista de passos pedagógicos."""
    st.markdown("##### 🔍 Como se chega ao resultado")
    for i, passo in enumerate(passos, start=1):
        with st.expander(f"Passo {i}: {passo.titulo}", expanded=True):
            if passo.detalhe:
                st.write(passo.detalhe)
            if passo.latex:
                st.latex(passo.latex)


def _latex_numerico(numerico) -> str:
    """Formata um escalar/vetor/matriz numérico como bracket LaTeX arredondado,
    para o lado 'Numérico' ter o mesmo aspeto visual do lado 'Simbólico'."""
    arr = np.asarray(numerico, dtype=float)
    arredondado = np.round(arr, 3)
    if arredondado.ndim == 0:
        return f"{arredondado:g}"
    return sp.latex(sp.Matrix(arredondado.tolist())) if arredondado.ndim == 2 \
        else sp.latex(sp.Matrix(arredondado.reshape(1, -1).tolist()))


def mostrar_resultado(numerico, simbolico_latex: str) -> None:
    """Mostra o resultado numérico e simbólico lado a lado, sempre no mesmo layout
    (ambos como bracket LaTeX, para consistência visual)."""
    with st.container(border=True):
        st.markdown("##### ✅ Resultado")
        col_num, col_sym = st.columns(2)
        with col_num:
            st.caption("Numérico")
            st.latex(_latex_numerico(numerico))
        with col_sym:
            st.caption("Simbólico")
            st.latex(simbolico_latex)
