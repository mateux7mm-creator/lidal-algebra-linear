"""CSS global injetado em streamlit_app.py para o Laboratório Interativo de Álgebra Linear.
Inclui Google Fonts (Outfit, Plus Jakarta Sans), animações CSS, gradientes dinâmicos,
estilização de cartões em glassmorphism, suporte responsivo e cartões de métricas.
"""
import streamlit as st  # só é preciso para st.markdown (injeta o CSS) e st.iframe (injeta o JS da barra lateral)

_PRIMARIA = "#4F46E5"  # cor indigo principal do tema, reutilizada em vários pontos do CSS abaixo
_TEXTO = "#0F172A"  # cor de texto principal (quase-preto), usada no corpo da página

# String CSS única, construída como f-string para poder interpolar as duas
# constantes acima; como o CSS usa chavetas { } para delimitar blocos, todas
# têm de vir duplicadas {{ }} para escapar da sintaxe de f-string do Python
# (uma chaveta simples seria interpretada como um placeholder a substituir).
_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

/* Fontes globais: aplica a fonte Plus Jakarta Sans e a cor de texto principal a toda a página */
html, body, [class*="css"] {{
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: {_TEXTO};
}}

/* Títulos (h1/h2/h3) e classes de texto especiais usam a fonte Outfit, mais geométrica/moderna */
h1, h2, h3, .hero-title, .gradient-text {{
    font-family: 'Outfit', sans-serif !important;
}}

/* Redução de espaçamentos padrão do Streamlit — o tema por omissão deixa
   demasiado espaço vazio no topo/fundo/largura para uma app com várias
   secções empilhadas como esta */
div[data-testid="stMainBlockContainer"],
div[data-testid="stAppViewContainer"] .block-container,
div.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1300px;
}}
/* barra de topo (ícone de menu/Deploy) mais baixa e transparente, para não
   competir visualmente com o conteúdo da página */
div[data-testid="stHeader"] {{
    height: 2.5rem;
    background: transparent !important;
}}
/* espaçamento vertical entre blocos de conteúdo (títulos, inputs, gráficos, ...) */
div[data-testid="stVerticalBlock"] {{
    gap: 0.75rem !important;
}}
/* linhas divisórias (st.divider()) mais finas e com uma cor discreta ligada ao tema */
hr {{
    margin: 1.25rem 0 !important;
    border-color: rgba(99, 102, 241, 0.15) !important;
}}

/* --------------------------------------------------------------------
   Animações Keyframes — definições reutilizadas por várias classes abaixo,
   via a propriedade CSS "animation: <nome-do-keyframe> ..."
   -------------------------------------------------------------------- */
/* entrada suave: nasce um pouco abaixo e transparente, sobe até à posição final e fica opaco */
@keyframes fadeInSlideUp {{
    from {{
        opacity: 0;
        transform: translateY(18px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

/* flutuação contínua: sobe/desce e roda ligeiramente, em loop, para dar sensação de "vida" a uma imagem */
@keyframes floatAnimation {{
    0% {{ transform: translateY(0px) rotate(0deg); }}
    50% {{ transform: translateY(-8px) rotate(0.5deg); }}
    100% {{ transform: translateY(0px) rotate(0deg); }}
}}

/* pulsação de sombra (não usada em nenhuma classe atual, mantida disponível para uso futuro) */
@keyframes glowPulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.35); }}
    70% {{ box-shadow: 0 0 0 12px rgba(79, 70, 229, 0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(79, 70, 229, 0); }}
}}

/* desloca a posição do gradiente de fundo da esquerda para a direita e de
   volta, em loop — dá o efeito de "cor a fluir" ao texto com gradiente */
@keyframes gradientShift {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

/* --------------------------------------------------------------------
   Título "LIDAL" — centrado, animado, acima do hero da Início
   -------------------------------------------------------------------- */
/* texto grande, centrado, com gradiente de cor animado (gradientShift) e
   uma entrada suave (fadeInSlideUp) quando a página Início carrega */
.lidal-titulo {{
    text-align: center;
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 3.2rem;
    letter-spacing: 0.15em;
    margin: 0.2rem 0 0.6rem 0;
    background: linear-gradient(90deg, #4F46E5 0%, #06B6D4 45%, #4F46E5 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 6s ease infinite, fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}}
/* em ecrãs estreitos (telemóvel/tablet) o título encolhe, para não ocupar
   demasiada altura nem forçar quebra de linha feia */
@media (max-width: 768px) {{
    .lidal-titulo {{
        font-size: 2.1rem;
        letter-spacing: 0.1em;
    }}
}}

/* --------------------------------------------------------------------
   Estilos do Hero & Boas-vindas — o banner grande no topo da página Início
   -------------------------------------------------------------------- */
/* cartão principal: fundo em gradiente suave, cantos arredondados, sombra
   e uma animação de entrada (fadeInSlideUp) quando a página carrega */
.hero-card {{
    background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(243,244,246,0.95) 100%);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 20px;
    padding: 2.2rem 2rem;
    box-shadow: 0 10px 30px -10px rgba(79, 70, 229, 0.15);
    animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
}}

/* faixa colorida vertical decorativa colada à borda esquerda do hero-card
   (elemento ::before = pseudo-elemento gerado só por CSS, sem HTML próprio) */
.hero-card::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 6px;
    height: 100%;
    background: linear-gradient(180deg, #4F46E5 0%, #06B6D4 100%);
    border-top-left-radius: 20px;
    border-bottom-left-radius: 20px;
}}

/* etiqueta pequena em forma de pílula (ex. "BEM VINDO AO LABORATÓRIO...") no topo do hero */
.lab-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.85rem;
    background: linear-gradient(90deg, rgba(79, 70, 229, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
    border: 1px solid rgba(79, 70, 229, 0.25);
    border-radius: 9999px;
    color: #4F46E5;
    font-weight: 700;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}}

/* título do hero com texto em gradiente animado (mesma técnica do .lidal-titulo) */
.gradient-text {{
    background: linear-gradient(135deg, #1E1B4B 0%, #4F46E5 40%, #06B6D4 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientShift 8s ease infinite;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -0.02em;
}}

/* parágrafo de subtítulo/descrição do hero, num tom de cinzento mais suave que o título */
.hero-sub {{
    font-size: 1.1rem;
    color: #475569;
    line-height: 1.6;
    margin-top: 0.6rem;
    font-weight: 400;
}}

/* moldura decorativa para uma eventual imagem no hero: cantos arredondados,
   sombra e animação de flutuação contínua (floatAnimation) */
.hero-img-wrap {{
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(15, 23, 42, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.8);
    transition: transform 0.4s ease, box-shadow 0.4s ease;
    animation: floatAnimation 6s ease-in-out infinite;
}}

/* efeito ao passar o rato: a imagem cresce ligeiramente e a sombra intensifica */
.hero-img-wrap:hover {{
    transform: scale(1.02) translateY(-4px);
    box-shadow: 0 22px 45px rgba(79, 70, 229, 0.25);
}}

/* a própria imagem dentro da moldura preenche sempre a largura disponível */
.hero-img-wrap img {{
    width: 100%;
    height: auto;
    display: block;
    object-fit: cover;
}}

/* Stats Pills - Largura Total Horizontal: os pequenos cartões "Recursos do
   Laboratório" (ex. "Módulos de Cálculo", "Passo a Passo") na página Início */
.recursos-container {{
    width: 100%;
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
}}

/* cada "pílula" de estatística: cartão branco com ícone, número/título e legenda lado a lado */
.stat-pill {{
    display: flex;
    align-items: center;
    gap: 0.85rem;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    padding: 1rem 1.25rem;
    border-radius: 14px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    height: 100%;
}}
/* efeito ao passar o rato: eleva-se ligeiramente e a borda fica mais colorida */
.stat-pill:hover {{
    transform: translateY(-3px);
    border-color: #818CF8;
    box-shadow: 0 10px 22px rgba(79, 70, 229, 0.12);
}}
/* ícone emoji à esquerda de cada pílula */
.stat-icon {{
    font-size: 1.8rem;
    line-height: 1;
}}
/* linha de texto principal (título) de cada pílula */
.stat-num {{
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    color: #1E1B4B;
}}
/* linha de texto secundária (legenda) de cada pílula */
.stat-label {{
    font-size: 0.8rem;
    color: #64748B;
}}

/* --------------------------------------------------------------------
   Cartões dos Módulos (Grid com Mesma Altura - Equal Height Cards)
   -------------------------------------------------------------------- */
/* cada coluna do Streamlit (st.columns) passa a ser um contentor flexível em
   coluna, condição necessária para o cartão lá dentro poder esticar até
   100% da altura da coluna (ver regra seguinte) */
div[data-testid="stColumn"] {{
    display: flex;
    flex-direction: column;
}}

/* o cartão (st.container(border=True)) dentro de uma coluna estica para
   preencher toda a altura disponível, com uma altura mínima e o conteúdo
   distribuído verticalmente (título no topo, texto espaçado até ao fundo) —
   garante que todos os cartões de uma grelha ficam com a mesma altura,
   mesmo que o texto de cada um tenha um comprimento diferente */
div[data-testid="stColumn"] > div[data-testid="stVerticalBlockBorderWrapper"] {{
    height: 100% !important;
    min-height: 175px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
}}

/* aparência base de qualquer cartão com borda (st.container(border=True)) em toda a app:
   cantos arredondados, borda subtil, fundo branco, sombra ligeira e transição suave */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-radius: 16px !important;
    border: 1px solid rgba(226, 232, 240, 0.8) !important;
    background: #FFFFFF;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}}

/* ao passar o rato sobre qualquer cartão: eleva-se, aumenta ligeiramente de
   tamanho e a sombra/borda ficam mais destacadas (feedback visual de "clicável") */
div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    transform: translateY(-4px) scale(1.005) !important;
    box-shadow: 0 16px 32px -8px rgba(79, 70, 229, 0.18) !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
}}

/* cabeçalho de um cartão de módulo: ícone à esquerda, badge (etiqueta) à direita */
.module-header-box {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.4rem;
}}

/* forma base de uma badge (etiqueta) pequena em pílula, usada nos cartões de
   módulo e também no cabeçalho do editor de matrizes (componentes.py) */
.module-badge {{
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
/* 4 variantes de cor da badge, escolhidas por módulo/contexto para os distinguir visualmente */
.badge-indigo {{ background: #EEF2FF; color: #4F46E5; border: 1px solid #C7D2FE; }}
.badge-cyan {{ background: #ECFEFF; color: #0891B2; border: 1px solid #A5F3FC; }}
.badge-emerald {{ background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }}
.badge-amber {{ background: #FFFBEB; color: #D97706; border: 1px solid #FDE68A; }}

/* imagem ilustrativa dentro de um cartão de módulo (ex. vitrine de objetos 3D) */
.math-object-img {{
    width: 100%;
    height: 140px;
    object-fit: cover;
    border-radius: 12px;
    margin-bottom: 0.75rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    transition: transform 0.3s ease;
}}
/* efeito de zoom ligeiro ao passar o rato sobre a imagem */
.math-object-img:hover {{
    transform: scale(1.03);
}}

/* --------------------------------------------------------------------
   Botões e Controlos
   -------------------------------------------------------------------- */
/* aparência base de todos os botões da app (st.button e st.form_submit_button) */
div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {{
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all 0.2s ease !important;
    border: 1px solid rgba(79, 70, 229, 0.2) !important;
}}

/* ao passar o rato: o botão eleva-se e fica preenchido a indigo (feedback de hover) */
div[data-testid="stButton"] button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.25) !important;
    background-color: #4F46E5 !important;
    color: #FFFFFF !important;
}}

/* Botão Primário no Streamlit (st.button(..., type="primary")): sempre
   preenchido com um gradiente indigo, independentemente do hover */
div[data-testid="stButton"] button[kind="primary"] {{
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3) !important;
}}

/* --------------------------------------------------------------------
   Caixas de Passos e Expansores — os st.expander("Passo N: ...") do modo
   pedagógico passo-a-passo, definidos em componentes.mostrar_passos()
   -------------------------------------------------------------------- */
div[data-testid="stExpander"] {{
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    background: #FAFAFA !important;
    overflow: hidden !important;
}}

/* o título clicável (summary) de cada expander, a negrito e na cor de texto escura do tema */
div[data-testid="stExpander"] summary {{
    font-weight: 600 !important;
    color: #1E1B4B !important;
}}

/* --------------------------------------------------------------------
   Barra Lateral & Status Badge
   -------------------------------------------------------------------- */
/* fundo e borda direita da barra lateral (menu de navegação + "Modo leve") */
section[data-testid="stSidebar"] {{
    background-color: #F8FAFC !important;
    border-right: 1px solid #E2E8F0 !important;
}}

/* espaçamento do bloco de cabeçalho no topo da barra lateral (badge + título + descrição) */
.sidebar-header-box {{
    padding: 0.6rem 0.2rem;
}}

/* pequena etiqueta verde "⚡ ONLINE · V1.0" no cabeçalho da barra lateral */
.lab-status-badge {{
    display: inline-block;
    padding: 0.2rem 0.5rem;
    background: #DCFCE7;
    color: #15803D;
    border: 1px solid #86EFAC;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}}

/* --------------------------------------------------------------------
   Métricas estilizadas — os st.metric(...) usados em Determinantes,
   Jogos e Desafios, etc.
   -------------------------------------------------------------------- */
div[data-testid="stMetric"] {{
    background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%) !important;
    border: 1px solid #C7D2FE !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    border-left: 4px solid #4F46E5 !important;
}}
/* o número/valor da métrica destaca-se a negrito na cor indigo do tema */
div[data-testid="stMetricValue"] {{
    color: #4F46E5 !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
}}

/* --------------------------------------------------------------------
   Responsividade para Ecrãs Pequenos (Telemóveis / Tablets) — o Streamlit
   já empilha as colunas sozinho abaixo de 768px; aqui só se ajustam
   tamanhos/espaçamentos para caberem confortavelmente num ecrã estreito
   -------------------------------------------------------------------- */
@media (max-width: 768px) {{
    /* menos espaço lateral desperdiçado num ecrã já estreito */
    div[data-testid="stMainBlockContainer"] {{
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
    }}
    /* hero mais compacto (menos padding interno) */
    .hero-card {{
        padding: 1.4rem 1.1rem !important;
    }}
    /* título do hero mais pequeno, para não quebrar de forma feia */
    .gradient-text {{
        font-size: 1.8rem !important;
    }}
    /* subtítulo do hero um pouco mais pequeno */
    .hero-sub {{
        font-size: 0.95rem !important;
    }}
    /* imagens ilustrativas mais baixas, para não dominarem o ecrã pequeno */
    .math-object-img {{
        height: 110px !important;
    }}
}}
</style>
"""


def injetar_css() -> None:
    """Aplica o CSS global e executa o script de controlo inteligente da barra lateral (Aberta na Home, Fechada nos Módulos)."""
    st.markdown(_CSS, unsafe_allow_html=True)  # injeta o bloco <style> inteiro na página (invisível, só define regras CSS)
    # st.iframe com um bloco de HTML/JS "cru" (não um URL) — o Streamlit
    # deteta que não é um URL válido e embute-o como conteúdo direto de um
    # iframe de 1×1 pixel (invisível), a única forma de correr JavaScript
    # personalizado dentro de uma app Streamlit
    st.iframe(
        """
        <script>
        (function() {
            // Impede o browser de oferecer traduzir a página (ex. "Traduzir
            // para Português?" no Edge/Chrome). O Streamlit declara a página
            // como inglês (sem <html lang>), por isso o browser costuma
            // sugerir tradução automática; se o utilizador aceitar, a
            // tradução reescreve nós de texto por fora do React, e a
            // aplicação rebenta com "NotFoundError: Failed to execute
            // 'removeChild'..." na primeira vez que o React tentar atualizar
            // esses mesmos nós (ex. ao mudar de tópico em Conteúdo). Já foi
            // reproduzido assim num PC de aluno.
            function impedirTraducaoAutomatica() {
                try {
                    const parentDoc = window.parent.document;
                    // marca o documento como português e "não traduzir" —
                    // o próprio atributo `translate="no"` é o sinal padrão
                    // (norma HTML) que Chrome/Edge respeitam
                    parentDoc.documentElement.lang = "pt";
                    parentDoc.documentElement.translate = false;
                    parentDoc.documentElement.setAttribute("translate", "no");
                    // reforço específico do Google Translate (usado pelo
                    // motor de tradução do Chrome/Edge, que nem sempre olha
                    // só para o atributo "translate")
                    if (!parentDoc.querySelector('meta[name="google"]')) {
                        const meta = parentDoc.createElement("meta");
                        meta.name = "google";
                        meta.content = "notranslate";
                        parentDoc.head.appendChild(meta);
                    }
                } catch (e) {
                    console.log("Impedir tradução automática:", e);
                }
            }

            // função principal: decide, a partir do URL atual, se a barra
            // lateral deve estar aberta (página Início) ou fechada (dentro
            // de um módulo) e clica no botão de expandir/colapsar em conformidade
            function gerirBarraLateral() {
                try {
                    impedirTraducaoAutomatica();
                    // o iframe corre num documento próprio; para aceder à
                    // página Streamlit real é preciso ir a "window.parent"
                    const parentDoc = window.parent.document;
                    const parentWin = window.parent;
                    const href = parentWin.location.href.toLowerCase();
                    const pathname = parentWin.location.pathname.toLowerCase();
                    const search = parentWin.location.search.toLowerCase();
                    const fullUrl = (href + pathname + search);

                    // Verificar se estamos na página inicial ("Início")
                    const eInicio = fullUrl.endsWith('/inicio') ||
                                   pathname === '/' ||
                                   pathname.endsWith('/inicio') ||
                                   pathname.endsWith('app/') ||
                                   search.includes('inicio') ||
                                   (!fullUrl.includes('matrizes') &&
                                    !fullUrl.includes('determinantes') &&
                                    !fullUrl.includes('sistemas') &&
                                    !fullUrl.includes('exploracao') &&
                                    !fullUrl.includes('vetores') &&
                                    !fullUrl.includes('valores-proprios') &&
                                    !fullUrl.includes('jogos') &&
                                    !fullUrl.includes('conteudo'));

                    // localiza o elemento <section> da barra lateral no documento pai; se ainda não existir, desiste desta chamada
                    const sidebar = parentDoc.querySelector('section[data-testid="stSidebar"]');
                    if (!sidebar) return;

                    // o Streamlit marca o estado aberto/fechado neste atributo ARIA
                    const estaExpandida = sidebar.getAttribute('aria-expanded') === 'true';

                    if (eInicio) {
                        // Na página inicial: Garantir que a barra lateral fica ABERTA (Expandida)
                        if (!estaExpandida) {
                            // procura o botão de expandir por várias formas possíveis (a
                            // versão do Streamlit pode mudar o data-testid/aria-label exato)
                            const expandBtn = parentDoc.querySelector('button[data-testid="stSidebarExpandButton"]') ||
                                             parentDoc.querySelector('div[data-testid="stSidebarCollapsedControl"] button') ||
                                             parentDoc.querySelector('[aria-label="Expand sidebar"]') ||
                                             parentDoc.querySelector('[aria-label="Open sidebar"]');
                            if (expandBtn) expandBtn.click();  // simula o clique do utilizador nesse botão
                        }
                    } else {
                        // Dentro de qualquer módulo (Matrizes, Sistemas, etc.): Garantir que FECHA (Recolhe)
                        if (estaExpandida) {
                            // mesma estratégia de fallback, mas para o botão de colapsar
                            const collapseBtn = parentDoc.querySelector('button[data-testid="stSidebarCollapseButton"]') ||
                                                parentDoc.querySelector('section[data-testid="stSidebar"] button') ||
                                                parentDoc.querySelector('[aria-label="Close sidebar"]') ||
                                                parentDoc.querySelector('[aria-label="Collapse sidebar"]');
                            if (collapseBtn) collapseBtn.click();
                        }
                    }
                } catch (e) {
                    // falha silenciosa: um erro aqui (ex. elemento ainda não
                    // existe) não deve rebentar a app, só não aplica o ajuste desta vez
                    console.log("Gerir barra lateral:", e);
                }
            }

            // corre imediatamente e depois mais 3 vezes com atraso crescente,
            // para cobrir o caso de a barra lateral ainda não ter sido
            // desenhada pelo React na primeira chamada (não há evento "pronto"
            // fiável para nos avisarmos disso)
            gerirBarraLateral();
            setTimeout(gerirBarraLateral, 150);
            setTimeout(gerirBarraLateral, 450);
            setTimeout(gerirBarraLateral, 900);
        })();
        </script>
        """,
        height=1,  # iframe de 1×1 pixel: executa o script sem ocupar espaço visível na página
        width=1,
    )
