import pytest

from src.servico import ErroServico
from src.servico_ia import ServicoIA
from src.servico_mock import ServicoMock


@pytest.fixture
def mock():
    return ServicoMock(atraso_segundos=0)


def test_mock_devolve_fixture_do_formato(mock):
    r = mock.gerar("Power Query", "intermediario", "quiz")
    assert r["status"] == "success"
    assert r["answer"]["metadata"]["format_generated"] == "quiz"
    assert r["answer"]["metadata"]["profile_applied"] == "intermediario"


def test_mock_sem_contexto_com_palavra_chave(mock):
    assert mock.gerar("nada a ver", "iniciante", "quiz")["status"] == "insufficient_context"


def test_mock_recusa_pergunta_vazia_e_arquivo_invalido(mock):
    with pytest.raises(ErroServico):
        mock.gerar("   ", "iniciante", "quiz")
    with pytest.raises(ErroServico):
        mock.indexar("planilha.xlsx", b"123")
    assert mock.indexar("doc.md", b"# ok") == "doc.md"


def test_servico_ia_exige_groq_api_key(monkeypatch, pasta_tmp):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr("src.servico_ia.load_dotenv", lambda *a, **k: None)
    servico = ServicoIA(pasta_uploads=pasta_tmp)
    with pytest.raises(ErroServico, match="GROQ_API_KEY"):
        servico.gerar("Power Query", "iniciante", "quiz")


def test_servico_ia_recusa_extensao_antes_de_carregar_modelo(monkeypatch, pasta_tmp):
    monkeypatch.setenv("GROQ_API_KEY", "teste")
    servico = ServicoIA(pasta_uploads=pasta_tmp)
    with pytest.raises(ErroServico, match="não suportado"):
        servico.indexar("imagem.png", b"\x89PNG")
    assert not list(pasta_tmp.iterdir())  # nada foi gravado
