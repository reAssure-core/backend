from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
from openai.embeddings_utils import get_embedding
from project_secrets import chat_key, embedding_key, azure_url, embed_azure_url

ALLOWED_EXTENSIONS = ["pdf"]

systemPrompt = """
    You are a helpful AI-based financial expert specialized in extracting answers from a policy document. These are to be used as valid answers to autofill in a website. 
    You will be given a question to answer and the Context required to answer the question. 
    Keywords for possible question types:
    "insurer" (non-explanatory type)
    "insuree" (non-explanatory type)
    "poicy_premium" (non-explanatory type)
    "policy_expiry" (non-explanatory type)
    "coverage_amt"  (explanatory type)
    "coverage_details" (explanatory type)
    ---------------------------------
    Instructions:
    1. Answer the query strictly as per the details given Context only. Do not invent any new details. Strictly follow expected output format.
    Expected output format: JSON as per example. 
    Keep answers short and to the point if the question is non-explanatory-type.
    If the question is explanatory-type, write a short paragraph as an answer. Answer all parts of question in this case.
    2. Context is comprised of excerpts from the document that details ... in decreasing order of vector embedding similarity.
    A good answer will make use of only the provided information to provide an understandable and satisfactory response to the user's query.
    3. Not all parts of the context may be relevant to the question. Pick and choose wisely.
    5. Do not talk about yourself. Do not respond to questions that is not relevant to a normal Kotak Securities user. 
    If a user asks such questions, respond with "N/A"
    ---------------------------------
    EXAMPLE OUTPUT:
    {
        'keyword for question type': 'answer'
    }
"""
userPrompt = """
    User question:
    {query}
    ---
    Context:
    {context}
    ---
    Your Answer:
"""


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def add_to_embeddings(dbClient, file_path, className="AutofillTest"):
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
    docs = text_splitter.split_documents(docs)

    opdocs = []
    for i in range(len(docs)):
        opdocs.append(docs[i].page_content)
    doc_and_embedding = []
    openai.api_type = "azure"
    openai.api_base = embed_azure_url
    openai.api_version = "2023-05-15"
    openai.api_key = embedding_key

    for doc in opdocs:
        doc_and_embedding.append({
            'doc': doc,
            'embedding': get_embedding(doc, engine="onfi-embedding-playground")
        })

    dbClient.batch.configure(batch_size=10)
    for item in doc_and_embedding:
        with dbClient.batch as batch2:
            properties = {'doc': item['doc']}
            batch2.add_data_object(
                data_object=properties,
                class_name=className,
                vector=item['embedding']
            )
    return file_path


def read_embeddings(query, dbClient, className="AutofillTest"):
    chunks = []

    openai.api_type = "azure"
    openai.api_base = embed_azure_url
    openai.api_version = "2023-05-15"
    openai.api_key = embedding_key

    queryVector = get_embedding(query, engine="onfi-embedding-playground")

    nearVector = {
        "vector": queryVector
    }

    result = dbClient.query.get(
        className, ['doc']
    ).with_near_vector(
        nearVector
    ).with_limit(4).with_additional(['certainty']).do()

    context = ""
    i = 0
    for chunk in result['data']['Get'][className]:
        i += 1
        localCtx = "Excerpt " + str(i) + ": " + chunk['doc'] + "\n"
        score = chunk['_additional']['certainty']
        chunks.append((localCtx,  score))
        context += localCtx

    return context, chunks


def openai_autcomplete(message, temperature=0):
    openai.api_type = "azure"
    openai.api_base = azure_url
    openai.api_version = "2023-05-15"
    openai.api_key = chat_key

    response = openai.ChatCompletion.create(
        engine="onfi-gpt35-16k",
        messages=message,
        temperature=temperature
    )
    return response['choices'][0]['message']['content']


def msg_formatter(query, context):
    return [
        {"role": "system", "content": systemPrompt},
        {"role": "user", "content": userPrompt.format(query=query, context=context)}
    ]
