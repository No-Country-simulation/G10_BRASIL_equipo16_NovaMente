

from pydantic import BaseModel,Field,model_validator
from enum import Enum
from typing import Literal


class Formats(Enum):
    flashcards="flashcards"
    tutorial = "tutorial"


class EducationMetadata(BaseModel):
    profile_applied:Literal["iniciante","intermediario"]
    format_generated : Formats
    key_concepts : list[str]= Field(min_length=1)
    study_time_minutes : int = Field(ge=1 )
    prerequisites : list[str]


class TutorialStep(BaseModel):
    title: str=Field(min_length=1)
    explanation : str= Field(min_length=1)
    example : str | None = None

class TutorialContent(BaseModel):
    title: str=Field(min_length=1)
    introduction : str=Field(min_length=1)
    steps : list[TutorialStep] = Field(min_length=1)

class FlashCard(BaseModel):
    front : str = Field(min_length=1)
    back : str = Field(min_length=1)

class FlashcardContent(BaseModel):
    title : str = Field(min_length=1)
    cards : list[FlashCard]= Field(min_length=1)

class EducationalPackage(BaseModel):
    metadata : EducationMetadata
    content : TutorialContent | FlashcardContent

    @model_validator(mode='after')
    def validacao(self):
        if self.metadata.format_generated==Formats.tutorial and isinstance(self.content,TutorialContent):
                return self
        elif self.metadata.format_generated==Formats.flashcards and isinstance(self.content,FlashcardContent):
                return self
        else:
             raise ValueError("O formato declarado nos metadados não corresponde ao tipo de conteúdo fornecido.")



        
class QuizOption(BaseModel):
     option_id: str  = Field(min_length=1, max_length=16)
     text : str


class QuizQuestion(BaseModel):
     question_id: str = Field(min_length=1, max_length=64)
     question : str
     options: list[QuizOption] = Field(min_length= 2)
     correct_option_id: str = Field(min_length=1, max_length=16)
     justification : str

     @model_validator(mode='after')
     def validar_resposta(self):
          ids = [option.option_id for option in self.options]
          ids_unicos = set(ids)
          if len(ids)!=len(ids_unicos):
               raise ValueError("Existem ids de opções duplicados")
          if self.correct_option_id not in ids :
               raise ValueError("A resposta correta não corresponde a nenhuma opção.")
          return self


          
class QuizContent(BaseModel):
     title : str
     questions : list[QuizQuestion] = Field(min_length= 4, max_length=4)
     