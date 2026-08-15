
import json
import os
import io
from flask import Flask, request, render_template_string, jsonify, send_file
from openai import OpenAI
from docx import Document

# --- 1. CONFIGURAÇÃO DA APLICAÇÃO FLASK E API ---
app = Flask(__name__)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 2. TEMPLATE HTML MULTILÍNGUE ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fábrica de Conhecimento CEO</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f0f2f5;
            color: #1c1e21;
            padding: 2rem 1rem;
        }
        .page-header {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            max-width: 800px;
            margin: 0 auto 1rem auto;
        }
        .lang-selector-wrapper {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: #fff;
            border: 1px solid #dddfe2;
            border-radius: 8px;
            padding: 0.4rem 0.8rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        }
        .lang-selector-wrapper span { font-size: 1.1rem; }
        .lang-selector-wrapper select {
            border: none;
            outline: none;
            font-size: 0.9rem;
            font-weight: 600;
            color: #1c1e21;
            background: transparent;
            cursor: pointer;
        }
        .container {
            background: #fff;
            padding: 2rem 3rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            max-width: 800px;
            margin: auto;
        }
        h1, h3 { text-align: center; }
        h1 { font-size: 1.6rem; margin-bottom: 0.3rem; }
        h2 { font-size: 1.3rem; color: #1c1e21; margin-top: 1.5rem; border-bottom: 1px solid #dddfe2; padding-bottom: 0.5rem; }
        h3 { font-size: 1.05rem; color: #606770; margin-bottom: 2rem; }
        input[type="text"] {
            width: 100%;
            padding: 0.8rem;
            margin-bottom: 1rem;
            border: 1px solid #dddfe2;
            border-radius: 6px;
            font-size: 1rem;
        }
        .button-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        .block-button {
            background-color: #1877f2;
            color: white;
            border: none;
            padding: 0.8rem;
            border-radius: 6px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .block-button:hover:not(:disabled) { background-color: #166fe5; }
        .block-button:disabled { background-color: #dddfe2; color: #8a8d91; cursor: not-allowed; }
        .block-button.completed { background-color: #36a420; }

        .info {
            background-color: #e7f3ff;
            border-left: 5px solid #1877f2;
            padding: 1rem;
            margin: 1.5rem 0;
            text-align: left;
            font-size: 0.9rem;
            border-radius: 6px;
        }
        .footer { margin-top: 2rem; font-size: 0.8rem; color: #8a8d91; text-align: center; }
        #results { margin-top: 1rem; }
        .block-container {
            background-color: #fafafa;
            border: 1px solid #dddfe2;
            padding: 1.5rem;
            margin-top: 1rem;
            border-radius: 8px;
        }
        .block-content { white-space: pre-wrap; word-wrap: break-word; line-height: 1.7; }

        #docx-button {
            background-color: #34495e;
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 6px;
            font-size: 1rem;
            cursor: pointer;
            transition: background-color 0.3s;
            width: 100%;
            margin-top: 1.5rem;
            display: none;
        }
        #docx-button:hover:not(:disabled) { background-color: #2c3e50; }

        #kindle-instructions {
            background-color: #fdf9e4;
            border-left: 5px solid #f1c40f;
            padding: 1rem;
            margin-top: 1rem;
            font-size: 0.9rem;
            border-radius: 6px;
            display: none;
        }
        #kindle-instructions ol { margin-top: 0.5rem; padding-left: 1.5rem; }
        #kindle-instructions li { margin-bottom: 0.3rem; }

        .placeholder { color: #8a8d91; font-style: italic; text-align: center; padding: 2rem; }

        @media (max-width: 600px) {
            .container { padding: 1.5rem 1.2rem; }
            .button-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <div class="page-header">
        <div class="lang-selector-wrapper">
            <span>🌐</span>
            <select id="lang-select" onchange="applyLanguage(this.value)">
                <option value="pt">Português</option>
                <option value="en">English</option>
                <option value="es">Español</option>
            </select>
        </div>
    </div>

    <div class="container">
        <h1>🏭 <span data-i18n="title"></span></h1>
        <h3 data-i18n="subtitle"></h3>

        <input type="text" id="livro-input" data-i18n-placeholder="placeholder_book">
        <input type="text" id="autor-input" data-i18n-placeholder="placeholder_author">

        <div class="info"><strong data-i18n="info_label"></strong> <span data-i18n="info_text"></span></div>

        <div class="button-grid">
            <button id="btn-block-1" class="block-button" onclick="generateBlock(1)" data-i18n="btn_block_1"></button>
            <button id="btn-block-2" class="block-button" onclick="generateBlock(2)" data-i18n="btn_block_2"></button>
            <button id="btn-block-3" class="block-button" onclick="generateBlock(3)" data-i18n="btn_block_3"></button>
            <button id="btn-block-4" class="block-button" onclick="generateBlock(4)" data-i18n="btn_block_4"></button>
        </div>

        <div id="results"><p class="placeholder" data-i18n="placeholder_results"></p></div>

        <button id="docx-button" onclick="generateDocx()" data-i18n="btn_docx"></button>

        <div id="kindle-instructions">
            <strong data-i18n="kindle_title"></strong>
            <ol>
                <li data-i18n="kindle_step1"></li>
                <li data-i18n="kindle_step2"></li>
                <li data-i18n="kindle_step3"></li>
            </ol>
            <small data-i18n="kindle_note"></small>
        </div>

        <div class="footer" data-i18n="footer"></div>
    </div>

    <script>
        const TRANSLATIONS = {
            pt: {
                title: "Fábrica de Conhecimento CEO",
                subtitle: "Transformando livros em Dossiês Estratégicos para Executivos",
                placeholder_book: "1. Título do Livro (Obrigatório)",
                placeholder_author: "2. Autor (Opcional)",
                info_label: "Estratégia:",
                info_text: "Gere cada bloco do dossiê individualmente, na ordem que preferir.",
                btn_block_1: "Bloco 1 – Tese Central e Visão Geral",
                btn_block_2: "Bloco 2 – Exemplos e Alavancagem",
                btn_block_3: "Bloco 3 – Liderança e Governança",
                btn_block_4: "Bloco 4 – Plano de Ação e Retenção",
                placeholder_results: "Os blocos gerados aparecerão aqui...",
                btn_docx: "📥 Baixar Word (.docx)",
                btn_generating: "Gerando...",
                btn_done: "✅ Bloco {n} Gerado",
                btn_retry: "Gerar Bloco {n}",
                kindle_title: "Para enviar ao Kindle:",
                kindle_step1: "Baixe o arquivo .docx clicando no botão acima.",
                kindle_step2: "Abra seu e-mail e anexe o arquivo que você baixou.",
                kindle_step3: 'Envie para seu endereço Kindle (ex: seunome@kindle.com).',
                kindle_note: 'Você pode encontrar seu endereço Kindle na página "Gerencie seu conteúdo e dispositivos" na Amazon.',
                footer: "Desenvolvido para o Protocolo de Superpoder de Estudo CEO",
                alert_no_book: "Por favor, insira o título do livro antes de gerar um bloco.",
                alert_fail: "Falha ao gerar o Bloco {n}: {msg}",
                alert_fail_docx: "Falha ao gerar o arquivo: {msg}",
                btn_docx_generating: "Gerando .docx...",
            },
            en: {
                title: "CEO Knowledge Factory",
                subtitle: "Turning Books into Strategic Dossiers for Executives",
                placeholder_book: "1. Book Title (Required)",
                placeholder_author: "2. Author (Optional)",
                info_label: "Strategy:",
                info_text: "Generate each dossier block individually, in any order you prefer.",
                btn_block_1: "Block 1 – Core Thesis & Overview",
                btn_block_2: "Block 2 – Examples & Leverage",
                btn_block_3: "Block 3 – Leadership & Governance",
                btn_block_4: "Block 4 – Action Plan & Retention",
                placeholder_results: "Generated blocks will appear here...",
                btn_docx: "📥 Download Word (.docx)",
                btn_generating: "Generating...",
                btn_done: "✅ Block {n} Generated",
                btn_retry: "Generate Block {n}",
                kindle_title: "To send to Kindle:",
                kindle_step1: "Download the .docx file by clicking the button above.",
                kindle_step2: "Open your email and attach the downloaded file.",
                kindle_step3: "Send it to your Kindle address (e.g.: yourname@kindle.com).",
                kindle_note: 'You can find your Kindle address on the "Manage Your Content and Devices" page on Amazon.',
                footer: "Built for the CEO Study Superpower Protocol",
                alert_no_book: "Please enter the book title before generating a block.",
                alert_fail: "Failed to generate Block {n}: {msg}",
                alert_fail_docx: "Failed to generate file: {msg}",
                btn_docx_generating: "Generating .docx...",
            },
            es: {
                title: "Fábrica de Conocimiento CEO",
                subtitle: "Convirtiendo libros en Dossieres Estratégicos para Ejecutivos",
                placeholder_book: "1. Título del Libro (Obligatorio)",
                placeholder_author: "2. Autor (Opcional)",
                info_label: "Estrategia:",
                info_text: "Genera cada bloque del dossier individualmente, en el orden que prefieras.",
                btn_block_1: "Bloque 1 – Tesis Central y Visión General",
                btn_block_2: "Bloque 2 – Ejemplos y Apalancamiento",
                btn_block_3: "Bloque 3 – Liderazgo y Gobernanza",
                btn_block_4: "Bloque 4 – Plan de Acción y Retención",
                placeholder_results: "Los bloques generados aparecerán aquí...",
                btn_docx: "📥 Descargar Word (.docx)",
                btn_generating: "Generando...",
                btn_done: "✅ Bloque {n} Generado",
                btn_retry: "Generar Bloque {n}",
                kindle_title: "Para enviar al Kindle:",
                kindle_step1: "Descarga el archivo .docx haciendo clic en el botón de arriba.",
                kindle_step2: "Abre tu correo electrónico y adjunta el archivo descargado.",
                kindle_step3: "Envíalo a tu dirección Kindle (ej: tunombre@kindle.com).",
                kindle_note: 'Puedes encontrar tu dirección Kindle en la página "Administra tu contenido y dispositivos" en Amazon.',
                footer: "Desarrollado para el Protocolo de Superpoder de Estudio CEO",
                alert_no_book: "Por favor, ingresa el título del libro antes de generar un bloque.",
                alert_fail: "Error al generar el Bloque {n}: {msg}",
                alert_fail_docx: "Error al generar el archivo: {msg}",
                btn_docx_generating: "Generando .docx...",
            }
        };

        let currentLang = 'pt';

        function t(key, replacements = {}) {
            let str = TRANSLATIONS[currentLang][key] || key;
            for (const [k, v] of Object.entries(replacements)) {
                str = str.replace(`{${k}}`, v);
            }
            return str;
        }

        function applyLanguage(lang) {
            currentLang = lang;
            document.documentElement.lang = lang === 'pt' ? 'pt-BR' : lang;

            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                el.textContent = t(key);
            });
            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                const key = el.getAttribute('data-i18n-placeholder');
                el.placeholder = t(key);
            });

            // Re-apply button states correctly
            for (let i = 1; i <= 4; i++) {
                const btn = document.getElementById(`btn-block-${i}`);
                if (btn && !btn.classList.contains('completed') && !btn.disabled) {
                    btn.textContent = t(`btn_block_${i}`);
                }
            }
        }

        // Initialize with Portuguese
        applyLanguage('pt');

        async function generateBlock(blockNumber) {
            const livroInput = document.getElementById('livro-input');
            if (!livroInput.value.trim()) {
                alert(t('alert_no_book'));
                return;
            }

            const button = document.getElementById(`btn-block-${blockNumber}`);
            const resultsDiv = document.getElementById('results');

            button.disabled = true;
            button.textContent = t('btn_generating');

            try {
                const response = await fetch('/generate-block', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        livro: livroInput.value.trim(),
                        autor: document.getElementById('autor-input').value.trim(),
                        block_number: blockNumber,
                        lang: currentLang
                    })
                });

                const data = await response.json();
                if (!response.ok) throw new Error(data.error || "Unknown server error.");

                const placeholder = resultsDiv.querySelector('.placeholder');
                if (placeholder) placeholder.remove();

                const blockContainer = document.createElement('div');
                blockContainer.className = 'block-container';
                blockContainer.id = `content-block-${blockNumber}`;

                blockContainer.innerHTML = `<h2>Parte ${data.indice}: ${data.tema}</h2><div class="block-content"></div>`;
                blockContainer.querySelector('.block-content').textContent = data.texto_bloco;

                const existingBlock = document.getElementById(blockContainer.id);
                if (existingBlock) resultsDiv.replaceChild(blockContainer, existingBlock);
                else resultsDiv.appendChild(blockContainer);

                button.textContent = t('btn_done', { n: blockNumber });
                button.classList.add('completed');
                document.getElementById('docx-button').style.display = 'block';
                document.getElementById('kindle-instructions').style.display = 'block';

            } catch (error) {
                alert(t('alert_fail', { n: blockNumber, msg: error.message }));
                button.disabled = false;
                button.textContent = t(`btn_block_${blockNumber}`);
            }
        }

        async function generateDocx() {
            const button = document.getElementById('docx-button');
            button.disabled = true;
            button.textContent = t('btn_docx_generating');

            const livro = document.getElementById('livro-input').value.trim() || "dossie";
            const autor = document.getElementById('autor-input').value.trim();
            const blocks = [];
            document.querySelectorAll('.block-container').forEach(container => {
                blocks.push({
                    title: container.querySelector('h2').textContent,
                    content: container.querySelector('.block-content').textContent
                });
            });

            try {
                const response = await fetch('/generate-docx', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ livro, autor, blocks })
                });

                if (!response.ok) throw new Error((await response.json()).error || `Erro ${response.status}`);

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `DOSSIE_${livro.replace(/ /g, '_')}.docx`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);

            } catch (error) {
                alert(t('alert_fail_docx', { msg: error.message }));
            } finally {
                button.disabled = false;
                button.textContent = t('btn_docx');
            }
        }
    </script>
</body>
</html>
'''

# --- 3. TEMAS DOS BLOCOS POR IDIOMA ---
BLOCOS_TEMAS = {
    'pt': [
        "Tese Central, Fundamentos e Visão Geral",
        "Mecanismos de Alavancagem, Exemplos e Comparações",
        "Estratégias de Liderança, Governança e Aplicação Executiva",
        "Plano de Ação, Retenção e Exercícios Práticos"
    ],
    'en': [
        "Core Thesis, Foundations & Overview",
        "Leverage Mechanisms, Examples & Comparisons",
        "Leadership Strategies, Governance & Executive Application",
        "Action Plan, Retention & Practical Exercises"
    ],
    'es': [
        "Tesis Central, Fundamentos y Visión General",
        "Mecanismos de Apalancamiento, Ejemplos y Comparaciones",
        "Estrategias de Liderazgo, Gobernanza y Aplicación Ejecutiva",
        "Plan de Acción, Retención y Ejercicios Prácticos"
    ]
}

LANG_NAMES = {
    'pt': 'Português do Brasil',
    'en': 'English',
    'es': 'Español'
}

# --- 4. LÓGICA DE GERAÇÃO PYTHON ---
def gerar_bloco_estrategico(client, nome_livro, autor_livro, tema, indice, lang='pt'):
    lang_name = LANG_NAMES.get(lang, 'Português do Brasil')
    autor_str = f"de '{autor_livro}'" if autor_livro else ""

    prompt = f'''
[IDIOMA DE RESPOSTA]: Escreva TODO o conteúdo EXCLUSIVAMENTE em {lang_name}. Nenhuma outra língua.

[SEU PAPEL]
Você é um Mentor Executivo que formou dezenas de CEOs e Diretores de grandes empresas. Você leu este livro várias vezes e vai explicar ele para um executivo — alguém que está se preparando para ser CEO ou já é CEO — de forma direta, prática e fácil de guardar na memória.

[LIVRO]: '{nome_livro}' {autor_str}
[PARTE {indice} do DOSSIÊ]: {tema}

[REGRAS ABSOLUTAS DE LINGUAGEM]
1. PROIBIDO linguagem acadêmica ou abstrata. Palavras como "ontológico", "paradigma sistêmico", "epistemológico" e similares são PROIBIDAS. Se um conceito precisa ser explicado, use uma analogia ou exemplo real de negócio.
2. FALE como um CEO experiente falaria para outro CEO: direto, claro, sem rodeios.
3. Cada ideia principal do livro DEVE vir acompanhada de:
   - Um exemplo concreto do próprio livro (o que o autor diz / mostra / usa como caso).
   - Uma analogia ou comparação com um cenário corporativo real que qualquer executivo reconhece (Amazon, Apple, startups, mercado financeiro, varejo, indústria, etc.).
4. Conecte SEMPRE as ideias do livro com as realidades do dia a dia de um CEO:
   - Como isso afeta a Cultura da empresa?
   - Como isso impacta a Lucratividade (EBITDA, Margens)?
   - Como isso ajuda a Escalar o negócio?
   - Como isso torna a Liderança mais efetiva?
5. Termos técnicos e conceitos-chave de negócios devem aparecer em {lang_name} com o equivalente em Inglês entre parênteses logo após. Ex: "Receita Recorrente (Recurring Revenue)", "Cultura de Alta Performance (High-Performance Culture)".
6. NÃO faça resumo. NÃO liste bullet points genéricos. DESENVOLVA as ideias em parágrafos ricos, com profundidade e exemplos.
7. EXTENSÃO: Aproximadamente 3.000 palavras. Nem mais, nem menos. Texto corrido, sem markdown.
8. NÃO inclua introduções como "Neste bloco vou falar sobre..." ou "Como mencionado anteriormente...". Vá direto ao conteúdo.

[ESTRUTURA RECOMENDADA PARA ESTE BLOCO — use como guia, não como lista visível]
- Abra com a ideia central desta parte do livro, em 1 parágrafo impactante que dê o contexto.
- Desenvolva cada conceito importante com explicação + exemplo do livro + comparação com o mundo corporativo real.
- Conecte os conceitos com as decisões que um CEO toma no dia a dia.
- Feche com uma reflexão que conecte esta parte à jornada de quem lidera uma empresa.
'''

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an elite executive mentor. You write in {lang_name} only. Your writing is practical, clear, and rich with real-world business examples. You never use academic jargon. You write exclusively in plain text, no markdown, no bullet points, just well-developed paragraphs."
                },
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERRO_API: {str(e)}"

# --- 5. ROTAS DA APLICAÇÃO ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate-block', methods=['POST'])
def generate_block_route():
    data = request.get_json()
    if not all([data.get('livro'), data.get('block_number')]):
        return jsonify({"error": "Dados insuficientes."}), 400
    if not DEEPSEEK_API_KEY:
        return jsonify({"error": "Chave da API não configurada no servidor."}), 500

    lang = data.get('lang', 'pt')
    if lang not in BLOCOS_TEMAS:
        lang = 'pt'

    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
    blocos_temas = BLOCOS_TEMAS[lang]
    block_number = data['block_number']

    if not 1 <= block_number <= len(blocos_temas):
        return jsonify({"error": "Número do bloco inválido."}), 400

    tema = blocos_temas[block_number - 1]
    texto_gerado = gerar_bloco_estrategico(
        client,
        data['livro'],
        data.get('autor', ''),
        tema,
        block_number,
        lang
    )

    if texto_gerado.startswith("ERRO_API:"):
        return jsonify({"error": texto_gerado}), 500

    return jsonify({"indice": block_number, "tema": tema, "texto_bloco": texto_gerado})

@app.route('/generate-docx', methods=['POST'])
def generate_docx_route():
    try:
        data = request.get_json()
        livro = data.get('livro', 'Dossiê')
        autor = data.get('autor', '')
        blocks = data.get('blocks', [])

        if not blocks:
            return jsonify({"error": "Nenhum conteúdo para gerar o documento."}), 400

        document = Document()
        document.add_heading(livro, level=0)
        if autor:
            document.add_paragraph(f'Por: {autor}')
        document.add_paragraph('')

        for block in blocks:
            document.add_heading(block.get('title', 'Seção'), level=1)
            document.add_paragraph(block.get('content', ''))

        f = io.BytesIO()
        document.save(f)
        f.seek(0)

        safe_name = livro.replace(' ', '_').replace('/', '-')
        return send_file(
            f,
            as_attachment=True,
            download_name=f'DOSSIE_{safe_name}.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        print(f"[SERVER ERROR] {e}")
        return jsonify({"error": "Erro interno no servidor ao gerar o arquivo DOCX."}), 500

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
