"""Persistência simples do "modo turma": ranking partilhado por código de turma.

Usa sqlite3 (biblioteca padrão) para não acrescentar dependências novas.
Funciona bem no executável desktop e em self-hosting; no Streamlit Community
Cloud gratuito o sistema de ficheiros pode ser reiniciado entre deploys —
tratar o ranking web como "da sessão de aula atual", não permanente.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

CAMINHO_BD = Path(__file__).resolve().parent.parent.parent / "data" / "pontuacoes.db"


def _conexao() -> sqlite3.Connection:
    CAMINHO_BD.parent.mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect(CAMINHO_BD)
    conexao.execute(
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
    with _conexao() as conexao:
        conexao.execute(
            "INSERT INTO pontuacoes (codigo_turma, nome_jogador, topico, pontos, data) VALUES (?, ?, ?, ?, ?)",
            (codigo_turma.strip(), nome_jogador.strip(), topico, pontos, datetime.now().isoformat(timespec="seconds")),
        )


def obter_ranking(codigo_turma: str, topico: str | None = None, limite: int = 10) -> list[dict]:
    with _conexao() as conexao:
        if topico:
            cursor = conexao.execute(
                """SELECT nome_jogador, SUM(pontos) AS total
                   FROM pontuacoes WHERE codigo_turma = ? AND topico = ?
                   GROUP BY nome_jogador ORDER BY total DESC LIMIT ?""",
                (codigo_turma.strip(), topico, limite),
            )
        else:
            cursor = conexao.execute(
                """SELECT nome_jogador, SUM(pontos) AS total
                   FROM pontuacoes WHERE codigo_turma = ?
                   GROUP BY nome_jogador ORDER BY total DESC LIMIT ?""",
                (codigo_turma.strip(), limite),
            )
        return [{"jogador": linha[0], "pontos": linha[1]} for linha in cursor.fetchall()]
