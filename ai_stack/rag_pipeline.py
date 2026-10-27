from langchain_core.prompts import ChatPromptTemplate

from langchain_core.messages import convert_to_openai_messages
from ai_stack.retrieval import retrieve_context_from_db
from ai_stack.llm import generate_completion
def generate_rag_response(pergunta, db_vector):
    documentos = retrieve_context_from_db( db_vector,pergunta, k=3)
    if not documentos:
        return {
            "answer": "Desculpe, não consegui encontrar informações relevantes para responder à sua pergunta.",
            "sources": []
        }
    contexto= "\n\n".join([  f"Fonte: {doc.metadata.get('source', 'Desconhecido')}\n Contexto: {doc.page_content}\n Página: {doc.metadata.get('page', 'Desconhecido')}"
                             for doc in documentos])
    metadados= [{"source": doc.metadata.get("source", "Desconhecido"),
                 "page": doc.metadata.get("page", "Desconhecido")
               } for doc in documentos]
    
    prompt = ChatPromptTemplate.from_messages([
    ("system", """És o assistente educativo do NovaMente.
Responde em português. Fundamenta as respostas no contexto fornecido.
Se a informação for insuficiente, admite-o.
Não inventes factos nem fontes."""),
    ("user", "Contexto:\n{context}\n\nPergunta: {question}")
])
    prompt_value = prompt.invoke({
    "context": contexto,
    "question": pergunta
})
    messages = convert_to_openai_messages(prompt_value.to_messages())
    resposta = generate_completion(messages)
    return {
        "answer": resposta,
        "sources": metadados
    }