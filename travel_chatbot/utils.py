from travel_chatbot.basemodels import TravelDetails
from travel_chatbot.dicts import ask_for_dict
import pandas as pd
from google.cloud import bigquery

#check what is empty
# ask for country and then for a budget
def check_what_is_empty(user_travel_details):
    ask_for = []
    # Check if fields are empty
    for field, value in user_travel_details.dict().items():
        if value in [None, "", 0]:  # You can add other 'empty' conditions as per your requirements
            ask_for.append(ask_for_dict[field])

    if 'what country are you looking to travel to?' in ask_for:
        ask_for.remove('what country are you looking to travel to?')
        ask_for.insert(0, 'what country are you looking to travel to?')
    elif 'how much are you looking to spend?' in ask_for:
        ask_for.remove('how much are you looking to spend?')
        ask_for.insert(0, 'how much are you looking to spend?')


    return ask_for

## checking the response and adding it
def add_non_empty_details(current_details: TravelDetails, new_details: TravelDetails):
    non_empty_details = {k: v for k, v in new_details.dict().items() if v not in [False, None, ""]}
    updated_details = current_details.copy(update=non_empty_details)
    return updated_details


# Define a custom function to find the first non-null value in columns 9 to the end of the df
# used for finding the costs
def find_first_non_null(row):
    for value in row[12:]:  # Slice from the 9th column to the end
        if not pd.isna(value):
            return value
    return None

def get_filtered_df(df, user_travel_details):
    trip_details_dict = user_travel_details.dict()
    filled_out_dictionary = {k: v for k, v in user_travel_details.dict().items() if v not in [False, None, "",0]}

    # convert dates to datetime format
    df['duration'] = df['duration'].str.replace(' days', '').astype(int)
    df['start_date'] = pd.to_datetime(df['start_date'], format='%Y-%m-%d')

    # Apply the custom function to each row to find cost
    df['first_non_null'] = df.apply(find_first_non_null, axis=1)

    # Filtering the DataFrame
    filtered_df = df.copy()  # Make a copy of the original DataFrame to keep it intact

    # Iterate through the list of potential inputs
    for input_column in filled_out_dictionary.keys():
        if input_column == 'country':
            filtered_df = filtered_df[filtered_df['visited_countries'] == trip_details_dict["country"]]
        elif input_column == 'max_budget':
            filtered_df = filtered_df[filtered_df['first_non_null'] <= trip_details_dict["max_budget"]]
        elif input_column == 'min_budget':
            filtered_df = filtered_df[filtered_df['first_non_null'] >= trip_details_dict["min_budget"]]
        elif input_column == 'departing_after':
            filtered_df = filtered_df[filtered_df['start_date'] >= trip_details_dict["departing_after"]]
        elif input_column == 'departing_before':
            filtered_df = filtered_df[filtered_df['start_date'] <= trip_details_dict["departing_before"]]
        elif input_column == 'max_duration':
            filtered_df = filtered_df[filtered_df['duration'] <= trip_details_dict["max_duration"]]
        elif input_column == 'min_duration':
            filtered_df = filtered_df[filtered_df['duration'] >= trip_details_dict["min_duration"]]

    return filtered_df

# helper function that can be used in the info gathering prompt
# still being worked on to present a more conversational approach to gathering info
# it can also be used to guide the user on things like budget
def prompt_amendments(ask_for, filtered_df, found_itineraries):
    if ask_for[0] == 'how much are you looking to spend?':
        min_budget = filtered_df['first_non_null'].min()
        mean_budget = filtered_df['first_non_null'].mean()
        return f'In your answer tell the user there are {len(found_itineraries)} itineraries that fit their needs.\
        The minimim trip cost is {min_budget} and the average tripcost is {mean_budget} to their destination.'
    if ask_for[0] == 'when are you looking to travel?':
         print('The question is about when to travel')
    if ask_for[0] == 'how long do you want your trip to be?':
         print('The question is about the duration')
    if ask_for[0] == 'what country are you looking to travel to?':
         print('The question is about where they want to travel to')


def conversation_history(messages):
    # conversation history needed for the model
    conversation_history = []

    for message in messages:
        if message['role'] == 'user':
            # Append the modified user message to conversation_history
            conversation_history.append('User: ' + message['content'])
        elif message['role'] == 'assistant':
            # Append the modified assistant message to conversation_history
            conversation_history.append('Francis: ' + message['content'])
    return conversation_history


def big_query_filter(user_travel_details: TravelDetails):

    PROJECT = "wagon-bootcamp-377120"
    DATASET = "g_adventures_dataset"
    TABLE = "one_month"

    query = f"SELECT DISTINCT tour_name FROM {PROJECT}.{DATASET}.{TABLE} WHERE 1 = 1"

    # Iterate through the provided filter criteria and add them to the query
    if user_travel_details.country:
        query += f" AND visited_countries LIKE '%{user_travel_details.country}%'"

    if user_travel_details.max_budget:
        query += f" AND Standard___Adult <= {user_travel_details.max_budget}"

    if user_travel_details.departing_after:
        query += f" AND start_date >= '{user_travel_details.departing_after}'"

    if user_travel_details.departing_before:
        query += f" AND start_date <= '{user_travel_details.departing_before}'"

    if user_travel_details.max_duration:
        query += f" AND duration <= {user_travel_details.max_duration}"

    if user_travel_details.min_duration:
        query += f" AND duration >= {user_travel_details.min_duration}"

    client = bigquery.Client(project=PROJECT)
    query_job = client.query(query)
    result = query_job.result()
    df = result.to_dataframe()

    return list(df["tour_name"])
