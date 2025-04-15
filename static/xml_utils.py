import xml.etree.ElementTree as ET
import os

XML_PATH = 'static/dados_padrao.xml'

def carregar_xml():
    if not os.path.exists(XML_PATH):
        root = ET.Element("dados")
        ET.SubElement(root, "modulos")
        ET.SubElement(root, "inversores")
        ET.ElementTree(root).write(XML_PATH, encoding='utf-8', xml_declaration=True)
    tree = ET.parse(XML_PATH)
    return tree, tree.getroot()

def adicionar_modulo(fabricante, modelo, potencia):
    tree, root = carregar_xml()
    modulos = root.find('modulos')

    for m in modulos.findall('modulo'):
        if (m.findtext('fabricante') == fabricante and
            m.findtext('modelo') == modelo and
            m.findtext('potencia') == potencia):
            return  # Já existe

    novo = ET.SubElement(modulos, 'modulo')
    ET.SubElement(novo, 'fabricante').text = fabricante
    ET.SubElement(novo, 'modelo').text = modelo
    ET.SubElement(novo, 'potencia').text = potencia
    tree.write(XML_PATH, encoding='utf-8', xml_declaration=True)

def adicionar_inversor(fabricante, modelo, potencia):
    tree, root = carregar_xml()
    inversores = root.find('inversores')

    for i in inversores.findall('inversor'):
        if (i.findtext('fabricante') == fabricante and
            i.findtext('modelo') == modelo and
            i.findtext('potencia') == potencia):
            return  # Já existe

    novo = ET.SubElement(inversores, 'inversor')
    ET.SubElement(novo, 'fabricante').text = fabricante
    ET.SubElement(novo, 'modelo').text = modelo
    ET.SubElement(novo, 'potencia').text = potencia
    tree.write(XML_PATH, encoding='utf-8', xml_declaration=True)
