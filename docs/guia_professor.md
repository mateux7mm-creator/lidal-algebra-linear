# Guia rápido do Professor — Laboratório Digital de Álgebra Linear

Este guia é dirigido ao professor que queira usar a aplicação como recurso
de apoio nas aulas de Álgebra Linear, como mediador entre a ferramenta e os
alunos.

## Visão geral dos módulos

| Módulo | Objetivo pedagógico |
|---|---|
| Matrizes | Praticar as operações básicas e ver o efeito geométrico do produto escalar |
| Determinantes / Inversa | Ligar o cálculo algébrico à noção geométrica de área/singularidade |
| Sistemas Lineares | Ver a solução de um sistema como a interseção de retas |
| Vetores | Explorar operações vetoriais com visualização imediata |
| Valores/Vetores Próprios | Visualizar direções invariantes de uma transformação |
| Jogos e Desafios | Praticar de forma gamificada, individualmente ou em "modo turma" |
| Conteúdo | Consulta teórica (definição, propriedades, exemplo) por tópico |

## Sugestões de atividade por módulo

**Matrizes** — Peça aos alunos que calculem à mão o produto de duas matrizes
2×2 e depois confirmem o resultado na app, ativando o modo passo-a-passo.
Em seguida, explore o slider de `k·A` para discutir o efeito de escalar uma
matriz.

**Determinantes** — Peça aos alunos que prevejam se uma matriz é singular
antes de calcular; depois use a animação para observar visualmente o
paralelogramo a "colapsar numa linha" quando o determinante se aproxima de
zero.

**Sistemas Lineares** — Compare a solução algébrica com o gráfico das duas
retas; use a animação para discutir o que acontece à solução quando um
coeficiente varia (e o que significa as retas ficarem paralelas).

**Vetores** — Peça a dois alunos que escolham vetores diferentes e discutam
em conjunto se são ortogonais, confirmando com o teste da app.

**Valores/Vetores Próprios** — Use a animação `t: 0→1` para mostrar a
transformação a "nascer" da identidade; peça aos alunos que identifiquem
visualmente as direções que não mudam de sentido.

## Modo turma (Jogos e Desafios)

1. Peça a cada aluno que preencha o mesmo **código de turma** (ex. o nome da
   disciplina + a data) e o seu próprio nome, na barra lateral do módulo
   "Jogos e Desafios".
2. Cada aluno resolve os desafios ao seu ritmo; o ranking da turma atualiza-se
   automaticamente por tópico.
3. Nota: no executável desktop ou em self-hosting, o ranking persiste no
   ficheiro local do servidor. No Streamlit Community Cloud gratuito, trate
   o ranking como válido apenas durante a sessão de aula atual.

## Modo leve

Se a ligação à internet ou o dispositivo dos alunos for mais limitado,
recomende ativar o **Modo leve** na barra lateral — reduz a densidade dos
gráficos e das animações sem alterar os resultados.
