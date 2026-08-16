from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

def generar_prompt(curs, tema, durada):
    return f"""
Ets un expert en educació primària a Catalunya. Has de generar material didàctic per a mestres.

Curs: {curs}è de Primària
Tema: {tema}
Durada: {durada} minuts

Has de generar exactament aquestes 7 seccions en català:

1. EXPLICACIÓ: Explica el concepte principal de manera clara i adequada per a l'edat.
2. FITXA: Crea una fitxa per a l'alumnat amb el contingut essencial.
3. ACTIVITATS: Proposa 4-5 activitats pràctiques per treballar el tema.
4. COMPRENSIÓ: Fes 5 preguntes per comprovar si l'alumnat ha entès el concepte (tipus veritat/fals, relacionar, o preguntes obertes curtes).
5. VERSIÓ FÀCIL: Adapta el contingut per a alumnes que necessiten suport.
6. VERSIÓ AMPLIACIÓ: Proposa activitats d'aprofundiment per a alumnes avançats.
7. SOLUCIONARI: Dona les respostes a totes les activitats i preguntes.

IMPORTANT: 
- El nivell ha de ser adequat per a {curs}è de Primària.
- Les operacions matemàtiques han de ser correctes.
- El llenguatge ha de ser clar i en català.
- Utilitza un format net i ben estructurat.
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    try:
        dades = request.json
        curs = dades.get('curs')
        tema = dades.get('tema')
        durada = dades.get('durada')

        if not curs or not tema:
            return jsonify({'error': 'Falten dades'}), 400

        prompt = generar_prompt(curs, tema, durada)

        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': 'Ets un expert en educació primària a Catalunya.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 4000
        }

        response = requests.post(DEEPSEEK_URL, headers=headers, json=data)

        if response.status_code != 200:
            return jsonify({'error': f'Error de l\'API: {response.status_code}'}), 500

        resultat = response.json()
        contingut = resultat['choices'][0]['message']['content']

        return jsonify({'material': contingut})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
