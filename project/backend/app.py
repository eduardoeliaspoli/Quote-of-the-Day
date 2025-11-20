from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
import random
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# ==============================
#   CONFIGURAÇÃO DA API GEMINI
# ==============================

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("🚨 ERRO: GOOGLE_API_KEY não definida no ambiente do Render!")
    print("A rota /api/frase/ia NÃO irá funcionar.")
    gemini_model = None
else:
    try:
        genai.configure(api_key=api_key)

        print("🔍 Listando modelos suportados pelo generateContent:")
        try:
            for m in genai.list_models():
                if "generateContent" in m.supported_generation_methods:
                    print(f"- {m.name}")
        except Exception as e:
            print(f"Falha ao listar modelos: {e}")

        # Modelo atual
        gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")

        print("✅ Modelo Gemini carregado com sucesso.")

    except Exception as e:
        print(f"❌ Falha ao configurar Gemini: {e}")
        gemini_model = None


# ==============================
#   CARREGAR FRASES DO JSON
# ==============================

FRASES_JSON = "frases.json"

if os.path.exists(FRASES_JSON):
    with open(FRASES_JSON, "r", encoding="utf-8") as f:
        FRASES = json.load(f)
else:
    FRASES = []
    print(f"⚠️ Aviso: Arquivo {FRASES_JSON} não encontrado.")


# ==============================
#   ROTA: FRASE ALEATÓRIA DO JSON
# ==============================

@app.route("/api/frase", methods=["GET"])
def get_frase():
    if not FRASES:
        return jsonify({"error": "Nenhuma frase disponível"}), 404

    frase = random.choice(FRASES)
    return jsonify(frase)


# ==============================
#   ROTA: FRASE GERADA PELA IA
# ==============================

@app.route("/api/frase/ia", methods=["GET"])
def get_frase_ia():
    if not gemini_model:
        return jsonify({"error": "IA não configurada no servidor"}), 500

    try:
        prompt = """
        Gere APENAS uma frase motivacional curta e inspiradora.
        Não coloque aspas.
        Não adicione autor.
        Apenas o texto da frase.
        """

        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        response = gemini_model.generate_content(prompt, safety_settings=safety_settings)

        frase_texto = response.text.strip()

        if frase_texto.startswith('"') and frase_texto.endswith('"'):
            frase_texto = frase_texto[1:-1]

        return jsonify({
            "frase": frase_texto,
            "autor": "IA Motivacional"
        })

    except Exception as e:
        print(f"❌ Erro ao gerar frase com IA: {e}")
        return jsonify({"error": "Não foi possível gerar a frase no momento."}), 503


# ==============================
#   INICIAR SERVIDOR
# ==============================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
