import zipfile
import os
from datetime import datetime
from babel.dates import format_date

# Dados simulados (normalmente vindos do formulário Flask)
dados = {
    "nome": "Rosana de Fátima Menezes",
    "cpf": "446.790.168-09",
    "uc": "5555",
    "endereco": "Praça Rui Barbosa, 3730",
    "cidade": "Mineiros",
    "uf": "GO",
    "cep": "75830112",
    "mod_pot_total": "9.90",
    "inv_pot_total": "10.00",
    "pot_utilizada": "9.90",
    "responsavel_nome": "João Técnico",
    "responsavel_email": "joao@email.com",
    "responsavel_tel": "(17) 99999-9999",
}

# Formata data final
data_local = f"{dados['cidade']}-{dados['uf']} {format_date(datetime.today(), format='d ' 'de' ' MMMM ' 'de' ' y', locale='pt_BR')}"

# Carrega o document.xml do .docx
with zipfile.ZipFile("anexo_e1_template.docx", 'r') as zin:
    zin.extractall("temp_docx")

# Lê o conteúdo XML do documento
doc_path = os.path.join("temp_docx", "word", "document.xml")
with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Substituições dinâmicas por padrão textual
content = content.replace("Informar nome do consumidor", dados["nome"])
content = content.replace("000.000.000-00", dados["cpf"])
content = content.replace("0000", dados["uc"])
content = content.replace("Endereço do consumidor", dados["endereco"])
content = content.replace("Cidade/UF", f"{dados['cidade']}-{dados['uf']}")
content = content.replace("9999", dados["mod_pot_total"])
content = content.replace("8888", dados["inv_pot_total"])
content = content.replace("7777", dados["pot_utilizada"])
content = content.replace("Nome do responsável", dados["responsavel_nome"])
content = content.replace("email@responsavel.com", dados["responsavel_email"])
content = content.replace("(00) 00000-0000", dados["responsavel_tel"])
content = content.replace("Clique ou toque aqui para inserir uma data", data_local)

# Sobrescreve o document.xml com conteúdo editado
with open(doc_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Recompacta novo .docx com as alterações
saida_path = "gerados/anexo_e1_editado.docx"
with zipfile.ZipFile(saida_path, 'w', zipfile.ZIP_DEFLATED) as zout:
    for foldername, subfolders, filenames in os.walk("temp_docx"):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            arcname = os.path.relpath(file_path, "temp_docx")
            zout.write(file_path, arcname)

print(f"Arquivo gerado com sucesso em: {saida_path}")
