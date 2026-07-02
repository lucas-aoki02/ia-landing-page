import os
import json
import base64
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

# Criar uma pasta pública estática caso não exista para servir dados limpos na Cloud
STATIC_DIR = os.path.join(os.path.dirname(st.__file__), "static", "api")
os.makedirs(STATIC_DIR, exist_ok=True)

# ===================================================================
# 🔌 ENDPOINT REST API INTERCEPTOR NATIVO
# ===================================================================
query_params = {}
if hasattr(st, "query_parameters"):
    try: query_params = {k: v for k, v in st.query_parameters.to_dict().items()}
    except Exception:
        try: query_params = {k: v for k, v in st.query_parameters.items()}
        except Exception: pass

# Se o modo API for chamado na interface ou via query (para uso local)
def processar_analise_ia(nome_api, idade_api, renda_api, score_api, valor_api):
    prompt_api = f"""
    Aja como o motor de análise de risco de crédito de uma Fintech.
    Analise o seguinte perfil de forma estrita:
    - Cliente: {nome_api}
    - Idade: {idade_api} anos
    - Renda Mensal: R$ {renda_api}
    - Score de Crédito Serasa: {score_api}
    - Valor do Empréstimo Solicitado: R$ {valor_api}
    
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

# Interceptador para Localhost (funciona direto na URL)
if "api_mode" in query_params or query_params.get("api_mode") == "true":
    try:
        res = processar_analise_ia(
            query_params.get("nome", "Cliente API"),
            query_params.get("idade", "30"),
            query_params.get("renda", "5000"),
            query_params.get("score", "500"),
            query_params.get("valor", "10000")
        )
        st.text(json.dumps(res))
        st.stop()
    except Exception as e:
        st.text(json.dumps({"error": str(e)}))
        st.stop()

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

with st.container():
    st.markdown("""
    <div class="retro-container">
        <h1>Análise de Crédito com IA</h1>
        <h3><p style='text-align: center; color: #00ffff; margin: 10px 0;'>STAGE 4: AUTOMACAO E API INTEGRADA</p></h3>
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
        with st.spinner("🧠 GROQ LOADING..."):
            try:
                resposta_json = processar_analise_ia(nome, idade, renda, score, valor_solicitado)
                
                # Salva a resposta estática limpa acessível globalmente via URL horizontal
                with open(os.path.join(STATIC_DIR, "credito.json"), "w") as f:
                    json.dump(resposta_json, f)
                
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
    <p style='font-size: 8pt; line-height: 1.5; color: #ffffff;'>LEITURA HORIZONTAL LIMPA DO ARQUIVO DE DADOS EM PRODUÇÃO (SEM CÁPSULA HTML):</p>
    """, unsafe_allow_html=True)
    
    codigo_exemplo = """# Script do Aluno: testar_api.py
import requests

# URL apontando para a pasta estática que o Streamlit Cloud expõe sem o bloqueio de HTML!
url_api = "https://SUA-URL-AQUI.streamlit.app/st-allowed/api/credito.json"

print("📡 CONNECTING TO SERVER...")
resposta = requests.get(url_api)

if resposta.status_code == 200:
    print("📥 DATA RECEIVED:", resposta.json())
else:
    print("❌ FALHA AO CONECTAR:", resposta.status_code)
"""
    st.code(codigo_exemplo, language="python")