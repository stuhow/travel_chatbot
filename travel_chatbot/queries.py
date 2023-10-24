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
