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
from pathlib import Path

app = Flask(__name__)

WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
SOFFICE_PATH = r"C:\Program Files\LibreOffice\program\soffice.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
os.makedirs('gerados', exist_ok=True)

# === Função para converter documentos usando LibreOffice ===
def converter_docx_para_pdf(input_path, output_dir):
    try:
        result = subprocess.run([
            SOFFICE_PATH, '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_dir,
            input_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("stdout:", result.stdout)
        print("stderr:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print("Erro ao converter com LibreOffice:")
        print("stdout:", e.stdout)
        print("stderr:", e.stderr)
        return False

# === Rota para carregar apenas o formulário dinamicamente ===
@app.route('/gerar-formulario')
def gerar_formulario():
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

@app.route('/cadastro-modulo')
def cadastro_modulo():
    return render_template('cadastro_modulo.html')

@app.route('/cadastro-inversor')
def cadastro_inversor():
    return render_template('cadastro_inversor.html')

# === Rota principal: Painel ===
@app.route('/')
def painel():
    projetos = carregar_estrutura_projetos()
    return render_template("painel.html", projetos=projetos)

# === Rota que carrega apenas o conteúdo interno do painel ===
@app.route('/painel-conteudo')
def painel_conteudo():
    projetos = carregar_estrutura_projetos()
    return render_template("painel_conteudo.html", projetos=projetos)

# === Função para estruturar os projetos ===
def carregar_estrutura_projetos():
    projetos = {}
    base_path = Path('gerados')
    if not base_path.exists():
        return {}

    for estado_dir in base_path.iterdir():
        if estado_dir.is_dir():
            estado = estado_dir.name
            projetos[estado] = {}
            for cidade_dir in estado_dir.iterdir():
                if cidade_dir.is_dir():
                    cidade = cidade_dir.name
                    projetos[estado][cidade] = []
                    for cliente_dir in cidade_dir.iterdir():
                        if cliente_dir.is_dir():
                            cliente_nome = cliente_dir.name
                            arquivos = []
                            for arq in cliente_dir.iterdir():
                                if arq.is_file():
                                    arquivos.append({
                                        "nome": arq.name,
                                        "caminho": str(arq)
                                    })
                            projetos[estado][cidade].append({
                                "nome": cliente_nome,
                                "arquivos": arquivos
                            })
    return projetos

# === Rota para gerar documentos ===
@app.route('/gerar', methods=['POST'])
def gerar_tudo_zip():
    pass  # Substitua este pass pelo corpo completo da sua função atual de geração

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
