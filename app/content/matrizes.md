# Matrizes

## Definição

Uma **matriz** é uma tabela retangular de números, organizada em linhas e
colunas. Uma matriz com $m$ linhas e $n$ colunas diz-se de tipo $m \times n$.
Cada número da tabela chama-se **entrada** ou **elemento**, identificado por
dois índices: $a_{ij}$ é a entrada na linha $i$, coluna $j$.

$$
A = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix}
$$

## Propriedades principais

- **Soma**: só é possível somar matrizes com a mesma dimensão; soma-se
  entrada a entrada.
- **Produto por um escalar**: multiplica-se cada entrada da matriz pelo
  número (escalar).
- **Produto matricial**: só é possível multiplicar $A$ (tipo $m\times n$) por
  $B$ (tipo $n \times p$) se o número de colunas de $A$ for igual ao número
  de linhas de $B$; o resultado é do tipo $m \times p$. O produto matricial
  **não é comutativo** em geral: $AB \neq BA$.
- **Transposição**: a transposta $A^T$ troca linhas por colunas.

## Quando se usa (aplicações)

Matrizes representam, entre outras coisas, transformações geométricas
(rotações, escalas), sistemas de equações lineares, grafos e redes, e dados
tabulares em geral (ex. quantidades vendidas por produto e por período).

## Exemplo ilustrativo

<!-- exemplo:matrizes -->

## Ver também

- Determinantes e Matriz Inversa
- Sistemas Lineares
