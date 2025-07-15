from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

SPREADSHEET_ID = "1JUv5wtErk51JcD7P8A8uEjfv6IZOWHnYUYl2AwxYluE"
SHEET_NAME = "Agenda"
API_KEY = "AIzaSyC2V1h6GwyJkvvovyZBAODcZTWhkWKjsnE"

def buscar_dados():
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{SHEET_NAME}?key={API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get("values", [])

def processar_dados(data, filtro_data=None):
    cabecalho = data[0]
    linhas = data[1:]

    fornecedores = {}
    total_paletes = 0
    total_fob = 0
    total_cif = 0

    for linha in linhas:
        item = dict(zip(cabecalho, linha))
        data_agendamento = item.get("Data", "")
        fornecedor = item.get("Fornecedor", "Desconhecido")
        tipo_frete = item.get("Frete", "").upper()
        qtd_paletes = int(item.get("Paletes", 0))

        if filtro_data and data_agendamento != filtro_data:
            continue

        total_paletes += qtd_paletes

        if tipo_frete == "FOB":
            total_fob += qtd_paletes
        elif tipo_frete == "CIF":
            total_cif += qtd_paletes

        if fornecedor not in fornecedores:
            fornecedores[fornecedor] = 0
        fornecedores[fornecedor] += qtd_paletes

    porcentagem_fob = round((total_fob / total_paletes) * 100, 1) if total_paletes else 0
    porcentagem_cif = round((total_cif / total_paletes) * 100, 1) if total_paletes else 0

    return fornecedores, total_paletes, porcentagem_fob, porcentagem_cif

@app.route("/", methods=["GET", "POST"])
def index():
    hoje = datetime.now().strftime("%d/%m/%Y")
    filtro_data = request.form.get("data", hoje)

    dados = buscar_dados()
    fornecedores, total_paletes, fob_pct, cif_pct = processar_dados(dados, filtro_data)

    return render_template("dashboard.html",
                           data=filtro_data,
                           fornecedores=fornecedores,
                           total_paletes=total_paletes,
                           fob_pct=fob_pct,
                           cif_pct=cif_pct)

if __name__ == "__main__":
    app.run(debug=True)
