from transformers import pipeline
from app.utils import clean_filing_html

qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

def answer_question(context, question, chunk_size=1000, stride=500):
    # Clean and chunk the text
    chunks = []
    for i in range(0, len(context), stride):
        chunk = context[i:i + chunk_size]
        if chunk:
            chunks.append(chunk)
        if i + chunk_size > len(context):
            break

    best_score = -1
    best_answer = "No confident answer found."

    for chunk in chunks:
        try:
            result = qa_pipeline(question=question, context=chunk)
            if result['score'] > best_score and result['answer'].strip():
                best_score = result['score']
                best_answer = result['answer']
        except Exception as e:
            continue

    return best_answer