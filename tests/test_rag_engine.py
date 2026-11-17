from rag_engine import DocumentRAG, extract_pages, split_text


def test_split_text_uses_overlap_and_keeps_content():
    text = "palavra " * 400
    chunks = split_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)
    assert chunks[0][-20:] in chunks[1]


def test_extract_markdown():
    pages = extract_pages("manual.md", b"# Titulo\nConteudo importante")
    assert pages == [("# Titulo\nConteudo importante", None)]


def test_local_retrieval_returns_relevant_source():
    engine = DocumentRAG()
    engine.add_files([
        ("rede.md", b"O servidor utiliza PostgreSQL para persistencia e Docker para containerizacao."),
        ("frontend.md", b"A interface web utiliza componentes React e CSS responsivo."),
    ])
    results = engine.retrieve("Qual banco de dados e usado no servidor?", top_k=2)
    assert results
    assert results[0].source == "rede.md"


def test_answer_local_mode_discloses_no_llm():
    engine = DocumentRAG()
    engine.add_files([("manual.txt", b"A API usa autenticacao por token e limita requisicoes." )])
    answer, sources = engine.answer("Como a API faz autenticacao?")
    assert "Modo local" in answer
    assert sources


def test_openai_mode_uses_embeddings_and_chat_completion():
    from types import SimpleNamespace

    class FakeEmbeddings:
        def create(self, model, input):
            data = []
            for text in input:
                vector = [1.0, 0.0] if "servidor" in text.lower() or "servidor" in str(text).lower() else [0.0, 1.0]
                data.append(SimpleNamespace(embedding=vector))
            return SimpleNamespace(data=data)

    class FakeCompletions:
        def create(self, **kwargs):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Resposta fundamentada no contexto."))])

    fake_client = SimpleNamespace(
        embeddings=FakeEmbeddings(),
        chat=SimpleNamespace(completions=FakeCompletions()),
    )
    engine = DocumentRAG(api_key="test-key", client=fake_client)
    engine.add_files([
        ("servidor.md", b"O servidor utiliza PostgreSQL."),
        ("interface.md", b"A interface usa React."),
    ])
    answer, sources = engine.answer("O que utiliza o servidor?")
    assert answer == "Resposta fundamentada no contexto."
    assert sources
    assert sources[0].source == "servidor.md"
