# ============================================================
# DOCSCRIPTA AI
# MÓDULO: ORIGINALIDADE ACADÊMICA
# VERSÃO: NCBI/PUBMED DIRETO + ABSTRACTS
# ============================================================

import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from difflib import SequenceMatcher
from typing import Optional, List, Dict, Any


# ============================================================
# CONFIGURAÇÃO NCBI
# ============================================================

NCBI_BASE_URL = (
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
)

NCBI_TOOL = "DocScriptaAI"

NCBI_EMAIL = os.environ.get(
    "NCBI_EMAIL",
    ""
)

NCBI_API_KEY = os.environ.get(
    "NCBI_API_KEY",
    ""
)


# ============================================================
# 1. NORMALIZAÇÃO
# ============================================================

def normalizar_texto(
    texto: str
) -> str:

    if not texto:
        return ""

    texto = str(
        texto
    ).lower()

    texto = re.sub(
        r"https?://\S+",
        " ",
        texto
    )

    texto = re.sub(
        r"[^a-záàâãéêíóôõúç0-9\s]",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ============================================================
# 2. TOKENIZAÇÃO
# ============================================================

def tokenizar_texto(
    texto: str
) -> List[str]:

    texto = normalizar_texto(
        texto
    )

    if not texto:
        return []

    return texto.split()


# ============================================================
# 3. SHINGLES
# ============================================================

def criar_shingles(
    texto: str,
    tamanho: int = 5
) -> set:

    tokens = tokenizar_texto(
        texto
    )

    if len(tokens) < tamanho:
        return set()

    return {
        " ".join(
            tokens[i:i + tamanho]
        )
        for i in range(
            len(tokens) - tamanho + 1
        )
    }


# ============================================================
# 4. SIMILARIDADE POR SHINGLES
# ============================================================

def similaridade_shingles(
    texto_a: str,
    texto_b: str,
    tamanho: int = 5
) -> float:

    shingles_a = criar_shingles(
        texto_a,
        tamanho
    )

    shingles_b = criar_shingles(
        texto_b,
        tamanho
    )

    if (
        not shingles_a
        or
        not shingles_b
    ):
        return 0.0

    uniao = (
        shingles_a
        |
        shingles_b
    )

    intersecao = (
        shingles_a
        &
        shingles_b
    )

    if not uniao:
        return 0.0

    return (
        len(intersecao)
        /
        len(uniao)
    ) * 100.0


# ============================================================
# 5. SIMILARIDADE SEQUENCIAL
# ============================================================

def similaridade_sequencial(
    texto_a: str,
    texto_b: str
) -> float:

    a = normalizar_texto(
        texto_a
    )

    b = normalizar_texto(
        texto_b
    )

    if not a or not b:
        return 0.0

    return (
        SequenceMatcher(
            None,
            a,
            b
        ).ratio()
        * 100.0
    )


# ============================================================
# 6. ÍNDICE GERAL
# ============================================================

def calcular_similaridade(
    texto_a: str,
    texto_b: str
) -> float:

    if not texto_a or not texto_b:
        return 0.0

    shingle = (
        similaridade_shingles(
            texto_a,
            texto_b
        )
    )

    sequencial = (
        similaridade_sequencial(
            texto_a,
            texto_b
        )
    )

    resultado = (
        (shingle * 0.65)
        +
        (sequencial * 0.35)
    )

    return round(
        resultado,
        2
    )


# ============================================================
# 7. CLASSIFICAÇÃO
# ============================================================

def classificar_similaridade(
    percentual: float
) -> str:

    if percentual < 10:
        return "BAIXA"

    if percentual < 25:
        return "MODERADA"

    if percentual < 40:
        return "ALTA"

    return "MUITO ALTA"


# ============================================================
# 8. TRECHOS SEMELHANTES
# ============================================================

def detectar_trechos_semelhantes(
    texto_principal: str,
    texto_fonte: str,
    minimo_palavras: int = 8
) -> List[Dict[str, Any]]:

    principal = tokenizar_texto(
        texto_principal
    )

    fonte = tokenizar_texto(
        texto_fonte
    )

    if (
        len(principal) < minimo_palavras
        or
        len(fonte) < minimo_palavras
    ):
        return []

    resultados = []

    indices_fonte = {}

    limite_fonte = min(
        len(fonte),
        5000
    )

    for j in range(
        limite_fonte - minimo_palavras + 1
    ):

        chave = " ".join(
            fonte[
                j:j + minimo_palavras
            ]
        )

        indices_fonte.setdefault(
            chave,
            []
        ).append(j)

    limite_principal = min(
        len(principal),
        5000
    )

    i = 0

    while (
        i <
        limite_principal - minimo_palavras + 1
    ):

        chave = " ".join(
            principal[
                i:i + minimo_palavras
            ]
        )

        locais = (
            indices_fonte.get(
                chave,
                []
            )
        )

        melhor_tamanho = 0

        for j in locais:

            tamanho = minimo_palavras

            while (
                i + tamanho < len(principal)
                and
                j + tamanho < len(fonte)
                and
                principal[i + tamanho]
                ==
                fonte[j + tamanho]
            ):

                tamanho += 1

            if tamanho > melhor_tamanho:
                melhor_tamanho = tamanho

        if (
            melhor_tamanho
            >=
            minimo_palavras
        ):

            trecho = " ".join(
                principal[
                    i:i + melhor_tamanho
                ]
            )

            resultados.append({
                "trecho":
                    trecho,

                "quantidade_palavras":
                    melhor_tamanho,

                "posicao":
                    i
            })

            i += melhor_tamanho

        else:

            i += 1

    resultados.sort(
        key=lambda item:
        item["quantidade_palavras"],
        reverse=True
    )

    finais = []

    vistos = set()

    for item in resultados:

        chave = item[
            "trecho"
        ]

        if chave in vistos:
            continue

        vistos.add(
            chave
        )

        finais.append(
            item
        )

    return finais[:20]


# ============================================================
# 9. POSSÍVEIS CITAÇÕES
# ============================================================

def detectar_possiveis_citacoes(
    texto: str
) -> List[str]:

    if not texto:
        return []

    frases = re.split(
        r"(?<=[.!?])\s+",
        texto.strip()
    )

    indicadores = [
        "segundo",
        "estudo",
        "estudos",
        "pesquisa",
        "pesquisas",
        "artigo",
        "artigos",
        "evidência",
        "evidências",
        "dados",
        "resultado",
        "resultados",
        "pesquisadores",
        "autores",
        "cientistas",
        "demonstrou",
        "demonstram",
        "indica",
        "indicam",
        "aponta",
        "apontam",
        "associado",
        "associada",
        "aumenta",
        "reduz",
        "causa",
        "taxa",
        "percentual",
        "%",
        "segundo o estudo",
        "de acordo com"
    ]

    candidatos = []

    for frase in frases:

        frase = frase.strip()

        if len(
            frase.split()
        ) < 8:

            continue

        frase_lower = (
            frase.lower()
        )

        if any(
            indicador in frase_lower
            for indicador in indicadores
        ):

            candidatos.append(
                frase
            )

    return candidatos[:30]


# ============================================================
# 10. REQUISIÇÃO AO NCBI
# ============================================================

def requisicao_ncbi(
    endpoint: str,
    parametros: Dict[str, str],
    timeout: int = 20
) -> Optional[str]:

    parametros = dict(
        parametros
    )

    parametros.setdefault(
        "tool",
        NCBI_TOOL
    )

    if NCBI_EMAIL:

        parametros.setdefault(
            "email",
            NCBI_EMAIL
        )

    if NCBI_API_KEY:

        parametros.setdefault(
            "api_key",
            NCBI_API_KEY
        )

    query = urllib.parse.urlencode(
        parametros
    )

    url = (
        NCBI_BASE_URL
        +
        endpoint
        +
        "?"
        +
        query
    )

    try:

        requisicao = urllib.request.Request(
            url,
            headers={
                "User-Agent":
                    "DocScriptaAI/1.0"
            }
        )

        with urllib.request.urlopen(
            requisicao,
            timeout=timeout
        ) as resposta:

            return (
                resposta.read()
                .decode(
                    "utf-8",
                    errors="replace"
                )
            )

    except Exception as erro:

        print(
            "[Originalidade] "
            f"Erro NCBI: {erro}"
        )

        return None


# ============================================================
# 11. BUSCAR PMIDS NO PUBMED
# ============================================================

def buscar_pmids_pubmed(
    consulta: str,
    max_resultados: int = 5
) -> List[str]:

    if not consulta:
        return []

    consulta = (
        consulta
        .replace("\n", " ")
        .strip()
    )

    consulta = consulta[:500]

    print(
        "[Originalidade] "
        f"Busca PubMed: {consulta}"
    )

    xml_texto = requisicao_ncbi(
        "esearch.fcgi",
        {
            "db":
                "pubmed",

            "term":
                consulta,

            "retmode":
                "xml",

            "retmax":
                str(
                    max_resultados
                )
        }
    )

    if not xml_texto:

        return []

    try:

        raiz = ET.fromstring(
            xml_texto
        )

    except ET.ParseError as erro:

        print(
            "[Originalidade] "
            f"Erro no XML do PubMed: {erro}"
        )

        return []

    pmids = []

    for elemento in raiz.findall(
        ".//Id"
    ):

        if elemento.text:

            pmids.append(
                elemento.text.strip()
            )

    return pmids


# ============================================================
# 12. BUSCAR REGISTROS / ABSTRACTS
# ============================================================

def buscar_artigos_por_pmids(
    pmids: List[str]
) -> List[Dict[str, Any]]:

    if not pmids:
        return []

    ids = [
        str(pmid).strip()
        for pmid in pmids
        if str(pmid).strip()
    ]

    if not ids:
        return []

    print(
        "[Originalidade] "
        f"Recuperando {len(ids)} artigo(s)..."
    )

    xml_texto = requisicao_ncbi(
        "efetch.fcgi",
        {
            "db":
                "pubmed",

            "id":
                ",".join(ids),

            "retmode":
                "xml"
        }
    )

    if not xml_texto:
        return []

    try:

        raiz = ET.fromstring(
            xml_texto
        )

    except ET.ParseError as erro:

        print(
            "[Originalidade] "
            f"Erro no XML dos artigos: {erro}"
        )

        return []

    artigos = []

    for artigo_xml in raiz.findall(
        ".//PubmedArticle"
    ):

        # ----------------------------------------------------
        # PMID
        # ----------------------------------------------------

        elemento_pmid = (
            artigo_xml.find(
                ".//PMID"
            )
        )

        pmid = ""

        if (
            elemento_pmid is not None
            and
            elemento_pmid.text
        ):

            pmid = (
                elemento_pmid.text
                .strip()
            )

        if not pmid:
            continue

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        elemento_titulo = (
            artigo_xml.find(
                ".//ArticleTitle"
            )
        )

        titulo = ""

        if elemento_titulo is not None:

            titulo = "".join(
                elemento_titulo.itertext()
            ).strip()

        # ----------------------------------------------------
        # ABSTRACT
        # ----------------------------------------------------

        partes_abstract = []

        for elemento_abstract in (
            artigo_xml.findall(
                ".//AbstractText"
            )
        ):

            texto_abstract = "".join(
                elemento_abstract.itertext()
            ).strip()

            if not texto_abstract:
                continue

            label = (
                elemento_abstract.attrib.get(
                    "Label",
                    ""
                )
            )

            if label:

                partes_abstract.append(
                    f"{label}: "
                    f"{texto_abstract}"
                )

            else:

                partes_abstract.append(
                    texto_abstract
                )

        abstract = "\n".join(
            partes_abstract
        )

        # ----------------------------------------------------
        # DOI
        # ----------------------------------------------------

        doi = ""

        for identificador in (
            artigo_xml.findall(
                ".//ArticleId"
            )
        ):

            tipo = (
                identificador.attrib.get(
                    "IdType",
                    ""
                )
            )

            if (
                tipo.lower() == "doi"
                and
                identificador.text
            ):

                doi = (
                    identificador.text
                    .strip()
                )

                break

        # ----------------------------------------------------
        # AUTORES
        # ----------------------------------------------------

        autores = []

        for autor_xml in (
            artigo_xml.findall(
                ".//Author"
            )
        ):

            sobrenome = ""
            iniciais = ""

            elemento_sobrenome = (
                autor_xml.find(
                    "LastName"
                )
            )

            elemento_iniciais = (
                autor_xml.find(
                    "Initials"
                )
            )

            if (
                elemento_sobrenome is not None
                and
                elemento_sobrenome.text
            ):

                sobrenome = (
                    elemento_sobrenome.text
                    .strip()
                )

            if (
                elemento_iniciais is not None
                and
                elemento_iniciais.text
            ):

                iniciais = (
                    elemento_iniciais.text
                    .strip()
                )

            nome_autor = (
                f"{sobrenome} {iniciais}"
                .strip()
            )

            if nome_autor:

                autores.append(
                    nome_autor
                )

        link = (
            "https://pubmed.ncbi.nlm.nih.gov/"
            +
            pmid
            +
            "/"
        )

        artigos.append({
            "titulo":
                titulo,

            "pmid":
                pmid,

            "doi":
                doi,

            "autores":
                autores,

            "abstract":
                abstract,

            "texto":
                abstract,

            "link":
                link,

            "tem_abstract":
                bool(
                    abstract
                )
        })

    return artigos


# ============================================================
# 13. PESQUISA PUBMED COMPLETA
# ============================================================

def pesquisar_pubmed_direto(
    consulta: str,
    max_resultados: int = 5
) -> List[Dict[str, Any]]:

    pmids = buscar_pmids_pubmed(
        consulta,
        max_resultados
    )

    if not pmids:

        print(
            "[Originalidade] "
            "Nenhum PMID encontrado."
        )

        return []

    print(
        "[Originalidade] "
        f"PMIDs encontrados: {', '.join(pmids)}"
    )

    artigos = buscar_artigos_por_pmids(
        pmids
    )

    print(
        "[Originalidade] "
        f"Artigos recuperados: {len(artigos)}"
    )

    artigos_com_abstract = sum(
        1
        for artigo in artigos
        if artigo.get(
            "tem_abstract"
        )
    )

    print(
        "[Originalidade] "
        f"Artigos com abstract: "
        f"{artigos_com_abstract}"
    )

    return artigos


# ============================================================
# 14. ANÁLISE DE UMA FONTE
# ============================================================

def analisar_fonte(
    texto_principal: str,
    fonte: Dict[str, Any]
) -> Dict[str, Any]:

    titulo = fonte.get(
        "titulo",
        "Fonte sem título"
    )

    texto_fonte = (
        fonte.get(
            "texto",
            ""
        )
        or
        fonte.get(
            "abstract",
            ""
        )
    )

    resultado = {
        "titulo":
            titulo,

        "similaridade":
            None,

        "classificacao":
            "SEM TEXTO",

        "trechos":
            [],

        "pmid":
            fonte.get(
                "pmid",
                ""
            ),

        "doi":
            fonte.get(
                "doi",
                ""
            ),

        "link":
            fonte.get(
                "link",
                ""
            ),

        "tem_texto":
            False,

        "tem_abstract":
            fonte.get(
                "tem_abstract",
                False
            )
    }

    if not texto_fonte:

        return resultado

    resultado[
        "tem_texto"
    ] = True

    indice = (
        calcular_similaridade(
            texto_principal,
            texto_fonte
        )
    )

    resultado[
        "similaridade"
    ] = indice

    resultado[
        "classificacao"
    ] = (
        classificar_similaridade(
            indice
        )
    )

    resultado[
        "trechos"
    ] = (
        detectar_trechos_semelhantes(
            texto_principal,
            texto_fonte
        )
    )

    for trecho in resultado[
        "trechos"
    ]:

        trecho[
            "fonte"
        ] = titulo

    return resultado


# ============================================================
# 15. ANÁLISE COMPLETA
# ============================================================

def analisar_originalidade(
    texto: str,
    fontes: Optional[
        List[Dict[str, Any]]
    ] = None
) -> Dict[str, Any]:

    if not texto:

        return {
            "status":
                "SEM TEXTO",

            "indice_maximo":
                0.0,

            "classificacao":
                "INDETERMINADA",

            "fontes_analisadas":
                0,

            "fontes_com_texto":
                0,

            "fontes":
                [],

            "trechos":
                [],

            "citacoes":
                []
        }

    fontes = fontes or []

    resultados = []

    for fonte in fontes:

        if not isinstance(
            fonte,
            dict
        ):
            continue

        resultados.append(
            analisar_fonte(
                texto,
                fonte
            )
        )

    valores = [
        item[
            "similaridade"
        ]
        for item in resultados
        if item[
            "similaridade"
        ] is not None
    ]

    if valores:

        indice_maximo = max(
            valores
        )

        classificacao = (
            classificar_similaridade(
                indice_maximo
            )
        )

    else:

        indice_maximo = 0.0

        classificacao = (
            "SEM CORPUS COMPARÁVEL"
        )

    trechos = []

    for resultado in resultados:

        trechos.extend(
            resultado.get(
                "trechos",
                []
            )
        )

    trechos.sort(
        key=lambda item:
        item.get(
            "quantidade_palavras",
            0
        ),
        reverse=True
    )

    citacoes = (
        detectar_possiveis_citacoes(
            texto
        )
    )

    fontes_com_texto = sum(
        1
        for item in resultados
        if item.get(
            "tem_texto"
        )
    )

    if trechos:

        status = (
            "REVISÃO RECOMENDADA"
        )

    elif citacoes:

        status = (
            "VERIFICAR CITAÇÕES"
        )

    elif (
        resultados
        and
        not fontes_com_texto
    ):

        status = (
            "FONTES ENCONTRADAS — "
            "TEXTO NÃO DISPONÍVEL"
        )

    else:

        status = (
            "SEM ALERTAS SIGNIFICATIVOS"
        )

    return {
        "status":
            status,

        "indice_maximo":
            round(
                indice_maximo,
                2
            ),

        "classificacao":
            classificacao,

        "fontes_analisadas":
            len(resultados),

        "fontes_com_texto":
            fontes_com_texto,

        "fontes":
            resultados,

        "trechos":
            trechos[:20],

        "citacoes":
            citacoes
    }


# ============================================================
# 16. RELATÓRIO
# ============================================================

def gerar_relatorio_originalidade(
    resultado: Dict[str, Any]
) -> str:

    linhas = []

    linhas.append(
        "# RELATÓRIO DE ORIGINALIDADE ACADÊMICA"
    )

    linhas.append("")

    linhas.append(
        f"**Status:** "
        f"{resultado.get('status', '')}"
    )

    linhas.append(
        f"**Índice máximo de similaridade "
        f"encontrado:** "
        f"{resultado.get('indice_maximo', 0)}%"
    )

    linhas.append(
        f"**Classificação:** "
        f"{resultado.get('classificacao', '')}"
    )

    linhas.append(
        f"**Fontes encontradas:** "
        f"{resultado.get('fontes_analisadas', 0)}"
    )

    linhas.append(
        f"**Fontes com texto comparável:** "
        f"{resultado.get('fontes_com_texto', 0)}"
    )

    linhas.append("")

    # ========================================================
    # FONTES
    # ========================================================

    linhas.append(
        "## FONTES ANALISADAS"
    )

    fontes = resultado.get(
        "fontes",
        []
    )

    if not fontes:

        linhas.append(
            "Nenhuma fonte foi encontrada."
        )

    else:

        for fonte in fontes:

            titulo = fonte.get(
                "titulo",
                "Fonte sem título"
            )

            similaridade = (
                fonte.get(
                    "similaridade"
                )
            )

            classificacao = (
                fonte.get(
                    "classificacao",
                    ""
                )
            )

            pmid = fonte.get(
                "pmid",
                ""
            )

            doi = fonte.get(
                "doi",
                ""
            )

            tem_texto = fonte.get(
                "tem_texto",
                False
            )

            if similaridade is None:

                linhas.append(
                    f"- **{titulo}** — "
                    f"{classificacao}"
                )

            else:

                linhas.append(
                    f"- **{titulo}** — "
                    f"{similaridade}% — "
                    f"{classificacao}"
                )

            if pmid:

                linhas.append(
                    f"  PMID: {pmid}"
                )

            if doi:

                linhas.append(
                    f"  DOI: {doi}"
                )

            if tem_texto:

                linhas.append(
                    "  Conteúdo textual: disponível"
                )

            else:

                linhas.append(
                    "  Conteúdo textual: "
                    "não disponível"
                )

    linhas.append("")

    # ========================================================
    # TRECHOS
    # ========================================================

    linhas.append(
        "## TRECHOS PARA REVISÃO"
    )

    trechos = resultado.get(
        "trechos",
        []
    )

    if not trechos:

        linhas.append(
            "Nenhum trecho longo com coincidência "
            "foi encontrado nas fontes comparáveis."
        )

    else:

        for item in trechos[:10]:

            linhas.append(
                f"**Fonte:** "
                f"{item.get('fonte', '')}"
            )

            linhas.append(
                f"**Trecho:** "
                f"{item.get('trecho', '')}"
            )

            linhas.append(
                f"**Palavras consecutivas:** "
                f"{item.get('quantidade_palavras', 0)}"
            )

            linhas.append("")

    # ========================================================
    # CITAÇÕES
    # ========================================================

    linhas.append(
        "## POSSÍVEIS CITAÇÕES A VERIFICAR"
    )

    citacoes = resultado.get(
        "citacoes",
        []
    )

    if not citacoes:

        linhas.append(
            "Nenhuma frase foi sinalizada automaticamente."
        )

    else:

        for frase in citacoes:

            linhas.append(
                f"- {frase}"
            )

    linhas.append("")

    # ========================================================
    # OBSERVAÇÃO
    # ========================================================

    linhas.append(
        "## OBSERVAÇÃO"
    )

    linhas.append(
        "Este relatório apresenta uma análise de "
        "similaridade em relação às fontes e textos "
        "disponíveis para comparação. "
        "Similaridade, isoladamente, não constitui "
        "uma conclusão definitiva de plágio."
    )

    return "\n".join(
        linhas
    )


# ============================================================
# 17. PARÁFRASE
# ============================================================

def construir_prompt_parafrase(
    trecho: str,
    referencia: str = ""
) -> str:

    return f"""
Reescreva o trecho abaixo com redação acadêmica
própria, clara e natural.

OBJETIVO:
Produzir uma paráfrase legítima.

REGRAS:

1. Preserve o significado.
2. Preserve fatos, números e resultados.
3. Não altere o sentido científico.
4. Não faça substituição mecânica de palavras.
5. Evite copiar a estrutura original.
6. Mantenha a necessidade de citação.
7. Não invente informações.
8. Não tente burlar detectores.

TRECHO ORIGINAL:

{trecho}

REFERÊNCIA:

{referencia}

FORMATO:

PARÁFRASE ACADÊMICA:
[texto]

OBSERVAÇÃO:
A ideia continua exigindo atribuição à fonte original.
"""


# ============================================================
# 18. COMPARAÇÃO ANTES/DEPOIS
# ============================================================

def comparar_antes_depois(
    texto_original: str,
    texto_revisado: str,
    fonte: str
) -> Dict[str, Any]:

    antes = calcular_similaridade(
        texto_original,
        fonte
    )

    depois = calcular_similaridade(
        texto_revisado,
        fonte
    )

    antes = round(
        antes,
        2
    )

    depois = round(
        depois,
        2
    )

    reducao = round(
        antes - depois,
        2
    )

    return {
        "antes":
            antes,

        "depois":
            depois,

        "reducao":
            reducao,

        "classificacao_antes":
            classificar_similaridade(
                antes
            ),

        "classificacao_depois":
            classificar_similaridade(
                depois
            )
    }


# ============================================================
# 19. FUNÇÃO PRINCIPAL
# ============================================================

def executar_analise_originalidade(
    texto: str,
    fontes: Optional[
        List[Dict[str, Any]]
    ] = None,
    consultar_pubmed: bool = False,
    consulta_pubmed: Optional[str] = None,
    max_resultados_pubmed: int = 5
) -> Dict[str, Any]:

    # ----------------------------------------
    # Fontes fornecidas manualmente
    # ----------------------------------------

    if fontes is not None:

        return analisar_originalidade(
            texto,
            fontes
        )

    # ----------------------------------------
    # Pesquisa PubMed direta
    # ----------------------------------------

    if consultar_pubmed:

        consulta = (
            consulta_pubmed
            if consulta_pubmed
            else
            "hypertension"
        )

        fontes_pubmed = (
            pesquisar_pubmed_direto(
                consulta,
                max_resultados_pubmed
            )
        )

        return analisar_originalidade(
            texto,
            fontes_pubmed
        )

    return analisar_originalidade(
        texto,
        []
    )


# ============================================================
# 20. TESTE LOCAL + PUBMED DIRETO
# ============================================================

if __name__ == "__main__":

    texto_teste = """
    Hypertension is a major cardiovascular risk factor
    associated with increased mortality and morbidity.
    """

    print("")
    print("=" * 60)
    print("TESTE DO MÓDULO ORIGINALIDADE ACADÊMICA")
    print("=" * 60)
    print("")

    # ========================================================
    # TESTE 1
    # ========================================================

    fonte_teste = {
        "titulo":
            "Fonte de teste",

        "texto":
            """
            Hypertension is a major cardiovascular
            risk factor associated with increased
            mortality and morbidity.
            """,

        "pmid":
            "",

        "doi":
            "",

        "link":
            ""
    }

    print(
        "[TESTE 1] "
        "Comparando com fonte local..."
    )

    resultado_local = (
        executar_analise_originalidade(
            texto_teste,
            fontes=[
                fonte_teste
            ]
        )
    )

    print(
        gerar_relatorio_originalidade(
            resultado_local
        )
    )

    # ========================================================
    # TESTE 2
    # ========================================================

    print("")
    print("=" * 60)
    print("TESTE 2 — PUBMED DIRETO + ABSTRACT")
    print("=" * 60)
    print("")

    resultado_pubmed = (
        executar_analise_originalidade(
            texto_teste,
            consultar_pubmed=True,
            consulta_pubmed="hypertension",
            max_resultados_pubmed=3
        )
    )

    print(
        gerar_relatorio_originalidade(
            resultado_pubmed
        )
    )