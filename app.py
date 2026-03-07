
from flask import Flask, Response, request, render_template_string
from openai import OpenAI
from io import BytesIO
import os
import time
import json

# --- 1. CONFIGURAÇÃO DA APLICAÇÃO FLASK E API ---
app = Flask(__name__)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 2. HTML DA INTERFACE (EMBUTIDO DIRETAMENTE) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fábrica de Conhecimento CEO</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.9.3/html2pdf.bundle.min.js"></script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background-color: #f0f2f5; color: #1c1e21; margin: 0; padding: 2rem; }
        .container { background: #fff; padding: 2rem 3rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); max-width: 800px; margin: auto; }
        h1 { font-size: 1.5rem; color: #1c1e21; text-align: center; }
        h2 { font-size: 1.3rem; color: #1c1e21; margin-top: 1.5rem; border-bottom: 1px solid #dddfe2; padding-bottom: 0.5rem; }
        h3 { font-size: 1.1rem; color: #606770; margin-bottom: 2rem; text-align: center;}
        input[type="text"] { width: 100%; padding: 0.8rem; margin-bottom: 1rem; border: 1px solid #dddfe2; border-radius: 6px; font-size: 1rem; box-sizing: border-box; }
        button { background-color: #1877f2; color: white; border: none; padding: 0.8rem 1.5rem; border-radius: 6px; font-size: 1rem; cursor: pointer; transition: background-color 0.3s; width: 100%; }
        button:hover:not(:disabled) { background-color: #166fe5; }
        button:disabled { background-color: #a0bdf5; cursor: not-allowed; }
        .info { background-color: #e7f3ff; border-left: 5px solid #1877f2; padding: 1rem; margin: 1.5rem 0; text-align: left; font-size: 0.9rem; border-radius: 6px; }
        .footer { margin-top: 2rem; font-size: 0.8rem; color: #8a8d91; text-align: center; }
        #results { margin-top: 2rem; padding: 1.5rem; border-radius: 8px; background-color: #fafafa; border: 1px solid #dddfe2; }
        #pdf-button { background-color: #42b72a; margin-top: 1rem; display: none; } 
        #pdf-button:hover { background-color: #36a420; }
        .placeholder { color: #8a8d91; }
        .final-status { text-align: center; padding: 1rem; font-weight: bold; border-radius: 6px; margin-top: 1rem; }
        .success { color: #36a420; background-color: #eaf7e9; border: 1px solid #36a420; }
        .error { color: #fa383e; background-color: #feeef0; border: 1px solid #fa383e; }
    </style>
    <script>
        function startGeneration() { // Removido o 'event' que não é mais necessário aqui
            const form = document.getElementById('generation-form');
            const livro = form.querySelector('input[name="livro"]').value;
            const autor = form.querySelector('input[name="autor"]').value;
            const submitButton = form.querySelector('button[type="button"]');
            const resultsDiv = document.getElementById('results');
            const pdfButton = document.getElementById('pdf-button');

            if (!livro) {
                alert("Por favor, insira o título do livro.");
                return;
            }
            if (!confirm("Você está prestes a iniciar a geração de um dossiê, o que irá gerar custos com a API. Deseja continuar?")) {
                return;
            }

            submitButton.disabled = true;
            submitButton.textContent = 'Gerando... Por favor, aguarde.';
            resultsDiv.innerHTML = '<p class="placeholder">Aguardando o primeiro bloco da IA...</p>';
            pdfButton.style.display = 'none';

            const eventSource = new EventSource(`/stream-generate?livro=${encodeURIComponent(livro)}&autor=${encodeURIComponent(autor)}`);
            
            resultsDiv.innerHTML = ""; // Limpa o placeholder inicial

            eventSource.onmessage = function(e) {
                const data = JSON.parse(e.data);

                if (data.error) {
                    resultsDiv.innerHTML += `<div class="final-status error"><b>Erro:</b> ${data.error}</div>`;
                    eventSource.close();
                    submitButton.disabled = false;
                    submitButton.textContent = '🚀 INICIAR EXTRAÇÃO DE ELITE';
                    return;
                }

                if (data.status === 'complete') {
                    resultsDiv.innerHTML += `<div class="final-status success">${data.message}</div>`;
                    eventSource.close();
                    submitButton.disabled = false;
                    submitButton.textContent = '🚀 INICIAR NOVA EXTRAÇÃO';
                    pdfButton.style.display = 'block';
                    return;
                }
                
                resultsDiv.innerHTML += `<h2>Parte ${data.indice}: ${data.tema}</h2>`;
                resultsDiv.innerHTML += `<p>${data.texto_bloco.replace(/\n/g, '<br>')}</p><hr>`;
            };

            eventSource.onerror = function(e) {
                resultsDiv.innerHTML += '<div class="final-status error"><b>Conexão perdida.</b> A geração foi interrompida. O conteúdo gerado até agora está visível abaixo e pode ser salvo em PDF.</div>';
                eventSource.close();
                submitButton.disabled = false;
                submitButton.textContent = 'Tentar Novamente';
                pdfButton.style.display = 'block';
            };
        }

        function generatePdf() {
            const resultsDiv = document.getElementById('results');
            const livro = document.querySelector('input[name="livro"]').value || "dossie";
            const options = {
                margin:       1,
                filename:     `DOSSIE_${livro.replace(/ /g, '_')}.pdf`,
                image:        { type: 'jpeg', quality: 0.98 },
                html2canvas:  { scale: 2, useCORS: true },
                jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
            };
            html2pdf().set(options).from(resultsDiv).save();
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>🏭 Fábrica de Conhecimento CEO</h1>
        <h3>Transformando livros em Dossiês Estratégicos (Versão Streaming)</h3>
        <form id="generation-form">
            <input type="text" name="livro" placeholder="Título do Livro (Ex: Gestão de Alta Performance)" required>
            <input type="text" name="autor" placeholder="Autor (Ex: Andrew Grove)">
            <div class="info">
                <strong>Estratégia:</strong> O Dossiê será gerado em 4 blocos, exibidos em tempo real logo abaixo.
            </div>
            <button type="button" onclick="startGeneration()">🚀 INICIAR EXTRAÇÃO DE ELITE</button>
        </form>

        <div id="results">
            <p class="placeholder">O conteúdo do dossiê aparecerá aqui...</p>
        </div>

        <button id="pdf-button" onclick="generatePdf()">📥 Gerar PDF do Conteúdo Acima</button>

        <div class="footer">
            Desenvolvido para o Protocolo de Superpoder de Estudo CEO
        </div>
    </div>
</body>
</html>
'''

# --- 3. A LÓGICA DE GERAÇÃO (O ALGORITMO) ---
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
                {"role": "system", "content": "You are a helpful assistant that writes detailed technical content in Portuguese."},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao contatar a API da DeepSeek: {str(e)}"

# --- 4. ROTAS DA APLICAÇÃO WEB ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/stream-generate')
def stream_generate():
    livro = request.args.get('livro', 'Livro Desconhecido')
    autor = request.args.get('autor', 'Autor Desconhecido')

    if not DEEPSEEK_API_KEY:
        def error_stream():
            error_message = json.dumps({"error": "Variável de ambiente 'DEEPSEEK_API_KEY' não configurada."})
            yield f"data: {error_message}\n\n"
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
            
            if "Erro ao contatar a API" in texto_bloco:
                payload = json.dumps({"error": texto_bloco})
            else:
                payload = json.dumps({
                    "indice": i + 1,
                    "tema": tema,
                    "texto_bloco": texto_bloco
                })

            yield f"data: {payload}\n\n"
            time.sleep(1) 
            
            if "Erro ao contatar a API" in texto_bloco:
                break 
        else: 
            completion_message = json.dumps({"status": "complete", "message": "✅ Dossiê gerado completamente! Você já pode gerar o PDF."})
            yield f"data: {completion_message}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
