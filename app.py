from flask import Flask, render_template, request, send_file
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resultado', methods=['POST'])
def resultado():
    nome_crianca = request.form.get("nome_crianca", "")
    nome_responsavel = request.form.get("nome_responsavel", "")
    nome_terapeuta = request.form.get("nome_terapeuta", "")

    scores = [int(request.form.get(f'q{i}', 0)) for i in range(1, 16)]
    total = sum(scores)
    interpretation = "Baixo" if total <= 15 else "Médio" if total <= 30 else "Alto"

    # Gerar gráfico de barras
    perguntas = [f'Pergunta {i}' for i in range(1, 16)]
    respostas = scores

    plt.figure(figsize=(10, 5))
    bars = plt.bar(perguntas, respostas, color='#007bff')
    plt.ylim(0, 3.5)
    plt.ylabel('Pontuação')
    plt.title('Avaliação das Respostas')
    plt.xticks(rotation=45, ha='right')
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom')

    img_buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(img_buffer, format='PNG')
    plt.close()
    img_buffer.seek(0)

    # Salvar imagem temporariamente para o FPDF
    with open("grafico_temp.png", "wb") as f:
        f.write(img_buffer.getbuffer())

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Relatório de Avaliação de Sinais de Autismo", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Criança/Adolescente: {nome_crianca}", ln=True)
    pdf.cell(200, 10, txt=f"Responsável: {nome_responsavel}", ln=True)
    if nome_terapeuta:
        pdf.cell(200, 10, txt=f"Terapeuta: {nome_terapeuta}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Pontuação total: {total}", ln=True)
    pdf.cell(200, 10, txt=f"Nível de risco: {interpretation}", ln=True)
    pdf.ln(10)

    # Inserir gráfico (usando imagem salva)
    pdf.image("grafico_temp.png", x=10, y=pdf.get_y(), w=190)
    pdf.ln(75)

    disclaimer = (
        "Este relatório não possui caráter avaliativo e não tem como finalidade substituir ou afirmar "
        "um diagnóstico de autismo. Ele serve apenas como uma forma de facilitar, ajudar e promover "
        "conscientização para pais e profissionais sobre sinais relacionados ao autismo.\n\n"
        "Em caso de dúvidas, procure um médico neurologista ou profissional de saúde qualificado."
    )

    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 7, disclaimer)
    pdf.ln(5)

    pdf.set_y(-15)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, txt="© 2025 BY: Vinícius Andrey", ln=True, align="C")

    output = BytesIO()
    pdf.output(output)
    output.seek(0)

    return send_file(output, download_name="relatorio_com_grafico.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
