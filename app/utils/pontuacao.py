"""Persistência simples do "modo turma": ranking partilhado por código de turma.

Usa sqlite3 (biblioteca padrão) para não acrescentar dependências novas.
Funciona bem no executável desktop e em self-hosting; no Streamlit Community
Cloud gratuito o sistema de ficheiros pode ser reiniciado entre deploys —
tratar o ranking web como "da sessão de aula atual", não permanente.
"""
from __future__ import annotations  # permite usar "str | None" em anotações mesmo em versões mais antigas do Python

import sqlite3  # motor de base de dados embutido no Python, guarda tudo num único ficheiro local
from datetime import datetime  # para registar a data/hora de cada pontuação
from pathlib import Path  # manipulação de caminhos de ficheiros de forma independente do sistema operativo

# caminho do ficheiro da base de dados: <raiz do projeto>/data/pontuacoes.db
# (sobe 3 níveis a partir deste ficheiro: utils/ -> app/ -> raiz)
CAMINHO_BD = Path(__file__).resolve().parent.parent.parent / "data" / "pontuacoes.db"


def _conexao() -> sqlite3.Connection:
    # cria a pasta data/ se ainda não existir, para o sqlite3.connect não falhar
    CAMINHO_BD.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(CAMINHO_BD)  # abre (ou cria) o ficheiro da base de dados
    conexao.execute(
        # cria a tabela "pontuacoes" só se ainda não existir (idempotente,
        # seguro chamar em cada arranque da app)
        """
        CREATE TABLE IF NOT EXISTS pontuacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_turma TEXT NOT NULL,
            nome_jogador TEXT NOT NULL,
            topico TEXT NOT NULL,
            pontos INTEGER NOT NULL,
            data TEXT NOT NULL
        )
        """
    )
    return conexao


def registar_pontuacao(codigo_turma: str, nome_jogador: str, topico: str, pontos: int) -> None:
    # "with" garante commit automático no fim do bloco (ou rollback se houver erro)
    with _conexao() as conexao:
        # insere uma nova linha de pontuação; "?" são parâmetros ligados (evita SQL injection)
        conexao.execute(
            "INSERT INTO pontuacoes (codigo_turma, nome_jogador, topico, pontos, data) VALUES (?, ?, ?, ?, ?)",
            (codigo_turma.strip(), nome_jogador.strip(), topico, pontos, datetime.now().isoformat(timespec="seconds")),
        )


def obter_ranking(codigo_turma: str, topico: str | None = None, limite: int = 10) -> list[dict]:
    with _conexao() as conexao:
        if topico:
            # ranking filtrado a um único tópico: soma os pontos por jogador,
            # ordena do maior para o menor e limita ao número de linhas pedido
            cursor = conexao.execute(
                """SELECT nome_jogador, SUM(pontos) AS total
                   FROM pontuacoes WHERE codigo_turma = ? AND topico = ?
                   GROUP BY nome_jogador ORDER BY total DESC LIMIT ?""",
                (codigo_turma.strip(), topico, limite),
            )
        else:
            # sem tópico: ranking geral da turma, somando pontos de todos os tópicos
            cursor = conexao.execute(
                """SELECT nome_jogador, SUM(pontos) AS total
                   FROM pontuacoes WHERE codigo_turma = ?
                   GROUP BY nome_jogador ORDER BY total DESC LIMIT ?""",
                (codigo_turma.strip(), limite),
            )
        # converte cada linha (tuplo) do cursor num dicionário {"jogador": ..., "pontos": ...}
        return [{"jogador": linha[0], "pontos": linha[1]} for linha in cursor.fetchall()]
