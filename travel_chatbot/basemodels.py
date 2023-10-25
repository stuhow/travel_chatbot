from typing import Optional
from pydantic import BaseModel, Field

class UserInterests(BaseModel):
    interest: Optional[str] = Field(
        None,
        description="""Any experiances, interests, places or activities the user has expressed an interest in.
        Do not include a Months, Country name or tour types. Leave blank if none are mentioned""",
    )


class TravelDetails(BaseModel):
    introduction: Optional[bool] = Field(
        False,
        description="Has francis introducted himself and asked if the user is interested in a group tour.",
    )
    qualification: Optional[str] = Field(
        None,
        description="Did the user confirm they are looking for a group tour or answer positivley when asked. If the user asks about a trip assume the answer is yes",
        enum=["Yes", "No", "Unsure"]
    )
    country: Optional[str] = Field(
        "",
        description="This is the name of the country the user is wanting to visit. If they name a place within a country always return the country",
        enum=['Nicaragua', 'Jordan', 'New Zealand', 'Colombia', 'Maldives', 'Uzbekistan', 'Monaco', 'Italy', 'Austria', 'Iceland', 'Argentina', 'Oman',
                'Malaysia', 'Poland', 'Bosnia and Herzegovina', 'Laos', 'Hungary', 'Zambia', 'Bhutan', 'United States', 'Turkey', 'Morocco', 'Montenegro',
                'Serbia', 'Belgium', 'China', 'Peru', 'Israel', 'Egypt', 'Netherlands', 'Indonesia', 'Sri Lanka', 'Czech Republic',  'Honduras', 'Mexico',
                'Madagascar', 'Greece', 'Cuba', 'Kenya', 'Turkmenistan', 'Belize', 'Portugal', 'Cambodia', 'Rwanda', 'Botswana', 'Spain', 'India', 'Switzerland',
                'Australia', 'Uruguay', 'Uganda', 'Namibia', 'Croatia', 'France', 'South Korea', 'Brazil', 'Zimbabwe', 'Chile', 'Thailand', 'South Africa',
                'El Salvador', 'Nepal', 'Japan', 'Guatemala', 'Bolivia', 'Slovenia', 'Germany', 'Ecuador', 'Singapore', 'Vietnam', 'Costa Rica', 'Tanzania', 'Malawi']
    )

    departing_after: Optional[str] = Field(
        "",
        description="This is the first date from which the user can depart. If the user gives a month assume this is the first of the month. If year is not given assume 2024. In the format '%Y-%m-%d'",
    )
    departing_before: Optional[str] = Field(
        "",
        description="This is the last date from which the user can depart. If the user gives a month assume this is the last day of the month. If year is not given assume 2024. In the format '%Y-%m-%d'",
    )
    max_budget: Optional[int] = Field(
        0,
        description="This is the maximun amount of money the user is looking to spend on their trip.",
    )
    max_duration: Optional[int] = Field(
        None,
        description="This is the maximum duration of their trip."
    )
    min_duration: Optional[int] = Field(
        None,
        description="This is the minimum duration of their trip.",
    )
