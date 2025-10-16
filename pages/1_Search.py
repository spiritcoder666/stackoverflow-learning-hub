# =============================================================================
# Stack Overflow Learning Hub - V8 (Deployment Fix)
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import re
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import requests
from db_functions import save_user_data
# --- 1. IMPORT THE DOWNLOADER ---
from deployment_setup import download_files_if_needed

# --- 2. RUN THE DOWNLOADER AT THE START ---
download_files_if_needed()

st.set_page_config(page_title="Search", page_icon="🔎", layout="wide")

# Check for Login
if not st.session_state.get("user_id"):
    st.warning("Please connect your account on the Welcome page to use the search.")
    st.stop()

# Caching & Loading
@st.cache_resource
def load_model(): return SentenceTransformer('all-MiniLM-L6-v2')
@st.cache_resource
def load_faiss_index(): return faiss.read_index('faiss_index.bin')
@st.cache_data
def load_data(): return pd.read_parquet('processed_data.parquet')

model, index, df = load_model(), load_faiss_index(), load_data()

# Preprocessing & API Functions
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
def preprocess_text(text):
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    tokens = [word for word in text.split() if word not in stop_words]
    return " ".join([lemmatizer.lemmatize(word) for word in tokens])

@st.cache_data(show_spinner="Fetching best answer...", ttl=3600)
def get_top_so_answer(question_id):
    api_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {"site": "stackoverflow", "order": "desc", "sort": "votes", "filter": "withbody"}
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        answers = response.json().get("items", [])
        if not answers: return "No answers found."
        for answer in answers:
            if answer.get("is_accepted"): return answer.get("body")
        return answers[0].get("body")
    except requests.exceptions.RequestException as e:
        return f"Could not fetch answers. Error: {e}"

# Hybrid Search
def find_similar_questions(query, top_k=5, user_tags=None):
    processed_query = preprocess_text(query)
    query_embedding = model.encode([processed_query])
    faiss.normalize_L2(query_embedding)
    search_k = min(len(df), top_k * 20)
    distances, indices = index.search(query_embedding.astype(np.float32), search_k)
    semantic_results_df = df.iloc[indices[0]].copy()
    semantic_results_df['Similarity'] = distances[0]
    semantic_results_df['is_exact_match'] = False
    exact_match_df = df[df['Title'].str.lower() == query.lower()].copy()
    if not exact_match_df.empty:
        exact_match_df['Similarity'] = 1.0
        exact_match_df['is_exact_match'] = True
    combined_df = pd.concat([exact_match_df, semantic_results_df]).drop_duplicates(subset=['Id'], keep='first')
    final_results = combined_df
    final_results['PersonalizationScore'] = final_results['CleanTags'].apply(lambda tags: 1 if user_tags and any(tag in tags for tag in user_tags) else 0)
    final_results['CombinedScore'] = (0.9 * final_results['Similarity']) + (0.1 * final_results['PersonalizationScore'])
    final_results.loc[final_results['is_exact_match'], 'CombinedScore'] = 1.0
    return final_results.sort_values(by='CombinedScore', ascending=False).head(top_k)

# UI
st.title("🔎 Find Real Stack Overflow Solutions")
st.markdown("Describe your problem to find the best existing questions and their top-rated answers.")
query = st.text_input("**Enter your question or problem description**", placeholder="e.g., how to sort a python dictionary by value", key="search_query")

if query:
    user_tags = st.session_state.get("user_tags", [])
    recommendations = find_similar_questions(query, top_k=5, user_tags=user_tags)

    if not recommendations.empty:
        top_result_id = recommendations.iloc[0]['Id']
        if top_result_id not in st.session_state.search_history:
            st.session_state.search_history.append(top_result_id)
            save_user_data(
                st.session_state.user_id,
                st.session_state.user_tags,
                st.session_state.saved_questions,
                st.session_state.search_history
            )

    st.subheader("🏆 Top Recommended Questions")
    if not recommendations.empty:
        for _, row in recommendations.iterrows():
            question_id = row['Id']
            with st.container(border=True):
                if row['PersonalizationScore'] > 0: st.markdown("⭐ **Personalized for you!**")
                st.markdown(f"#### [{row['Title']}](https://stackoverflow.com/q/{question_id})")
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1: st.caption(f"Tags: `{row['CleanTags']}`")
                with col2: st.metric(label="Relevance", value=f"{row['CombinedScore']:.2f}")
                with col3:
                    if question_id in st.session_state.get("saved_questions", []):
                        st.button("✅ Saved", key=f"save_{question_id}", disabled=True)
                    else:
                        if st.button("💾 Save for Later", key=f"save_{question_id}"):
                            st.session_state.saved_questions.append(question_id)
                            save_user_data(st.session_state.user_id, st.session_state.user_tags, st.session_state.saved_questions, st.session_state.search_history)
                            st.rerun()
                with st.expander("Show Top Answer from Stack Overflow"):
                    st.markdown(get_top_so_answer(question_id), unsafe_allow_html=True)
    else:
        st.warning("No related questions found in the dataset.")
