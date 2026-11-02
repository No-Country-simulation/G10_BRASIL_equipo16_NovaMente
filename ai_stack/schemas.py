

from pydantic import BaseModel,Field,model_validator, ConfigDict
from enum import Enum
from typing import Literal


class NovaMenteBaseModel(BaseModel):
     model_config = ConfigDict(
        str_strip_whitespace=True
    )

class Formats(str,Enum):
    flashcards="flashcards"
    quiz= "quiz"
    tutorial = "tutorial"


class EducationMetadata(NovaMenteBaseModel):
    profile_applied:Literal["iniciante","intermediario"]
    format_generated : Formats
    key_concepts : list[str]= Field(min_length=1)
    study_time_minutes : int = Field(ge=1 )
    prerequisites : list[str]


class TutorialStep(NovaMenteBaseModel):
    title: str=Field(min_length=1)
    explanation : str= Field(min_length=1)
    example : str | None = None

class TutorialContent(NovaMenteBaseModel):
    title: str=Field(min_length=1)
    introduction : str=Field(min_length=1)
    steps : list[TutorialStep] = Field(min_length=1)

class FlashCard(NovaMenteBaseModel):
    card_id : str = Field( min_length=1, max_length=16)
    front :str = Field(  min_length=1)

    back :str = Field(  min_length=1)

class FlashcardContent(NovaMenteBaseModel):
    title: str = Field(min_length=1)
    cards: list[FlashCard] = Field(min_length=1)

    @model_validator(mode="after")
    def validar_cards(self):
        ids = [card.card_id for card in self.cards]
        ids_unicos = set(ids)

        if len(ids) != len(ids_unicos):
            raise ValueError("Existem identificadores de cartões duplicados.")

        return self

        
class QuizOption(NovaMenteBaseModel):
     option_id: str  = Field(min_length=1, max_length=16)
     text : str = Field(  min_length=1)


class QuizQuestion(NovaMenteBaseModel):
     question_id: str = Field(min_length=1, max_length=64)
     question : str = Field(min_length=1)
     options: list[QuizOption] = Field(min_length= 2)
     correct_option_id: str = Field(min_length=1, max_length=16)
     justification :str = Field(  min_length=1)

     @model_validator(mode='after')
     def validar_resposta(self):
           
          ids = [option.option_id for option in self.options]
          ids_unicos = set(ids)
          if len(ids)!=len(ids_unicos):
               raise ValueError("Existem ids de opções duplicados")
          
          if self.correct_option_id not in ids :
               raise ValueError("A resposta correta não corresponde a nenhuma opção.")
          return self


          
class QuizContent(NovaMenteBaseModel):
     title : str = Field(  min_length=1)

     questions : list[QuizQuestion] = Field(min_length= 1)
     @model_validator(mode="after")
     def validar_perguntas(self):
          ids = [question.question_id for question in self.questions]
          ids_unicos = set(ids)
          if len(ids)!= len (ids_unicos):
               raise ValueError("Existem ids  duplicados de perguntas")
          return self
               
     

class EducationalPackage(NovaMenteBaseModel):
    metadata : EducationMetadata
    content : TutorialContent | FlashcardContent | QuizContent

    @model_validator(mode='after')
    def validacao(self):
        if self.metadata.format_generated==Formats.tutorial and isinstance(self.content,TutorialContent):
                return self
        elif self.metadata.format_generated==Formats.flashcards and isinstance(self.content,FlashcardContent):
                return self
        elif self.metadata.format_generated==Formats.quiz and isinstance(self.content,QuizContent):
                return self
        else:
             raise ValueError("O formato declarado nos metadados não corresponde ao tipo de conteúdo fornecido.")


