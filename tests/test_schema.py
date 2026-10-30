from ai_stack.schemas import EducationalPackage,FlashcardContent,TutorialContent
import pytest
from pydantic import ValidationError
def test_flashcard():
    dados={ "metadata" :{ "profile_applied":"iniciante", "format_generated" : "flashcards","key_concepts" : ["SQl"],"study_time_minutes" : 4, "prerequisites" : ["Banco de dados"]
}, "content":{
    "title": "Banco de dados",
    "cards":[
        {"front":"O qe quer dizer SQL","back":" Structured Query Language"}
             ]

}
}
    dados_validados = EducationalPackage.model_validate(dados)
    assert isinstance(dados_validados,EducationalPackage)
    assert isinstance(dados_validados.content,FlashcardContent)

def test_tutorial():
    dados={ "metadata" :{ "profile_applied":"iniciante",
                          "format_generated" : "tutorial",
                          "key_concepts" : ["SQl"],
                          "study_time_minutes" : 4,
                            "prerequisites" : ["Banco de dados"] },
                            "content": {
        "title": "Banco de dados",
        "introduction": "sdcbcshbdchh",
        "steps":[
         {"title": "Apostila banco de dados",
                        "explanation" :"banco de dados sao ...",
                        "example" : "postgresql e um banco de dados ..."
                        }  ]
    
    }
    }
    dados_validados = EducationalPackage.model_validate(dados)
    assert isinstance(dados_validados,EducationalPackage)
    assert isinstance(dados_validados.content,TutorialContent)



def test_formato_incompativel():
    dados={ "metadata" :{ "profile_applied":"iniciante", "format_generated" : "tutorial","key_concepts" : ["SQl"],"study_time_minutes" : 4, "prerequisites" : ["Banco de dados"]
    }, "content":{
        "title": "Banco de dados",
        "cards":[
            {"front":"O qe quer dizer SQL","back":" Structured Query Language"}
                 ]
    
    }
    }
    with pytest.raises(ValidationError):
        dados_validados = EducationalPackage.model_validate(dados)
    
