import streamlit as st
import google.generativeai as genai
from docx import Document
from io import BytesIO
import os
import time

# --- 1. CONFIGURAÇÃO DE SEGURANÇA E AMBIENTE ---
# O código busca a chave nas variáveis de ambiente do sistema ou do Streamlit Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

# Se estiver usando Streamlit Cloud, ele pode buscar em st.secrets
if not GEMINI_API_KEY and "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# --- 2. CONFIGURAÇÃO DA UI (USER INTERFACE) ---
st.set_page_config(page_title="CEO Knowledge Factory", page_icon="🏢", layout="centered")

st.title("🏭 Fábrica de Conhecimento CEO")
st.subheader("Transformando livros em Dossiês Estratégicos de 1 Hora")

# Inputs do Usuário
with st.container():
    livro = st.text_input("Título do Livro", placeholder="Ex: Gestão de Alta Performance")
    autor = st.text_input("Autor", placeholder="Ex: Andrew Grove")
    
    st.info("Estratégia: Masterclass de 24.000 palavras dividida em 4 Blocos Ontológicos.")

# --- 3. A LÓGICA DE GERAÇÃO (O ALGORITMO) ---
def gerar_bloco_estrategico(model, nome_livro, autor_livro, tema, indice):
    """
    Função que executa o prompt de alta densidade para cada pilar do método.
    """
    prompt = f"""
    [ROLE] Atue como uma Cientista Experimental e CEO Estrategista.
    [OBJETIVO] Escreva a PARTE {indice} de um Dossiê Técnico exaustivo sobre o livro '{nome_livro}' de '{autor_livro}'.
    [FOCO DO BLOCO] {tema}.
    
    [DIRETRIZES TÉCNICAS]
    1. EXTENSÃO: Mínimo de 6.000 palavras para este bloco. Seja prolixo na profundidade técnica.
    2. TOM: Executivo, analítico e focado em governança de alto nível.
    3. ESTRUTURA: Use títulos H2 e H3, listas de verificação, análise de causa e efeito e modelos mentais.
    4. CONTEÚDO: Não resuma. Explique o 'Como' e o 'Porquê'. Conecte com EBITDA, cultura e escalabilidade.
    5. IDIOMA: Português, mantendo termos técnicos em Inglês entre parênteses.
    """
    
    response = model.generate_content(prompt)
    return response.text

# --- 4. FLUXO DE EXECUÇÃO ---
if st.button("🚀 INICIAR EXTRAÇÃO DE ELITE"):
    if not GEMINI_API_KEY:
        st.error("ERRO: Variável de ambiente 'GEMINI_API_KEY' não encontrada.")
    elif not livro:
        st.warning("Por favor, forneça ao menos o título do livro.")
    else:
        try:
            # Inicializa o Cliente
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            doc = Document()
            doc.add_heading(f'DOSSIÊ EXECUTIVO: {livro}', 0)
            doc.add_paragraph(f"Autor: {autor if autor else 'Não informado'}")
            
            # Definição dos Blocos da nossa Estratégia Validada
            blocos = [
                "Engenharia de Sistemas e Tese Central Ontológica",
                "Mecanismos de Alavancagem e Casos de Estudo Reais",
                "Estratégias de Governança para Diretores e CEOs",
                "Protocolo de Implementação e Exercícios de Retenção (Cicatriz Sináptica)"
            ]
            
            progresso = st.progress(0)
            status_text = st.empty()
            
            for i, tema in enumerate(blocos):
                status_text.text(f"⏳ Minerando Bloco {i+1}/4: {tema}...")
                
                texto_bloco = gerar_bloco_estrategico(model, livro, autor, tema, i+1)
                
                doc.add_heading(f"Parte {i+1}: {tema}", level=1)
                doc.add_paragraph(texto_bloco)
                
                progresso.progress((i + 1) / 4)
                time.sleep(2) # Pequena pausa para estabilidade
            
            # Finalização do Documento em Memória
            buffer = BytesIO()
            doc.save(buffer)
            buffer.seek(0)
            
            st.success(f"🏆 Dossiê de '{livro}' gerado com sucesso!")
            
            st.download_button(
                label="📥 Baixar Masterclass para Kindle (.docx)",
                data=buffer,
                file_name=f"MASTERCLASS_{livro.replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            
        except Exception as e:
            st.error(f"Erro Crítico no Sistema: {e}")

# --- 5. FOOTER ---
st.markdown("---")
st.caption("Desenvolvido para o Protocolo de Superpoder de Estudo CEO - Cientista Experimental v3.0")