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

# Lógica para listar modelos e permitir escolha se o padrão falhar
available_models = []
try:
    available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
except:
    available_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

with st.sidebar:
    st.header("🤖 Modelo")
    selected_model_name = st.selectbox(
        "Selecione o modelo:",
        options=available_models,
        index=available_models.index("gemini-1.5-flash") if "gemini-1.5-flash" in available_models else 0
    )
    grounding = st.checkbox("Habilitar Pesquisa Google (Grounding)", value=True)

# Inicialização do modelo selecionado
def get_model(name, use_grounding):
    tools = [{'google_search_retrieval': {}}] if use_grounding else None
    return genai.GenerativeModel(model_name=f"models/{name}", tools=tools)

model = get_model(selected_model_name, grounding)

# Debug: Mostrar modelos disponíveis se solicitado ou se houver erro
with st.sidebar:
    st.info("💡 A 'Rita Referência' agora utiliza o Google Search oficial para buscar questões em tempo real.")
    if st.button("🔍 Verificar Erro de Conexão"):
        try:
            genai.list_models()
            st.success("Conexão com Google AI OK!")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")

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
        
        REGRAS DE FORMATAÇÃO (CRÍTICO):
        - Cada alternativa (a, b, c, d, e) DEVE estar em uma nova linha.
        - Use DUAS quebras de linha (\n\n) entre o enunciado e as alternativas.
        - Use DUAS quebras de linha (\n\n) entre cada uma das alternativas.
        - Inclua Banca, Ano e Dificuldade no topo de cada questão.
        - Gabarito organizado em uma tabela ao final do documento.
        - Use Markdown puro.
        """
        
        try:
            # Definindo um timeout de 60 segundos para evitar que o Streamlit trave por 10 min
            response = model.generate_content(
                prompt,
                request_options={"timeout": 600} # Aumentado para 10min mas com tratamento de erro
            )
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
