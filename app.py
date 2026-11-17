from __future__ import annotations

import os
import streamlit as st
from dotenv import load_dotenv
from rag_engine import DocumentRAG

load_dotenv()
st.set_page_config(page_title="Document Intelligence | RAG", page_icon="📚", layout="wide")
st.title("📚 Document Intelligence")
st.caption("Assistente de consulta documental com RAG, recuperação de contexto e fontes rastreáveis.")

with st.sidebar:
    st.header("Configuração")
    api_key = st.text_input(
        "OpenAI API key (opcional para modo local)",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="A chave é usada somente no servidor Streamlit; não a coloque no Git.",
    )
    chat_model = st.text_input("Modelo de chat", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    st.divider()
    st.markdown("**Pipeline**\n\n1. Extração de PDF/TXT/MD\n2. Chunking com sobreposição\n3. Embeddings + busca vetorial ou TF-IDF local\n4. Geração limitada ao contexto recuperado")

if (
    "rag_engine" not in st.session_state
    or st.session_state.get("rag_api_key") != api_key
    or st.session_state.get("rag_chat_model") != chat_model
):
    st.session_state.rag_engine = DocumentRAG(api_key=api_key.strip() or None, chat_model=chat_model)
    st.session_state.rag_api_key = api_key
    st.session_state.rag_chat_model = chat_model
    st.session_state.rag_files = []
    st.session_state.chat_history = []

engine: DocumentRAG = st.session_state.rag_engine

st.info(f"Modo atual: **{engine.mode}**")

uploaded_files = st.file_uploader(
    "Adicione documentos para indexação",
    type=["pdf", "txt", "md"],
    accept_multiple_files=True,
)
if st.button("Indexar documentos", type="primary", disabled=not uploaded_files):
    try:
        source_files = [(file.name, file.getvalue()) for file in uploaded_files]
        with st.spinner("Extraindo conteúdo e construindo o índice..."):
            total = engine.add_files(source_files)
        st.session_state.rag_files = sorted({name for name, _ in source_files})
        st.success(f"Índice atualizado: {total} novos trechos de {len(source_files)} arquivo(s).")
    except Exception as exc:
        st.error(f"Falha na indexação: {exc}")

if engine.chunks:
    left, right = st.columns([2, 1])
    with left:
        st.subheader("Converse com seus documentos")
    with right:
        st.metric("Trechos indexados", len(engine.chunks))
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
            if item.get("sources"):
                with st.expander("Fontes recuperadas"):
                    for source in item["sources"]:
                        st.write(source)
    question = st.chat_input("Faça uma pergunta sobre os documentos")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Recuperando contexto e elaborando resposta..."):
                try:
                    answer, sources = engine.answer(question)
                    st.markdown(answer)
                    source_labels = [
                        f"{source.source}{' — página ' + str(source.page) if source.page else ''} (score {source.score:.3f})"
                        for source in sources
                    ]
                    if source_labels:
                        with st.expander("Fontes recuperadas"):
                            for label in source_labels:
                                st.write(label)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": answer, "sources": source_labels}
                    )
                except Exception as exc:
                    st.error(f"Não foi possível responder: {exc}")
else:
    st.markdown(
        "Envie um PDF, TXT ou Markdown e clique em **Indexar documentos**. "
        "Sem chave da OpenAI, a recuperação local continua disponível para validar o fluxo; "
        "a geração por LLM exige uma chave própria."
    )
