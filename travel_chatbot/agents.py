
from chains import check_conversation_stage
from prompts import customize_prompt
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.chat_models import ChatOpenAI

def run_francis(input,
                conversation_history,
                user_travel_details,
                list_of_interests,
                interest_asked,
                tools,
                asked_for):

    llm = ChatOpenAI(temperature=0.9, model="gpt-3.5-turbo")

    user_input = f"User: {input}"

    conversation_history.append(user_input)

    conversation_stage, user_travel_details = check_conversation_stage(conversation_history,
                                                                       user_travel_details,
                                                                       list_of_interests,
                                                                       list_of_interests,
                                                                       interest_asked,
                                                                       asked_for)

    final_prompt = customize_prompt(conversation_history, conversation_stage)

    # Create the agent
    agent = OpenAIFunctionsAgent(llm=llm,
                                 tools=tools,
                                 prompt=final_prompt)
    # agent = OpenAIMultiFunctionsAgent(llm=llm, tools=tools, prompt=final_prompt)

    # Run the agent with the actions
    agent_executor = AgentExecutor(agent=agent,
                                   tools=tools,
                                   verbose=False,
                                   max_iterations=5)

    francis = agent_executor.run(input)
    francis1 = f"Francis: {francis}"
    conversation_history.append(francis1)

    return francis, user_travel_details
