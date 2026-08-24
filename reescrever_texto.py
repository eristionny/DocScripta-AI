from typing import Optional, Callable


TONS_DISPONIVEIS = {
    "academico": (
        "Use linguagem formal, acadêmica, precisa, objetiva "
        "e adequada a trabalhos universitários."
    ),
    "claro": (
        "Use linguagem simples, clara, direta e fácil "
        "de compreender, sem perder informações importantes."
    ),
    "conciso": (
        "Seja direto e objetivo, eliminando repetições "
        "sem remover informações essenciais."
    ),
    "criativo": (
        "Use linguagem rica, envolvente e expressiva, "
        "mantendo o significado e as informações originais."
    ),
    "profissional": (
        "Use linguagem profissional, sóbria, objetiva "
        "e adequada ao ambiente de trabalho."
    ),
}


NIVEIS_DISPONIVEIS = {
    "leve": (
        "Faça pequenas alterações na redação, mantendo "
        "a estrutura original o máximo possível."
    ),
    "medio": (
        "Reestruture frases e parágrafos, modificando "
        "a forma, mas preservando as ideias e informações."
    ),
    "forte": (
        "Reescreva amplamente o texto, modificando a estrutura "
        "e a redação, mas preservando integralmente o significado."
    ),
}


def _obter_motor_ia():

    try:
        from sintetizador import chamar_gemini
        return chamar_gemini

    except ImportError as erro:

        raise ImportError(
            "Não foi possível localizar a função "
            "chamar_gemini no sintetizador.py."
        ) from erro


def criar_prompt_reescrita(
    texto_original: str,
    tom: str = "academico",
    nivel: str = "medio"
) -> str:

    tom = tom.lower().strip()
    nivel = nivel.lower().strip()

    if tom not in TONS_DISPONIVEIS:
        raise ValueError(
            f"Tom inválido: {tom}. "
            f"Use: {', '.join(TONS_DISPONIVEIS)}"
        )

    if nivel not in NIVEIS_DISPONIVEIS:
        raise ValueError(
            f"Nível inválido: {nivel}. "
            f"Use: {', '.join(NIVEIS_DISPONIVEIS)}"
        )

    return f"""
Você é o módulo de REESCRITA DE TEXTO do DocScripta AI.

Reescreva o texto fornecido pelo usuário.

TOM:
{TONS_DISPONIVEIS[tom]}

NÍVEL:
{NIVEIS_DISPONIVEIS[nivel]}

REGRAS OBRIGATÓRIAS:

1. Preserve o significado original.
2. Preserve todas as informações importantes.
3. Não invente informações.
4. Não remova informações importantes.
5. Não altere nomes, instituições, lugares ou autores.
6. Não altere números, datas, valores ou porcentagens.
7. Não altere fórmulas ou dados técnicos.
8. Não altere citações ou referências.
9. Não invente fontes ou referências.
10. Corrija gramática, ortografia e pontuação.
11. Evite repetições desnecessárias.
12. Preserve o propósito original.
13. Entregue somente o texto reescrito.
14. Não explique o que foi alterado.

TEXTO ORIGINAL:
============================================================

{texto_original}

============================================================

TEXTO REESCRITO:
"""


def reescrever_texto(
    texto_original: str,
    tom: str = "academico",
    nivel: str = "medio",
    on_chunk: Optional[Callable] = None
):

    if not isinstance(texto_original, str):
        raise TypeError(
            "O texto original deve ser uma string."
        )

    texto_original = texto_original.strip()

    if not texto_original:
        raise ValueError(
            "O texto original está vazio."
        )

    prompt = criar_prompt_reescrita(
        texto_original,
        tom,
        nivel
    )

    chamar_gemini = _obter_motor_ia()

    resposta = chamar_gemini(
        prompt,
        modelo=None,
        max_tokens=max(
            1000,
            min(
                12000,
                len(texto_original.split()) * 8
            )
        ),
        usar_google_search=False,
        on_chunk=on_chunk
    )

    if not resposta:
        raise RuntimeError(
            "A IA não retornou um texto reescrito."
        )

    resposta = str(resposta).strip()

    return (
        resposta,
        prompt,
        "reescrita"
    )