
import json
import os
from flask import Flask, Response, request, render_template_string, jsonify
from openai import OpenAI

# --- 1. CONFIGURAÇÃO DA APLICAÇÃO FLASK E API ---
app = Flask(__name__)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 2. TEMPLATE HTML COM ARQUITETURA FINAL (MULTI-BOTÕES) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fábrica de Conhecimento CEO v6.0 (Final)</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.9.3/html2pdf.bundle.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; margin: 0; padding: 2rem; }
        .container { background: #fff; padding: 2rem 3rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); max-width: 800px; margin: auto; }
        h1, h3 { text-align: center; }
        h1 { font-size: 1.6rem; }
        h2 { font-size: 1.3rem; color: #1c1e21; margin-top: 1.5rem; border-bottom: 1px solid #dddfe2; padding-bottom: 0.5rem; }
        h3 { font-size: 1.1rem; color: #606770; margin-bottom: 2rem; }
        input[type="text"] { width: 100%; padding: 0.8rem; margin-bottom: 1rem; border: 1px solid #dddfe2; border-radius: 6px; font-size: 1rem; box-sizing: border-box; }
        
        .button-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1rem; }
        .block-button { background-color: #1877f2; color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 6px; font-size: 1rem; cursor: pointer; transition: background-color 0.3s; }
        .block-button:hover:not(:disabled) { background-color: #166fe5; }
        .block-button:disabled { background-color: #dddfe2; color: #8a8d91; cursor: not-allowed; }
        .block-button.completed { background-color: #36a420; }

        .info { background-color: #e7f3ff; border-left: 5px solid #1877f2; padding: 1rem; margin: 1.5rem 0; text-align: left; font-size: 0.9rem; border-radius: 6px; }
        .footer { margin-top: 2rem; font-size: 0.8rem; color: #8a8d91; text-align: center; }
        #results { margin-top: 1rem; }
        .block-container { page-break-inside: avoid; background-color: #fafafa; border: 1px solid #dddfe2; padding: 1.5rem; margin-top: 1rem; border-radius: 8px; }
        .block-container h2, .block-container div { page-break-inside: avoid; } /* Evita corte no PDF */
        .block-content { white-space: pre-wrap; word-wrap: break-word; } /* Preserva quebras de linha */

        #pdf-button { background-color: #e67e22; color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 6px; font-size: 1rem; cursor: pointer; transition: background-color 0.3s; width: 100%; margin-top: 1.5rem; display: none; } 
        #pdf-button:hover:not(:disabled) { background-color: #d35400; }
        .placeholder { color: #8a8d91; font-style: italic; text-align: center; padding: 2rem; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏭 Fábrica de Conhecimento CEO</h1>
        <h3>Transformando livros em Dossiês Estratégicos</h3>
        
        <input type="text" id="livro-input" placeholder="1. Título do Livro (Obrigatório)" required>
        <input type="text" id="autor-input" placeholder="2. Autor (Opcional)">
        
        <div class="info"><strong>Estratégia:</strong> Gere cada bloco do dossiê individualmente, na ordem que preferir.</div>
        
        <div class="button-grid">
            <button id="btn-block-1" class="block-button" onclick="generateBlock(1)">Gerar Bloco 1</button>
            <button id="btn-block-2" class="block-button" onclick="generateBlock(2)">Gerar Bloco 2</button>
            <button id="btn-block-3" class="block-button" onclick="generateBlock(3)">Gerar Bloco 3</button>
            <button id="btn-block-4" class="block-button" onclick="generateBlock(4)">Gerar Bloco 4</button>
        </div>

        <div id="results"><p class="placeholder">Os blocos gerados aparecerão aqui...</p></div>
        
        <button id="pdf-button" onclick="generatePdf()">📥 Gerar PDF do Dossiê</button>

        <div class="footer">Desenvolvido para o Protocolo de Superpoder de Estudo CEO</div>
    </div>

    <script>
        const blocosInfo = {
            1: "Engenharia de Sistemas e Tese Central Ontológica",
            2: "Mecanismos de Alavancagem e Casos de Estudo Reais",
            3: "Estratégias de Governança para Diretores e CEOs",
            4: "Protocolo de Implementação e Exercícios de Retenção"
        };

        async function generateBlock(blockNumber) {
            const livroInput = document.getElementById('livro-input');
            if (!livroInput.value) {
                alert("Por favor, insira o título do livro antes de gerar um bloco.");
                return;
            }

            const button = document.getElementById(`btn-block-${blockNumber}`);
            const autorInput = document.getElementById('autor-input');
            const resultsDiv = document.getElementById('results');
            const pdfButton = document.getElementById('pdf-button');

            button.disabled = true;
            button.textContent = "Gerando...";

            try {
                const response = await fetch('/generate-block', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        livro: livroInput.value,
                        autor: autorInput.value,
                        block_number: blockNumber
                    })
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || "Erro desconhecido no servidor.");
                }
                
                // Remove o placeholder se ele existir
                const placeholder = resultsDiv.querySelector('.placeholder');
                if (placeholder) placeholder.remove();

                // Cria o container para o novo bloco
                const blockContainer = document.createElement('div');
                blockContainer.className = 'block-container';
                blockContainer.id = `content-block-${blockNumber}`;

                const title = document.createElement('h2');
                title.textContent = `Parte ${data.indice}: ${data.tema}`;

                const content = document.createElement('div');
                content.className = 'block-content';
                content.textContent = data.texto_bloco;

                blockContainer.appendChild(title);
                blockContainer.appendChild(content);

                // Se já existir um bloco com esse ID, substitui. Senão, adiciona.
                const existingBlock = document.getElementById(blockContainer.id);
                if (existingBlock) {
                    resultsDiv.replaceChild(blockContainer, existingBlock);
                } else {
                    resultsDiv.appendChild(blockContainer);
                }

                button.textContent = `✅ Bloco ${blockNumber} Gerado`;
                button.classList.add('completed');
                pdfButton.style.display = 'block'; // Mostra o botão de PDF

            } catch (error) {
                alert(`Falha ao gerar o Bloco ${blockNumber}: ${error.message}`);
                button.disabled = false;
                button.textContent = `Gerar Bloco ${blockNumber}`;
            }
        }

        function generatePdf() {
            const resultsDiv = document.getElementById('results');
            const livro = document.getElementById('livro-input').value || "dossie";
            
            // Clona o elemento para não modificar o original
            const contentToPrint = resultsDiv.cloneNode(true);
            
            // Remove elementos que não devem aparecer no PDF (como o placeholder)
            const placeholder = contentToPrint.querySelector('.placeholder');
            if (placeholder) placeholder.remove();

            const options = {
                margin: 1,
                filename: `DOSSIE_${livro.replace(/ /g, '_')}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true },
                jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
            };

            html2pdf().set(options).from(contentToPrint).save();
        }
    </script>
</body>
</html>
'''

# --- 3. LÓGICA DE GERAÇÃO PYTHON (ROBUSTA) ---
def gerar_bloco_estrategico(client, nome_livro, autor_livro, tema, indice):
    prompt = f'''
    [ROLE] Atue como uma Cientista Experimental e CEO Estrategista.
    [OBJETIVO] Escreva a PARTE {indice} de um Dossiê Técnico exaustivo sobre o livro '{nome_livro}' de '{autor_livro}'.
    [FOCO DO BLOCO] {tema}.
    [DIRETRIZES TÉCNICAS]
    1. TOM: Executivo, analítico e focado em governança de alto nível.
    2. ESTRUTURA: Use parágrafos bem desenvolvidos. Não use markdown, apenas texto plano com quebras de linha.
    3. CONTEÚDO: Não resuma. Explique o 'Como' e o 'Porquê'. Conecte com EBITDA, cultura e escalabilidade.
    4. IDIOMA: Português, mantendo termos técnicos em Inglês entre parênteses.
    5. FOCO: Gere apenas o texto do bloco solicitado, sem introduções ou conclusões sobre o processo de geração.
    '''
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Você é um assistente que escreve conteúdo técnico detalhado em Português, usando apenas texto plano.",},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERRO_API: {str(e)}"

# --- 4. ROTAS DA APLICAÇÃO (ARQUITETURA FINAL) ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate-block', methods=['POST'])
def generate_block():
    data = request.get_json()
    livro = data.get('livro')
    autor = data.get('autor')
    block_number = data.get('block_number')

    if not all([livro, block_number]):
        return jsonify({"error": "Dados insuficientes (livro e block_number são obrigatórios)."}), 400

    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "Chave da API não configurada no servidor."}), 500

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
    
    blocos_temas = [
        "Engenharia de Sistemas e Tese Central Ontológica",
        "Mecanismos de Alavancagem e Casos de Estudo Reais",
        "Estratégias de Governança para Diretores e CEOs",
        "Protocolo de Implementação e Exercícios de Retenção (Cicatriz Sináptica)"
    ]

    if not 1 <= block_number <= len(blocos_temas):
        return jsonify({"error": "Número do bloco inválido."}), 400

    tema_escolhido = blocos_temas[block_number - 1]
    
    texto_gerado = gerar_bloco_estrategico(client, livro, autor, tema_escolhido, block_number)

    if texto_gerado.startswith("ERRO_API:"):
        return jsonify({"error": texto_gerado}), 500

    return jsonify({
        "indice": block_number,
        "tema": tema_escolhido,
        "texto_bloco": texto_gerado
    })

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
