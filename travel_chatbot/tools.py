
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
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.document_loaders import BigQueryLoader
from travel_chatbot.queries import bq_single_itinerary_query
from langchain.tools import StructuredTool

def bq_single_solution_presentation_tool(found_itineraries, interests, user_travel_details):
    print('Summaristion tool started')

    valid_interests = [interest for interest in interests if interest is not None]
    interests_string = ", ".join(valid_interests)

    # Define prompt
    prompt_template = f"""Write a summary and only include the itinerary name, tour length, a summary of departure dates, summary of costs, travel style, physical grading, a summary of the itinerary and present the url to the user.
    Include a mention of any potential interests: {interests_string}.
    """
    prompt_template += """"
    {text}"
    Produce a summary paragraph not a list or bullet points.
    CONCISE SUMMARY:"""
    prompt = PromptTemplate.from_template(prompt_template)

    # Define LLM chain
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Define StuffDocumentsChain
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name="text"
    )
    query = bq_single_itinerary_query(user_travel_details, found_itineraries)

    loader = BigQueryLoader(query)
    docs = loader.load()
    itinerary_summary = stuff_chain.run(docs)

    conversation_stage = f"""You are at the solution presentation stage of you conversation.
    You are in the process of gathering the basic information you need from the client along with their interests.
    Using this information you have gathered there is one itinery that fits the users needs.
    Present the summary, found between the two sets of == below, to the client.
    ==
    {itinerary_summary}
    ==
    """
    print('Summaristion tool finished')
    return conversation_stage

def get_bq_tools(found_itineraries, interests, new_user_travel_details):
    addition_tool = StructuredTool.from_function(
        name="single_itinerary_summarisation",
        description="use this tool when you need to summarise a single itinerary",
        func = lambda: bq_single_solution_presentation_tool(found_itineraries, interests, new_user_travel_details)
        )
    return addition_tool

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
