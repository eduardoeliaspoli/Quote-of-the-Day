from dotenv import load_dotenv
load_dotenv() # Carrega as variáveis do arquivo .env

from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
import random
import google.generativeai as genai # IMPORTADO

app = Flask(__name__)
CORS(app)

# --- Configuração do Modelo Gemini ---
try:
    # Carregue a chave de API da variável de ambiente (agora carregada do .env)
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Aviso: GOOGLE_API_KEY não definida. A rota /api/frase/ia não funcionará.")
        gemini_model = None
    else:
        # Configure a API
        genai.configure(api_key=api_key)
        
        # --- ADIÇÃO: Listar modelos disponíveis ---
        print("--- Modelos de IA Disponíveis (que suportam 'generateContent') ---")
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # O nome 'm.name' é o que você deve usar
                    print(f"- {m.name}") 
        except Exception as e:
            print(f"Não foi possível listar os modelos: {e}")
        print("-----------------------------------------------------------------")
        # --- FIM DA ADIÇÃO ---

        # Inicialize o modelo (MUDANÇA AQUI para o modelo da sua lista)
        gemini_model = genai.GenerativeModel('models/gemini-2.5-flash')


except Exception as e:
    print(f"Falha ao carregar o modelo Gemini: {e}")
    gemini_model = None
# --- Fim da Configuração ---


# --- Lógica Original (JSON) ---
FRASES_JSON = "frases.json"
# ... (o resto do seu código permanece exatamente o mesmo) ...
if os.path.exists(FRASES_JSON):
    with open(FRASES_JSON, "r", encoding="utf-8") as f:
        FRASES = json.load(f)
else:
    FRASES = []
    print(f"Arquivo {FRASES_JSON} não encontrado. A rota /api/frase não retornará frases.")

@app.route("/api/frase", methods=["GET"])
def get_frase():
    """Retorna uma frase aleatória do arquivo JSON"""
    if not FRASES:
        return jsonify({"error": "Nenhuma frase disponível no JSON"}), 404
    frase = random.choice(FRASES)
    return jsonify(frase)
# --- Fim da Lógica Original ---


# --- NOVA Rota para IA (Gemini) ---
@app.route("/api/frase/ia", methods=["GET"])
def get_frase_ia():
    """Retorna uma frase motivacional gerada pela IA (Gemini)"""
    
    if not gemini_model:
        return jsonify({"error": "Configuração do servidor (IA) incompleta"}), 500

    try:
        # Prompt claro para a IA
        prompt = """
        Gere uma (e apenas uma) frase motivacional curta e inspiradora.
        Seja original.
        Não inclua o autor.
        Não use aspas no início ou no fim.
        Responda apenas com o texto da frase.
        """

        # Configurações de segurança
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = gemini_model.generate_content(prompt, safety_settings=safety_settings)

        if not response.parts:
             print(f"Resposta bloqueada pelo filtro de segurança: {response.prompt_feedback}")
             return jsonify({"error": "A frase gerada foi bloqueada por filtros de segurança."}), 500

        frase_texto = response.text.strip()
        
        if frase_texto.startswith('"') and frase_texto.endswith('"'):
            frase_texto = frase_texto[1:-1]

        # Monta o objeto JSON que seu frontend espera
        frase_obj = {
            "frase": frase_texto,
            "autor": "IA Motivacional" # Autor para frases geradas por IA
        }
        
        return jsonify(frase_obj)

    except Exception as e:
        print(f"Erro ao chamar a API Gemini: {e}")
        return jsonify({"error": "Não foi possível gerar a frase no momento."}), 503
# --- Fim da NOVA Rota ---


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

