"""Launcher usado pelo executável PyInstaller: arranca o servidor Streamlit local.

Sem --server.headless=true: mantém-se o comportamento por omissão do
Streamlit de abrir automaticamente o browser predefinido — dá a experiência
de "duplo-clique e a app abre".
"""
import os  # variáveis de ambiente e caminhos de ficheiros/pastas
import sys  # argumentos de linha de comandos (sys.argv) e deteção de executável "congelado" (frozen)

# sys.frozen só existe (e é True) quando o script corre dentro de um .exe
# gerado pelo PyInstaller — fora daí (ex. "python run_app.py" normal), este
# bloco é ignorado.
if getattr(sys, "frozen", False):
    # O PyInstaller extrai os pacotes para sys._MEIPASS/streamlit/..., sem o
    # segmento "site-packages" no caminho. O Streamlit usa esse segmento para
    # detetar se foi "instalado normalmente"; a ausência liga automaticamente
    # o global.developmentMode, que faz o servidor NÃO montar os ficheiros
    # estáticos do frontend (espera um dev-server Node em localhost:3000) —
    # e por isso "/" devolve 404 dentro do executável empacotado.
    os.environ.setdefault("STREAMLIT_GLOBAL_DEVELOPMENT_MODE", "false")

# módulo interno do Streamlit que implementa o comando "streamlit run" —
# reutilizado aqui para arrancar o servidor sem precisar do executável "streamlit" no PATH
from streamlit.web import cli as stcli


def _skip_onboarding_prompt() -> None:
    """Evita o prompt "Welcome to Streamlit! Email:" na primeira execução,
    que bloqueia para sempre num .exe sem terminal interativo."""
    # pasta de configuração do Streamlit no perfil do utilizador (~/.streamlit)
    config_dir = os.path.join(os.path.expanduser("~"), ".streamlit")
    # ficheiro de credenciais onde o Streamlit guarda a resposta ao prompt de boas-vindas
    credentials_path = os.path.join(config_dir, "credentials.toml")
    if not os.path.exists(credentials_path):
        # ainda não existe: cria a pasta (se preciso) e escreve um email vazio,
        # simulando a resposta que o utilizador daria ao prompt interativo
        os.makedirs(config_dir, exist_ok=True)
        with open(credentials_path, "w", encoding="utf-8") as f:
            f.write("[general]\nemail = \"\"\n")


def main() -> None:
    _skip_onboarding_prompt()  # garante que o Streamlit não fica à espera de input na consola
    if getattr(sys, "frozen", False):
        # Executável PyInstaller: --add-data "app;app" coloca a pasta app/ na raiz
        # do bundle extraído (sys._MEIPASS), não um nível acima deste ficheiro.
        base_dir = sys._MEIPASS  # type: ignore[attr-defined]  # pasta temporária onde o PyInstaller extraiu tudo
        app_path = os.path.join(base_dir, "app", "streamlit_app.py")  # caminho para o ponto de entrada real da app
        # O Streamlit procura .streamlit/config.toml relativo ao diretório de
        # trabalho atual, não a sys._MEIPASS — mudamos para lá para o tema
        # (cores, fonte) também se aplicar dentro do executável.
        os.chdir(base_dir)
    else:
        # execução normal (fora do .exe): caminhos relativos a este ficheiro
        base_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(base_dir, "..", "app", "streamlit_app.py")
    # simula a chamada "streamlit run <app_path>" na linha de comandos
    sys.argv = ["streamlit", "run", app_path]
    sys.exit(stcli.main())  # arranca o servidor Streamlit; sys.exit propaga o código de saída


if __name__ == "__main__":
    main()  # só corre quando este ficheiro é executado diretamente (não quando importado)
