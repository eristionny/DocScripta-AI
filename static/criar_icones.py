from PIL import Image
import os

pasta = os.path.dirname(os.path.abspath(__file__))
origem = os.path.join(pasta, "tonnybot.png")

for tamanho, nome in [(192, "tonnybot-192.png"), (512, "tonnybot-512.png")]:
    img = Image.open(origem).convert("RGBA")
    img = img.resize((tamanho, tamanho), Image.LANCZOS)
    destino = os.path.join(pasta, nome)
    img.save(destino, "PNG")
    print(f"Criado: {destino}")

print("Pronto! Agora suba os 2 arquivos .png para a pasta static/ no GitHub")