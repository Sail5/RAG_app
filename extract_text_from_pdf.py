import os
import fitz  # PyMuPDF
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchFieldDataType, SearchableField
import base64

# Azure AI Searchの設定
AZURE_SEARCH_ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
AZURE_SEARCH_API_KEY = os.getenv('AZURE_SEARCH_API_KEY')
AZURE_SEARCH_INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME')

# OpenAI APIキーの設定
#openai.api_key = os.getenv('OPENAI_API_KEY')
#OPENAI_MODEL = "text-embedding-ada-002"

# 環境変数が正しく設定されていることを確認
assert AZURE_SEARCH_ENDPOINT is not None, "AZURE_SEARCH_ENDPOINT is not set"
assert AZURE_SEARCH_API_KEY is not None, "AZURE_SEARCH_API_KEY is not set"
assert AZURE_SEARCH_INDEX_NAME is not None, "AZURE_SEARCH_INDEX_NAME is not set"

# PDFからテキストの抽出
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = []
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text.append(page.get_text())
    return text

# AI searchのインデックス作成
def create_search_index():
    client = SearchIndexClient(endpoint=AZURE_SEARCH_ENDPOINT, credential=AzureKeyCredential(AZURE_SEARCH_API_KEY))
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String)
    ]
    index = SearchIndex(name=AZURE_SEARCH_INDEX_NAME, fields=fields)
    client.create_index(index)

# ドキュメントのキーをエンコード
def encode_document_key(key):
    """URLセーフなBase64形式にエンコード"""
    return base64.urlsafe_b64encode(key.encode()).decode()

# ドキュメントをAzure AI searchインデックスにアップロード
def upload_documents(documents):
    client = SearchClient(endpoint=AZURE_SEARCH_ENDPOINT, index_name=AZURE_SEARCH_INDEX_NAME, credential=AzureKeyCredential(AZURE_SEARCH_API_KEY))
    if not documents:
        print("No documents to upload.")
    client.upload_documents(documents=documents)

# メイン関数
def main():
    pdf_dir = 'pdfs/'
    documents = []

    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, pdf_file)
            texts = extract_text_from_pdf(pdf_path)
            for i, text in enumerate(texts):
                document_id = encode_document_key(f"{pdf_file}-{i}")
                print(f"Document ID: {document_id}")
                documents.append({
                    "id": document_id,
                    "content": text
                })
    
    print(f"Total documents to upload: {len(documents)}")

    create_search_index()
    upload_documents(documents)

if __name__ == "__main__":
    main()
