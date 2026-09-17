# Plano de Trabalho — Projecto 5: Laboratório Digital de Álgebra Linear

**Unidade Curricular:** Tecnologias Educativas — Mestrado em Ensino da Matemática
**Prazo:** 10 a 25 de Setembro de 2026 (15 dias)
**Defesa:** 25/09/2026, 15h30, online

---

## 1. Enquadramento do Projeto

Desenvolver um ambiente tecnológico interativo para o ensino e aprendizagem de Álgebra
Linear, combinando representação **algébrica, numérica e gráfica** dos conteúdos:

- Matrizes e operações matriciais (soma, produto, transposição)
- Determinantes
- Matriz inversa
- Sistemas de equações lineares (resolução e interpretação geométrica)
- Vetores e operações vetoriais
- Valores próprios e vetores próprios (eigenvalues/eigenvectors)

**Tecnologias:** Python, NumPy, SymPy, Matplotlib, Streamlit (interface), Jupyter Notebook
(exploração/documentação).

---

## 2. Problema Educacional a Resolver

*(a refinar com o grupo — hipótese de trabalho)*

Estudantes do ensino secundário/universitário têm dificuldade em construir intuição
geométrica sobre operações de Álgebra Linear porque o ensino tradicional é
predominantemente algébrico/simbólico, sem visualização imediata do efeito das operações
(ex.: como uma matriz transforma o plano, o que significa geometricamente um valor
próprio). Isto gera aprendizagem mecânica e dificuldade de transferência para outras
disciplinas (Física, Computação Gráfica, Estatística).

**Pergunta de investigação:** De que forma um ambiente interativo que combine cálculo
simbólico, numérico e visualização gráfica pode melhorar a compreensão concetual de
conceitos fundamentais de Álgebra Linear?

---

## 3. Objetivos

1. Conceber um recurso interativo que permita manipular matrizes/vetores e observar
   imediatamente o efeito algébrico e geométrico das operações.
2. Fundamentar pedagogicamente a solução com literatura sobre ensino de Álgebra Linear
   e visualização matemática.
3. Implementar um protótipo funcional (aplicação web) cobrindo os conteúdos do programa.
4. Avaliar a usabilidade e o valor pedagógico do recurso junto de um grupo-alvo.
5. Redigir um manuscrito científico no formato IEEE Conference documentando todo o
   processo.

---

## 4. Público-Alvo

Estudantes do ensino secundário (11º/12º ano) e/ou primeiro ano do ensino superior que
estejam a estudar Álgebra Linear pela primeira vez; professores de Matemática como
utilizadores/mediadores do recurso em sala de aula.

---

## 5. Conteúdo Matemático Abordado

| Módulo | Conceitos |
|---|---|
| Matrizes | Definição, tipos, soma, multiplicação escalar, produto matricial, transposição |
| Determinantes | Cálculo (regra de Sarrus, expansão de Laplace, eliminação), propriedades |
| Matriz Inversa | Existência, método de Gauss-Jordan, matriz adjunta |
| Sistemas Lineares | Eliminação de Gauss, regra de Cramer, interpretação geométrica (interseção de retas/planos) |
| Vetores | Operações, norma, produto interno, produto externo (3D), ortogonalidade |
| Valores/Vetores Próprios | Cálculo, interpretação geométrica (direções invariantes), diagonalização |

---

## 6. Produto Tecnológico

**Formato:** Aplicativo web interativo — uma aplicação multi-página (menu lateral tipo
app, cada módulo como um "ecrã" próprio), construída em **Streamlit** (alternativa: Dash),
com aparência e navegação semelhantes a uma app, mas acessível diretamente pelo navegador
(sem necessidade de instalação, partilhável via link — ex. Streamlit Community Cloud).
Complementada por Jupyter Notebooks de apoio/documentação.

### Funcionalidades principais
- **Módulo Matrizes:** input de matrizes (editor de células), operações com visualização
  passo-a-passo do cálculo (SymPy para forma simbólica).
- **Módulo Determinantes/Inversa:** cálculo com explicação do método, deteção de matrizes
  singulares.
- **Módulo Sistemas Lineares:** resolução + representação gráfica 2D/3D da interseção de
  retas/planos (Matplotlib/Plotly).
- **Módulo Vetores:** visualização gráfica de vetores no plano/espaço, operações
  interativas (soma, produto interno).
- **Módulo Valores/Vetores Próprios:** cálculo + visualização gráfica da transformação
  linear e das direções próprias (animação simples do efeito da matriz sobre um conjunto
  de vetores).
- **Modo "passo-a-passo" pedagógico:** cada operação mostra o método de resolução, não só
  o resultado final (alinhado com o espírito do enunciado — evitar ferramenta de "caixa
  preta").

### Arquitetura técnica (proposta)
```
/app
  streamlit_app.py       # interface principal
  /modules
    matrizes.py
    determinantes.py
    sistemas.py
    vetores.py
    valores_proprios.py
  /utils
    simbolico.py          # wrappers SymPy
    visualizacao.py        # wrappers Matplotlib/Plotly
/notebooks
  exploracao_conceitos.ipynb
/docs
  manuscrito_ieee/
```

---

## 7. Fundamentação Teórica (pontos a pesquisar)

- Dificuldades de aprendizagem em Álgebra Linear (ex.: Dorier, Sierpinska — obstáculos
  epistemológicos).
- Papel da visualização/representações múltiplas na aprendizagem matemática (Duval —
  registos de representação semiótica).
- Tecnologia educativa e manipulação interativa (Computer Algebra Systems no ensino).
- Estudos prévios com GeoGebra/Python no ensino de Álgebra Linear.

*(Tarefa: cada membro do grupo traz 2-3 referências científicas até ao dia 3 do prazo)*

---

## 8. Estratégia de Avaliação do Recurso

- **Teste de usabilidade** com um pequeno grupo de utilizadores-alvo (colegas ou
  estudantes), com tarefas guiadas (ex.: "calcule os valores próprios desta matriz e
  interprete graficamente").
- **Questionário pós-uso** (escala tipo Likert) sobre clareza, utilidade percebida,
  facilidade de uso.
- **Análise qualitativa** de observações/feedback recolhido.
- Comparação (se possível) entre compreensão antes/depois da utilização do recurso.

---

## 9. Requisitos Obrigatórios (checklist do enunciado)

- [ ] Identificação clara do problema educacional
- [ ] Definição dos objetivos
- [ ] Fundamentação teórica baseada em literatura científica
- [ ] Identificação do público-alvo
- [ ] Descrição do conteúdo matemático abordado
- [ ] Justificação das tecnologias selecionadas
- [ ] Produto/protótipo funcional desenvolvido
- [ ] Exemplos de utilização apresentados
- [ ] Estratégia de avaliação do recurso definida
- [ ] Análise crítica de potencialidades e limitações
- [ ] Manuscrito científico em formato IEEE Conference
- [ ] Apresentação e defesa pública

---

## 10. Estrutura do Manuscrito IEEE (6-8 páginas, 2 colunas)

1. **Title** — título científico claro e informativo
2. **Authors and Affiliations**
3. **Abstract**
4. **Keywords** (4-6 termos)
5. **I. Introduction** — contexto, problema, motivação, objetivos, contribuições
6. **II. Related Work / Theoretical Background** — literatura sobre o conteúdo
   matemático, pedagogia e tecnologia
7. **III. Methodology** — metodologia de desenvolvimento e avaliação
8. **IV. Design and Implementation** — arquitetura, funcionalidades, ferramentas,
   algoritmos, interface, decisões pedagógicas
9. **V. Results and Evaluation** — resultados, exemplos de funcionamento, testes,
   avaliação
10. **VI. Discussion** — interpretação dos resultados, contributos, limitações,
    comparação com trabalhos relacionados
11. **VII. Conclusion and Future Work**
12. **References** (estilo IEEE)

*Template oficial: IEEE Conference Template (obter em ieee.org / Overleaf).*

---

## 11. Divisão de Responsabilidades (8 elementos)

| Função | Responsável | Notas |
|---|---|---|
| Coordenação do projeto | — | acompanha prazos e integração |
| Revisão da literatura | — | secção II do manuscrito |
| Componente matemática | — | validação da correção matemática dos módulos |
| Desenho pedagógico | — | fundamentação e estratégia de avaliação |
| Programação (backend/lógica) | — | módulos SymPy/NumPy |
| Interface e UX (Streamlit/visualização) | — | módulos gráficos |
| Testes e avaliação | — | condução do teste de usabilidade |
| Elaboração do manuscrito e apresentação | — | compilação final, slides |

> Nota: todos os membros devem ter conhecimento global do projeto — serão questionados
> individualmente na defesa.

---

## 12. Calendário (15 dias — 10 a 25 Set 2026)

| Dias | Fase | Entregas |
|---|---|---|
| Dia 1-2 (10-11 Set) | Kickoff: definição final do problema, objetivos, divisão de papéis | Problema + objetivos definidos |
| Dia 3-4 (12-13 Set) | Revisão de literatura + desenho da arquitetura técnica | Lista de referências, esboço da arquitetura |
| Dia 5-9 (14-18 Set) | Desenvolvimento incremental do protótipo (módulos 1 a 5) | Protótipo funcional por módulo |
| Dia 10-11 (19-20 Set) | Integração, testes internos, início da escrita do manuscrito | App integrada, rascunho secções I-IV |
| Dia 12-13 (21-22 Set) | Teste de usabilidade com utilizadores + análise de resultados | Dados de avaliação, secção V-VI do manuscrito |
| Dia 14 (23 Set) | Finalização do manuscrito IEEE + revisão cruzada | Manuscrito completo (PDF) |
| Dia 15 (24 Set) | Preparação da apresentação, ensaio da defesa | Slides + ensaio |
| 25 Set, 15h30 | **Apresentação e Defesa** | Todos os entregáveis submetidos |

> Recomendação do enunciado: desenvolvimento incremental — evitar deixar
> implementação/manuscrito/defesa para os últimos dias.

---

## 13. Elementos a Entregar (checklist final)

- [ ] Manuscrito científico em PDF (template IEEE Conference)
- [ ] Código-fonte organizado, documentado e comentado
- [ ] Produto tecnológico / protótipo funcional
- [ ] Ficheiro ou link para executar a aplicação (ex.: Streamlit Cloud, repositório com
      instruções)
- [ ] Apresentação usada na defesa (slides)
- [ ] Documentação complementar (ex.: guia de utilização)

---

## 14. Critérios de Avaliação (referência)

| Critério | Peso |
|---|---|
| Relevância e definição do problema | 10% |
| Fundamentação teórica e revisão da literatura | 10% |
| Qualidade científica e metodológica | 10% |
| Integração Matemática/Pedagogia/Tecnologia | 15% |
| Qualidade e funcionalidade do produto tecnológico | 20% |
| Inovação e criatividade | 10% |
| Qualidade do manuscrito IEEE | 10% |
| Apresentação e demonstração | 5% |
| Defesa e domínio individual dos conteúdos | 10% |

---

## 15. Perguntas-Guia para a Defesa

*(secção 13 do enunciado — todos os membros podem ser questionados individualmente sobre
qualquer uma destas questões; devem ser preparadas em conjunto pelo grupo)*

1. Que problema de ensino ou aprendizagem da Matemática pretendemos resolver?
2. Por que razão a tecnologia selecionada (Python/NumPy/SymPy/Matplotlib/Streamlit) é
   adequada para esse problema?
3. Que conhecimentos matemáticos e pedagógicos estão subjacentes à solução?
4. Que evidências demonstram que o recurso desenvolvido é funcional e pedagogicamente
   útil?
5. Quais são as limitações da solução e como poderá ser melhorada?

> Recomendação: preparar uma resposta curta e fundamentada para cada pergunta, com
> referência direta ao manuscrito (secção correspondente), para que qualquer membro do
> grupo consiga responder na sessão de perguntas e respostas.

---

## 16. Próximos Passos Imediatos

1. Confirmar composição do grupo (8 elementos) e atribuir responsabilidades (secção 11).
2. Validar/refinar a definição do problema educacional (secção 2) com o grupo.
3. Criar estrutura de repositório/pastas do projeto (`/app`, `/notebooks`, `/docs`).
4. Iniciar recolha de referências bibliográficas.
5. Configurar ambiente de desenvolvimento (Python + dependências: numpy, sympy,
   matplotlib, streamlit, plotly).
