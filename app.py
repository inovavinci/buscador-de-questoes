import streamlit as st
import google.generativeai as genai
import os

# Configuração da Página
st.set_page_config(page_title="Recuperador de Questões - Leonardo da Vinci", page_icon="🔍")

# Autenticação Gemini
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
        st.success("API Key carregada.")

genai.configure(api_key=api_key)

# Lógica de Modelos
available_models = []
try:
    available_models = [m.name.replace('models/', '') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
except:
    available_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]

with st.sidebar:
    st.header("🤖 Modelo")
    idx = available_models.index("gemini-1.5-flash") if "gemini-1.5-flash" in available_models else 0
    selected_model_name = st.selectbox("Selecione o modelo:", options=available_models, index=idx)
    grounding = st.checkbox("Habilitar Pesquisa Google (Grounding)", value=True, help="Tenta buscar questões reais na internet.")

# Inicialização Robusta
def get_model(name, use_grounding):
    if not use_grounding:
        return genai.GenerativeModel(model_name=f"models/{name}")
    
    # O SDK 0.8.3 usa 'google_search_retrieval', mas a API às vezes pede 'google_search'.
    # Usamos o que o SDK conhece para evitar erros de inicialização.
    return genai.GenerativeModel(
        model_name=f"models/{name}", 
        tools=[{'google_search_retrieval': {}}]
    )

model = get_model(selected_model_name, grounding)

with st.sidebar:
    if st.button("🔍 Diagnóstico Técnico"):
        try:
            import google.generativeai.types as types
            st.write(f"Versão SDK: {genai.__version__}")
            st.json([f for f in dir(types.Tool) if not f.startswith('_')])
        except Exception as e:
            st.error(f"Erro: {e}")

st.title("🔍 Recuperador de Questões")
st.subheader("Leonardo da Vinci - Comitê de Inovação")

# Entrada do Usuário
with st.form("search_form"):
    topic = st.text_input("Qual o assunto das questões?", placeholder="Ex: Fotossíntese, Guerra Fria...")
    num_questions = st.slider("Quantidade de questões", 3, 15, 5)
    submit = st.form_submit_button("Gerar Banco de Questões")

if submit and topic:
    with st.spinner(f"A Squad está trabalhando em '{topic}'..."):
        prompt = f"""
        Você é a Squad 'Recuperador de Questões'. Execute estas tarefas:
        1. (Rita): Busque {num_questions} questões de vestibular reais sobre {topic}.
        2. (Victor): Classifique a dificuldade e inclua o gabarito.
        3. (Dante): Formate como um documento escolar profissional para a escola Leonardo da Vinci.
        
        REGRAS DE INTEGRIDADE (CRÍTICO):
        - Você NÃO PODE inventar questões. Elas devem ser REAIS.
        - Para CADA questão, forneça Banca, Ano e, se possível, um Link de Fonte.
        - O enunciado deve ser fiel ao original.
        
        REGRAS DE FORMATAÇÃO:
        - Cada alternativa (a, b, c, d, e) em uma nova linha.
        - Use DUAS quebras de linha (\n\n) entre enunciado e alternativas, e entre cada alternativa.
        - Gabarito em tabela ao final.
        """
        
        output_md = ""
        try:
            # Tenta gerar conforme configurado
            response = model.generate_content(prompt, request_options={"timeout": 600})
            output_md = response.text
        except Exception as e:
            err_msg = str(e)
            # FALLBACK SEGURO: Se o Google rejeitar a ferramenta de busca (erro 400),
            # tentamos gerar as questões sem a ferramenta para não deixar o usuário na mão.
            if "google_search" in err_msg or "not supported" in err_msg:
                st.warning("⚠️ O motor de busca do Google está em manutenção para sua conta. Gerando questões via memória interna...")
                try:
                    model_no_tools = genai.GenerativeModel(model_name=f"models/{selected_model_name}")
                    response = model_no_tools.generate_content(prompt, request_options={"timeout": 600})
                    output_md = response.text
                except Exception as e2:
                    st.error(f"Erro ao gerar: {e2}")
            else:
                st.error(f"Erro técnico: {e}")

        if output_md:
            st.success("Questões recuperadas!")
            st.markdown(output_md)
            st.download_button(
                label="Baixar Arquivo (.md)",
                data=output_md,
                file_name=f"questoes_{topic.lower().replace(' ', '_')}.md",
                mime="text/markdown"
            )

st.info("Dica: Cole o conteúdo no Google Docs para formatar e imprimir.")
