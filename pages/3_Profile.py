# =============================================================================
# Stack Overflow Learning Hub - V7 (Navigation Fix)
# =============================================================================
import streamlit as st
import pandas as pd

# Import our database function
from db_functions import save_user_data

st.set_page_config(page_title="My Profile", page_icon="👤", layout="wide")

# --- Check for Login ---
if not st.session_state.get("user_id"):
    st.warning("Please connect your account on the Welcome page to view your profile.")
    st.stop()


# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_parquet("processed_data.parquet")


df = load_data()

# --- UI and Logic ---
st.title(f"👤 Profile & Settings for {st.session_state.display_name}")

# --- Section 1: Manage Interests ---
with st.container(border=True):
    st.subheader("Manage Your Interests")
    st.write(
        "Your recommendations are personalized based on these tags. You can add new tags or remove existing ones."
    )

    # A function to simplify saving ALL data to the DB
    def update_db():
        # It now correctly passes the search_history list
        save_user_data(
            st.session_state.user_id,
            st.session_state.user_tags,
            st.session_state.saved_questions,
            st.session_state.search_history,
        )

    # Display current tags with a remove button for each
    for tag in list(st.session_state.user_tags):  # Iterate over a copy
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"`{tag}`")
        with col2:
            if st.button("Remove", key=f"remove_{tag}"):
                st.session_state.user_tags.remove(tag)
                update_db()  # Save changes
                st.rerun()

    # Add a new tag
    new_tag = st.text_input(
        "Add a new tag to your interests:", placeholder="e.g., machine-learning"
    )
    if st.button("Add Tag"):
        if new_tag and new_tag not in st.session_state.user_tags:
            st.session_state.user_tags.append(new_tag)
            update_db()  # Save changes
            st.rerun()
        elif not new_tag:
            st.warning("Please enter a tag to add.")
        else:
            st.info("This tag is already in your list.")

# --- Section 2: Saved Recommendations ---
with st.container(border=True):
    st.subheader("📚 Your Saved Recommendations")
    saved_ids = st.session_state.get("saved_questions", [])

    if not saved_ids:
        st.info(
            "You haven't saved any questions yet. Use the 'Save for Later' button on the Search page!"
        )
    else:
        st.write("Here are the questions you've saved for future reference.")
        saved_questions_df = df[df["Id"].isin(saved_ids)]

        for _, row in saved_questions_df.iterrows():
            question_id = row["Id"]
            st.markdown(f"##### {row['Title']}")
            st.caption(f"Tags: `{row['CleanTags']}`")
            with st.expander("Show Answer"):
                answer = row["Answer"]
                if answer == "LQ_CLOSE":
                    st.info(
                        "This question was closed as low-quality on Stack Overflow and does not have a formal answer."
                    )
                else:
                    st.markdown(answer, unsafe_allow_html=True)
            if st.button("Remove from Saved", key=f"unsave_{question_id}"):
                st.session_state.saved_questions.remove(question_id)
                update_db()  # Save changes
                st.rerun()
            st.markdown("---")

# --- Section 3: Account ---
with st.container(border=True):
    st.subheader("Account")
    if st.button("Log Out", type="primary"):
        for key in st.session_state.keys():
            del st.session_state[key]
        # --- FIX: Use correct path and new filename ---
        st.switch_page("app.py")
