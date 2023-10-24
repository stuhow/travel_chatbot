
import glob
import openai
from pydantic import BaseModel, Field
from langchain.agents import Tool
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

def get_tools():
    #tru start
    class DocumentInput(BaseModel):
        question: str = Field()


    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    tools = []

    files = []
    for file in glob.glob('raw_data/itinerary_text/*'):
        file_dict = {'name': file.split("/")[-1].replace('.txt','').replace('& ','').replace(':','').replace(' ','_'),
                    "path": file}
        files.append(file_dict)

    for file in files[:1]:
        loader = TextLoader(file["path"])
        pages = loader.load_and_split()
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(pages)
        embeddings = OpenAIEmbeddings()
        retriever = FAISS.from_documents(docs, embeddings).as_retriever()

        # Wrap retrievers in a Tool
        tools.append(
            Tool(
                args_schema=DocumentInput,
                name=file["name"],
                description=f"needed when you want to answer questions about {file['name']} itinerary",
                func=RetrievalQA.from_chain_type(llm=llm, retriever=retriever),
            )
        )

    return tools
