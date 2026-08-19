
import os
import io
from flask import Flask, request, render_template_string, jsonify, send_file
from openai import OpenAI
from docx import Document

# --- 1. CONFIGURAÇÃO DA APLICAÇÃO FLASK E API ---
app = Flask(__name__)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# --- 2. TEMPLATE HTML MULTILÍNGUE + SELETOR DE PROFISSÃO ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fábrica de Conhecimento</title>
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
            max-width: 820px;
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
            max-width: 820px;
            margin: auto;
        }
        h1, .subtitle { text-align: center; }
        h1 { font-size: 1.6rem; margin-bottom: 0.3rem; }
        h2 { font-size: 1.3rem; color: #1c1e21; margin-top: 1.5rem; border-bottom: 1px solid #dddfe2; padding-bottom: 0.5rem; }
        .subtitle { font-size: 1.05rem; color: #606770; margin-bottom: 1.5rem; }

        /* ---- Profession Selector ---- */
        .profession-selector {
            display: flex;
            justify-content: center;
            gap: 0.8rem;
            margin-bottom: 1.5rem;
        }
        .prof-btn {
            padding: 0.55rem 1.6rem;
            border-radius: 50px;
            border: 2px solid #dddfe2;
            background: #fff;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            color: #606770;
        }
        .prof-btn:hover { border-color: #1877f2; color: #1877f2; }
        .prof-btn.active-ceo {
            background: #1877f2;
            border-color: #1877f2;
            color: #fff;
        }
        .prof-btn.active-empreendedor {
            background: #e67e22;
            border-color: #e67e22;
            color: #fff;
        }
        /* -------------------------------- */

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
        .prof-empreendedor .block-button { background-color: #e67e22; }
        .prof-empreendedor .block-button:hover:not(:disabled) { background-color: #ca6f1e; }

        .info {
            background-color: #e7f3ff;
            border-left: 5px solid #1877f2;
            padding: 1rem;
            margin: 1rem 0 1.5rem 0;
            text-align: left;
            font-size: 0.9rem;
            border-radius: 6px;
        }
        .info.empreendedor-info {
            background-color: #fef5ec;
            border-left-color: #e67e22;
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
            .profession-selector { flex-direction: column; align-items: center; }
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

    <div class="container" id="main-container">
        <h1>🏭 <span data-i18n="title"></span></h1>
        <p class="subtitle" data-i18n="subtitle"></p>

        <!-- Profession Selector -->
        <div class="profession-selector">
            <button class="prof-btn active-ceo" id="prof-btn-ceo" onclick="selectProfession('ceo')" data-i18n="prof_ceo"></button>
            <button class="prof-btn" id="prof-btn-empreendedor" onclick="selectProfession('empreendedor')" data-i18n="prof_empreendedor"></button>
        </div>

        <input type="text" id="livro-input" data-i18n-placeholder="placeholder_book">
        <input type="text" id="autor-input" data-i18n-placeholder="placeholder_author">

        <div class="info" id="info-box"><strong data-i18n="info_label"></strong> <span data-i18n="info_text"></span></div>

        <div class="button-grid" id="button-grid">
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
                title: "Fábrica de Conhecimento",
                subtitle_ceo: "Dossiês Estratégicos para CEOs e Grandes Corporações",
                subtitle_empreendedor: "Dossiês Estratégicos para Empreendedores e Novos Negócios",
                subtitle: "Dossiês Estratégicos para CEOs e Grandes Corporações",
                prof_ceo: "CEO",
                prof_empreendedor: "Empreendedor",
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
                kindle_step3: "Envie para seu endereço Kindle (ex: seunome@kindle.com).",
                kindle_note: 'Encontre seu endereço Kindle em "Gerencie seu conteúdo e dispositivos" na Amazon.',
                footer: "Fábrica de Conhecimento — Powered by DeepSeek AI",
                alert_no_book: "Por favor, insira o título do livro antes de gerar um bloco.",
                alert_fail: "Falha ao gerar o Bloco {n}: {msg}",
                alert_fail_docx: "Falha ao gerar o arquivo: {msg}",
                btn_docx_generating: "Gerando .docx...",
            },
            en: {
                title: "Knowledge Factory",
                subtitle_ceo: "Strategic Dossiers for CEOs and Large Corporations",
                subtitle_empreendedor: "Strategic Dossiers for Entrepreneurs and New Ventures",
                subtitle: "Strategic Dossiers for CEOs and Large Corporations",
                prof_ceo: "CEO",
                prof_empreendedor: "Entrepreneur",
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
                kindle_note: 'Find your Kindle address on the "Manage Your Content and Devices" page on Amazon.',
                footer: "Knowledge Factory — Powered by DeepSeek AI",
                alert_no_book: "Please enter the book title before generating a block.",
                alert_fail: "Failed to generate Block {n}: {msg}",
                alert_fail_docx: "Failed to generate file: {msg}",
                btn_docx_generating: "Generating .docx...",
            },
            es: {
                title: "Fábrica de Conocimiento",
                subtitle_ceo: "Dossieres Estratégicos para CEOs y Grandes Corporaciones",
                subtitle_empreendedor: "Dossieres Estratégicos para Emprendedores y Nuevos Negocios",
                subtitle: "Dossieres Estratégicos para CEOs y Grandes Corporaciones",
                prof_ceo: "CEO",
                prof_empreendedor: "Emprendedor",
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
                kindle_note: 'Encuentra tu dirección Kindle en "Administra tu contenido y dispositivos" en Amazon.',
                footer: "Fábrica de Conocimiento — Powered by DeepSeek AI",
                alert_no_book: "Por favor, ingresa el título del libro antes de generar un bloque.",
                alert_fail: "Error al generar el Bloque {n}: {msg}",
                alert_fail_docx: "Error al generar el archivo: {msg}",
                btn_docx_generating: "Generando .docx...",
            }
        };

        let currentLang = 'pt';
        let currentProfession = 'ceo';

        function t(key, replacements = {}) {
            let str = TRANSLATIONS[currentLang][key] || key;
            for (const [k, v] of Object.entries(replacements)) {
                str = str.replace(`{${k}}`, v);
            }
            return str;
        }

        function selectProfession(prof) {
            currentProfession = prof;

            const ceoBtnEl = document.getElementById('prof-btn-ceo');
            const empBtnEl = document.getElementById('prof-btn-empreendedor');
            const infoBox = document.getElementById('info-box');
            const buttonGrid = document.getElementById('button-grid');

            // Reset buttons
            ceoBtnEl.className = 'prof-btn';
            empBtnEl.className = 'prof-btn';

            if (prof === 'ceo') {
                ceoBtnEl.classList.add('active-ceo');
                infoBox.className = 'info';
                buttonGrid.className = 'button-grid';
                document.querySelector('.subtitle').textContent = t('subtitle_ceo');
            } else {
                empBtnEl.classList.add('active-empreendedor');
                infoBox.className = 'info empreendedor-info';
                buttonGrid.className = 'button-grid prof-empreendedor';
                document.querySelector('.subtitle').textContent = t('subtitle_empreendedor');
            }

            // Reset any completed blocks visually when switching profession
            for (let i = 1; i <= 4; i++) {
                const btn = document.getElementById(`btn-block-${i}`);
                btn.disabled = false;
                btn.classList.remove('completed');
                btn.textContent = t(`btn_block_${i}`);
            }
            document.getElementById('results').innerHTML = `<p class="placeholder">${t('placeholder_results')}</p>`;
            document.getElementById('docx-button').style.display = 'none';
            document.getElementById('kindle-instructions').style.display = 'none';
        }

        function applyLanguage(lang) {
            currentLang = lang;
            document.documentElement.lang = lang === 'pt' ? 'pt-BR' : lang;

            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                const val = TRANSLATIONS[currentLang][key];
                if (val !== undefined) el.textContent = val;
            });
            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                const key = el.getAttribute('data-i18n-placeholder');
                el.placeholder = t(key);
            });

            // Update subtitle based on current profession
            const subtitleKey = currentProfession === 'ceo' ? 'subtitle_ceo' : 'subtitle_empreendedor';
            document.querySelector('.subtitle').textContent = t(subtitleKey);

            // Re-apply button labels for non-completed buttons
            for (let i = 1; i <= 4; i++) {
                const btn = document.getElementById(`btn-block-${i}`);
                if (btn && !btn.classList.contains('completed')) {
                    btn.textContent = t(`btn_block_${i}`);
                }
            }
        }

        // Initialize
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
                        lang: currentLang,
                        profession: currentProfession
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


# --- 4. PROMPT DO CEO ---
def gerar_bloco_ceo(client, nome_livro, autor_livro, tema, indice, lang):
    lang_name = LANG_NAMES.get(lang, 'Português do Brasil')
    autor_str = f"de '{autor_livro}'" if autor_livro else ""

    prompt = f'''
[IDIOMA DE RESPOSTA]: Escreva TODO o conteúdo EXCLUSIVAMENTE em {lang_name}. Nenhuma outra língua.

[SEU PAPEL]
Você é um Mentor Executivo de alto nível que formou dezenas de CEOs de grandes corporações. Você leu este livro profundamente e vai destilá-lo para um CEO — alguém que opera em ambientes corporativos consolidados, com modelo de negócio já provado, e cujo desafio é execução impecável, gestão de riscos em cadeias complexas e melhoria contínua das margens.

[LIVRO]: '{nome_livro}' {autor_str}
[PARTE {indice} DO DOSSIÊ]: {tema}

[CONTEXTO DO CEO — O QUE IMPORTA PARA ELE]
O CEO de uma grande corporação não está tentando provar que o modelo funciona — ele já funciona. O desafio dele é MAXIMIZAR a eficiência, ganhar e manter Market Share (Participação de Mercado), e entregar resultados para o Board (Conselho de Administração) e acionistas. Os indicadores que movem o seu mundo são:

- Margem EBITDA (Earnings Before Interest, Taxes, Depreciation and Amortization): O termômetro máximo de eficiência operacional. Cada decisão estratégica impacta aqui. O controle rigoroso de COGS (Custo dos Produtos Vendidos / Cost of Goods Sold) via excelência em procurement (compras) e operações, e a disciplina no SG&A (Despesas Gerais, de Venda e Administrativas / Selling, General & Administrative Expenses) são os principais alavancadores.
- ROIC (Retorno sobre o Capital Investido / Return on Invested Capital): Indica se a empresa está alocando seu capital nas iniciativas certas para gerar lucros superiores ao custo desse capital.
- CCC (Ciclo de Conversão de Caixa / Cash Conversion Cycle): Fundamental em operações de grande volume. Quanto mais curto o ciclo, mais eficiente é a operação de transformar estoque em caixa.
- Market Share e Crescimento YoY (Year-over-Year): A batalha pelo território frente a concorrentes estabelecidos.
- Gestão de Risco Sistêmico: Mitigação de riscos operacionais, de cadeia de suprimentos (Supply Chain) e de mercado em escala global.
- Planejamento Estratégico de 3 a 5 anos com pressão por resultados trimestrais (Quarterly Results).

[REGRAS ABSOLUTAS DE LINGUAGEM]
1. PROIBIDO linguagem acadêmica ou abstrata. Palavras como "ontológico", "paradigma sistêmico" e similares são PROIBIDAS. Se precisar explicar um conceito, use uma analogia ou exemplo real de negócio.
2. Fale como um CEO experiente falaria para outro CEO: direto, claro, sem rodeios.
3. Cada ideia principal do livro DEVE vir acompanhada de:
   a. Um exemplo concreto do próprio livro (o que o autor diz, mostra ou usa como caso).
   b. Uma comparação com um cenário corporativo real que qualquer CEO reconhece (Amazon, Walmart, Toyota, LVMH, Vale, Ambev, Unilever, etc.).
4. Conecte SEMPRE as ideias do livro com as realidades do CEO: como isso impacta EBITDA, ROIC, CCC, Market Share ou a gestão de risco?
5. Termos técnicos de negócios devem aparecer em {lang_name} com o equivalente em Inglês entre parênteses. Ex: "Custo dos Produtos Vendidos (COGS)", "Retorno sobre Capital Investido (ROIC)".
6. NÃO faça resumo. NÃO liste bullet points genéricos. DESENVOLVA as ideias em parágrafos ricos, com profundidade e exemplos.
7. EXTENSÃO: Aproximadamente 3.000 palavras. Texto corrido, sem markdown, sem asteriscos, sem títulos internos.
8. NÃO inclua introduções como "Neste bloco vou falar sobre..." ou "Como mencionado anteriormente...". Vá direto ao conteúdo.
'''

    system_msg = f"You are an elite CEO mentor advising large-corporation executives. You write in {lang_name} only. Your writing is direct, strategic, and grounded in real corporate examples. No academic jargon. Plain text paragraphs only — no markdown, no bullet points, no asterisks."

    return _call_api(client, system_msg, prompt)


# --- 5. PROMPT DO EMPREENDEDOR ---
def gerar_bloco_empreendedor(client, nome_livro, autor_livro, tema, indice, lang):
    lang_name = LANG_NAMES.get(lang, 'Português do Brasil')
    autor_str = f"de '{autor_livro}'" if autor_livro else ""

    prompt = f'''
[IDIOMA DE RESPOSTA]: Escreva TODO o conteúdo EXCLUSIVAMENTE em {lang_name}. Nenhuma outra língua.

[SEU PAPEL]
Você é um Mentor de Empreendedores que viveu nas trincheiras: construiu e escalonou negócios do zero, passou por fases críticas de Burn Rate alto, encontrou o Product-Market Fit (Ajuste Produto-Mercado) na raça, e sabe o que separa startups que morrem das que se tornam negócios sólidos. Você leu este livro e vai destilá-lo para um empreendedor — alguém que atua em ambiente de extrema incerteza, recursos limitados e que precisa provar que o modelo de negócio funciona antes de qualquer outra coisa.

[LIVRO]: '{nome_livro}' {autor_str}
[PARTE {indice} DO DOSSIÊ]: {tema}

[CONTEXTO DO EMPREENDEDOR — O QUE IMPORTA PARA ELE]
O empreendedor não está gerindo uma máquina já azeitada. Ele está construindo a máquina enquanto pilota ela. A prioridade número um não é otimizar centavos no COGS no dia zero — é descobrir se as pessoas querem e pagam pelo que ele está construindo. Os indicadores que movem o seu mundo são:

- Burn Rate e Runway: Quanto dinheiro a empresa queima por mês e quantos meses de vida ela tem até o caixa acabar. Este é o KPI (Indicador-Chave de Desempenho) de sobrevivência. Tudo o mais é secundário se o caixa acabar.
- MRR / ARR (Receita Recorrente Mensal / Monthly Recurring Revenue e Receita Recorrente Anual / Annual Recurring Revenue): O pulso do crescimento em modelos de assinatura ou SaaS (Software como Serviço). É a prova de que o mercado aceitou o produto.
- CAC vs. LTV (Custo de Aquisição de Cliente / Customer Acquisition Cost vs. Valor do Tempo de Vida do Cliente / Lifetime Value): A pergunta mais importante do modelo de negócio — o cliente custa mais para conquistar do que ele vai gerar de receita ao longo do tempo? Se o LTV não for pelo menos 3x o CAC, o modelo tem um problema estrutural.
- Churn Rate (Taxa de Cancelamento): Se os clientes vão embora tão rápido quanto chegam, nenhuma estratégia de aquisição resolve o problema. A retenção é a prova definitiva de que o produto tem valor real.
- Product-Market Fit: O momento em que o produto encaixou tão bem com uma necessidade real do mercado que o crescimento começa a acontecer quase que organicamente.
- Bootstrapping vs. Captação (Fundraising): A decisão de crescer com recursos próprios ou levantar capital externo (Venture Capital, Angel Investors) molda toda a estratégia e velocidade do negócio.
- COGS e SG&A tornam-se críticos à medida que o negócio escala, mas nos primeiros estágios o foco é estruturar a operação aceitando margens espremidas para ganhar base de usuários e aprender.
- Growth Hacking e Go-to-Market (GTM): Como alcançar e converter clientes com eficiência máxima e orçamento mínimo.
- Pivô (Pivot): A capacidade de mudar de direção rapidamente com base no feedback real dos clientes, sem perder a essência da visão original.

[REGRAS ABSOLUTAS DE LINGUAGEM]
1. PROIBIDO linguagem acadêmica ou abstrata. Se precisar explicar um conceito, use uma analogia prática ou um exemplo real de startup ou negócio em crescimento.
2. Fale como um empreendedor experiente falaria para outro empreendedor: honesto, prático, sem rodeios, com a urgência de quem sabe que o tempo e o caixa são finitos.
3. Cada ideia principal do livro DEVE vir acompanhada de:
   a. Um exemplo concreto do próprio livro (o que o autor diz, mostra ou usa como caso).
   b. Uma comparação com um cenário real do mundo do empreendedorismo que qualquer fundador reconhece (Nubank, Airbnb, iFood, Rappi, Gympass, 99, Hotmart, startups de tecnologia, pequenos negócios escalando, etc.).
4. Conecte SEMPRE as ideias do livro com as realidades do empreendedor: como isso ajuda a estender o Runway? Como isso acelera o Product-Market Fit? Como isso reduz o Churn ou melhora o LTV? Como isso permite crescer com menos dinheiro?
5. Traga também a perspectiva de aplicação com recursos limitados — o empreendedor raramente tem o orçamento de uma grande corporação. A adaptação prática é fundamental.
6. Termos técnicos de negócios devem aparecer em {lang_name} com o equivalente em Inglês entre parênteses. Ex: "Taxa de Cancelamento (Churn Rate)", "Ajuste Produto-Mercado (Product-Market Fit)".
7. NÃO faça resumo. NÃO liste bullet points genéricos. DESENVOLVA as ideias em parágrafos ricos, com profundidade, exemplos reais e comparações que ajudem a reter e aplicar o conhecimento.
8. EXTENSÃO: Aproximadamente 3.000 palavras. Texto corrido, sem markdown, sem asteriscos, sem títulos internos.
9. NÃO inclua introduções como "Neste bloco vou falar sobre..." ou "Como mencionado anteriormente...". Vá direto ao conteúdo.
'''

    system_msg = f"You are an elite startup mentor and serial entrepreneur. You write in {lang_name} only. Your writing is honest, practical, and grounded in real startup examples. No academic jargon. Plain text paragraphs only — no markdown, no bullet points, no asterisks."

    return _call_api(client, system_msg, prompt)


# --- 6. CHAMADA À API (COMPARTILHADA) ---
def _call_api(client, system_msg, prompt):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ERRO_API: {str(e)}"


# --- 7. ROTAS DA APLICAÇÃO ---
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

    profession = data.get('profession', 'ceo')
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
    blocos_temas = BLOCOS_TEMAS[lang]
    block_number = data['block_number']

    if not 1 <= block_number <= len(blocos_temas):
        return jsonify({"error": "Número do bloco inválido."}), 400

    tema = blocos_temas[block_number - 1]
    nome_livro = data['livro']
    autor_livro = data.get('autor', '')

    if profession == 'empreendedor':
        texto_gerado = gerar_bloco_empreendedor(client, nome_livro, autor_livro, tema, block_number, lang)
    else:
        texto_gerado = gerar_bloco_ceo(client, nome_livro, autor_livro, tema, block_number, lang)

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
