# =============================================================================
# Stack Overflow Learning Hub - V6 (Database Fix)
# =============================================================================
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Learning Path", page_icon="📚", layout="wide")

# --- Check for Login ---
if not st.session_state.get("user_id"):
    st.warning(
        "Please connect your account on the Welcome page to explore your Learning Path."
    )
    st.stop()


# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_parquet("processed_data.parquet")


df = load_data()


# --- API Function ---
@st.cache_data(show_spinner="Fetching best answer from Stack Overflow...", ttl=3600)
def get_top_so_answer(question_id):
    api_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        "site": "stackoverflow",
        "order": "desc",
        "sort": "votes",
        "filter": "withbody",
    }
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        answers = response.json().get("items", [])
        if not answers:
            return "No answers found for this question on Stack Overflow."
        for answer in answers:
            if answer.get("is_accepted"):
                return answer.get("body")
        return answers[0].get("body")
    except requests.exceptions.RequestException as e:
        return f"Could not fetch answers from Stack Overflow. Error: {e}"


# --- UI and Logic ---
st.title("📚 Your Infinite Learning Path")
st.markdown(
    "Discover interesting and highly-rated questions based on your favorite topics. Select a tag to begin exploring."
)

user_tags = st.session_state.get("user_tags", [])

if not user_tags:
    st.info(
        "We couldn't find any tags from your profile. Start by using the Search page!"
    )
    st.stop()

# Create tabs for each of the user's top tags
selected_tag = st.radio(
    "**Choose one of your top tags to explore:**",
    options=user_tags,
    horizontal=True,
)

if selected_tag:
    st.subheader(f"Questions tagged with `{selected_tag}`")
    tagged_questions = (
        df[df["CleanTags"].str.contains(selected_tag, case=False, na=False)]
        .sort_values(by="Score", ascending=False)
        .head(20)
    )

    if not tagged_questions.empty:
        for _, row in tagged_questions.iterrows():
            with st.container(border=True):
                st.markdown(f"##### {row['Title']}")
                with st.expander("Show Top Answer from Stack Overflow"):
                    top_answer_body = get_top_so_answer(row["Id"])
                    st.markdown(top_answer_body, unsafe_allow_html=True)

                # "Find more like this" button
                if st.button(
                    "Find more questions like this", key=f"find_more_{row['Id']}"
                ):
                    st.session_state.search_query = row["Title"]
                    # --- FIX: Removed "pages/" prefix ---
                    st.switch_page("1_🔎_Search.py")
    else:
        st.write("No questions found in our dataset for this tag.")
