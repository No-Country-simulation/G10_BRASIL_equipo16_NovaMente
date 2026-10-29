from ai_stack.prompts import prompt

from langchain_core.messages import convert_to_openai_messages
from ai_stack.retrieval import retrieve_context_from_db
from ai_stack.llm import generate_completion
from ai_stack.schemas import Formats

def validar_nivel(nivel):


        if not isinstance(nivel,str) :
            nivel="iniciante"

        nivel = nivel.strip().lower()

        if nivel not in ["iniciante","intermediario"]:
                 nivel="iniciante"

        return nivel

def validar_formato(formato):
    if not isinstance(formato,str):
            raise TypeError("Tipo invalido")

    formato= formato.strip().lower()

    formato_convertido= Formats(formato)
    return formato_convertido




def generate_rag_response(pergunta, db_vector, nivel, formato):
      nivel_valido= validar_nivel(nivel)
      formato_valido = validar_formato(formato)
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




      prompt_value = prompt.invoke({
    "context": contexto,
    "question": pergunta,
    "nivel_valido": nivel_valido,
    "formato_valido":formato_valido.value
})
      messages = convert_to_openai_messages(prompt_value.to_messages())
      resposta = generate_completion(messages)

      return {
        "answer": resposta,
        "sources": metadados
    }