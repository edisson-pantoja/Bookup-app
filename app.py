
from flask import Flask, request, render_template_string, send_file
import google.generativeai as genai
from docx import Document
from io import BytesIO
import os

# --- 1. CONFIGURAÇÃO DA APLICAÇÃO FLASK E API ---
app = Flask(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- 2. HTML DA INTERFACE (EMBUTIDO DIRETAMENTE) ---
# Movido o HTML para dentro do Python para simplicidade, dispensando a pasta 'templates'.
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fábrica de Conhecimento CEO</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: #fff; padding: 2rem 3rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); text-align: center; max-width: 500px; width: 100%; }
        h1 { font-size: 1.5rem; color: #1c1e21; }
        h2 { font-size: 1.1rem; color: #606770; margin-bottom: 2rem; }
        input[type="text"] { width: 100%; padding: 0.8rem; margin-bottom: 1rem; border: 1px solid #dddfe2; border-radius: 6px; font-size: 1rem; }
        button { background-color: #1877f2; color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 6px; font-size: 1rem; cursor: pointer; transition: background-color: 0.3s; width: 100%; }
        button:hover { background-color: #166fe5; }
        .info { background-color: #e7f3ff; border-left: 5px solid #1877f2; padding: 1rem; margin: 1.5rem 0; text-align: left; font-size: 0.9rem; border-radius: 6px; }
        .footer { margin-top: 2rem; font-size: 0.8rem; color: #8a8d91; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏭 Fábrica de Conhecimento CEO</h1>
        <h2>Transformando livros em Dossiês Estratégicos</h2>
        <form action="/generate" method="post">
            <input type="text" name="livro" placeholder="Título do Livro (Ex: Gestão de Alta Performance)" required>
            <input type="text" name="autor" placeholder="Autor (Ex: Andrew Grove)">
            <div class="info">
                <strong>Estratégia:</strong> Masterclass de 24.000 palavras dividida em 4 Blocos Ontológicos.
            </div>
            <button type="submit">🚀 INICIAR EXTRAÇÃO DE ELITE</button>
        </form>
        <div class="footer">
            Desenvolvido para o Protocolo de Superpoder de Estudo CEO
        </div>
    </div>
</body>
</html>
'''

# --- 3. A LÓGICA DE GERAÇÃO (O ALGORITMO) ---
def gerar_bloco_estrategico(model, nome_livro, autor_livro, tema, indice):
    prompt = f'''
    [ROLE] Atue como uma Cientista Experimental e CEO Estrategista.
    [OBJETIVO] Escreva a PARTE {indice} de um Dossiê Técnico exaustivo sobre o livro '{nome_livro}' de '{autor_livro}'.
    [FOCO DO BLOCO] {tema}.
    
    [DIRETRIZES TÉCNICAS]
    1. EXTENSÃO: Mínimo de 6.000 palavras para este bloco. Seja prolixo na profundidade técnica.
    2. TOM: Executivo, analítico e focado em governança de alto nível.
    3. ESTRUTURA: Use títulos H2 e H3, listas de verificação, análise de causa e efeito e modelos mentais.
    4. CONTEÚDO: Não resuma. Explique o 'Como' e o 'Porquê'. Conecte com EBITDA, cultura e escalabilidade.
    5. IDIOMA: Português, mantendo termos técnicos em Inglês entre parênteses.
    '''
    response = model.generate_content(prompt)
    return response.text

# --- 4. ROTAS DA APLICAÇÃO WEB ---
@app.route('/')
def index():
    # Renderiza o HTML diretamente da string
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate_dossier():
    livro = request.form['livro']
    autor = request.form['autor']

    if not GEMINI_API_KEY:
        return "ERRO: Variável de ambiente 'GEMINI_API_KEY' não configurada no Vercel.", 500
    
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        doc = Document()
        doc.add_heading(f'DOSSIÊ EXECUTIVO: {livro}', 0)
        doc.add_paragraph(f"Autor: {autor if autor else 'Não informado'}")
        
        blocos = [
            "Engenharia de Sistemas e Tese Central Ontológica",
            "Mecanismos de Alavancagem e Casos de Estudo Reais",
            "Estratégias de Governança para Diretores e CEOs",
            "Protocolo de Implementação e Exercícios de Retenção (Cicatriz Sináptica)"
        ]
        
        for i, tema in enumerate(blocos):
            texto_bloco = gerar_bloco_estrategico(model, livro, autor, tema, i+1)
            doc.add_heading(f"Parte {i+1}: {tema}", level=1)
            doc.add_paragraph(texto_bloco)
            
        # Salva o documento em um buffer de memória
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        file_name = f"MASTERCLASS_{livro.replace(' ', '_')}.docx"

        # Envia o arquivo para download
        return send_file(
            buffer,
            as_attachment=True,
            download_name=file_name,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        return f"Erro Crítico no Sistema durante a geração: {e}", 500

# O Vercel gerencia a execução do app, então a linha abaixo não é estritamente necessária para o deploy,
# mas é útil para testes locais (executando 'python app.py').
if __name__ == "__main__":
    app.run(debug=True)
