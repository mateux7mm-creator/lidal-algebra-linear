# Valores e Vetores Próprios

## Definição

Dada uma matriz quadrada $A$, um vetor não-nulo $v$ é um **vetor próprio**
(eigenvector) de $A$ se, ao aplicar $A$, o vetor apenas é escalado (não muda
de direção):

$$
Av = \lambda v
$$

onde $\lambda$ (lambda) é o **valor próprio** (eigenvalue) correspondente.

## Propriedades principais

- Os valores próprios são as soluções da **equação característica**
  $\det(A - \lambda I) = 0$.
- Uma matriz $n \times n$ diagonalizável tem $n$ vetores próprios
  linearmente independentes, e pode escrever-se $A = PDP^{-1}$, onde $D$ é
  diagonal (com os valores próprios) e $P$ tem os vetores próprios como
  colunas.
- Geometricamente, as direções próprias são as direções que a transformação
  $A$ "não desvia" — só estica ou encolhe (pelo fator $\lambda$).

## Quando se usa (aplicações)

Análise de estabilidade de sistemas dinâmicos, compressão/análise de dados
(ex. PCA), vibrações e modos próprios em engenharia, motores de pesquisa
(PageRank), entre muitas outras.

## Exemplo ilustrativo

<!-- exemplo:valores_proprios -->

## Ver também

- Matrizes
- Determinantes e Matriz Inversa
