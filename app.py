from flask import Flask, render_template, request, send_file
from datetime import datetime
import pdfkit
import os
import requests
import xml.etree.ElementTree as ET
from babel.dates import format_date
import zipfile
import io
import shutil
import subprocess
from static.xml_utils import adicionar_modulo, adicionar_inversor
from static.utils_excel import preencher_anexo_f

app = Flask(__name__)

WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
os.makedirs('gerados', exist_ok=True)

def converter_docx_para_pdf(input_path, output_dir):
    try:
        subprocess.run([
            SOFFICE_PATH, '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            input_path
        ], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print("Erro ao converter com LibreOffice:", e)
        return False

@app.route('/')
def formulario():
    modulos, inversores = [], []
    try:
        tree = ET.parse('static/dados_padrao.xml')
        root = tree.getroot()
        for m in root.findall('./modulos/modulo'):
            modulos.append({k: m.findtext(k) for k in ('fabricante', 'modelo', 'potencia')})
        for i in root.findall('./inversores/inversor'):
            inversores.append({k: i.findtext(k) for k in ('fabricante', 'modelo', 'potencia')})
    except Exception as e:
        print(f"Erro ao carregar XML: {e}")
    return render_template('form.html', modulos=modulos, inversores=inversores)

@app.route('/gerar', methods=['POST'])
def gerar_tudo_zip():
    nome = request.form['nome']
    cpf = request.form['cpf_cnpj']
    telefone = request.form['telefone']
    email = request.form['email']
    cep = request.form['cep'].replace("-", "").strip()
    numero = request.form['numero']
    endereco = request.form['endereco']
    cidade_form = request.form['cidade']
    uc = request.form['codigo_uc']
    latitude = request.form.get('latitude', '')
    longitude = request.form.get('longitude', '')
    data_operacao = request.form.get('data_operacao', '')
    padrao = request.form.get('padrao_cpfl', '')
    forma_conexao = request.form.get('forma_conexao', '')
    qtd_modulos = int(request.form['mod_quantidade'])
    qtd_inversores = int(request.form['inv_quantidade'])

    mod_novo_fabricante = request.form.get('mod_novo_fabricante', '').strip()
    mod_novo_modelo = request.form.get('mod_novo_modelo', '').strip()
    mod_novo_potencia = request.form.get('mod_novo_potencia', '').strip()

    if mod_novo_fabricante and mod_novo_modelo and mod_novo_potencia:
        mod_fabricante = mod_novo_fabricante
        mod_modelo = mod_novo_modelo
        pot_modulo = float(mod_novo_potencia)
        adicionar_modulo(mod_fabricante, mod_modelo, str(pot_modulo))
    else:
        mod_fabricante, mod_modelo, pot_modulo = request.form['modulo_escolhido'].split('|')
        pot_modulo = float(pot_modulo)

    inv_novo_fabricante = request.form.get('inv_novo_fabricante', '').strip()
    inv_novo_modelo = request.form.get('inv_novo_modelo', '').strip()
    inv_novo_potencia = request.form.get('inv_novo_potencia', '').strip()

    if inv_novo_fabricante and inv_novo_modelo and inv_novo_potencia:
        inv_fabricante = inv_novo_fabricante
        inv_modelo = inv_novo_modelo
        pot_inversor = float(inv_novo_potencia)
        adicionar_inversor(inv_fabricante, inv_modelo, str(pot_inversor))
    else:
        inv_fabricante, inv_modelo, pot_inversor = request.form['inversor_escolhido'].split('|')
        pot_inversor = float(pot_inversor)

    try:
        via_cep = requests.get(f'https://viacep.com.br/ws/{cep}/json/').json()
        cidade = via_cep.get("localidade", cidade_form)
        uf = via_cep.get("uf", "XX")
    except:
        cidade, uf = cidade_form, "XX"

    cep_formatado = f"{cep[:5]}-{cep[5:]}" if len(cep) == 8 else cep
    endereco_uc = f"{endereco}, {numero}, {cidade}-{uf} – {cep_formatado}"
    data_formatada = format_date(datetime.today(), format="d 'de' MMMM 'de' y", locale='pt_BR')
    potencia_modulos = round((qtd_modulos * pot_modulo) / 1000, 2)
    potencia_inversores = round((qtd_inversores * pot_inversor) / 1000, 2)
    potencia_utilizada = min(potencia_modulos, potencia_inversores)

    try:
        tree = ET.parse('responsavel.xml')
        root = tree.getroot()
        responsavel_nome = root.findtext('nome', 'NOME TÉCNICO')
        responsavel_email = root.findtext('email', 'email@dominio.com')
        responsavel_telefone = root.findtext('telefone', '(00) 00000-0000')
    except:
        responsavel_nome = "NOME TÉCNICO"
        responsavel_email = "email@dominio.com"
        responsavel_telefone = "(00) 00000-0000"

    html_proc = render_template("modelo_procuracao.html",
        nome=nome, cpf=cpf, endereco=endereco, endereco_uc=endereco_uc,
        cidade=cidade, uc=uc, data=f"{cidade}-{uf} {data_formatada}",
        logo_path=os.path.abspath("static/logo.png")
    )
    proc_path = "gerados/procuracao.pdf"
    pdfkit.from_string(html_proc, proc_path, configuration=config, options={'enable-local-file-access': None, 'quiet': ''})

    # === GERA ANEXO E.1 ===
    template_odt = "modelos/anexo_e1_template.odt"
    temp_dir = "temp_anexo"
    os.makedirs(temp_dir, exist_ok=True)
    with zipfile.ZipFile(template_odt, 'r') as zin:
        zin.extractall(temp_dir)
    content_path = os.path.join(temp_dir, "content.xml")
    with open(content_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = (content
        .replace("#UC", uc)
        .replace("#KW", str(potencia_utilizada))
        .replace("#FABINV", inv_fabricante)
        .replace("#MODINV", inv_modelo)
        .replace("#QNTINV", str(qtd_inversores))
        .replace("#POTTOTAL", f"{potencia_inversores} kW")
        .replace("#NOMETEC", responsavel_nome)
        .replace("#CONTATOTEC", f"{responsavel_telefone} / {responsavel_email}")
        .replace("#LOCAL", f"{cidade}-{uf}")
        .replace("#DATA", data_formatada)
    )
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(content)
    docx_out = "gerados/anexo_e1_editado.docx"
    with zipfile.ZipFile(docx_out, 'w') as zout:
        for root_dir, _, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root_dir, file)
                arcname = os.path.relpath(full_path, temp_dir)
                zout.write(full_path, arcname)
    shutil.rmtree(temp_dir)
    pdf_e1 = "gerados/anexo_e1_editado.pdf"
    if not converter_docx_para_pdf(docx_out, "gerados") or not os.path.exists(pdf_e1):
        return "Erro ao converter Anexo E.1 com LibreOffice", 500

    # === GERA ANEXO F (.xlsx) ===
    anexo_f_saida = "gerados/anexo_f_preenchido.xlsx"
    preencher_anexo_f(
        modelo_path='modelos/anexo_f_modelo.xlsx',
        saida_path=anexo_f_saida,
        nome=nome,
        cpf=cpf,
        telefone=telefone,
        email=email,
        endereco=f"{endereco}, {numero}",
        cidade=cidade,
        latitude=latitude,
        longitude=longitude,
        data_operacao=data_operacao,
        qnt_mod=str(qtd_modulos),
        fab_mod=mod_fabricante,
        qnt_inv=str(qtd_inversores),
        fab_inv=inv_fabricante,
        mod_inv=inv_modelo,
        pot_mod=str(pot_modulo),
        pot_inv=str(pot_inversor),
        pot_total=str(potencia_utilizada),
        padrao=padrao,
        forma_conexao=forma_conexao
    )
    pdf_anexo_f = "gerados/anexo_f_preenchido.pdf"
    if not converter_docx_para_pdf(anexo_f_saida, "gerados") or not os.path.exists(pdf_anexo_f):
        return "Erro ao converter Anexo F com LibreOffice", 500

    # === ZIP FINAL ===
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        zipf.write(proc_path, arcname="procuracao.pdf")
        zipf.write(pdf_e1, arcname="anexo_e1.pdf")
        zipf.write(pdf_anexo_f, arcname="anexo_f.pdf")
        zipf.write(anexo_f_saida, arcname="anexo_f.xlsx")
    zip_buffer.seek(0)

    nome_cliente = nome.lower().strip().replace(" ", "_")
    return send_file(zip_buffer, as_attachment=True,
        download_name=f"{nome_cliente}_cpfl.zip", mimetype="application/zip")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
