from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
import tempfile


def load_document(uploaded_file):
    suffix = uploaded_file.name.split(".")[-1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    if suffix == "pdf":
        loader = PyPDFLoader(tmp_path)
    elif suffix == "txt":
        loader = TextLoader(tmp_path)
    elif suffix == "docx":
        loader = Docx2txtLoader(tmp_path)
    else:
        raise ValueError("Unsupported file type")

    return loader.load()
