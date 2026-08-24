import os

# ============================================================
# CONFIGURAÇÃO
# ============================================================

p = r"C:\Users\TONNY\Documents\robo-academico\DocScriptaAI_Portatil\app.py"

if not os.path.exists(p):
    print("ERRO: O arquivo app.py não foi encontrado:")
    print(p)
    raise SystemExit(1)

# ============================================================
# LER O ARQUIVO CORRETAMENTE
# ============================================================

with open(p, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Arquivo carregado: {p}")
print(f"Total de linhas: {len(lines)}")

# ============================================================
# NOVO CABEÇALHO
# ============================================================

new_block = '''# ============================================================
# CABECALHO COM TONNYBOT
# ============================================================

_imagem_tonnybot = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "tonnybot.png"
)

_col_titulo, _col_robo = st.columns([3, 1])

with _col_titulo:
    st.title("📚 DocScripta AI")

    st.caption(
        "Assistente acadêmica para pesquisa, resolução, "
        "revisão, originalidade e análise de IA."
    )

    st.markdown(
        "<span style='font-size:0.8em;color:#888;'>"
        "criado por: Eristionny"
        "</span>",
        unsafe_allow_html=True
    )

with _col_robo:
    if os.path.exists(_imagem_tonnybot):
        st.image(_imagem_tonnybot, width=200)

'''

# ============================================================
# LOCALIZAR O CABEÇALHO ATUAL
# ============================================================

header_index = None

for i, line in enumerate(lines):
    if "CABECALHO COM TONNYBOT" in line:
        header_index = i
        break

# ============================================================
# SE NÃO ENCONTROU
# ============================================================

if header_index is None:
    print()
    print("ERRO: Não encontrei:")
    print("CABECALHO COM TONNYBOT")
    print()
    print("Nenhuma alteração foi feita.")
    raise SystemExit(1)

print(f"Cabeçalho encontrado na linha: {header_index + 1}")

# ============================================================
# ENCONTRAR O INÍCIO REAL DO BLOCO
# ============================================================

start_index = header_index

# Volta algumas linhas para pegar o separador =====
j = header_index - 1

while j >= 0:
    texto = lines[j].strip()

    if texto.startswith("# ==="):
        start_index = j
        break

    # Não subir demais
    if j < header_index - 10:
        break

    j -= 1

print(f"Início do bloco identificado na linha: {start_index + 1}")

# ============================================================
# ENCONTRAR O FINAL DO BLOCO
# ============================================================

end_index = None

# Primeiro procuramos "# ABAS"
for i in range(header_index + 1, len(lines)):
    texto = lines[i].strip()

    if texto == "# ABAS":
        end_index = i
        break

# Se não encontrou "# ABAS", procura a próxima seção
if end_index is None:
    for i in range(header_index + 1, len(lines)):
        texto = lines[i].strip()

        if (
            texto.startswith("# ===")
            and i > header_index + 3
        ):
            end_index = i
            break

# ============================================================
# SEGURANÇA
# ============================================================

if end_index is None:
    print()
    print("ERRO: Encontrei o cabeçalho, mas não consegui")
    print("identificar onde termina o bloco.")
    print()
    print("Nenhuma alteração foi feita.")
    raise SystemExit(1)

print(f"Fim do bloco identificado antes da linha: {end_index + 1}")

# ============================================================
# CRIAR BACKUP
# ============================================================

backup = p + ".backup"

with open(backup, "w", encoding="utf-8") as f:
    f.writelines(lines)

print()
print("Backup criado:")
print(backup)

# ============================================================
# SUBSTITUIR O BLOCO
# ============================================================

new_lines = []

# Parte anterior
new_lines.extend(lines[:start_index])

# Novo cabeçalho
new_lines.append(new_block)

# Parte posterior
new_lines.extend(lines[end_index:])

# ============================================================
# SALVAR
# ============================================================

with open(p, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

# ============================================================
# CONFERÊNCIA
# ============================================================

print()
print("==============================================")
print("ALTERAÇÃO CONCLUÍDA COM SUCESSO")
print("==============================================")
print()
print("Cabeçalho atualizado.")
print("TonnyBot: 200px")
print("Criado por: Eristionny")
print()
print("Backup:")
print(backup)
print()
print("Arquivo atualizado:")
print(p)
print()