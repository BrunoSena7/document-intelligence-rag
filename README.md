# Document Intelligence — RAG com fontes rastreáveis

Aplicação Streamlit para consultar documentos PDF, TXT e Markdown por meio de Retrieval-Augmented Generation (RAG).

> **Origem acadêmica:** projeto refatorado a partir do exercício “Chatbot com PDF — Streamlit” do repositório de materiais do curso de extensão em IA Generativa (Dia 04, Projeto 5). A implementação atual reorganiza o pipeline em um módulo testável e moderniza a experiência de execução. O projeto original utilizava LangChain, OpenAI e FAISS.

## O que demonstra

- Extração de texto de PDFs e arquivos de texto;
- divisão em chunks com sobreposição;
- indexação e recuperação de trechos relevantes;
- embeddings da OpenAI quando há chave configurada;
- busca lexical local com TF-IDF para validar o pipeline sem credenciais;
- geração de respostas condicionada ao contexto recuperado;
- indicação de arquivo e página como fonte;
- testes automatizados para extração, chunking e recuperação local.

## Arquitetura

```text
Upload (PDF/TXT/MD)
        |
        v
  Extração de texto
        |
        v
 Chunking + metadados
        |
        +----------------------------+
        |                            |
        v                            v
 OpenAI Embeddings              TF-IDF local
        |                            |
        +-------------+--------------+
                      |
                      v
             Recuperação Top-K
                      |
                      v
          Contexto com metadados
                      |
                      v
        OpenAI Chat Completions
          (quando configurado)
                      |
                      v
             Resposta + fontes
```

## Como executar

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env  # Windows: copie o arquivo manualmente
streamlit run app.py
```

Sem `OPENAI_API_KEY`, a aplicação executa a extração e a recuperação local com TF-IDF, exibindo os trechos encontrados. Para embeddings e geração por LLM, configure uma chave própria no `.env` ou na barra lateral da aplicação.

## Testes

```bash
pytest -q
```

Para testar rapidamente, envie `examples/guia_api_demo.md` pela interface e pergunte, por exemplo: “Qual o limite de requisições por minuto?”

## Limitações conhecidas

- A busca local TF-IDF é lexical, não semântica; embeddings são utilizados apenas no modo com API configurada.
- O índice fica em memória durante a sessão Streamlit; não há persistência ou isolamento multiusuário.
- O texto é extraído de PDFs digitais; PDFs escaneados exigem OCR, que não está implementado.
- O projeto é demonstrativo e não deve receber documentos sensíveis ou confidenciais.
- A geração por LLM depende de credenciais e custos do provedor escolhido.

## Créditos e escopo

Versão de portfólio refatorada com apoio de ferramentas de IA por Bruno Sena a partir do exercício acadêmico do curso. O material original utilizava LangChain, OpenAI e FAISS. O código desta versão deve ser revisado e compreendido pelo autor antes de ser apresentado. A aplicação não representa um produto implantado em ambiente de produção.
