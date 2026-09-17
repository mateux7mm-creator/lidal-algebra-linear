# Laboratório Digital de Álgebra Linear

Aplicação web interativa para o ensino e aprendizagem de Álgebra Linear
(matrizes, determinantes, sistemas lineares, vetores, valores/vetores
próprios), com representação algébrica, numérica e gráfica, modo
passo-a-passo, animações em tempo real e uma secção de jogos e desafios.

Projeto do Mestrado em Ensino da Matemática — Unidade Curricular de
Tecnologias Educativas. Ver [plan.md](plan.md) para o plano de trabalho
completo do grupo.

## Estrutura do projeto

```
app/                  código da aplicação (Streamlit)
  streamlit_app.py     ponto de entrada
  modules/             um ficheiro por módulo/página
  utils/               cálculo simbólico, visualização, componentes partilhados
  content/             texto teórico do módulo "Conteúdo" (Markdown)
desktop/               empacotamento como executável Windows
docs/                  guia do professor, manuscrito IEEE
notebooks/             notebooks de apoio/exploração
data/                  base de dados local do "modo turma" (criada em runtime)
```

## Como correr localmente (versão web)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

A app abre automaticamente no browser em `http://localhost:8501`.

## Como gerar o executável desktop (Windows)

Requer algumas centenas de MB de espaço livre em disco.

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements-desktop.txt
.\desktop\build_exe.ps1
```

O executável fica em `dist/LaboratorioAlgebraLinear.exe` — pode ser
distribuído e corrido em qualquer PC Windows, sem precisar de instalar
Python.

## Como publicar na web (Streamlit Community Cloud)

1. Fazer *push* deste repositório para o GitHub.
2. Em [share.streamlit.io](https://share.streamlit.io), criar uma nova app
   apontando para `app/streamlit_app.py`.
3. O Streamlit Cloud instala automaticamente as dependências listadas em
   `requirements.txt`.

## Documentação complementar

- [docs/guia_professor.md](docs/guia_professor.md) — guia rápido para uso em sala de aula.
- [plan.md](plan.md) — plano de trabalho do grupo (cronograma, responsabilidades, critérios de avaliação).
