from flask import request, jsonify, render_template
from RAG_app1 import app
import openai
import os
import requests

# OpenAI APIキーの設定
openai.api_key = os.getenv('OPENAI_API_KEY')
# Azure AI Searchの設定
AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
AZURE_SEARCH_API_KEY = os.getenv('AZURE_SEARCH_API_KEY')
AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({'answer': 'No question provided'}), 400

    try:
        # Azure AI Searchを使用して類似文章を取得
        headers = {"Content-Type": "application/json", "api-key": AZURE_SEARCH_API_KEY}
        search_url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX_NAME}/docs/search?api-version=2024-05-01-preview"  # 最新のAPIバージョンに更新
        search_payload = {
            "search": question,
            "queryType": "simple",  # セマンティック検索を無効にする
            "top": 2
        }

        search_response = requests.post(search_url, headers=headers, json=search_payload)
        search_results = search_response.json()

        # 類似文章をプロンプトに含める
        retrieved_texts = "\n".join([doc.get('content', '') for doc in search_results.get('value', [])])
        # prompt = f"Context:\n{retrieved_texts}\n\nQuestion:\n{question}\nAnswer:"
        prompt = f"あなたは優秀な就活生です。面接官からの【質問内容】に対して、下記の【参考情報】を参考にして、簡潔に回答してください。その際に会話として違和感のない、自然な回答を作成してください。\n【参考情報】:\n{retrieved_texts}\n\n【質問内容】:\n{question}"
        # デバッグ情報の出力
        print("Input Question:", question)
        print("Search Response:", search_response.text)
        print("Search Results:", search_results)
        print("retrieved_texts:", retrieved_texts)
        print("prompt:", prompt)

        # OpenAI APIを使用して回答を生成
        response = openai.ChatCompletion.create(
            # model="gpt-3.5-turbo",
            # model="gpt-4-turbo",
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "日本語で簡潔に答えてください。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'answer': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3001)
