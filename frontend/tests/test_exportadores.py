import json

from src import exportadores
from src.adaptador import adaptar_resposta


def test_json_enunciado_tem_blocos_do_contrato(resposta_flashcards, requisicao):
    r = adaptar_resposta(resposta_flashcards)
    dados = exportadores.para_json_enunciado(r, requisicao)
    assert dados["status"] == "sucesso"
    assert set(dados) >= {"metadados", "conteudo_adaptado", "avaliacao_qualidade", "armazenamento_oci"}
    assert dados["metadados"]["perfil_aplicado"] == "Iniciante"
    assert dados["metadados"]["formato_gerado"] == "Flashcards"
    assert dados["conteudo_adaptado"]["itens"][0] == {
        "tipo": "flashcard",
        "frente": "O que é o Power Query?",
        "verso": resposta_flashcards["answer"]["content"]["cards"][0]["back"],
    }
    assert dados["avaliacao_qualidade"]["ancoragem_fonte_score"] == 1.0
    json.loads(exportadores.para_json_texto(dados))  # serializável


def test_json_enunciado_quiz_expoe_resposta_em_texto(resultado_quiz, requisicao):
    item = exportadores.para_json_enunciado(resultado_quiz, requisicao)["conteudo_adaptado"]["itens"][0]
    assert item["tipo"] == "quiz"
    assert item["resposta_correta"] in item["opcoes"]


def test_csv_anki_uma_linha_por_cartao(resposta_flashcards):
    r = adaptar_resposta(resposta_flashcards)
    linhas = exportadores.para_csv_anki(r).splitlines()
    assert len(linhas) == 5
    assert linhas[0].split("\t")[0] == "O que é o Power Query?"


def test_markdown_quiz_marca_correta(resultado_quiz):
    md = exportadores.para_markdown(resultado_quiz)
    assert md.startswith("# Modelagem dimensional")
    assert "✅ A tabela fato" in md
    assert "## Fontes" in md


def test_exportar_sem_pacote_nao_quebra(resposta_sem_contexto, requisicao):
    r = adaptar_resposta(resposta_sem_contexto)
    assert exportadores.para_json_enunciado(r, requisicao)["status"] == "erro"
    assert exportadores.para_csv_anki(r) == ""
    assert "Sem conteúdo" in exportadores.para_markdown(r)
