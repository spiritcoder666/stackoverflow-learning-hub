import streamlit as st
import requests
import os

# --- Define the file URLs and their local paths ---
# IMPORTANT: Replace these URLs with the ones you copied from your GitHub Release
FILES_TO_DOWNLOAD = {
    "faiss_index.bin": "https://github.com/spiritcoder666/stackoverflow-learning-hub/releases/download/v1.0/faiss_index.bin",
    "processed_data.parquet": "https://github.com/spiritcoder666/stackoverflow-learning-hub/releases/download/v1.0/processed_data.parquet",
}


def download_files_if_needed():
    """
    Checks if the necessary data files exist locally. If not, it downloads
    them from the URLs specified in FILES_TO_DOWNLOAD.
    This function is cached to run only once per session.
    """
    for local_filename, url in FILES_TO_DOWNLOAD.items():
        if not os.path.exists(local_filename):
            st.info(f"Downloading required file: {local_filename}... Please wait.")
            try:
                r = requests.get(url, stream=True)
                r.raise_for_status()  # Raise an exception for bad status codes
                with open(local_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                st.success(f"Downloaded {local_filename} successfully!")
            except requests.exceptions.RequestException as e:
                st.error(f"Error downloading {local_filename}: {e}")
                # Stop the app if a required file cannot be downloaded
                st.stop()


# ```

# **Crucial:** Remember to replace the placeholder URLs in this file with the actual URLs you copied from your GitHub release.

# ---

# #### **Step 3: Update Your App Pages to Call the Downloader**

# Now, we need to tell each of your pages that uses the data files to run our new downloader function first. This only requires adding two lines to each of the four page files.

# For example, in `pages/1_Search.py`, it would look like this:

# ```python
# # In pages/1_Search.py, pages/2_Learning_Path.py, etc.

import streamlit as st
from deployment_setup import download_files_if_needed  # <-- 1. IMPORT

# --- Run the downloader at the top of the script ---
download_files_if_needed()  # <-- 2. CALL THE FUNCTION

# --- Check for Login ---
if not st.session_state.get("user_id"):
    st.warning("Please connect your account...")
    st.stop()

# ... rest of the file continues as normal ...
