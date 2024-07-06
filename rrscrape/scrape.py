import copy
from datetime import datetime as dt
import json
import os
from typing import Union, Dict

import requests
from bs4 import BeautifulSoup
import openai

from consts import GENERAL_COLUMNS, RR_COLUMNS, VALUE_TYPES
from general_utils import fix_json_string, normalize_vals


def llm_fill_values(data: Dict[str, VALUE_TYPES], model="gpt-4o", attempts: int = 2) -> Dict[str, VALUE_TYPES]:
    """
    Uses a Large Language Model to go over the data and try to infer missing values which require some holistic
    understanding of the data. Only fill in values that are missing (None) in the data dictionary.

    :param data: Dictionary containing data with potentially missing values (None).
    :param model: Optional string specifying the model to use (default is "gryphe/mythomax-l2-13b").
    :param attempts: Optional integer specifying the number of attempts to make to fill in the missing values.
    :return: Updated dictionary with inferred missing values.
    """
    if None not in data.values():  # If there are no missing values - return
        return data
    res = copy.deepcopy(data)  # make this a pure function
    missing, filled = [], {}  # Collate missing and filled values
    for k, v in res.items():
        if v is None:
            missing.append(k)
        else:
            filled[k] = v
    filled_formatted = "\n".join([f"{k}: {v}" for k, v in filled.items()])
    client = openai.Client(
        api_key=os.environ.get("OPENAI_API_KEY"),
        base_url=os.environ.get("OPENAI_API_BASE"),
    )
    prompt = f"""
You are a working on a project to analyze web serial stories from RoyalRoad. You have collected some data from a story, but some values are missing.
Below is data collected from a RoyalRoad story. RoyalRoad stories are mostly Progression Fantasy. MC means Main Character. 
Please use it to try to fill in the missing values listed at the end of this message. 

===COLLECTED DATA===
{filled_formatted}
===END COLLECTED DATA===

===KEYS FOR MISSING VALUES===
{set(missing)}
===END KEYS FOR MISSING VALUES===
If you cannot be reasonably sure of a value with the given data, put in null instead. 
Output: json-format response of the keys and filled values. Format it in one line, no linebreaks, no preamble - straight to the json! Only fill in missing values. Do not return any of the existing data.
    """
    tentative_values = {}
    for attempt in range(attempts):
        # Call OpenAI API to fill missing value using the model
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}],
            max_tokens=200,
            temperature=0.25,
            response_format={"type": "json_object"},
        )
        # Extract filled value from API response
        response_text = response.choices[0].message.content.strip()
        # remove preamble before parsing JSON (e.g., "Here is your json: {...")
        json_start_idx = response_text.find("{")
        try:
            tentative_values = json.loads(response_text[json_start_idx:])
            break
        except ValueError:  # if the response is not valid JSON.
            tentative_values = fix_json_string(response_text[json_start_idx:])
            print(f"Invalid JSON response: {response.choices[0].message.content}")
            if attempt == attempts - 1:
                raise ValueError(f"Failed to parse LLM JSON response in {attempts} attempts.")
    if len(tentative_values) == 0:
        return data
    for key in missing:
        if tentative_values[key] in (None, "null"):  # assume that json parsed 'null' into None, but verify
            res[key] = None
        else:
            res[key] = tentative_values[key]

    return res


def rr_scrape(url: str) -> Dict[str, VALUE_TYPES]:
    """
    Scrapes a RoyalRoad story page and extracts relevant information.

    This function visits a RoyalRoad story page and extracts various statistics about the story,
    such as the title, author, overall rating, average views, followers, tags, warnings, and favorites.
    The extracted data is normalized and returned as a dictionary.

    Args:
        url (str): The URL of the RoyalRoad story page to scrape.
    Returns:
        Dict[str, Union[str, int, float]]: A dictionary containing the extracted data. The keys of the dictionary
        correspond to the column names in the final dataset, and the values are the extracted data.

    Raises:
        ValueError: If the value is a score or a count string but cannot be converted to a float or an integer.
    """
    soup = BeautifulSoup(requests.get(url).content, "lxml")
    data = {
        "RR Retrieved at": dt.now().strftime("%Y-%m-%d"),
        "RR URL": url,
        "RR Title": soup.find("div", class_="row fic-header").find("h1").text.strip(),
        "RR Author": soup.find("div", class_="row fic-header").find("a").text.strip(),
        "RR Thumbnail URL": soup.find("img", class_="thumbnail inline-block").get("src").split("?")[0],
        **{col: None for col in GENERAL_COLUMNS},
    }

    stats_container = soup.find("div", class_="stats-content")
    if stats_container:
        # Extract overall, style, story, grammar, and character scores
        scores = stats_container.find_all("span", class_="star")
        for score in scores:
            title = "RR " + score.get("data-original-title")
            value = score.get("data-content")
            if title in RR_COLUMNS:
                data[title] = value
        # Extract other stats
        stats_list = stats_container.find_all(
            "li", class_="bold uppercase font-red-sunglo"
        )  # TODO - find better way to do this so that it doesn't break
        data["RR Total Views"] = stats_list[0].text.strip()
        data["RR Average Views"] = stats_list[1].text.strip()
        data["RR Followers"] = stats_list[2].text.strip()
        data["RR Favorites"] = stats_list[3].text.strip()
        data["RR Ratings"] = stats_list[4].text.strip()
        data["RR Pages"] = stats_list[5].text.strip()
    else:
        print("Stats container not found")

    info_container = soup.find("div", class_="fiction-info")
    data["RR Tags"] = ", ".join(tag.text.strip() for tag in info_container.find("span", class_="tags").find_all("a"))

    data["RR Warnings"] = ", ".join(
        warning.text.strip() for warning in info_container.find("ul", class_="list-inline").find_all("li")
    )

    data["RR Blurb"] = "\n".join(
        row.text.strip().replace("\xa0", " ") for row in info_container.find("div", class_="description")
    )

    try:
        relevant_data = {
            k: v
            for k, v in data.items()
            if k
            in GENERAL_COLUMNS
            + [
                "RR Blurb",
                "RR Tags",
                "RR Warnings",
                "RR Title",
            ]
        }
        inferred_data = llm_fill_values(relevant_data)
    except ValueError as e:
        print(f"Error filling missing values: {e}")
        raise e
    data.update(inferred_data)
    data = {k: normalize_vals(v) for k, v in data.items()}

    return data


def example_for_debug():
    urls = [
        "https://www.royalroad.com/fiction/76259/ultimate-level-1",
        "https://www.royalroad.com/fiction/45048/hive-minds-give-good-hugs",
        "https://www.royalroad.com/fiction/36299/beneath-the-dragoneye-moons",
        "https://www.royalroad.com/fiction/52854/an-unwavering-craftsman"
    ]
    rr_dicts = []
    for url in urls:
        curr_dict = rr_scrape(url)
        rr_dicts.append(curr_dict)
    print("stop here")


if __name__ == "__main__":
    example_for_debug()
