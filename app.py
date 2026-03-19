import streamlit as st
import google.generativeai as genai
import os
import requests
import json

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
        st.success("API Key carregada via Secrets.")

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

# Inicialização Robusta (para o modo sem busca)
def get_model(name, use_grounding):
    if not use_grounding:
        return genai.GenerativeModel(model_name=f"models/{name}")
    # Nota: No modo Grounding, usamos a generate_with_rest_api abaixo
    return genai.GenerativeModel(model_name=f"models/{name}")

# Função para chamada direta via REST API (Bypass de SDK para Grounding)
def generate_with_rest_api(prompt, api_key, model_name):
    model_id = model_name.split('/')[-1]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
    
    # Tenta primeiro com o nome recomendado pelo Google atualmente
    tools_options = [
        {"google_search_retrieval": {"dynamic_retrieval_config": {"mode": "DYNAMIC", "dynamic_threshold": 0.1}}},
        {"google_search": {}}
    ]
    
    # Configurações de segurança para evitar bloqueios de "RECITATION" (Direitos Autorais) 
    # em questões de vestibular que são textos públicos/oficiais.
    safety_settings = [
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
    
    last_error = ""
    for tool_config in tools_options:
        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "tools": [tool_config],
                "safetySettings": safety_settings
            }
            response = requests.post(url, json=payload, timeout=600)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        return candidate['content']['parts'][0]['text']
                    elif 'finishReason' in candidate:
                        reason = candidate['finishReason']
                        if reason == "RECITATION":
                            return "O Google bloqueou por 'RECITATION' (Direitos Autorais). Isso acontece quando ele encontra a questão exata mas o filtro de proteção é muito rigoroso. Tente um assunto mais específico ou desabilite o Grounding."
                        return f"O Google bloqueou a resposta por segurança (Motivo: {reason}). Tente outro assunto."
                return "O Google não encontrou resultados para esta pesquisa."
            else:
                last_error = f"Erro {response.status_code}: {response.text}"
        except Exception as e:
            last_error = str(e)
            
    raise Exception(f"Falha na Pesquisa Google: {last_error}")

model = get_model(selected_model_name, grounding)

# Diagnóstico Técnico
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
    topic = st.text_input("Qual o assunto das questões?", placeholder="Ex: Fotossíntese, Oriente Médio...")
    num_questions = st.slider("Quantidade de questões", 3, 15, 5)
    submit = st.form_submit_button("Gerar Banco de Questões")

if submit and topic:
    with st.spinner(f"A Squad está buscando questões OFICIAIS sobre {topic}..."):
        prompt = f"""
        Você é um buscador de elite de questões de vestibular. Sua missão é fornecer apenas questões REAIS e VERIFICÁVEIS.
        
        ASSUNTO: {topic}
        QUANTIDADE: {num_questions}
        
        INSTRUÇÕES:
        1. Use o Google Search para encontrar questões de vestibulares reais.
        2. COPIE o texto INTEGRAL da questão.
        3. Identifique BANCA, ANO e forneça o LINK real da fonte.
        
        REGRAS DE OURO:
        - PROIBIDO INVENTAR questões.
        - PROIBIDO CRIAR links falsos. Se não tiver o link, cite apenas a fonte (ex: Brasil Escola).
        - Use DUAS quebras de linha (\n\n) entre enunciado e alternativas, e entre cada alternativa.
        - Gabarito em tabela ao final.
        """
        
        output_md = ""
        try:
            if grounding:
                output_md = generate_with_rest_api(prompt, api_key, selected_model_name)
            else:
                response = model.generate_content(prompt, request_options={"timeout": 600})
                output_md = response.text
        except Exception as e:
            st.error(f"Erro na geração: {e}")
            st.info("💡 Dica: Se o erro persistir, tente desativar o 'Habilitar Pesquisa Google' na barra lateral.")
            st.stop()

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
