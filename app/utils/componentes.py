"""Widgets Streamlit partilhados por todos os módulos.

Centralizar aqui o input de matrizes/vetores e a apresentação de
resultados/passos garante que os 5 módulos matemáticos têm sempre o mesmo
aspeto e comportamento, e que uma melhoria futura (ex. à forma como os passos
são mostrados) só precisa de ser feita num sítio.
"""
from __future__ import annotations  # permite anotações de tipo como "np.ndarray | None" em qualquer versão do Python

from typing import Callable  # tipo usado para descrever "uma função sem argumentos, sem retorno" (barra_menus)

import numpy as np  # arrays para guardar/manipular matrizes e vetores
import pandas as pd  # tabela intermediária exigida pelo st.data_editor (rótulos de linha/coluna)
import sympy as sp  # formatação em LaTeX da forma simbólica de matrizes/vetores
import streamlit as st  # todos os widgets desta biblioteca partilhada

from utils.simbolico import Passo  # tipo de dados de um "passo pedagógico", usado por mostrar_passos/mostrar_resultado


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
    colunas = st.columns(len(menus))  # uma coluna de largura igual por cada entrada do menu
    # percorre em paralelo as colunas e os pares (rótulo, função) do dicionário
    for coluna, (rotulo, desenhar_conteudo) in zip(colunas, menus.items()):
        with coluna:
            # popover: menu suspenso que só mostra o conteúdo quando clicado
            with st.popover(f"{rotulo} ▾", width="stretch"):
                desenhar_conteudo()  # chama a função de callback para desenhar o conteúdo deste menu


def cabecalho(icone_titulo: str) -> None:
    """Título da página — só o título, sem legenda: uma vez dentro do
    módulo, a descrição já não acrescenta nada e só ocupa espaço.
    Uso: cabecalho("🔢 Matrizes")"""
    st.title(icone_titulo)  # título grande, estilo nativo do Streamlit


def legenda_centrada(texto: str) -> None:
    """Rótulo pequeno e centrado, mesmo estilo do st.caption mas centrado —
    usado acima/ao lado de conteúdo em LaTeX (ex. "Forma simbólica",
    "Numérico"/"Simbólico"), em vez do alinhamento à esquerda por omissão."""
    # parágrafo HTML com CSS inline (cor/tamanho a imitar st.caption, mas centrado)
    st.markdown(
        f"<p style='text-align:center; color:rgba(49,51,63,0.6); "
        f"font-size:0.875rem; margin-bottom:0.25rem;'>{texto}</p>",
        unsafe_allow_html=True,
    )


def matriz_input(chave: str, linhas: int = 2, colunas: int = 2, titulo: str = "Matriz",
                  valor_defeito: np.ndarray | None = None, permitir_redimensionar: bool = True,
                  quadrada: bool = False) -> np.ndarray:
    """Editor de células para uma matriz, com rótulos "1ª lin"/"1ª col",
    pré-visualização simbólica ao vivo, e (se `permitir_redimensionar`) botões
    para adicionar/remover linhas e colunas. Com `quadrada=True` (ex.
    Determinantes, Valores Próprios), um único par de botões "➕/➖ Dimensão"
    cresce/encolhe linhas e colunas em conjunto, mantendo a matriz quadrada.
    Devolve um numpy.ndarray."""
    # chaves de sessão: os dados atuais da matriz, e um contador de "versão"
    # (incrementado sempre que a forma muda) usado para forçar o data_editor
    # a recriar-se com uma nova key, em vez de tentar reconciliar dimensões diferentes
    chave_dados = f"{chave}_dados"
    chave_versao = f"{chave}_versao"
    if chave_dados not in st.session_state:  # primeira visita a este editor nesta sessão
        if quadrada:
            linhas = colunas = max(linhas, colunas)  # força linhas==colunas no caso quadrado
        if valor_defeito is None or valor_defeito.shape != (linhas, colunas):
            # sem valor por omissão válido: usa a matriz identidade recortada ao tamanho pedido
            valor_defeito = np.eye(max(linhas, colunas))[:linhas, :colunas]
        st.session_state[chave_dados] = valor_defeito.astype(float)
        st.session_state[chave_versao] = 0

    dados = st.session_state[chave_dados]  # estado atual (fonte da verdade entre reruns)
    n_linhas, n_colunas = dados.shape

    with st.container(border=True):  # cartão com borda a envolver todo o editor
        # cabeçalho do cartão: nome da matriz + badge com as dimensões atuais (ex. "2×2")
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.1rem; color: #1E1B4B;">{titulo}</span>
                    <span class="module-badge badge-indigo" style="font-size: 0.75rem;">{n_linhas}×{n_colunas}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if permitir_redimensionar and quadrada:
            # caso quadrado: só 3 botões — crescer/encolher a matriz toda (linha+coluna
            # em simultâneo) e preencher como identidade
            b1, b2, b3 = st.columns([1, 1, 1.2])
            with b1:
                if st.button("➕ Dimensão", key=f"{chave}_add_dim", help="Adicionar linha e coluna (+1×1)", width="stretch"):
                    # acrescenta uma linha de zeros e depois uma coluna de zeros (cresce em ambas as direções)
                    nova = np.vstack([dados, np.zeros((1, n_colunas))])
                    nova = np.hstack([nova, np.zeros((n_linhas + 1, 1))])
                    st.session_state[chave_dados] = nova
                    st.session_state[chave_versao] += 1  # força o data_editor a recriar-se com a nova forma
                    st.rerun()  # repete o script já com os novos dados em sessão
            with b2:
                if st.button("➖ Dimensão", key=f"{chave}_rem_dim", disabled=n_linhas <= 1, help="Remover linha e coluna (-1×1)", width="stretch"):
                    st.session_state[chave_dados] = dados[:-1, :-1]  # remove a última linha e a última coluna
                    st.session_state[chave_versao] += 1
                    st.rerun()
            with b3:
                if st.button("🆔 Identidade", key=f"{chave}_identidade", help="Preencher diagonal com 1 e o resto com 0", width="stretch"):
                    st.session_state[chave_dados] = np.eye(n_linhas, n_colunas)  # substitui pelo conteúdo da matriz identidade
                    st.session_state[chave_versao] += 1
                    st.rerun()
        elif permitir_redimensionar:
            # caso geral (não necessariamente quadrado): linhas e colunas podem
            # crescer/encolher de forma independente uma da outra
            b1, b2, b3, b4, b5 = st.columns([1, 1, 1, 1, 1.2])
            with b1:
                if st.button("➕ Linha", key=f"{chave}_add_l", help="Adicionar uma nova linha (+ Linha)", width="stretch"):
                    st.session_state[chave_dados] = np.vstack([dados, np.zeros((1, n_colunas))])  # acrescenta uma linha de zeros no fundo
                    st.session_state[chave_versao] += 1
                    st.rerun()
            with b2:
                if st.button("➖ Linha", key=f"{chave}_rem_l", disabled=n_linhas <= 1, help="Remover a última linha (- Linha)", width="stretch"):
                    st.session_state[chave_dados] = dados[:-1, :]  # remove a última linha
                    st.session_state[chave_versao] += 1
                    st.rerun()
            with b3:
                if st.button("➕ Coluna", key=f"{chave}_add_c", help="Adicionar uma nova coluna (+ Coluna)", width="stretch"):
                    st.session_state[chave_dados] = np.hstack([dados, np.zeros((n_linhas, 1))])  # acrescenta uma coluna de zeros à direita
                    st.session_state[chave_versao] += 1
                    st.rerun()
            with b4:
                if st.button("➖ Coluna", key=f"{chave}_rem_c", disabled=n_colunas <= 1, help="Remover a última coluna (- Coluna)", width="stretch"):
                    st.session_state[chave_dados] = dados[:, :-1]  # remove a última coluna
                    st.session_state[chave_versao] += 1
                    st.rerun()
            with b5:
                if st.button("🆔 Identidade", key=f"{chave}_identidade", help="Preencher como matriz identidade", width="stretch"):
                    # funciona mesmo em matrizes não-quadradas: 1 na diagonal principal, 0 no resto
                    st.session_state[chave_dados] = np.eye(n_linhas, n_colunas)
                    st.session_state[chave_versao] += 1
                    st.rerun()
        else:
            # sem redimensionamento: só o botão de preencher como identidade
            if st.button("🆔 Identidade", key=f"{chave}_identidade", help="Preencher como matriz identidade"):
                st.session_state[chave_dados] = np.eye(n_linhas, n_colunas)
                st.session_state[chave_versao] += 1
                st.rerun()

        # duas colunas lado a lado: a tabela editável à esquerda, a forma simbólica (LaTeX) à direita
        col_tabela, col_simbolica = st.columns(2)
        with col_tabela:
            # DataFrame intermediário só para dar rótulos "1ª lin"/"1ª col" ao data_editor
            # (o Streamlit não aceita rótulos personalizados diretamente sobre um numpy.ndarray)
            df = pd.DataFrame(
                dados,
                index=[f"{i + 1}ª lin" for i in range(n_linhas)],
                columns=[f"{i + 1}ª col" for i in range(n_colunas)],
            )
            # a key inclui o número de versão: ao mudar de forma, gera-se uma key nova, o
            # que faz o Streamlit tratar isto como um widget diferente (evita o erro de
            # tentar reaproveitar o estado de um data_editor com um número de colunas distinto)
            chave_editor = f"{chave}_editor_{st.session_state[chave_versao]}"
            editado = st.data_editor(
                df,
                key=chave_editor,
                num_rows="fixed",       # não permite adicionar/remover linhas por dentro da própria tabela
                width="content",
                row_height=28,           # linhas mais compactas (matrizes pequenas não precisam de muito espaço)
                column_config={c: st.column_config.NumberColumn(format="%.2f", width="small") for c in df.columns},
            )
            matriz = np.array(editado, dtype=float)  # volta a converter o DataFrame editado para numpy
            st.session_state[chave_dados] = matriz  # guarda o valor mais recente para a próxima execução
        with col_simbolica:
            legenda_centrada("Forma simbólica")
            # mostra a matriz em notação matemática (LaTeX), arredondada a 4 casas decimais
            st.latex(sp.latex(sp.Matrix(np.round(matriz, 4).tolist())))
    return matriz  # devolve sempre o valor atual (já lido do editor), para o módulo chamador usar no cálculo


def vetor_input(chave: str, dimensao: int = 2, titulo: str = "Vetor",
                 valor_defeito: np.ndarray | None = None) -> np.ndarray:
    """Editor de células para um vetor de `dimensao` componentes, com
    pré-visualização simbólica ao vivo (mesmo estilo de `matriz_input`)."""
    if valor_defeito is None or len(valor_defeito) != dimensao:
        valor_defeito = np.ones(dimensao)  # sem valor válido: começa com um vetor de uns
    with st.container(border=True):
        st.markdown(f"**{titulo}** · {dimensao}D")  # título simples: nome do vetor + dimensão (2D/3D)
        col_tabela, col_simbolica = st.columns(2)
        with col_tabela:
            # um vetor é representado como uma única linha de uma tabela (1 linha × `dimensao` colunas)
            df = pd.DataFrame([valor_defeito], columns=[f"{i + 1}ª col" for i in range(dimensao)])
            editado = st.data_editor(
                df,
                key=f"{chave}_{dimensao}d",  # a dimensão faz parte da key: 2D e 3D não partilham estado
                num_rows="fixed",
                hide_index=True,  # esconde o número da linha (só há uma, não é informativo)
                width="content",
                row_height=28,
                column_config={c: st.column_config.NumberColumn(format="%.2f", width="small") for c in df.columns},
            )
            vetor = np.array(editado, dtype=float).reshape(-1)  # achata a tabela 1×n para um vetor 1D
        with col_simbolica:
            legenda_centrada("Forma simbólica")
            st.latex(sp.latex(sp.Matrix(np.round(vetor, 4).tolist())))
    return vetor


def modo_passo_a_passo_ativo(chave_pagina: str) -> bool:
    """Toggle único, igual em todos os módulos, desligado por omissão."""
    # `key` inclui `chave_pagina` para cada módulo ter o seu próprio estado
    # independente (o toggle de Matrizes não afeta o de Sistemas, por exemplo)
    return st.toggle("🔍 Mostrar modo passo-a-passo", value=False, key=f"{chave_pagina}_passo_a_passo")


def modo_leve_ativo() -> bool:
    """Cria o toggle de modo leve na sidebar. Chamar UMA ÚNICA VEZ, em streamlit_app.py
    (o widget fica disponível em todas as páginas porque o script de entrada corre sempre).
    Dentro de cada módulo, usar `modo_leve_da_sessao()` para ler o valor sem recriar o widget."""
    # cabeçalho da barra lateral: badge de estado + nome do laboratório + identificação do grupo/UC
    st.sidebar.markdown(
        """
        <div class="sidebar-header-box">
            <span class="lab-status-badge">⚡ ONLINE · V1.0</span>
            <h3 style="margin-top: 0.4rem; margin-bottom: 0.1rem; font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 700; color: #1E1B4B;">
                🧮 Laboratório Interativo
            </h3>
            <p style="font-size: 0.82rem; color: #4F46E5; font-weight: 600; margin-bottom: 0.3rem;">Álgebra Linear Educativa</p>
            <p style="font-size: 0.73rem; color: #64748B; margin-bottom: 0; line-height: 1.35; font-weight: 500;">
                Desenvolvido pelo Grupo 8 / UC: Tecnologias Educativas Aplicadas ao Ensino da Matemática - ISCED - Huíla/2026
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.divider()  # linha a separar o cabeçalho do toggle "Modo leve"
    return st.sidebar.toggle(
        "🐢 Modo leve",
        value=False,
        key="modo_leve",  # chave global (sem prefixo de página): partilhada por toda a app
        help="Reduz a densidade das malhas e o número de frames das animações — "
             "para ligações ou dispositivos mais fracos.",
    )


def modo_leve_da_sessao() -> bool:
    """Lê o estado atual do modo leve, sem criar um novo widget."""
    # usa .get com valor por omissão False, para não rebentar se ainda não tiver sido criado
    return bool(st.session_state.get("modo_leve", False))


def mostrar_passos(passos: list[Passo]) -> None:
    """Renderização uniforme da lista de passos pedagógicos."""
    st.markdown("##### 🔍 Como se chega ao resultado")
    # um expander fechado por passo, numerado — só abre quando o utilizador clica
    for i, passo in enumerate(passos, start=1):
        with st.expander(f"Passo {i}: {passo.titulo}", expanded=False):
            if passo.detalhe:  # texto explicativo em português corrente (opcional)
                st.write(passo.detalhe)
            if passo.latex:  # expressão matemática em LaTeX (opcional)
                st.latex(passo.latex)


def _latex_numerico(numerico) -> str:
    """Formata um escalar/vetor/matriz numérico como bracket LaTeX arredondado,
    para o lado 'Numérico' ter o mesmo aspeto visual do lado 'Simbólico'."""
    arr = np.asarray(numerico, dtype=float)  # aceita tanto escalares como arrays
    arredondado = np.round(arr, 3)  # arredonda a 3 casas decimais, para não poluir o ecrã com dízimas
    if arredondado.ndim == 0:  # escalar (0 dimensões): formata como número simples
        return f"{arredondado:g}"
    # vetor (1D) ou matriz (2D): formata como bracket LaTeX; um vetor 1D é
    # primeiro transformado numa matriz-linha (1×n), para o sp.Matrix aceitar
    return sp.latex(sp.Matrix(arredondado.tolist())) if arredondado.ndim == 2 \
        else sp.latex(sp.Matrix(arredondado.reshape(1, -1).tolist()))


def mostrar_resultado(numerico, simbolico_latex: str, chave_pagina: str,
                       passos: list[Passo] | None = None) -> bool:
    """Mostra o resultado numérico e simbólico lado a lado (ambos como bracket
    LaTeX, para consistência visual), com o toggle "modo passo-a-passo" na
    mesma caixa — e, se ligado, os passos logo a seguir, ainda dentro dela.
    Devolve o estado do toggle, para quem precise dele fora desta chamada."""
    with st.container(border=True):  # cartão único, que engloba o toggle, o resultado e os passos
        col_titulo, col_toggle = st.columns([3, 2])
        with col_titulo:
            st.markdown("##### ✅ Resultado")
        with col_toggle:
            # o toggle vive dentro da própria caixa de resultado, para ficar
            # visualmente associado ao conteúdo que ele revela
            mostrar_passo_a_passo = modo_passo_a_passo_ativo(chave_pagina)
        col_num, col_sym = st.columns(2)  # numérico e simbólico lado a lado
        with col_num:
            legenda_centrada("Numérico")
            st.latex(_latex_numerico(numerico))
        with col_sym:
            legenda_centrada("Simbólico")
            st.latex(simbolico_latex)
        if mostrar_passo_a_passo and passos:  # só mostra os passos se o toggle estiver ligado E existirem passos
            st.divider()
            mostrar_passos(passos)
    return mostrar_passo_a_passo  # devolve o estado, caso o módulo chamador precise dele fora desta caixa
