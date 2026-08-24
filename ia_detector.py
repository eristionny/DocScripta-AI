# -*- coding: utf-8 -*-

import math
import re
from collections import Counter
from typing import Any, Dict, List


# ============================================================
# CONFIGURAÇÃO
# ============================================================

MINIMO_PALAVRAS_DOCUMENTO = 60
MINIMO_PALAVRAS_BLOCO = 45
PALAVRAS_ALVO_BLOCO = 90

MAX_TRECHOS_RELEVANTES = 5

# Resultado encontrado no pequeno corpus atual.
# É apenas um limiar preliminar de validação.
LIMIAR_VALIDACAO_PROVISORIO = 29.0


# ============================================================
# PALAVRAS FUNCIONAIS
# ============================================================

PALAVRAS_FUNCIONAIS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas",
    "de", "do", "da", "dos", "das", "em", "no", "na",
    "nos", "nas", "por", "para", "com", "sem", "e", "ou",
    "mas", "que", "se", "ao", "aos", "à", "às", "como",
    "quando", "onde", "porque", "pois", "já", "não", "sim",
    "ser", "são", "foi", "era", "tem", "têm", "mais",
    "menos", "muito", "muita", "muitos", "muitas", "todo",
    "toda", "todos", "todas", "este", "esta", "esse",
    "essa", "isso", "isto", "ele", "ela", "eles", "elas",
    "seu", "sua", "seus", "suas", "meu", "minha", "meus",
    "minhas", "nosso", "nossa", "nossos", "nossas",
    "lhe", "lhes", "sobre", "entre", "até", "após",
    "durante", "antes", "depois",
}


# ============================================================
# CONECTIVOS
# ============================================================

CONECTIVOS = [
    "além disso",
    "além do mais",
    "porém",
    "contudo",
    "entretanto",
    "todavia",
    "portanto",
    "por conseguinte",
    "consequentemente",
    "assim",
    "dessa forma",
    "dessa maneira",
    "desse modo",
    "por outro lado",
    "em contrapartida",
    "em síntese",
    "em suma",
    "por fim",
    "nesse sentido",
    "sob essa perspectiva",
    "vale ressaltar",
    "é importante destacar",
    "cabe destacar",
    "diante disso",
    "assim sendo",
    "em razão disso",
    "desse ponto de vista",
    "a partir disso",
    "de maneira geral",
    "em conclusão",
    "em primeiro lugar",
    "em segundo lugar",
    "por isso",
]


# ============================================================
# ESTRUTURAS REPETITIVAS
# ============================================================

ESTRUTURAS_REPETITIVAS = [
    "é importante",
    "é fundamental",
    "é necessário",
    "é essencial",
    "deve-se",
    "pode-se",
    "observa-se",
    "verifica-se",
    "destaca-se",
    "ressalta-se",
    "conclui-se",
    "torna-se",
    "faz-se necessário",
    "é possível observar",
    "é possível perceber",
]


# ============================================================
# UTILITÁRIOS
# ============================================================

def normalizar_texto(texto: str) -> str:
    if not texto:
        return ""

    texto = str(texto)
    texto = texto.replace("\r\n", "\n")
    texto = texto.replace("\r", "\n")
    texto = re.sub(r"[ \t]+", " ", texto)
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    return texto.strip()


def tokenizar(texto: str) -> List[str]:
    texto = normalizar_texto(texto).lower()

    if not texto:
        return []

    return re.findall(
        r"\b[\wÀ-ÿ'-]+\b",
        texto,
        flags=re.UNICODE,
    )


def dividir_frases(texto: str) -> List[str]:
    texto = normalizar_texto(texto)

    if not texto:
        return []

    frases = re.split(
        r"(?<=[.!?])\s+",
        texto,
    )

    return [
        frase.strip()
        for frase in frases
        if frase.strip()
    ]


def dividir_paragrafos(texto: str) -> List[str]:
    texto = normalizar_texto(texto)

    if not texto:
        return []

    paragrafos = re.split(
        r"\n\s*\n",
        texto,
    )

    return [
        p.strip()
        for p in paragrafos
        if p.strip()
    ]


# ============================================================
# MÉTRICAS LEXICAIS
# ============================================================

def diversidade_lexical(tokens: List[str]) -> float:
    if not tokens:
        return 0.0

    return len(set(tokens)) / len(tokens)


def diversidade_conteudo(tokens: List[str]) -> float:
    conteudo = [
        token
        for token in tokens
        if token not in PALAVRAS_FUNCIONAIS
        and len(token) > 2
    ]

    if not conteudo:
        return 0.0

    return len(set(conteudo)) / len(conteudo)


def analisar_repeticao_lexical(
    tokens: List[str],
) -> Dict[str, Any]:

    conteudo = [
        token
        for token in tokens
        if token not in PALAVRAS_FUNCIONAIS
        and len(token) > 2
    ]

    if not conteudo:
        return {
            "indice": 0.0,
            "repeticoes": {},
        }

    frequencias = Counter(conteudo)

    repeticoes = {
        palavra: quantidade
        for palavra, quantidade in frequencias.items()
        if quantidade >= 3
    }

    repeticoes_totais = sum(
        quantidade - 1
        for quantidade in frequencias.values()
        if quantidade >= 2
    )

    indice = (
        repeticoes_totais / len(conteudo)
    ) * 2.0

    return {
        "indice": round(
            max(0.0, min(1.0, indice)),
            4,
        ),
        "repeticoes": repeticoes,
    }


def analisar_ngramas(
    tokens: List[str],
    tamanho: int,
) -> Dict[str, Any]:

    if len(tokens) < tamanho * 2:
        return {
            "indice": 0.0,
            "repetidos": {},
        }

    ngrams = [
        " ".join(
            tokens[i:i + tamanho]
        )
        for i in range(
            len(tokens) - tamanho + 1
        )
    ]

    frequencias = Counter(ngrams)

    repetidos = {
        trecho: quantidade
        for trecho, quantidade in frequencias.items()
        if quantidade >= 2
    }

    total = sum(
        quantidade - 1
        for quantidade in frequencias.values()
        if quantidade >= 2
    )

    indice = (
        total / max(1, len(ngrams))
    ) * 3.0

    return {
        "indice": round(
            max(0.0, min(1.0, indice)),
            4,
        ),
        "repetidos": repetidos,
    }


# ============================================================
# FRASES
# ============================================================

def tamanhos_frases(frases: List[str]) -> List[int]:
    resultado = []

    for frase in frases:
        tokens = tokenizar(frase)

        if tokens:
            resultado.append(
                len(tokens)
            )

    return resultado


def comprimento_medio_frases(
    frases: List[str],
) -> float:

    valores = tamanhos_frases(frases)

    if not valores:
        return 0.0

    return sum(valores) / len(valores)


def mediana_frases(
    frases: List[str],
) -> float:

    valores = sorted(
        tamanhos_frases(frases)
    )

    if not valores:
        return 0.0

    n = len(valores)
    meio = n // 2

    if n % 2 == 0:
        return (
            valores[meio - 1]
            + valores[meio]
        ) / 2.0

    return float(
        valores[meio]
    )


def desvio_frases(
    frases: List[str],
) -> float:

    valores = tamanhos_frases(frases)

    if len(valores) < 2:
        return 0.0

    media = sum(valores) / len(valores)

    variancia = sum(
        (valor - media) ** 2
        for valor in valores
    ) / len(valores)

    return math.sqrt(
        variancia
    )


def coeficiente_variacao_frases(
    frases: List[str],
) -> float:

    media = comprimento_medio_frases(
        frases
    )

    if media <= 0:
        return 0.0

    return (
        desvio_frases(frases)
        / media
    )


def calcular_uniformidade_frases(
    frases: List[str],
) -> float:

    if len(frases) < 3:
        return 0.0

    cv = coeficiente_variacao_frases(
        frases
    )

    return max(
        0.0,
        min(
            1.0,
            1.0 - cv,
        ),
    )


# ============================================================
# CONECTIVOS
# ============================================================

def analisar_conectivos(
    texto: str,
) -> Dict[str, Any]:

    texto = normalizar_texto(
        texto
    ).lower()

    ocorrencias = {}
    total = 0

    for conectivo in CONECTIVOS:
        quantidade = texto.count(
            conectivo
        )

        if quantidade:
            ocorrencias[
                conectivo
            ] = quantidade

            total += quantidade

    tokens = tokenizar(
        texto
    )

    densidade = 0.0

    if tokens:
        densidade = (
            total / len(tokens)
        ) * 100.0

    return {
        "total": total,
        "densidade": round(
            densidade,
            3,
        ),
        "ocorrencias": ocorrencias,
    }


# ============================================================
# INÍCIOS DE FRASES
# ============================================================

def normalizar_inicio_frase(
    frase: str,
    quantidade_palavras: int = 3,
) -> str:

    tokens = tokenizar(
        frase
    )

    if not tokens:
        return ""

    return " ".join(
        tokens[:quantidade_palavras]
    )


def analisar_repeticao_frases(
    frases: List[str],
) -> Dict[str, Any]:

    inicios = [
        normalizar_inicio_frase(
            frase
        )
        for frase in frases
    ]

    inicios = [
        item
        for item in inicios
        if item
    ]

    if not inicios:
        return {
            "indice": 0.0,
            "inicios_repetidos": {},
        }

    contagem = Counter(
        inicios
    )

    repetidos = {
        inicio: quantidade
        for inicio, quantidade in contagem.items()
        if quantidade >= 2
    }

    total = sum(
        quantidade - 1
        for quantidade in contagem.values()
        if quantidade >= 2
    )

    indice = (
        total / len(inicios)
    ) * 2.0

    return {
        "indice": round(
            max(0.0, min(1.0, indice)),
            4,
        ),
        "inicios_repetidos": repetidos,
    }


# ============================================================
# ESTRUTURAS
# ============================================================

def analisar_estruturas_repetitivas(
    texto: str,
) -> Dict[str, Any]:

    texto = normalizar_texto(
        texto
    ).lower()

    ocorrencias = {}
    total = 0

    for estrutura in ESTRUTURAS_REPETITIVAS:

        quantidade = texto.count(
            estrutura
        )

        if quantidade:
            ocorrencias[
                estrutura
            ] = quantidade

            total += quantidade

    tokens = tokenizar(
        texto
    )

    indice = 0.0

    if tokens:
        indice = (
            total / len(tokens)
        ) * 3.0

    return {
        "total": total,
        "ocorrencias": ocorrencias,
        "indice": round(
            max(0.0, min(1.0, indice)),
            4,
        ),
    }


# ============================================================
# PREVISIBILIDADE
# ============================================================

def calcular_previsibilidade(
    tokens: List[str],
) -> float:

    if len(tokens) < 20:
        return 0.0

    frequencias = Counter(tokens)

    top = frequencias.most_common(
        min(
            10,
            len(frequencias),
        )
    )

    massa = sum(
        quantidade
        for _, quantidade in top
    )

    proporcao = (
        massa / len(tokens)
    )

    return max(
        0.0,
        min(
            1.0,
            proporcao * 2.0,
        ),
    )


# ============================================================
# COMPLEXIDADE
# ============================================================

def analisar_complexidade_superficial(
    texto: str,
    frases: List[str],
    tokens: List[str],
) -> Dict[str, Any]:

    if not tokens:
        return {
            "indice": 0.0,
            "palavras_medias": 0.0,
            "virgulas_por_frase": 0.0,
        }

    media_tamanho_palavra = (
        sum(
            len(token)
            for token in tokens
        )
        /
        len(tokens)
    )

    virgulas = texto.count(",")

    virgulas_por_frase = (
        virgulas
        /
        max(1, len(frases))
    )

    if media_tamanho_palavra >= 6:
        indicador = 1.0
    elif media_tamanho_palavra >= 5:
        indicador = 0.6
    elif media_tamanho_palavra >= 4:
        indicador = 0.3
    else:
        indicador = 0.0

    indice = (
        indicador * 0.5
        +
        min(
            1.0,
            virgulas_por_frase / 4.0,
        ) * 0.5
    )

    return {
        "indice": round(
            max(0.0, min(1.0, indice)),
            4,
        ),
        "palavras_medias": round(
            media_tamanho_palavra,
            2,
        ),
        "virgulas_por_frase": round(
            virgulas_por_frase,
            2,
        ),
    }


# ============================================================
# VARIAÇÃO SINTÁTICA
# ============================================================

def analisar_variacao_sintatica(
    frases: List[str],
) -> Dict[str, Any]:

    if not frases:
        return {
            "indice": 0.0,
            "padroes": {},
        }

    padroes = []

    for frase in frases:

        quantidade = len(
            tokenizar(frase)
        )

        virgulas = frase.count(",")
        dois_pontos = frase.count(":")
        ponto_virgula = frase.count(";")

        if quantidade < 10:
            tamanho = "curta"
        elif quantidade < 22:
            tamanho = "media"
        else:
            tamanho = "longa"

        padroes.append(
            (
                tamanho,
                virgulas,
                dois_pontos,
                ponto_virgula,
            )
        )

    contagem = Counter(
        padroes
    )

    maior = contagem.most_common(
        1
    )[0][1]

    uniformidade = (
        maior / len(padroes)
    )

    return {
        "indice": round(
            max(
                0.0,
                min(
                    1.0,
                    uniformidade,
                ),
            ),
            4,
        ),
        "padroes": {
            str(chave): valor
            for chave, valor
            in contagem.items()
        },
    }


# ============================================================
# PERFIL GLOBAL
# ============================================================

def calcular_perfil_estilistico(
    texto: str,
) -> Dict[str, float]:

    tokens = tokenizar(
        texto
    )

    frases = dividir_frases(
        texto
    )

    # CORREÇÃO DO ERRO:
    # usar MINIMO_PALAVRAS_BLOCO, que é a constante existente.
    if len(tokens) < MINIMO_PALAVRAS_BLOCO:
        return {}

    diversidade = diversidade_conteudo(
        tokens
    )

    uniformidade = calcular_uniformidade_frases(
        frases
    )

    previsibilidade = calcular_previsibilidade(
        tokens
    )

    conectivos = analisar_conectivos(
        texto
    )

    repeticao = analisar_repeticao_lexical(
        tokens
    )

    bigramas = analisar_ngramas(
        tokens,
        2,
    )

    trigramas = analisar_ngramas(
        tokens,
        3,
    )

    inicios = analisar_repeticao_frases(
        frases
    )

    estruturas = analisar_estruturas_repetitivas(
        texto
    )

    complexidade = analisar_complexidade_superficial(
        texto,
        frases,
        tokens,
    )

    sintaxe = analisar_variacao_sintatica(
        frases
    )

    return {

        "uniformidade":
            uniformidade * 100.0,

        "baixa_diversidade":
            max(
                0.0,
                min(
                    1.0,
                    1.0 - diversidade,
                ),
            ) * 100.0,

        "repeticao_lexical":
            repeticao["indice"] * 100.0,

        "repeticao_bigrams":
            bigramas["indice"] * 100.0,

        "repeticao_trigrams":
            trigramas["indice"] * 100.0,

        "inicios_repetidos":
            inicios["indice"] * 100.0,

        "repeticao_estrutural":
            estruturas["indice"] * 100.0,

        "previsibilidade":
            previsibilidade * 100.0,

        "conectivos":
            min(
                1.0,
                conectivos["densidade"] / 4.0,
            ) * 100.0,

        "variacao_sintatica":
            sintaxe["indice"] * 100.0,

        "complexidade_superficial":
            complexidade["indice"] * 100.0,
    }


# ============================================================
# BLOCOS MAIORES
# ============================================================

def criar_blocos_de_frases(
    texto: str,
) -> List[str]:

    paragrafos = dividir_paragrafos(
        texto
    )

    blocos = []

    # Primeiro, aproveitar parágrafos suficientemente grandes.
    for paragrafo in paragrafos:

        quantidade = len(
            tokenizar(paragrafo)
        )

        if quantidade >= MINIMO_PALAVRAS_BLOCO:
            blocos.append(
                paragrafo
            )

    if len(blocos) >= 2:
        return blocos

    # Se houver poucos parágrafos grandes,
    # juntar frases consecutivas.
    frases = dividir_frases(
        texto
    )

    atual = []
    quantidade = 0

    for frase in frases:

        tokens_frase = tokenizar(
            frase
        )

        if not tokens_frase:
            continue

        atual.append(
            frase
        )

        quantidade += len(
            tokens_frase
        )

        if quantidade >= PALAVRAS_ALVO_BLOCO:

            blocos.append(
                " ".join(atual)
            )

            atual = []
            quantidade = 0

    if atual:

        final = " ".join(
            atual
        )

        if len(
            tokenizar(final)
        ) >= MINIMO_PALAVRAS_BLOCO:

            blocos.append(
                final
            )

    return blocos


# ============================================================
# CLASSIFICAÇÃO
# ============================================================

def classificar_indice(
    indice: float,
) -> str:

    if indice < 20:
        return "MUITO BAIXO"

    if indice < LIMIAR_VALIDACAO_PROVISORIO:
        return "BAIXO"

    if indice < 40:
        return "MODERADO"

    if indice < 60:
        return "ALTO"

    return "MUITO ALTO"


# ============================================================
# ANÁLISE DE TRECHO
# ============================================================

def analisar_trecho(
    texto: str,
    perfil_global: Dict[str, float] = None,
) -> Dict[str, Any]:

    perfil_local = calcular_perfil_estilistico(
        texto
    )

    if not perfil_local:

        return {
            "texto": texto,
            "indice": 0.0,
            "nivel": "MUITO BAIXO",
            "motivos": [],
            "fatores": {},
            "comparacao_global": {},
            "proximidade_global": 0.0,
            "relevancia": 0.0,
        }

    pesos = {

        "uniformidade": 0.12,
        "baixa_diversidade": 0.12,
        "repeticao_lexical": 0.08,
        "repeticao_bigrams": 0.06,
        "repeticao_trigrams": 0.04,
        "inicios_repetidos": 0.08,
        "repeticao_estrutural": 0.10,
        "previsibilidade": 0.10,
        "conectivos": 0.04,
        "variacao_sintatica": 0.10,
        "complexidade_superficial": 0.06,
    }

    score_base = sum(
        perfil_local.get(
            nome,
            0.0,
        ) * peso
        for nome, peso
        in pesos.items()
    )

    comparacao = {}
    distancia_media = 0.0

    if perfil_global:

        diferencas = []

        for nome in pesos:

            local = perfil_local.get(
                nome,
                0.0,
            )

            global_ = perfil_global.get(
                nome,
                0.0,
            )

            diferenca = abs(
                local - global_
            )

            diferencas.append(
                diferenca
            )

            comparacao[nome] = round(
                diferenca,
                2,
            )

        if diferencas:

            distancia_media = (
                sum(diferencas)
                /
                len(diferencas)
            )

    proximidade_global = max(
        0.0,
        min(
            1.0,
            1.0
            -
            (
                distancia_media
                /
                100.0
            ),
        ),
    )

    score = (
        score_base * 0.75
        +
        (
            score_base
            * proximidade_global
            * 0.25
        )
    )

    fatores_fortes = sum(
        1
        for valor
        in perfil_local.values()
        if valor >= 55.0
    )

    if fatores_fortes == 0:
        score = min(
            score,
            28.0,
        )

    elif fatores_fortes == 1:
        score = min(
            score,
            39.0,
        )

    elif fatores_fortes == 2:
        score = min(
            score,
            55.0,
        )

    score = max(
        0.0,
        min(
            100.0,
            score,
        ),
    )

    motivos = []

    if perfil_local.get(
        "uniformidade",
        0,
    ) >= 70:

        motivos.append(
            "uniformidade elevada no comprimento das frases"
        )

    if perfil_local.get(
        "baixa_diversidade",
        0,
    ) >= 55:

        motivos.append(
            "diversidade lexical relativamente baixa"
        )

    if perfil_local.get(
        "repeticao_lexical",
        0,
    ) >= 25:

        motivos.append(
            "repetição relevante de palavras de conteúdo"
        )

    if perfil_local.get(
        "repeticao_bigrams",
        0,
    ) >= 12:

        motivos.append(
            "repetição de expressões"
        )

    if perfil_local.get(
        "repeticao_estrutural",
        0,
    ) >= 15:

        motivos.append(
            "repetição de estruturas linguísticas"
        )

    if perfil_local.get(
        "previsibilidade",
        0,
    ) >= 35:

        motivos.append(
            "concentração lexical elevada"
        )

    if perfil_local.get(
        "conectivos",
        0,
    ) >= 35:

        motivos.append(
            "uso frequente de conectivos estruturais"
        )

    if perfil_local.get(
        "variacao_sintatica",
        0,
    ) >= 70:

        motivos.append(
            "padrões sintáticos relativamente uniformes"
        )

    relevancia = (
        score * 0.75
        +
        proximidade_global
        * 100.0
        * 0.25
    )

    return {

        "texto": texto,

        "indice": round(
            score,
            2,
        ),

        "nivel": classificar_indice(
            score,
        ),

        "motivos": motivos,

        "fatores": {
            nome: round(
                valor,
                2,
            )
            for nome, valor
            in perfil_local.items()
        },

        "comparacao_global": comparacao,

        "proximidade_global": round(
            proximidade_global * 100.0,
            2,
        ),

        "relevancia": round(
            relevancia,
            2,
        ),
    }


# ============================================================
# TRECHOS DO DOCUMENTO
# ============================================================

def analisar_trechos_documento(
    texto: str,
    perfil_global: Dict[str, float] = None,
) -> List[Dict[str, Any]]:

    blocos = criar_blocos_de_frases(
        texto
    )

    resultados = []

    for bloco in blocos:

        if len(
            tokenizar(bloco)
        ) < MINIMO_PALAVRAS_BLOCO:
            continue

        resultado = analisar_trecho(
            bloco,
            perfil_global=perfil_global,
        )

        resultados.append(
            resultado
        )

    resultados.sort(
        key=lambda item:
        item.get(
            "relevancia",
            0.0,
        ),
        reverse=True,
    )

    return resultados


# ============================================================
# TRECHOS RELEVANTES
# ============================================================

def selecionar_trechos_relevantes(
    trechos: List[Dict[str, Any]],
    indice_geral: float,
) -> List[Dict[str, Any]]:

    if not trechos:
        return []

    acima_limiar = [
        item
        for item in trechos
        if item.get(
            "indice",
            0.0,
        )
        >= LIMIAR_VALIDACAO_PROVISORIO
    ]

    if acima_limiar:

        return acima_limiar[
            :MAX_TRECHOS_RELEVANTES
        ]

    # Se o documento global estiver no mínimo na faixa
    # moderada, mostrar os blocos mais relevantes para
    # explicar a classificação.
    if indice_geral >= LIMIAR_VALIDACAO_PROVISORIO:

        return trechos[
            :min(
                3,
                MAX_TRECHOS_RELEVANTES,
            )
        ]

    moderados = [
        item
        for item in trechos
        if item.get(
            "indice",
            0.0,
        ) >= 20.0
    ]

    return moderados[
        :min(
            3,
            MAX_TRECHOS_RELEVANTES,
        )
    ]


# ============================================================
# MUDANÇA DE ESTILO
# ============================================================

def detectar_mudanca_estilo(
    texto: str,
) -> List[Dict[str, Any]]:

    paragrafos = dividir_paragrafos(
        texto
    )

    if len(paragrafos) < 4:
        return []

    resultados = []

    for i in range(
        1,
        len(paragrafos),
    ):

        anterior = paragrafos[
            i - 1
        ]

        atual = paragrafos[
            i
        ]

        tokens_anterior = tokenizar(
            anterior
        )

        tokens_atual = tokenizar(
            atual
        )

        if (
            not tokens_anterior
            or
            not tokens_atual
        ):
            continue

        media_anterior = (
            comprimento_medio_frases(
                dividir_frases(
                    anterior
                )
            )
        )

        media_atual = (
            comprimento_medio_frases(
                dividir_frases(
                    atual
                )
            )
        )

        diversidade_anterior = (
            diversidade_conteudo(
                tokens_anterior
            )
        )

        diversidade_atual = (
            diversidade_conteudo(
                tokens_atual
            )
        )

        distancia_media = 0.0

        if media_anterior > 0:

            distancia_media = (
                abs(
                    media_anterior
                    -
                    media_atual
                )
                /
                max(
                    media_anterior,
                    1,
                )
            )

        distancia_diversidade = abs(
            diversidade_anterior
            -
            diversidade_atual
        )

        distancia = (
            distancia_media * 0.6
            +
            distancia_diversidade * 0.4
        )

        if distancia >= 0.25:

            resultados.append({

                "posicao": i,

                "distancia": round(
                    distancia,
                    3,
                ),

                "paragrafo_anterior":
                    anterior,

                "paragrafo_atual":
                    atual,
            })

    resultados.sort(
        key=lambda item:
        item["distancia"],
        reverse=True,
    )

    return resultados[:10]


# ============================================================
# FORÇA DA EVIDÊNCIA
# ============================================================

def calcular_forca_evidencia(
    texto: str,
    fatores: Dict[str, Any],
) -> str:

    quantidade_palavras = len(
        tokenizar(texto)
    )

    fortes = sum(
        1
        for valor in fatores.values()
        if float(valor) >= 55.0
    )

    if quantidade_palavras < 100:
        return "BAIXA"

    if fortes >= 5:
        return "ALTA"

    if fortes >= 3:
        return "MODERADA"

    return "BAIXA"


# ============================================================
# DISTRIBUIÇÃO
# ============================================================

def calcular_distribuicao_sinais(
    trechos: List[Dict[str, Any]],
) -> Dict[str, float]:

    if not trechos:

        return {
            "baixo": 0.0,
            "moderado": 0.0,
            "alto": 0.0,
            "muito_alto": 0.0,
        }

    contagem = {
        "baixo": 0,
        "moderado": 0,
        "alto": 0,
        "muito_alto": 0,
    }

    for trecho in trechos:

        indice = float(
            trecho.get(
                "indice",
                0,
            )
        )

        if indice < 29:
            contagem["baixo"] += 1

        elif indice < 40:
            contagem["moderado"] += 1

        elif indice < 60:
            contagem["alto"] += 1

        else:
            contagem["muito_alto"] += 1

    total = len(
        trechos
    )

    return {
        chave: round(
            valor / total * 100.0,
            2,
        )
        for chave, valor
        in contagem.items()
    }


# ============================================================
# ANÁLISE PRINCIPAL
# ============================================================

def analisar_texto_ia(
    texto: str,
) -> Dict[str, Any]:

    texto = normalizar_texto(
        texto
    )

    tokens = tokenizar(
        texto
    )

    frases = dividir_frases(
        texto
    )

    paragrafos = dividir_paragrafos(
        texto
    )

    if len(tokens) < MINIMO_PALAVRAS_DOCUMENTO:

        return {
            "indice_estimado": 0.0,
            "classificacao": "INSUFICIENTE",
            "nivel_alerta": "TEXTO MUITO CURTO",
            "trechos": [],
            "trechos_relevantes": [],
            "trechos_todos": [],
            "caracteristicas": [],
            "mudancas_estilo": [],
            "estatisticas": {},
            "distribuicao_sinais": {},
            "concentracao_documental": "BAIXA",
            "forca_evidencia": "BAIXA",
            "fatores": {},
            "observacao": (
                "O texto possui poucos elementos para uma "
                "análise estilística confiável."
            ),
            "texto_analisado": texto,
        }

    perfil_global = (
        calcular_perfil_estilistico(
            texto
        )
    )

    if not perfil_global:

        return {
            "indice_estimado": 0.0,
            "classificacao": "INSUFICIENTE",
            "nivel_alerta": "DADOS INSUFICIENTES",
            "trechos": [],
            "trechos_relevantes": [],
            "trechos_todos": [],
            "caracteristicas": [],
            "mudancas_estilo": [],
            "estatisticas": {},
            "distribuicao_sinais": {},
            "concentracao_documental": "BAIXA",
            "forca_evidencia": "BAIXA",
            "fatores": {},
            "observacao": (
                "Não foi possível construir um perfil "
                "estilístico suficiente."
            ),
            "texto_analisado": texto,
        }

    pesos = {

        "uniformidade": 0.12,
        "baixa_diversidade": 0.12,
        "repeticao_lexical": 0.08,
        "repeticao_bigrams": 0.06,
        "repeticao_trigrams": 0.04,
        "inicios_repetidos": 0.08,
        "repeticao_estrutural": 0.10,
        "previsibilidade": 0.10,
        "conectivos": 0.04,
        "variacao_sintatica": 0.10,
        "complexidade_superficial": 0.06,
    }

    score = sum(
        perfil_global.get(
            nome,
            0.0,
        ) * peso
        for nome, peso
        in pesos.items()
    )

    fatores_fortes = sum(
        1
        for valor
        in perfil_global.values()
        if valor >= 55.0
    )

    if fatores_fortes == 0:
        score = min(score, 28.0)

    elif fatores_fortes == 1:
        score = min(score, 39.0)

    elif fatores_fortes == 2:
        score = min(score, 55.0)

    if len(tokens) < 150:
        score = min(score, 59.0)

    score = max(
        0.0,
        min(
            100.0,
            score,
        ),
    )

    trechos_todos = analisar_trechos_documento(
        texto,
        perfil_global,
    )

    trechos_relevantes = (
        selecionar_trechos_relevantes(
            trechos_todos,
            score,
        )
    )

    mudancas_estilo = (
        detectar_mudanca_estilo(
            texto
        )
    )

    caracteristicas = []

    if perfil_global.get(
        "uniformidade",
        0,
    ) >= 70:

        caracteristicas.append(
            "uniformidade elevada no comprimento das frases"
        )

    elif perfil_global.get(
        "uniformidade",
        0,
    ) >= 55:

        caracteristicas.append(
            "alguma uniformidade no comprimento das frases"
        )

    if perfil_global.get(
        "baixa_diversidade",
        0,
    ) >= 55:

        caracteristicas.append(
            "diversidade lexical relativamente baixa"
        )

    if perfil_global.get(
        "repeticao_lexical",
        0,
    ) >= 25:

        caracteristicas.append(
            "repetição relevante de palavras de conteúdo"
        )

    if perfil_global.get(
        "repeticao_bigrams",
        0,
    ) >= 15:

        caracteristicas.append(
            "repetição de expressões de duas palavras"
        )

    if perfil_global.get(
        "repeticao_estrutural",
        0,
    ) >= 20:

        caracteristicas.append(
            "repetição de estruturas linguísticas"
        )

    if perfil_global.get(
        "previsibilidade",
        0,
    ) >= 35:

        caracteristicas.append(
            "concentração lexical elevada"
        )

    if perfil_global.get(
        "conectivos",
        0,
    ) >= 35:

        caracteristicas.append(
            "uso frequente de conectivos estruturais"
        )

    if perfil_global.get(
        "variacao_sintatica",
        0,
    ) >= 70:

        caracteristicas.append(
            "padrões sintáticos relativamente uniformes"
        )

    if (
        perfil_global.get(
            "uniformidade",
            0,
        ) >= 70
        and
        len(paragrafos) >= 3
    ):

        caracteristicas.append(
            "uniformidade entre diferentes parágrafos"
        )

    if mudancas_estilo:

        caracteristicas.append(
            "mudanças perceptíveis de estilo entre blocos"
        )

    forca_evidencia = (
        calcular_forca_evidencia(
            texto,
            perfil_global,
        )
    )

    classificacao = classificar_indice(
        score
    )

    if classificacao in [
        "ALTO",
        "MUITO ALTO",
    ]:

        nivel_alerta = "ATENÇÃO"

        observacao = (
            "Foram identificados vários sinais estilísticos "
            "compatíveis com geração ou assistência por IA. "
            "Isso não comprova autoria por IA."
        )

    elif classificacao == "MODERADO":

        nivel_alerta = "REVISÃO RECOMENDADA"

        observacao = (
            "Foram identificados alguns sinais estilísticos "
            "que merecem revisão. O resultado não comprova "
            "autoria por IA."
        )

    else:

        nivel_alerta = "SEM ALERTA FORTE"

        observacao = (
            "Foram identificados poucos sinais estilísticos "
            "compatíveis com geração ou assistência por IA."
        )

    trechos_acima_limiar = [
        trecho
        for trecho in trechos_todos
        if trecho.get(
            "indice",
            0,
        ) >= LIMIAR_VALIDACAO_PROVISORIO
    ]

    if trechos_todos:

        proporcao = (
            len(trechos_acima_limiar)
            /
            len(trechos_todos)
        )

    else:

        proporcao = 0.0

    if proporcao >= 0.50:
        concentracao = "ALTA"

    elif proporcao >= 0.25:
        concentracao = "MODERADA"

    else:
        concentracao = "BAIXA"

    distribuicao = (
        calcular_distribuicao_sinais(
            trechos_todos
        )
    )

    conectivos = analisar_conectivos(
        texto
    )

    estatisticas = {

        "palavras":
            len(tokens),

        "frases":
            len(frases),

        "paragrafos":
            len(paragrafos),

        "media_palavras_frase":
            round(
                comprimento_medio_frases(
                    frases
                ),
                2,
            ),

        "mediana_palavras_frase":
            round(
                mediana_frases(
                    frases
                ),
                2,
            ),

        "desvio_palavras_frase":
            round(
                desvio_frases(
                    frases
                ),
                2,
            ),

        "coeficiente_variacao_frases":
            round(
                coeficiente_variacao_frases(
                    frases
                ),
                3,
            ),

        "diversidade_lexical":
            round(
                diversidade_lexical(
                    tokens
                ),
                3,
            ),

        "diversidade_conteudo":
            round(
                diversidade_conteudo(
                    tokens
                ),
                3,
            ),

        "uniformidade":
            round(
                perfil_global.get(
                    "uniformidade",
                    0.0,
                ) / 100.0,
                3,
            ),

        "previsibilidade":
            round(
                perfil_global.get(
                    "previsibilidade",
                    0.0,
                ) / 100.0,
                3,
            ),

        "densidade_conectivos":
            round(
                conectivos["densidade"],
                3,
            ),
    }

    return {

        "indice_estimado":
            round(
                score,
                2,
            ),

        "classificacao":
            classificacao,

        "nivel_alerta":
            nivel_alerta,

        "trechos":
            trechos_relevantes,

        "trechos_relevantes":
            trechos_relevantes,

        "trechos_todos":
            trechos_todos,

        "caracteristicas":
            caracteristicas,

        "mudancas_estilo":
            mudancas_estilo,

        "estatisticas":
            estatisticas,

        "distribuicao_sinais":
            distribuicao,

        "concentracao_documental":
            concentracao,

        "forca_evidencia":
            forca_evidencia,

        "fatores":
            perfil_global,

        "pesos":
            pesos,

        "limiar_validacao_provisorio":
            LIMIAR_VALIDACAO_PROVISORIO,

        "observacao":
            observacao,

        "texto_analisado":
            texto,
    }


# ============================================================
# RELATÓRIO
# ============================================================

def gerar_relatorio_ia(
    resultado: Dict[str, Any],
) -> str:

    linhas = []

    linhas.append(
        "# RELATÓRIO DE ANÁLISE DE IA"
    )

    linhas.append("")

    linhas.append(
        f"**Índice estimado:** "
        f"{resultado.get('indice_estimado', 0):.1f}%"
    )

    linhas.append(
        f"**Classificação:** "
        f"{resultado.get('classificacao', '')}"
    )

    linhas.append(
        f"**Nível de alerta:** "
        f"{resultado.get('nivel_alerta', '')}"
    )

    linhas.append(
        f"**Força da evidência estilística:** "
        f"{resultado.get('forca_evidencia', 'BAIXA')}"
    )

    linhas.append("")

    linhas.append(
        "## CARACTERÍSTICAS OBSERVADAS"
    )

    caracteristicas = resultado.get(
        "caracteristicas",
        [],
    )

    if caracteristicas:

        for item in caracteristicas:
            linhas.append(
                f"- {item}"
            )

    else:

        linhas.append(
            "Nenhuma característica forte foi identificada."
        )

    linhas.append("")

    linhas.append(
        "## PRINCIPAIS FATORES"
    )

    nomes = {

        "uniformidade":
            "Uniformidade das frases",

        "baixa_diversidade":
            "Baixa diversidade lexical",

        "repeticao_lexical":
            "Repetição lexical",

        "repeticao_bigrams":
            "Repetição de expressões",

        "repeticao_trigrams":
            "Repetição de expressões maiores",

        "inicios_repetidos":
            "Repetição do início das frases",

        "repeticao_estrutural":
            "Repetição estrutural",

        "previsibilidade":
            "Concentração/previsibilidade lexical",

        "conectivos":
            "Uso de conectivos",

        "variacao_sintatica":
            "Uniformidade sintática",

        "complexidade_superficial":
            "Complexidade superficial",
    }

    fatores = resultado.get(
        "fatores",
        {},
    )

    ordenados = sorted(
        fatores.items(),
        key=lambda item:
        float(item[1]),
        reverse=True,
    )

    for nome, valor in ordenados:

        if float(valor) >= 25:

            linhas.append(
                f"- **{nomes.get(nome, nome)}:** "
                f"{float(valor):.1f}/100"
            )

    linhas.append("")

    linhas.append(
        "## TRECHOS MAIS RELEVANTES"
    )

    trechos = resultado.get(
        "trechos_relevantes",
        [],
    )

    if not trechos:

        linhas.append(
            "Nenhum bloco relevante foi identificado."
        )

    else:

        for numero, trecho in enumerate(
            trechos,
            start=1,
        ):

            linhas.append(
                f"### Trecho {numero}"
            )

            linhas.append(
                f"**Índice do bloco:** "
                f"{trecho.get('indice', 0):.1f}%"
            )

            linhas.append(
                f"**Relevância no documento:** "
                f"{trecho.get('relevancia', 0):.1f}%"
            )

            linhas.append(
                f"**Classificação:** "
                f"{trecho.get('nivel', '')}"
            )

            linhas.append("")

            linhas.append(
                "**Texto:**"
            )

            linhas.append(
                trecho.get(
                    "texto",
                    "",
                )
            )

            motivos = trecho.get(
                "motivos",
                [],
            )

            if motivos:

                linhas.append("")
                linhas.append(
                    "**Motivos:**"
                )

                for motivo in motivos:

                    linhas.append(
                        f"- {motivo}"
                    )

            linhas.append("")

    linhas.append(
        "## MUDANÇAS DE ESTILO"
    )

    mudancas = resultado.get(
        "mudancas_estilo",
        [],
    )

    if not mudancas:

        linhas.append(
            "Nenhuma mudança significativa foi detectada."
        )

    else:

        for numero, mudanca in enumerate(
            mudancas,
            start=1,
        ):

            linhas.append(
                f"### Mudança {numero}"
            )

            linhas.append(
                f"**Distância:** "
                f"{mudanca.get('distancia', 0)}"
            )

            linhas.append("")
            linhas.append(
                "**Bloco anterior:**"
            )

            linhas.append(
                mudanca.get(
                    "paragrafo_anterior",
                    "",
                )
            )

            linhas.append("")
            linhas.append(
                "**Bloco atual:**"
            )

            linhas.append(
                mudanca.get(
                    "paragrafo_atual",
                    "",
                )
            )

            linhas.append("")

    linhas.append(
        "## DISTRIBUIÇÃO DOS SINAIS"
    )

    distribuicao = resultado.get(
        "distribuicao_sinais",
        {},
    )

    linhas.append(
        f"- Baixo: "
        f"{distribuicao.get('baixo', 0):.1f}%"
    )

    linhas.append(
        f"- Moderado: "
        f"{distribuicao.get('moderado', 0):.1f}%"
    )

    linhas.append(
        f"- Alto: "
        f"{distribuicao.get('alto', 0):.1f}%"
    )

    linhas.append(
        f"- Muito alto: "
        f"{distribuicao.get('muito_alto', 0):.1f}%"
    )

    linhas.append("")

    linhas.append(
        "## ESTATÍSTICAS DO TEXTO"
    )

    estatisticas = resultado.get(
        "estatisticas",
        {},
    )

    for chave, valor in estatisticas.items():

        nome = chave.replace(
            "_",
            " ",
        ).capitalize()

        linhas.append(
            f"- {nome}: {valor}"
        )

    linhas.append("")

    linhas.append(
        "## OBSERVAÇÃO"
    )

    linhas.append(
        resultado.get(
            "observacao",
            "",
        )
    )

    linhas.append("")

    linhas.append(
        "O limiar de 29% é preliminar e foi obtido "
        "no pequeno corpus atual de validação."
    )

    linhas.append(
        "Ele não constitui uma prova de autoria por IA."
    )

    linhas.append(
        "Esta análise é probabilística e baseada em "
        "características estilísticas."
    )

    return "\n".join(
        linhas
    )


# ============================================================
# TESTE LOCAL
# ============================================================

if __name__ == "__main__":

    texto_teste = """
    O Sol é a estrela localizada no centro do Sistema Solar
    e representa a principal fonte de energia para a Terra.
    Formado principalmente por hidrogênio e hélio, ele produz
    energia por meio de reações de fusão nuclear que ocorrem
    em seu núcleo.

    A energia solar influencia o clima, o ciclo da água e a
    fotossíntese realizada pelas plantas. Por meio da
    fotossíntese, os vegetais utilizam a luz solar para produzir
    matéria orgânica e liberar oxigênio, desempenhando um papel
    essencial nos ecossistemas.

    Além disso, a atividade solar pode produzir fenômenos que
    afetam a Terra. Explosões solares e ejeções de massa coronal
    podem liberar partículas e radiação capazes de interferir
    temporariamente em satélites, comunicações e redes elétricas.

    O estudo do Sol permite compreender sua estrutura, sua
    evolução e sua influência sobre o Sistema Solar. Dessa
    maneira, a astronomia utiliza observações do Sol para ampliar
    o conhecimento sobre as estrelas e sobre o ambiente espacial
    próximo à Terra.
    """

    print("")
    print("=" * 70)
    print("TESTE DO DETECTOR DE IA")
    print("=" * 70)
    print("")

    resultado = analisar_texto_ia(
        texto_teste
    )

    print(
        gerar_relatorio_ia(
            resultado
        )
    )