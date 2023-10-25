from google.cloud import bigquery

PROJECT = "wagon-bootcamp-377120"
DATASET = "g_adventures_dataset"
TABLE = "one_month"


def list_column_names():
    client = bigquery.Client(project=PROJECT)
    dataset_ref = client.dataset(DATASET)
    table_ref = dataset_ref.table(TABLE)

    # Get the table schema
    table = client.get_table(table_ref)

    # Extract and return the column names
    column_names = [field.name for field in table.schema]

    filtered_categories = [category for category in column_names if "Adult" in category and "Promotion Description" not in category]

    return filtered_categories

def list_all_column_names():
    client = bigquery.Client(project=PROJECT)
    dataset_ref = client.dataset(DATASET)
    table_ref = dataset_ref.table(TABLE)

    # Get the table schema
    table = client.get_table(table_ref)

    # Extract and return the column names
    column_names = [field.name for field in table.schema]

    return column_names

def bq_single_itinerary_query(user_travel_details, found_itineraries):

    all_columns = list_all_column_names()
    all_columns_str = ",\n".join(all_columns)
    all_columns_str = all_columns_str + ","

    room_categories = [category for category in all_columns if "Adult" in category and "Promotion Description" not in category]

    category_cases = []

    for category in room_categories:
        category_case = f"CASE WHEN {category} > 0 THEN {category} ELSE 1000000 END"
        category_cases.append(category_case)

    category_cases_str = ",\n".join(category_cases)

    query = f"""
    SELECT
        MAX(tour_operator) AS tour_operator,
        tour_name,
        itinerary_name,
        MAX(visited_countries) AS visited_countries,
        MAX(currency) AS currency,
        ARRAY_AGG(DISTINCT cost) AS Costs,
        MAX(duration) AS duration,
        ARRAY_AGG(CAST(start_date AS STRING) ORDER BY start_date) AS start_dates,
        MAX(Travel_Style) AS Travel_Style,
        MAX(Service_Level) AS Service_Level,
        MAX(Physical_Grading) AS Physical_Grading,
        MAX(Merchandising) AS Merchandising,
        MAX(Trip_Type) AS Trip_Type,
        MAX(itinerary) AS itinerary,
        MAX(url) AS url
    FROM (
        SELECT
            {all_columns_str}
            LEAST(
                {category_cases_str}
            ) AS cost
        FROM {PROJECT}.{DATASET}.{TABLE}
    ) AS subquery
        WHERE 1 = 1
        """


    # Iterate through the provided filter criteria and add them to the query
    if user_travel_details.max_budget:
        query += f" AND cost <= {user_travel_details.max_budget}"

    if user_travel_details.departing_after:
        query += f" AND start_date >= '{user_travel_details.departing_after}'"

    if user_travel_details.departing_before:
        query += f" AND start_date <= '{user_travel_details.departing_before}'"

    query += f""" AND tour_name = '{found_itineraries[0]}'
    GROUP BY
        tour_name, itinerary_name;"""

    return query

def bq_multiple_itinerary_query(user_travel_details, found_itineraries):

    found_itineraries_string = ', '.join(["'" + item + "'" for item in found_itineraries])

    all_columns = list_all_column_names()
    all_columns_str = ",\n".join(all_columns)
    all_columns_str = all_columns_str + ","

    room_categories = [category for category in all_columns if "Adult" in category and "Promotion Description" not in category]

    category_cases = []

    for category in room_categories:
        category_case = f"CASE WHEN {category} > 0 THEN {category} ELSE 1000000 END"
        category_cases.append(category_case)

    category_cases_str = ",\n".join(category_cases)

    query = f"""
    SELECT
        MAX(tour_operator) AS tour_operator,
        tour_name,
        itinerary_name,
        MAX(visited_countries) AS visited_countries,
        MAX(currency) AS currency,
        ARRAY_AGG(DISTINCT cost) AS Costs,
        MAX(duration) AS duration,
        ARRAY_AGG(CAST(start_date AS STRING) ORDER BY start_date) AS start_dates,
        MAX(Travel_Style) AS Travel_Style,
        MAX(Service_Level) AS Service_Level,
        MAX(Physical_Grading) AS Physical_Grading,
        MAX(Merchandising) AS Merchandising,
        MAX(Trip_Type) AS Trip_Type,
        MAX(itinerary) AS itinerary,
        MAX(url) AS url
    FROM (
        SELECT
            {all_columns_str}
            LEAST(
                {category_cases_str}
            ) AS cost
        FROM {PROJECT}.{DATASET}.{TABLE}
    ) AS subquery
        WHERE 1 = 1
        """


    # Iterate through the provided filter criteria and add them to the query
    if user_travel_details.max_budget:
        query += f" AND cost <= {user_travel_details.max_budget}"

    if user_travel_details.departing_after:
        query += f" AND start_date >= '{user_travel_details.departing_after}'"

    if user_travel_details.departing_before:
        query += f" AND start_date <= '{user_travel_details.departing_before}'"

    query += f""" AND tour_name in ({found_itineraries_string})
    GROUP BY
        tour_name, itinerary_name;"""

    return query

def bq_filter_query(user_travel_details):

    room_categories = list_column_names()

    category_cases = []

    for category in room_categories:
        category_case = f"CASE WHEN {category} > 0 THEN {category} ELSE 1000000 END"
        category_cases.append(category_case)

    category_cases_str = ",\n".join(category_cases)

    query = f"""
    SELECT *
FROM (
    SELECT
        tour_name,
        itinerary_name,
        visited_countries,
        start_date,
        duration,
        LEAST(
            {category_cases_str}
        ) AS cost
    FROM {PROJECT}.{DATASET}.{TABLE}
) AS subquery
    WHERE 1 = 1
    """
    # Iterate through the provided filter criteria and add them to the query
    if user_travel_details.country:
        query += f" AND visited_countries LIKE '%{user_travel_details.country}%'"

    if user_travel_details.max_budget:
        query += f" AND cost <= {user_travel_details.max_budget}"

    # if user_travel_details.min_budget:
    #     query += f" AND cost >= {user_travel_details.min_budget}"

    if user_travel_details.departing_after:
        query += f" AND start_date >= '{user_travel_details.departing_after}'"

    if user_travel_details.departing_before:
        query += f" AND start_date <= '{user_travel_details.departing_before}'"

    if user_travel_details.max_duration:
        query += f" AND duration <= {user_travel_details.max_duration}"

    if user_travel_details.min_duration:
        query += f" AND duration >= {user_travel_details.min_duration}"

    return query
