import streamlit as st
import google.generativeai as genai
import os

# Configuração da Página
st.set_page_config(page_title="Recuperador de Questões - Leonardo da Vinci", page_icon="🔍")

# Autenticação Gemini
# Tenta pegar dos Secrets primeiro, se não, pede ao usuário na barra lateral
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

with st.sidebar:
    st.header("⚙️ Configurações")
    if not api_key:
        api_key_input = st.text_input("Insira sua Gemini API Key:", type="password", help="Pegue sua chave em https://aistudio.google.com/app/apikey")
        if api_key_input:
            api_key = api_key_input
        else:
            st.warning("Por favor, insira sua API Key para continuar.")
            st.stop()
    else:
        st.success("API Key carregada via Secrets (Modo Administrador).")

genai.configure(api_key=api_key)
# Usando o nome completo do modelo para evitar erros de versão da API
model = genai.GenerativeModel('models/gemini-1.5-flash')

st.title("🔍 Recuperador de Questões")
st.subheader("Leonardo da Vinci - Comitê de Inovação")

# Entrada do Usuário
with st.form("search_form"):
    topic = st.text_input("Qual o assunto das questões?", placeholder="Ex: Fotossíntese, Revolução Industrial...")
    num_questions = st.slider("Quantidade de questões", 3, 15, 5)
    submit = st.form_submit_button("Gerar Banco de Questões")

if submit and topic:
    with st.spinner(f"Rita Referência está pesquisando sobre {topic}..."):
        # Simulação simplificada do fluxo multi-agente via prompt estruturado
        prompt = f"""
        Você é a Squad 'Recuperador de Questões'. Execute estas tarefas:
        1. (Rita): Busque {num_questions} questões de vestibular reais sobre {topic}.
        2. (Victor): Classifique a dificuldade e inclua o gabarito.
        3. (Dante): Formate como um documento escolar profissional para a escola Leonardo da Vinci.
        
        REGRAS:
        - Inclua Banca, Ano e Dificuldade.
        - Gabarito ao final.
        - Use Markdown.
        - IMPORTANTE: Use quebras de linha duplas (linhas em branco extras) entre o enunciado, as alternativas e entre cada questão. Isso é essencial para que a conversão para PDF/Word fique legível.
        """
        
        try:
            response = model.generate_content(prompt)
            output_md = response.text
            
            st.success("Questões geradas com sucesso!")
            st.markdown(output_md)
            
            # Botão de Download
            st.download_button(
                label="Baixar Arquivo (.md)",
                data=output_md,
                file_name=f"questoes_{topic.lower().replace(' ', '_')}.md",
                mime="text/markdown"
            )
        except Exception as e:
            st.error(f"Erro ao gerar conteúdo: {e}")

st.info("Dica: Cole o conteúdo baixado no Google Docs para formatar e imprimir.")
