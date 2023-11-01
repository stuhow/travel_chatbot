
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
from travel_chatbot.queries import bq_single_itinerary_query, bq_multiple_itinerary_query
from langchain.tools import StructuredTool
from langchain.chains import ReduceDocumentsChain, MapReduceDocumentsChain
import pinecone
from langchain.vectorstores import Pinecone
import os
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.tools import BaseTool
from typing import Type

def bq_single_solution_presentation_tool(found_itineraries, interests, user_travel_details):
    print('Single Summaristion tool started')

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
    print('Single Summaristion tool finished')
    return conversation_stage

def bq_solution_presentation_tool(found_itineraries, interests, user_travel_details):
    print('Multiple Summaristion tool started')
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    valid_interests = [interest for interest in interests if interest is not None]
    interests = ", ".join(valid_interests)


    map_prompt = f"""Write a summary paragraph and only include the itinerary name, tour length, a list of possible departure dates, summary of costs, travel style, physical grading, a summary of the itinerary and present the url to the user.
    Include a mention of any potential interests: {interests}.
    """
    map_prompt += """"
    {docs}"
    Produce a summary paragraph. Do not product a list or bullet points.
    CONCISE SUMMARY:"""
    map_prompt = PromptTemplate.from_template(map_prompt)


    reduce_template = """
    You are an AI travel agent speaking to a user. The following is set of summaries that fits the users basic travel needs:
    {doc_summaries}
    """
    intermediate_template = f"""Take these and rank them based on the following user interests: {interests}.
    Return the ranked itineraries as a summary paragraph and only include the itinerary name, tour length, a list of possible departure dates, summary of costs, travel style, physical grading, a summary of the itinerary and present the url to the user.
    Only return each itinerary as a consise paragraph.
    Refer to the user as - you.
    Helpful Answer:"""
    reduce_template += intermediate_template

    reduce_prompt = PromptTemplate.from_template(reduce_template)


    # Map
    map_chain = LLMChain(llm=llm, prompt=map_prompt)

    # Run chain
    reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)

    # Takes a list of documents, combines them into a single string, and passes this to an LLMChain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name="doc_summaries"
    )

    # Combines and iteravely reduces the mapped documents
    reduce_documents_chain = ReduceDocumentsChain(
        # This is final chain that is called.
        combine_documents_chain=combine_documents_chain,
        # If documents exceed context for `StuffDocumentsChain`
        collapse_documents_chain=combine_documents_chain,
        # The maximum number of tokens to group documents into.
        token_max=4000,
    )

    # Combining documents by mapping a chain over them, then combining results
    map_reduce_chain = MapReduceDocumentsChain(
        # Map chain
        llm_chain=map_chain,
        # Reduce chain
        reduce_documents_chain=reduce_documents_chain, #_documents
        # The variable name in the llm_chain to put the documents in
        document_variable_name="docs",
        # Return the results of the map steps in the output
        return_intermediate_steps=False,
    )


    query = bq_multiple_itinerary_query(user_travel_details, found_itineraries)

    loader = BigQueryLoader(query)
    docs = loader.load()
    itinerary_summary = map_reduce_chain.run(docs)

    conversation_stage = f"""You are at the solution presentation stage of you conversation.
    You have gathered the basic information you need from the client along with their interests.
    Using this information you have found and ranked the itineraries that best fit the users needs.
    Present the solution, found between the two sets of == below, to the client.
    ==
    {itinerary_summary}
    ==

    """
    #Return each as a summary paragraph and only include the itinerary name, tour length, departure dates, summary of costs, travel style, physical grading, a summary of the itinerary and present the url to the user.
    print('Multiple Summaristion tool finished')
    return conversation_stage

def itinerary_name():
    pinecone.init(api_key=os.getenv('PINECONE_API_KEY'),
              environment=os.getenv('PINECONE_ENV'))

    embeddings = OpenAIEmbeddings()
    pinecone_index = pinecone.Index("chatbot")
    vectorstore = Pinecone(pinecone_index, embeddings, "text")
    filters = {"tour_name": "Complete list of tours"}
    retriever = vectorstore.as_retriever(search_kwargs={'filter': filters})

    retriever_tool = create_retriever_tool(
            retriever,
            name='itinerary_name_search',
            description='use to learn the correct spelling of an itinerary name'
        )
    return retriever_tool

def question_function(att: str, question: str):
    print("Question tool started...")
    embeddings = OpenAIEmbeddings()

    pinecone_index = pinecone.Index("chatbot")
    vectorstore = Pinecone(pinecone_index, embeddings.embed_query, "text")

    filters = {"tour_name": att}

    qa = RetrievalQA.from_chain_type(
        llm= ChatOpenAI(
                        model_name='gpt-3.5-turbo',
                        temperature=0.0
                    ),
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={'filter': filters})
    )

    response = qa.run(question)
    print("Question tool completed...")
    return response


class Itineraryname(BaseModel):
    """Inputs for my_profile function"""
    itinerary_name: str = Field(description="the correct spelling of an itinerary name")
    question: str = Field(description="the question to be passed to the model")

class ItineraryQuestions(BaseTool):
    name = "itinerary_question"
    description = """
        Needed when you want to ask a question about an itinerary.
        Use this tool once you have used the retriever_tool to get the correct name
        """
    args_schema: Type[BaseModel] = Itineraryname

    def _run(self, itinerary_name: str, question: str):
        profile_detail_attribute = question_function(itinerary_name, question)
        return profile_detail_attribute

    def _arun(self, itinerary_name: str):
        raise NotImplementedError(
            "itinerary_question does not support async calls")

def get_bq_tools(found_itineraries, interests, new_user_travel_details):
    single_itinerary_summarisation_tool = StructuredTool.from_function(
        name="single_itinerary_summarisation",
        description="only use this tool when you need to summarise a single itinerary",
        func = lambda: bq_single_solution_presentation_tool(found_itineraries, interests, new_user_travel_details)
        )
    multiple_itinerary_summarisation_tool = StructuredTool.from_function(
        name="multiple_itinerary_summarisation",
        description="only use this tool when you need to summarise multiple itineraries",
        func = lambda: bq_solution_presentation_tool(found_itineraries, interests, new_user_travel_details)
        )
    return [single_itinerary_summarisation_tool,
            multiple_itinerary_summarisation_tool,
            itinerary_name(),
            ItineraryQuestions()
            ]

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
