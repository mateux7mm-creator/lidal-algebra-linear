# Determinantes e Matriz Inversa

## Definição

O **determinante** de uma matriz quadrada $A$, denotado $\det(A)$ ou $|A|$,
é um número que resume propriedades importantes da matriz — em particular,
se a matriz é ou não invertível. Para uma matriz $2\times2$:

$$
\det\begin{bmatrix} a & b \\ c & d \end{bmatrix} = ad - bc
$$

A **matriz inversa** $A^{-1}$ é a matriz tal que $A \cdot A^{-1} = I$
(matriz identidade). Só existe se $\det(A) \neq 0$.

## Propriedades principais

- $\det(A) = 0$ ⟺ a matriz é **singular** (não tem inversa) ⟺ as linhas/colunas
  são linearmente dependentes.
- Geometricamente, $|\det(A)|$ é o fator de escala da área (2D) ou volume
  (3D) que a transformação $A$ aplica a uma figura.
- $\det(AB) = \det(A)\det(B)$.

## Quando se usa (aplicações)

Verificar se um sistema linear tem solução única, calcular áreas/volumes,
inverter transformações geométricas, e como ingrediente de outros cálculos
(ex. valores próprios).

## Exemplo ilustrativo

<!-- exemplo:determinantes -->

## Ver também

- Matrizes
- Sistemas Lineares
- Valores e Vetores Próprios
