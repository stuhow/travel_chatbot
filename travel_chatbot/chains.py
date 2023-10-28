import pandas as pd
from langchain.chat_models import ChatOpenAI
from travel_chatbot.basemodels import TravelDetails, UserInterests
from langchain.chains import create_tagging_chain_pydantic
from travel_chatbot.prompts import (no_results_prompt,
                    interest_gathering_prompt,
                    introduction_prompt,
                    info_gathering_prompt,
                    single_solution_presentation_prompt,
                    bq_single_solution_presentation_prompt,
                    bq_solution_presentation_prompt,
                    solution_presentation_prompt,
                    qualifiaction_prompt)
from travel_chatbot.utils import (add_non_empty_details,
                   check_what_is_empty,
                   get_filtered_df,
                   big_query_filter)

llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

def check_conversation_stage(conversation_history_list,
                             user_travel_details,
                             list_of_interests,
                             interest_asked,
                             asked_for):


    conversation_history = "\n".join(conversation_history_list)

    # extract travel details chain
    chain = create_tagging_chain_pydantic(TravelDetails, llm)
    res = chain.run(conversation_history)
    new_user_travel_details = add_non_empty_details(user_travel_details, res)

    # start conversation
    if new_user_travel_details.dict()['introduction'] == False:
        conversation_stage = introduction_prompt()
        return conversation_stage, user_travel_details

    # check what needs to be asked
    ask_for = check_what_is_empty(new_user_travel_details)

    # extract intrests chain
    chain = create_tagging_chain_pydantic(UserInterests, llm)
    interest = chain.run(conversation_history_list[-1])
    if interest.dict()['interest'] != None or interest.dict()['interest'] != "":
        list_of_interests.append(interest.dict()['interest'])

    # and remove country from the list
    if new_user_travel_details.dict()['country'] in list_of_interests:
        list_of_interests.remove(new_user_travel_details.dict()['country'])

    # # ----------- local df ----------
    # #load df
    # df = pd.read_csv("raw_data/one_day_test.csv")

    # # Filter df and gather available itineraries
    # filtered_df = get_filtered_df(df, new_user_travel_details)
    # found_itineraries = filtered_df['tour_name'].unique()
    # print(len(filtered_df))


    # # if there are no itineraries that fit the users needs we need to tell them
    # if len(filtered_df) == 0:
    #     conversation_stage = no_results_prompt(user_travel_details, new_user_travel_details)
    #     return conversation_stage, new_user_travel_details

    # # if there is only one itinerary
    # if len(filtered_df) == 1:
    #     conversation_stage = single_solution_presentation_prompt(found_itineraries, list_of_interests)
    #     return conversation_stage, new_user_travel_details

    # # if we have all the validated details we need to ask for a clients interests
    # elif len(ask_for) == 0 and len(found_itineraries) > 0 and len(interest_asked) == 0:
    #     print("All details gathered! Ask about interests...")
    #     conversation_stage = interest_gathering_prompt(found_itineraries, new_user_travel_details, list_of_interests)
    #     interest_asked.append(1)
    #     return conversation_stage, new_user_travel_details

    # # if we have all the validated details we need to present the list of itineraries rank by relevance to interests
    # elif len(ask_for) == 0 and len(found_itineraries) > 0:
    #     print("All details gathered! summarise the itineraries...")
    #     # conversation_stage = solution_presentation_prompt(found_itineraries, df) #
    #     conversation_stage = solution_presentation_prompt(found_itineraries, list_of_interests)
    #     return conversation_stage, new_user_travel_details

    # # if the user has not been qualified
    # elif new_user_travel_details.dict()['qualification'] == "" or new_user_travel_details.dict()['qualification'] != "Yes":
    #     conversation_stage = qualifiaction_prompt(new_user_travel_details)
    #     return conversation_stage, new_user_travel_details

    # # if the user is interested in a group tour gather required info
    # else:
    #     conversation_stage = info_gathering_prompt(ask_for, found_itineraries, filtered_df)
    #     asked_for.append(ask_for[0])
    #     return conversation_stage, new_user_travel_details


    # ----------- bigquery ---------------

    # Filtered available itineraries
    found_itineraries = big_query_filter(new_user_travel_details)
    filtered_df = None

    # if there are no itineraries that fit the users needs we need to tell them
    if len(found_itineraries) == 0:
        conversation_stage = no_results_prompt(user_travel_details, new_user_travel_details)
        return conversation_stage, new_user_travel_details

    # if there is only one itinerary
    if len(found_itineraries) == 1:
        print("Presenting the only itinerary found...")
        conversation_stage = bq_single_solution_presentation_prompt(found_itineraries, list_of_interests, new_user_travel_details)
        return conversation_stage, new_user_travel_details

    # if we have all the validated details we need to ask for a clients interests
    elif len(ask_for) == 0 and len(found_itineraries) > 0 and len(interest_asked) == 0:
        print("All details gathered! Ask about interests...")
        conversation_stage = interest_gathering_prompt(found_itineraries, new_user_travel_details, list_of_interests)
        interest_asked.append(1)
        return conversation_stage, new_user_travel_details

    # if we have all the validated details we need to present the list of itineraries rank by relevance to interests
    elif len(ask_for) == 0 and len(found_itineraries) > 0:
        print("All details gathered! summarise the itineraries...")
        # conversation_stage = solution_presentation_prompt(found_itineraries, df) #
        conversation_stage = bq_solution_presentation_prompt(found_itineraries, list_of_interests, user_travel_details)
        return conversation_stage, new_user_travel_details

    # if the user has not been qualified
    elif new_user_travel_details.dict()['qualification'] == "" or new_user_travel_details.dict()['qualification'] != "Yes":
        conversation_stage = qualifiaction_prompt(new_user_travel_details)
        return conversation_stage, new_user_travel_details

    # if the user is interested in a group tour gather required info
    else:
        conversation_stage = info_gathering_prompt(ask_for, found_itineraries, filtered_df)
        asked_for.append(ask_for[0])
        return conversation_stage, new_user_travel_details


def bq_check_conversation_stage(conversation_history_list,
                             user_travel_details,
                             list_of_interests,
                             interest_asked,
                             asked_for):


    conversation_history = "\n".join(conversation_history_list)

    # extract travel details chain
    chain = create_tagging_chain_pydantic(TravelDetails, llm)
    res = chain.run(conversation_history)
    new_user_travel_details = add_non_empty_details(user_travel_details, res)

    found_itineraries =None

    # start conversation
    if new_user_travel_details.dict()['introduction'] == False:
        conversation_stage = introduction_prompt()
        return conversation_stage, new_user_travel_details, list_of_interests, found_itineraries

    # check what needs to be asked
    ask_for = check_what_is_empty(new_user_travel_details)

    # extract intrests chain
    chain = create_tagging_chain_pydantic(UserInterests, llm)
    interest = chain.run(conversation_history_list[-1])
    if interest.dict()['interest'] != None or interest.dict()['interest'] != "":
        list_of_interests.append(interest.dict()['interest'])

    # and remove country from the list
    if new_user_travel_details.dict()['country'] in list_of_interests:
        list_of_interests.remove(new_user_travel_details.dict()['country'])

    # Filtered available itineraries
    found_itineraries = big_query_filter(new_user_travel_details)
    filtered_df = None

    # if there are no itineraries that fit the users needs we need to tell them
    if len(found_itineraries) == 0:
        print('No itineraries match the user needs....')
        conversation_stage = no_results_prompt(user_travel_details, new_user_travel_details)
        return conversation_stage, new_user_travel_details, list_of_interests, found_itineraries

    # if there is only one itinerary
    if len(found_itineraries) == 1:
        print("Presenting the only itinerary found...")
        # conversation_stage = bq_single_solution_presentation_prompt(found_itineraries, list_of_interests, new_user_travel_details)
        conversation_stage = "You have found a single itinerary that matches the users needs. Use the single_itinerary_summarisation tool to present the itinerary to the user."
        return conversation_stage, new_user_travel_details, list_of_interests, found_itineraries

    # if we have all the validated details we need to ask for a clients interests
    elif len(ask_for) == 0 and len(found_itineraries) > 0 and len(interest_asked) == 0:
        print("All details gathered! Ask about interests...")
        conversation_stage = interest_gathering_prompt(found_itineraries, new_user_travel_details, list_of_interests)
        interest_asked.append(1)
        return conversation_stage, new_user_travel_details, list_of_interests, found_itineraries

    # if we have all the validated details we need to present the list of itineraries rank by relevance to interests
    elif len(ask_for) == 0 and len(found_itineraries) > 0:
        print("All details gathered! summarise the itineraries...")
        # conversation_stage = solution_presentation_prompt(found_itineraries, df) #
        conversation_stage = bq_solution_presentation_prompt(found_itineraries, list_of_interests, user_travel_details)
        return conversation_stage, new_user_travel_details, list_of_interests, found_itineraries

    # if the user has not been qualified
    elif new_user_travel_details.dict()['qualification'] == "" or new_user_travel_details.dict()['qualification'] != "Yes":
        print('Qualify user...')
        conversation_stage = qualifiaction_prompt(new_user_travel_details)
        return conversation_stage, new_user_travel_details, list_of_interests, found_itineraries

    # if the user is interested in a group tour gather required info
    else:
        print('Ask the user a question to gather back travel information...')
        conversation_stage = info_gathering_prompt(ask_for, found_itineraries, filtered_df)
        asked_for.append(ask_for[0])
        return conversation_stage, new_user_travel_details, list_of_interests, found_itineraries
