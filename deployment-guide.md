# Guia de Implantação: Squad na Web (Custo Zero)

Siga estes passos para disponibilizar a squad para todos os professores da **Leonardo da Vinci**.

## 1. Preparar o Repositório no GitHub
1. Crie um novo repositório (pode ser privado) no GitHub.
2. Faça o upload dos seguintes arquivos e pastas que criamos:
   - `squads/recuperador-questoes/` (toda a pasta com agentes, tasks e dados).
   - `app.py` (o script que vou gerar a seguir).
   - `requirements.txt` (com as bibliotecas necessárias).

## 2. Obter a Chave da API do Gemini
Como a escola já usa Google Workspace, você pode gerar uma chave em:
[Google AI Studio](https://aistudio.google.com/app/apikey)

## 3. Configurar o Streamlit Cloud
1. Acesse [share.streamlit.io](https://share.streamlit.io/) e conecte sua conta do GitHub.
2. Clique em **"Create app"** e selecione o repositório da squad.
3. Em **"Main file path"**, coloque `app.py`.
4. **Importante:** Vá em "Advanced Settings" -> "Secrets" e adicione sua chave:
   ```toml
   GEMINI_API_KEY = "sua_chave_aqui"
   ```
5. Clique em **"Deploy"**.

## 4. Compartilhar
Pronto! O Streamlit gerará um link (ex: `https://vestibular-da-vinci.streamlit.app`) que você pode enviar para qualquer professor. Eles não precisam instalar nada, apenas digitar o assunto e baixar as questões.
