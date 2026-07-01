import os
import json
import base64
import asyncio
import threading
import uvicorn
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env local para o ambiente
load_dotenv()

# Configuração da página do Streamlit
st.set_page_config(page_title="FINTECH IA - LEVEL 4", page_icon="🎮", layout="wide")

# ===================================================================
# 🔑 INICIALIZAÇÃO SEGURA DA API DO GROQ
# ===================================================================
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("🔑 ERROR: CHAVE GROQ NAO ENCONTRADA! VERIFIQUE O .ENV")
    st.stop()

client = Groq(api_key=api_key)

# ===================================================================
# 🔌 CRIAÇÃO DA API REAL (FASTAPI) EM BACKGROUND
# ===================================================================
app_api = FastAPI(title="Fintech Credit API")

# Permite conexões de qualquer script externo
app_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app_api.get("/api/analise")
@app_api.post("/api/analise")
def api_analise_credito(
    nome: str = "Cliente API",
    idade: int = 30,
    renda: float = 5000.0,
    score: int = 500,
    valor: float = 10000.0
):
    try:
        prompt_api = f"""
        Aja como o motor de análise de risco de crédito de uma Fintech.
        Analise o seguinte perfil de forma estrita:
        - Cliente: {nome}
        - Idade: {idade} anos
        - Renda Mensal: R$ {renda}
        - Score de Crédito Serasa: {score}
        - Valor do Empréstimo Solicitado: R$ {valor}
        
        Responda de forma direta e estritamente em JSON.
        O formato JSON válido deve conter exatamente as chaves: 'status' (APROVADO ou REPROVADO), 'taxa_juros_anual' (string com a taxa sugerida ex: '12%') e 'justificativa' (uma frase curta com no máximo 10 palavras).
        """
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_api}],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=100,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# Função para iniciar o FastAPI em uma thread separada (porta 8000)
def rodar_fastapi():
    try:
        uvicorn.run(app_api, host="0.0.0.0", port=8000, log_level="warning")
    except Exception:
        pass

# Garante que a API só será iniciada uma única vez em segundo plano
if "fastapi_started" not in st.session_state:
    st.session_state["fastapi_started"] = True
    threading.Thread(target=rodar_fastapi, daemon=True).start()

# ===================================================================
# 🖼️ CONFIGURAÇÃO DA IMAGEM DE FUNDO LOCAL
# ===================================================================
NOME_IMAGEM_FUNDO = "background.png" 

def obter_css_fundo(nome_arquivo):
    if nome_arquivo and os.path.exists(nome_arquivo):
        with open(nome_arquivo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"""
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        """
    else:
        return "background-color: #0d0d1a !important;"

css_background = obter_css_fundo(NOME_IMAGEM_FUNDO)

# ESTILIZAÇÃO RETRÔ
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        {css_background}
        color: #00ff66 !important;
        font-family: 'Press Start 2P', monospace !important;
    }}
    h1, h2, h3, h4, h5, h6, p, label, span, div {{ font-family: 'Press Start 2P', monospace !important; }}
    .retro-container {{
        background-color: rgba(17, 17, 34, 0.90) !important;
        padding: 25px !important;
        border-radius: 8px !important;
        border: 2px solid #1a1a3a !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.8) !important;
        margin-bottom: 20px !important;
    }}
    h1 {{ color: #ff0055 !important; text-shadow: 3px 3px #000000; font-size: 22pt !important; text-align: center; margin: 0 !important; line-height: 1.4; }}
    h3 {{ color: #00ffff !important; font-size: 11pt !important; line-height: 1.6; margin-bottom: 20px !important; }}
    [data-testid="stHorizontalBlock"] > div {{
        background-color: rgba(17, 17, 34, 0.90) !important;
        padding: 25px !important;
        border-radius: 8px !important;
        border: 2px solid #1a1a3a !important;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.8);
    }}
    input, div[data-baseweb="input"], div[data-baseweb="select"] {{
        background-color: rgba(13, 13, 26, 0.95) !important;
        border: 2px solid #00ff66 !important;
        color: #ffffff !important;
    }}
    label p {{ color: #00ff66 !important; }}
    .stButton>button {{
        background-color: #ff0055 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        box-shadow: 4px 4px 0px #000000;
        font-family: 'Press Start 2P', monospace !important;
        font-size: 10pt !important;
        padding: 12px 24px !important;
        width: 100%;
    }}
    .stButton>button:hover {{ background-color: #00ff66 !important; color: #000000 !important; }}
    code, pre {{ background-color: rgba(0, 0, 0, 0.6) !important; color: #ffcc00 !important; border-left: 4px solid #ff0055; }}
    </style>
    """, unsafe_allow_html=True)

# ELEMENTOS VISUAIS DA LANDING PAGE
with st.container():
    st.markdown("""
    <div class="retro-container">
        <h1>Análise de Crédito com IA</h1>
        <h3><p style='text-align: center; color: #00ffff; margin: 10px 0;'>STAGE 4: AUTOMACAO E REST API REAL</p></h3>
        <p style='text-align: center; font-size: 8pt; color: #ffffff; margin-top: 10px;'>CONECTE VIA CODIGO LOCAL OU UTILIZE A INTERFACE ABAIXO.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<h3>🕹️ PLAYER 1: INTERFACE</h3>", unsafe_allow_html=True)
    nome = st.text_input("NOME DO CLIENTE", "LUCAS AOKI")
    idade = st.number_input("IDADE", min_value=18, max_value=100, value=29)
    renda = st.number_input("RENDA MENSAL (R$)", min_value=0.0, value=12500.0)
    score = st.slider("SCORE SERASA", min_value=0, max_value=1000, value=780)
    valor_solicitado = st.number_input("EMPRESTIMO (R$)", min_value=0.0, value=50000.0)

    if st.button("🚀 EXECUTE METHOD: POST"):
        prompt = f"""
        Aja como o motor de análise de risco de crédito de uma Fintech.
        Analise o seguinte perfil de forma estrita:
        - Cliente: {nome}
        - Idade: {idade} anos
        - Renda Mensal: R$ {renda}
        - Score de Crédito Serasa: {score}
        - Valor do Empréstimo Solicitado: R$ {valor_solicitado}
        
        Responda de forma direta e estritamente em JSON.
        O formato JSON válido deve conter exatamente as chaves: 'status' (APROVADO ou REPROVADO), 'taxa_juros_anual' (string com a taxa sugerida ex: '12%') e 'justificativa' (uma frase curta com no máximo 10 palavras).
        """
        with st.spinner("🧠 GROQ LOADING..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.1,
                    max_tokens=100,
                    response_format={"type": "json_object"}
                )
                resposta_json = json.loads(chat_completion.choices[0].message.content)
                st.write("---")
                if resposta_json.get("status") == "APROVADO":
                    st.success(f"🟢 WIN! STATUS: {resposta_json.get('status')} | TAXA: {resposta_json.get('taxa_juros_anual')}")
                else:
                    st.error(f"🔴 GAME OVER! STATUS: {resposta_json.get('status')}")
                st.info(f"INFO: {resposta_json.get('justificativa')}")
            except Exception as e:
                st.error(f"ERROR: {e}")

with col2:
    st.markdown("<h3>💻 PLAYER 2: CODE MODE</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-size: 8pt; line-height: 1.5; color: #ffffff;'>CRIE UM SCRIPT LOCAL APONTANDO PARA A PORTA DA API REAL (8000):</p>
    """, unsafe_allow_html=True)
    
    codigo_exemplo = """# Script do Aluno: testar_api.py
import requests

# Mude para o seu domínio do streamlit adicionando ':8000/api/analise' no final!
url_api = "http://localhost:8000/api/analise" 

dados_cliente = {
    "nome": "Mariana Silva",
    "idade": 34,
    "renda": 18000.0,
    "score": 890,
    "valor": 120000.0
}

print("📡 CONNECTING TO SERVER...")
resposta = requests.post(url_api, params=dados_cliente)

if resposta.status_code == 200:
    print("📥 DATA RECEIVED:", resposta.json())
else:
    print("❌ CONNECTION FAILED:", resposta.status_code)
"""
    st.code(codigo_exemplo, language="python")