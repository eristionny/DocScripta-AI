import os
import sys
import json
import urllib.request

# ============================================================
# GERADOR DO TONNYBOT (DocScripta AI) - CONEXÃO DIRETA API
# ============================================================

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("\nERRO: A variável GEMINI_API_KEY não foi encontrada.")
    print("Execute no CMD: set GEMINI_API_KEY=SUA_CHAVE_AQUI\n")
    sys.exit(1)

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_RAIZ = os.path.join(PASTA_PROJETO, "tonnybot.png")
PASTA_PATCH = os.path.join(PASTA_PROJETO, "patch_tonnybot4")
ARQUIVO_PATCH = os.path.join(PASTA_PATCH, "tonnybot.png")

PROMPT = """
A high-quality 3D digital illustration of TONNYBOT, a friendly academic robot mascot hovering directly above an open book, centered on a pure solid white background.

ROBOT DESIGN:
- A cute, futuristic white robot with a round head and smooth metallic body.
- Expressive black digital screen face with a happy, friendly glowing white smile and eyes.
- Wearing a black graduation cap (capelo) with a golden tassel hanging on the side.
- On its chest, a circular golden emblem badge with the text "TONNYBOT" engraved.
- Small rounded arms and legs hovering gracefully.

BOOK DESIGN:
- Positioned directly underneath the floating robot.
- A modern open academic book with a blue hardcover base.
- Clean white, slightly curved paper pages spread open wide.

COMPOSITION & RENDER:
- Perfectly centered composition on a clean, pure white canvas with no shadows or background details.
- Crisp Pixar or DreamWorks studio 3D render style with soft studio lighting.
- High resolution, bright colors, smooth glossy textures, polished aesthetic.
- No surrounding elements, no UI frames, no background scenes, no additional text outside the chest badge.
"""

print("\n==============================================")
print("        GERADOR DO TONNYBOT (DocScripta AI)")
print("==============================================\n")
print("Conectando à API Imagen 3...")

# URL oficial da REST API do Imagen 3
url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={API_KEY}"

payload = {
    "instances": [
        {"prompt": PROMPT}
    ],
    "parameters": {
        "sampleCount": 1,
        "aspectRatio": "1:1",
        "outputMimeType": "image/png"
    }
}

headers = {"Content-Type": "application/json"}

try:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode("utf-8"))

    # Extrai o base64 da imagem retornado pela API
    import base64
    image_b64 = result["predictions"][0]["bytesBase64Encoded"]
    image_bytes = base64.b64decode(image_b64)

    # Salva o arquivo na raiz
    with open(ARQUIVO_RAIZ, "wb") as f:
        f.write(image_bytes)

    # Salva também dentro da pasta patch_tonnybot4 se ela existir
    if os.path.exists(PASTA_PATCH):
        with open(ARQUIVO_PATCH, "wb") as f:
            f.write(image_bytes)

    print("\n==============================================")
    print("       TONNYBOT GERADO COM SUCESSO!")
    print("==============================================")
    print(f"Imagem salva em: {ARQUIVO_RAIZ}\n")

except urllib.error.HTTPError as e:
    err_body = e.read().decode("utf-8")
    print(f"\nERRO HTTP {e.code}: {err_body}\n")
except Exception as e:
    print(f"\nERRO AO GERAR A IMAGEM: {str(e)}\n")
