
import json
import os
import time
from flask import Flask, Response, request, render_template_string
from openai import OpenAI

# --- 1. CONFIGURAÇÃO DA APLICAÇÃO FLASK E API ---
app = Flask(__name__)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 2. TEMPLATE HTML COM CÓDIGO FINAL E CORRIGIDO ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fábrica de Conhecimento CEO v5.0 (Final)</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.9.3/html2pdf.bundle.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; margin: 0; padding: 2rem; }
        .container { background: #fff; padding: 2rem 3rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); max-width: 800px; margin: auto; }
        h1, h3 { text-align: center; }
        h1 { font-size: 1.6rem; }
        h2 { font-size: 1.3rem; color: #1c1e21; margin-top: 1.5rem; border-bottom: 1px solid #dddfe2; padding-bottom: 0.5rem; }
        h3 { font-size: 1.1rem; color: #606770; margin-bottom: 2rem; }
        input[type="text"] { width: 100%; padding: 0.8rem; margin-bottom: 1rem; border: 1px solid #dddfe2; border-radius: 6px; font-size: 1rem; box-sizing: border-box; }
        button { background-color: #1877f2; color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 6px; font-size: 1rem; cursor: pointer; transition: background-color 0.3s, color 0.3s; width: 100%; }
        button:hover:not(:disabled) { background-color: #166fe5; }
        button:disabled { background-color: #dddfe2; color: #8a8d91; cursor: not-allowed; }
        .info { background-color: #e7f3ff; border-left: 5px solid #1877f2; padding: 1rem; margin: 1.5rem 0; text-align: left; font-size: 0.9rem; border-radius: 6px; }
        .footer { margin-top: 2rem; font-size: 0.8rem; color: #8a8d91; text-align: center; }
        #results { margin-top: 2rem; padding: 1.5rem; border-radius: 8px; background-color: #fafafa; border: 1px solid #dddfe2; min-height: 50px; white-space: pre-wrap; }
        #pdf-button { background-color: #42b72a; margin-top: 1rem; display: none; } 
        #pdf-button:hover:not(:disabled) { background-color: #36a420; }
        .placeholder { color: #8a8d91; font-style: italic; }
        .final-status { text-align: center; padding: 1rem; font-weight: bold; border-radius: 6px; margin-top: 1rem; }
        .success { color: #36a420; background-color: #eaf7e9; border: 1px solid #36a420; }
        .error { color: #fa383e; background-color: #feeef0; border: 1px solid #fa383e; }
        hr { border: 0; border-top: 1px solid #dddfe2; margin: 2rem 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏭 Fábrica de Conhecimento CEO</h1>
        <h3>Transformando livros em Dossiês Estratégicos</h3>
        
        <form id="generation-form" onsubmit="return false;">
            <input type="text" id="livro-input" placeholder="Título do Livro (Ex: Gestão de Alta Performance)" required>
            <input type="text" id="autor-input" placeholder="Autor (Ex: Andrew Grove)">
            <div class="info"><strong>Estratégia:</strong> O Dossiê será gerado em 4 blocos, exibidos em tempo real.</div>
            <button type="button" id="start-button" onclick="startGeneration()">🚀 INICIAR EXTRAÇÃO DE ELITE</button>
        </form>

        <div id="results"><p class="placeholder">O conteúdo do dossiê aparecerá aqui...</p></div>
        <button id="pdf-button" onclick="generatePdf()">📥 Gerar PDF do Conteúdo Acima</button>

        <div class="footer">Desenvolvido para o Protocolo de Superpoder de Estudo CEO</div>
    </div>

    <script>
        let eventSource = null;

        function startGeneration() {
            const startButton = document.getElementById('start-button');
            const livroInput = document.getElementById('livro-input');

            if (!livroInput.value) {
                alert("Por favor, insira o título do livro.");
                return;
            }

            startButton.disabled = true;
            startButton.textContent = 'Aguardando confirmação...';

            setTimeout(() => {
                if (!confirm("Você está prestes a iniciar a geração de um dossiê. Isso irá gerar custos com a API. Deseja continuar?")) {
                    startButton.disabled = false;
                    startButton.textContent = '🚀 INICIAR EXTRAÇÃO DE ELITE';
                    return;
                }
                startStreaming();
            }, 50); 
        }

        function startStreaming() {
            const startButton = document.getElementById('start-button');
            const pdfButton = document.getElementById('pdf-button');
            const resultsDiv = document.getElementById('results');
            const livroInput = document.getElementById('livro-input');
            const autorInput = document.getElementById('autor-input');

            startButton.textContent = 'Gerando... Por favor, aguarde.';
            resultsDiv.innerHTML = '<p class="placeholder">Conectando com a IA...</p>';
            pdfButton.style.display = 'none';
            
            const livro = encodeURIComponent(livroInput.value);
            const autor = encodeURIComponent(autorInput.value);
            const streamURL = `/stream-generate?livro=${livro}&autor=${autor}`;
            
            eventSource = new EventSource(streamURL);
            
            eventSource.onopen = function() {
                updateResults('');
            };

            eventSource.onmessage = function(e) {
                const data = JSON.parse(e.data);

                if (data.error) {
                    handleCompletion(`<div class="final-status error"><b>Erro:</b> ${data.error}</div>`, 'block', 'Tentar Novamente');
                    return;
                }
                if (data.status === 'complete') {
                    handleCompletion(`<div class="final-status success">${data.message}</div>`, 'block', '🚀 INICIAR NOVA EXTRAÇÃO');
                    return;
                }
                
                let currentContent = resultsDiv.innerHTML.replace(/<p class="placeholder">.*<\/p>/, "");
                currentContent += `<h2>Parte ${data.indice}: ${data.tema}</h2><div>${data.texto_bloco}</div><hr>`;
                
                let blockCounter = data.indice + 1;
                if (blockCounter <= 4) {
                    currentContent += `<p class="placeholder">Aguardando Bloco ${blockCounter}...</p>`;
                }
                updateResults(currentContent);
            };

            eventSource.onerror = function(e) {
                handleCompletion('<div class="final-status error"><b>Conexão perdida.</b> A geração foi interrompida.</div>', 'block', 'Tentar Novamente');
            };
        }

        function handleCompletion(message, pdfButtonDisplay, startButtonText) {
            const startButton = document.getElementById('start-button');
            const pdfButton = document.getElementById('pdf-button');
            const resultsDiv = document.getElementById('results');
            
            let finalContent = resultsDiv.innerHTML.replace(/<p class="placeholder">.*<\/p>/, "");
            finalContent += message;
            updateResults(finalContent);

            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            
            pdfButton.style.display = pdfButtonDisplay;
            startButton.disabled = false;
            startButton.textContent = startButtonText;
        }

        function updateResults(content) {
            document.getElementById('results').innerHTML = content;
        }

        function generatePdf() {
            const resultsDiv = document.getElementById('results');
            const livro = document.getElementById('livro-input').value || "dossie";
            const clonedResults = resultsDiv.cloneNode(true);
            clonedResults.querySelectorAll('.placeholder, .final-status').forEach(el => el.remove());

            const options = { margin: 1, filename: `DOSSIE_${livro.replace(/ /g, '_')}.pdf`, image: { type: 'jpeg', quality: 0.98 }, html2canvas: { scale: 2, useCORS: true }, jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' } };
            html2pdf().set(options).from(clonedResults).save();
        }
    </script>
</body>
</html>
'''

# --- 3. LÓGICA DE GERAÇÃO PYTHON (VALIDADA) ---
def gerar_bloco_estrategico(client, nome_livro, autor_livro, tema, indice):
    prompt = f'''
    [ROLE] Atue como uma Cientista Experimental e CEO Estrategista.
    [OBJETIVO] Escreva a PARTE {indice} de um Dossiê Técnico exaustivo sobre o livro '{nome_livro}' de '{autor_livro}'.
    [FOCO DO BLOCO] {tema}.
    
    [DIRETRIZES TÉCNICAS]
    1. EXTENSÃO: Gere um texto com aproximadamente 1.500 palavras para este bloco.
    2. TOM: Executivo, analítico e focado em governança de alto nível.
    3. ESTRUTURA: Use títulos H2 e H3, listas de verificação, análise de causa e efeito e modelos mentais.
    4. CONTEÚDO: Não resuma. Explique o 'Como' e o 'Porquê'. Conecte com EBITDA, cultura e escalabilidade.
    5. IDIOMA: Português, mantendo termos técnicos em Inglês entre parênteses.
    '''
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "Você é um assistente prestativo que escreve conteúdo técnico detalhado em português."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        # A API retorna o texto com quebras de linha literais (\n), que serão preservadas
        return response.choices[0].message.content
    except Exception as e:
        return f"ERRO_API: {str(e)}"

# --- 4. ROTAS DA APLICAÇÃO WEB (VALIDADAS) ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/stream-generate')
def stream_generate():
    livro = request.args.get('livro', 'Livro Desconhecido')
    autor = request.args.get('autor', 'Autor Desconhecido')

    if not DEEPSEEK_API_KEY:
        def error_stream():
            error_data = json.dumps({"error": "Variável de ambiente 'DEEPSEEK_API_KEY' não configurada."})
            yield f"data: {error_data}\n\n"
        return Response(error_stream(), mimetype='text/event-stream')

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
    
    blocos = [
        "Engenharia de Sistemas e Tese Central Ontológica",
        "Mecanismos de Alavancagem e Casos de Estudo Reais",
        "Estratégias de Governança para Diretores e CEOs",
        "Protocolo de Implementação e Exercícios de Retenção (Cicatriz Sináptica)"
    ]

    def generate():
        for i, tema in enumerate(blocos):
            texto_bloco = gerar_bloco_estrategico(client, livro, autor, tema, i + 1)
            
            if texto_bloco.startswith("ERRO_API:"):
                payload = json.dumps({"error": texto_bloco})
                yield f"data: {payload}\n\n"
                break
            else:
                # O JSON preserva as quebras de linha (\n). O CSS fará o trabalho de exibí-las.
                payload = json.dumps({"indice": i + 1, "tema": tema, "texto_bloco": texto_bloco})
                yield f"data: {payload}\n\n"
                time.sleep(1)
        else: 
            completion_message = json.dumps({"status": "complete", "message": "✅ Dossiê gerado completamente! Você já pode gerar o PDF."})
            yield f"data: {completion_message}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
