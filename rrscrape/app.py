import os
import time

import pandas as pd
import openai
import streamlit as st
from openai import AuthenticationError, APIError
from typing import Optional, Dict, List

from consts import VALUE_TYPES, COLS_ORDER
from scrape import rr_scrape

st.set_page_config(layout="wide", page_title="rrscrape", page_icon=":fire:")


def is_valid_openai_key(api_key: str, base_url: Optional[str] = "https://api.openai.com/v1") -> bool:
    try:
        _ = openai.Client(api_key=api_key, base_url=base_url).models.list()
        return True
    except (AuthenticationError, APIError) as e:
        st.error(f"Validation failed: {e}")
        return False


def initialize_session_state():
    if "url" not in st.session_state:
        st.session_state.url = ""
    if "urls" not in st.session_state:
        st.session_state.urls = []
    if "data" not in st.session_state:
        st.session_state.data = []
    if "api_key_valid" not in st.session_state:
        st.session_state.api_key_valid = False


@st.cache_data
def convert_df(data: List[Dict[str, VALUE_TYPES]], columns: List[str]) -> bytes:
    df = pd.DataFrame(data, columns=columns)
    return df.to_csv(index=False).encode("utf-8")


def submit_url():
    if st.session_state.url in st.session_state.urls:
        st.warning(f"URL {st.session_state.url} has already been scraped.")
        return
    try:
        st.session_state.urls.append(st.session_state.url)
        row_data = rr_scrape(st.session_state.url)
        st.session_state.data.append(row_data)
        st.session_state.url = ""
    except Exception as e:
        st.error(f"Failed to scrape URL: {st.session_state.url}. Error: {e}")


def main():
    st.title("RoyalRoad Scraper :fire:")

    initialize_session_state()

    if not st.session_state.api_key_valid:
        with st.form("api_key_form"):
            api_key = st.text_input("Enter your OpenAI API key", type="password")
            base_url = st.text_input("Base URL (optional)", value="https://api.openai.com/v1")
            submit_button = st.form_submit_button("Get to scrapin'")

        if submit_button:
            if is_valid_openai_key(api_key, base_url):
                os.environ["OPENAI_API_KEY"] = api_key
                os.environ["OPENAI_API_BASE"] = base_url
                st.session_state.api_key_valid = True
                container = st.empty()
                container.success("API key and base URL validated successfully!")
                time.sleep(1)
                container.empty()
                st.rerun()
            else:
                st.error("Invalid API key or base URL. Please try again.")
    if st.session_state.api_key_valid:
        st.text_input("URL", key="url", on_change=submit_url)

        if len(st.session_state.data) > 0:
            st.dataframe(pd.DataFrame(st.session_state.data, columns=COLS_ORDER))


if __name__ == "__main__":
    main()
