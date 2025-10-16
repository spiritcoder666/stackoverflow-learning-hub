# =============================================================================
# Stack Overflow Learning Hub - V7 (Enhanced Recommendations)
# =============================================================================
import streamlit as st
import pandas as pd
from collections import Counter
import requests
import numpy as np
import re

st.set_page_config(page_title="Recommendations", page_icon="💡", layout="wide")

# --- Check for Login ---
if not st.session_state.get("user_id"):
    st.warning("Please connect your account to get personalized recommendations.")
    st.stop()


# --- Load Data & Functions ---
@st.cache_data
def load_data():
    return pd.read_parquet("processed_data.parquet")


df = load_data()


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


# --- Recommendation Logic ---
def get_user_topic_ranking(history_df):
    """Analyzes search history to rank topics by recency and frequency."""
    if history_df.empty:
        return []
    recency_weights = np.linspace(1, 2, len(history_df))
    weighted_tags = []
    tags_list = history_df["CleanTags"].fillna("").str.split().tolist()
    for i, tags in enumerate(tags_list):
        for tag in tags:
            if tag:
                weighted_tags.extend([tag] * int(recency_weights[i]))
    tag_counts = Counter(weighted_tags)
    ranked_tags = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
    return [tag for tag, count in ranked_tags][:7]


def get_recommendations_for_tag(tag, history_df, num_recs=5):
    """Gets progressive learning recommendations for a specific tag."""
    escaped_tag = r"\b" + re.escape(tag) + r"\b"
    tag_questions = df[df["CleanTags"].str.contains(escaped_tag, regex=True, na=False)]
    seen_ids = history_df["Id"].tolist()
    unseen_questions = tag_questions[~tag_questions["Id"].isin(seen_ids)].copy()
    if unseen_questions.empty:
        return pd.DataFrame()
    unseen_questions.loc[:, "title_length"] = unseen_questions["Title"].str.len()
    return unseen_questions.sort_values(by="title_length", ascending=True).head(
        num_recs
    )


# --- NEW: Master "All" Recommendation Logic ---
def get_all_recommendations(history_df, profile_tags, num_recs=10):
    """Generates a master list of recommendations based on all factors."""
    if history_df.empty:
        return pd.DataFrame()

    # 1. Create a relevance score for each recent topic
    ranked_topics = get_user_topic_ranking(history_df)
    topic_scores = {
        topic: len(ranked_topics) - i for i, topic in enumerate(ranked_topics)
    }

    # 2. Filter out questions already seen in search history
    seen_ids = history_df["Id"].tolist()
    unseen_questions = df[~df["Id"].isin(seen_ids)].copy()

    # 3. Define a function to calculate a relevance score for each question
    def calculate_relevance(row):
        score = 0
        tags = set(row["CleanTags"].split())
        # Add points based on recent search activity
        for tag in tags:
            score += topic_scores.get(tag, 0)
        # Add a bonus if tags match profile interests
        if any(tag in profile_tags for tag in tags):
            score += 2  # Bonus points for profile match
        return score

    # 4. Calculate scores and add a difficulty metric
    unseen_questions["relevance"] = unseen_questions.apply(calculate_relevance, axis=1)
    unseen_questions["title_length"] = unseen_questions["Title"].str.len()

    # 5. Sort by relevance, then by difficulty as a tie-breaker
    return unseen_questions.sort_values(
        by=["relevance", "title_length"], ascending=[False, True]
    ).head(num_recs)


# --- UI ---
st.title("💡 Your Personalized Recommendations")
st.markdown(
    "Based on your search history and interests, here are some topics and questions we think you should explore next."
)

search_history_ids = st.session_state.get("search_history", [])
profile_tags = st.session_state.get("user_tags", [])
history_df = df[df["Id"].isin(search_history_ids)]

if not search_history_ids:
    st.info(
        "Start searching on the 'Search' page to get personalized recommendations here!"
    )
    st.stop()

ranked_topics = get_user_topic_ranking(history_df)
# Prepend "All" to the list of topics
display_topics = ["All"] + ranked_topics

if not ranked_topics:
    st.info("We couldn't determine your interests yet. Make a few more searches.")
    st.stop()

selected_topic = st.radio(
    "**Choose a topic to explore (most relevant topics appear first):**",
    options=display_topics,
    horizontal=True,
)

if selected_topic == "All":
    st.subheader("Top Recommendations For You")
    recommendations = get_all_recommendations(history_df, profile_tags)
else:
    st.subheader(f"Next Steps for `{selected_topic}`")
    recommendations = get_recommendations_for_tag(selected_topic, history_df)

if not recommendations.empty:
    for _, row in recommendations.iterrows():
        with st.container(border=True):
            st.markdown(f"##### {row['Title']}")
            st.caption(f"Tags: `{row['CleanTags']}`")
            with st.expander("Show Top Answer from Stack Overflow"):
                st.markdown(get_top_so_answer(row["Id"]), unsafe_allow_html=True)
else:
    st.write(
        "No new recommendations found for this topic. Try searching for something new!"
    )
