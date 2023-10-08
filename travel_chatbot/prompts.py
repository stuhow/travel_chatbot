
# map prompt
def map_prompt(interests):
    interests = ", ".join(interests)

    intermediate_template = f"""Based on this list of docs, please identify the itinerary name, tour length, travel style, physical grading, an summary of the itinerary and this list of interests: {interests}.
    If one or more of the interests is not mentioned this include this in the answer.
    Helpful Answer:"""

    map_template = """The following is a set of documents
    {docs}
    """
    map_template += intermediate_template

    map_prompt = PromptTemplate.from_template(map_template)
    return map_prompt

# first reduce prompt
def first_reduce_prompt():
    # Reduce
    reduce_template = """The following is set of summaries:
    {doc_summaries}
    Take these and distill it into a final, consolidated summary of the main themes.
    Helpful Answer:"""
    reduce_prompt = PromptTemplate.from_template(reduce_template)
    return reduce_prompt

# second reduce prompt
def second_reduce_prompt(interests):
    interests = ", ".join(interests)

    intermediate_template = f"""Take these and rank them based on the following user interests: {interests}.
    Return the origional summary along with a reason for ranking each itinerary based on their interests.
    Refer to the user as - you.
    Helpful Answer:"""

    reduce_template = """
    You are an AI travel agent speaking to a user. The following is set of summaries that fits the users basic travel needs:
    {doc_summaries}
    """
    reduce_template += intermediate_template

    reduce_prompt = PromptTemplate.from_template(reduce_template)
    return reduce_prompt

# introduction prompt for francis to introduce himself
def introduction_prompt():
    conversation_stage = """Start the conversation by introducing yourself. Ask the user if they are interested in a group tour.
        Be polite and respectful while keeping the tone of the conversation professional."""
    return conversation_stage


# Qualification stage prompts to make sure the user is interested in a group tour
def qualifiaction_prompt(new_user_travel_details):

    conversation_stage = None
    if new_user_travel_details.dict()['qualification'] == 'No':
        conversation_stage = """The user is not interested in a group tour so politely end the conversation.
        Ask them to come back if they ever are"""
    elif new_user_travel_details.dict()['qualification'] == 'Unsure':
        conversation_stage = """Explain what a group tour is.
        End your response by asking the user if they are interested in a group tour?"""
    return conversation_stage

# Info gathering stage when there are still trip details to ask for
def info_gathering_prompt(ask_for, found_itineraries, filtered_df):
    if len(ask_for) == 6:
        PROMPT_TEMPLATE = f"""You are currently in the detail gathering phase of the conversation and are trying to get detail of the users trip to help find the the perfect trip.
            If the user has just asked a follow up question in the conversation history, answer it.
            Once you have answered their question ALWAYS ask the user the following question to gather the required information.
            Follow up question:
            {ask_for[0]}"""
    else:
        PROMPT_TEMPLATE = f"""You are currently in the trip detail phase of the conversation and are trying to get detail of the users trip to help find the the perfect trip.
            If the user has just asked a follow up question in the conversation history, answer it.
            Once you have answered their question ALWAYS ask the user the following question to gather the required information.
            Follow up question:
            {ask_for[0]}
            """
        # {prompt_amendments(ask_for, filtered_df, found_itineraries)}
    return PROMPT_TEMPLATE

# Info gathering stage when there are still trip details to ask for
def interest_gathering_prompt(found_itineraries, new_user_travel_details, list_of_interests):
    if len(list_of_interests) == 0:
        PROMPT_TEMPLATE = f"""You have gathered all the basic information you need from the user:
        - destination: {user_travel_details.dict()['country']}
        - budget
        - when they're looking to travel
        - How long they want to travel for
        You now need to learn more about the users interests to recommend to most suitable trip.
        Ask questions around why they want to visit {user_travel_details.dict()['country']}
        """
    else:
        PROMPT_TEMPLATE = f"""You have gathered all the basic information you need from the user:
        - destination: {user_travel_details.dict()['country']}
        - budget
        - when they're looking to travel
        - How long they want to travel for
        The following itineraries are available: {found_itineraries}
        You now need to learn more about the users interests to recommend to most suitable trip.
        This is a list of places & interests they have already expressed an interest in: {list_of_interests}
        Ask questions around why they choose the destination
        """
    return PROMPT_TEMPLATE

# still in the info gathering stage but there are no available itineraries based on preferences
def no_results_prompt(user_travel_details, new_user_travel_details):
    old_keys = new_user_travel_details.dict().keys()
    new_keys = new_user_travel_details.dict().keys()
    last_question = [x for x in new_keys if x not in old_keys]
    conversation_stage = f"""
        The user has provided details of their trip but unfortunatley there are no itineraries that match their needs.
        Explain this to the user and higlight they need to look at alternate: {", ".join(last_question)}"""
    return conversation_stage

# All the details are gathered and we're presenting a solution, list of available itineraries
def solution_presentation_prompt(found_itineraries, df):
    summary = ""
    for itinerary in found_itineraries:
        filtered_df = df[df['tour_name'] == itinerary]
        summary += f'Itinerary: {filtered_df["tour_name"].values[0]}\n'
        summary += f'Tour description: {filtered_df["tour_description"].values[0]}\n'
        summary += f'Link: {filtered_df["url"].values[0]}\n\n'

    conversation_stage = f"""Thank the user for providing the details.
        Based on all the users needs here is the list of itineraries and a summary that fit their needs:\n{summary}
        Present the itinerary or itineraries to the user.
        """
    # text summarisation needed for the above
    return conversation_stage
