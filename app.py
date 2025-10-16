# =============================================================================
# Stack Overflow Learning Hub - V7 (Final UI and Fixes)
# =============================================================================
import streamlit as st
import requests
from PIL import Image
import io
from db_functions import load_user_data, save_user_data, init_db

init_db()

st.set_page_config(
    page_title="Welcome - SO Learning Hub", page_icon="👋", layout="centered"
)

# Session State Initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.display_name = None
    st.session_state.profile_image = None
    st.session_state.user_tags = []
    st.session_state.saved_questions = []
    st.session_state.search_history = []


# API Function
@st.cache_data(ttl=3600)
def get_so_user_info(user_id):
    api_url = f"https://api.stackexchange.com/2.3/users/{user_id}?site=stackoverflow"
    tags_url = f"https://api.stackexchange.com/2.3/users/{user_id}/tags?site=stackoverflow&pagesize=10&order=desc&sort=popular"
    try:
        user_response = requests.get(api_url)
        user_response.raise_for_status()
        user_data = user_response.json().get("items", [])[0]
        tags_response = requests.get(tags_url)
        tags_response.raise_for_status()
        tags_data = tags_response.json().get("items", [])
        return {
            "display_name": user_data.get("display_name"),
            "profile_image_url": user_data.get("profile_image"),
            "tags": [tag["name"] for tag in tags_data],
        }
    except (requests.exceptions.RequestException, IndexError):
        return None


# Main App Logic
if not st.session_state.user_id:
    st.title("Welcome to the SO Learning Hub 👋")
    st.markdown(
        "Connect your Stack Overflow account to get personalized recommendations and start your learning journey."
    )
    so_user_id = st.text_input(
        "Enter your Stack Overflow User ID",
        help="You can find this in the URL of your user profile.",
    )
    if st.button("Connect Account", type="primary"):
        if so_user_id:
            with st.spinner("Connecting to your account..."):
                db_data = load_user_data(so_user_id)
                api_info = get_so_user_info(so_user_id)
                if api_info:
                    st.session_state.user_id = so_user_id
                    st.session_state.display_name = api_info["display_name"]
                    if db_data:
                        st.session_state.user_tags = sorted(
                            list(set(api_info["tags"] + db_data["tags"]))
                        )
                        st.session_state.saved_questions = db_data["questions"]
                        st.session_state.search_history = db_data["history"]
                    else:
                        st.session_state.user_tags = api_info["tags"]
                        st.session_state.saved_questions = []
                        st.session_state.search_history = []
                        save_user_data(
                            so_user_id,
                            st.session_state.user_tags,
                            st.session_state.saved_questions,
                            st.session_state.search_history,
                        )
                    if api_info["profile_image_url"]:
                        response = requests.get(api_info["profile_image_url"])
                        st.session_state.profile_image = Image.open(
                            io.BytesIO(response.content)
                        )
                    st.success("Account connected successfully!")
                    st.rerun()
                else:
                    st.error(
                        "Could not find a user with that ID. Please check and try again."
                    )
        else:
            st.warning("Please enter a User ID.")
else:
    # --- THIS IS THE RESTORED, IMPROVED UI WITH CORRECTED NAVIGATION ---
    st.title(f"Welcome back, {st.session_state.display_name}!")
    st.markdown(
        "This is your personalized learning dashboard. What would you like to do today?"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.session_state.profile_image:
            st.image(st.session_state.profile_image, width=150)
    with col2:
        st.subheader("Your Technical Interests")
        st.write(" ".join([f"`{tag}`" for tag in st.session_state.user_tags]))

    st.markdown("---")
    st.subheader("Start Exploring")

    # --- REFINED & ALIGNED 3-COLUMN LAYOUT ---
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("#### 💡My Recommendations")
            st.write(
                "Discover what to learn next based on your recent search activity."
            )

            if st.button("Go to Recommendations", use_container_width=True):
                st.switch_page("pages/4_Recommendations.py")

    with col2:
        with st.container(border=True):
            st.markdown("#### 🔎 Search for a Solution")
            st.write(
                "Have a specific problem? Find the most relevant, real-world solutions."
            )
            if st.button("Go to Search Page", use_container_width=True):
                st.switch_page("pages/1_Search.py")

    with col3:
        with st.container(border=True):
            st.markdown("#### 📚 Explore Your Learning Path")
            st.write("Explore highly-rated questions based on your favorite tags.")
            if st.button("Explore Learning Path", use_container_width=True):
                st.switch_page("pages/2_Learning_Path.py")
