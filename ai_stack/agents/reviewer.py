import json

from langchain_core.messages import convert_to_openai_messages

from ai_stack.agents.prompts import reviewer_prompt
from ai_stack.llm import generate_completion
from ai_stack.schemas import ReviewReport

def review_educational_content(context: str,educational_package: dict,profile: str,educational_format: str) -> ReviewReport:
   package_json = json.dumps(educational_package,ensure_ascii=False,indent=2)
   prompt_value = reviewer_prompt.invoke({
    "context": context,
    "educational_package": package_json,
    "profile": profile,
    "format": educational_format
})
   messages_langchain = prompt_value.to_messages()
   messages = convert_to_openai_messages(messages_langchain)
   response =generate_completion(messages)
   if not response or not response.strip():
    raise ValueError("O Revisor devolveu uma resposta vazia.")
   try:
    response_dict = json.loads(response)

   except json.JSONDecodeError as error:
    raise ValueError(f"O Revisor devolveu JSON inválido: {error}") from error

   review_report=ReviewReport.model_validate(response_dict)

   return review_report