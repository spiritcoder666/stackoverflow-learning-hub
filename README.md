
🚀 Stack Overflow Learning Hub 🚀

An intelligent, multi-page web application that transforms Stack Overflow into a personalized learning platform. This app analyzes your interests and search history to provide adaptive recommendations and a guided path to mastering new skills.

<p align="center">
<img src="https://www.google.com/search?q=https://placehold.co/800x400/2E3B4E/FFFFFF%3Ftext%3DAdd%2Ba%2BGIF%2Bof%2Byour%2Bapp%2Bin%2Baction!%26font%3Dsans" alt="Demo GIF placeholder">
</p>
<p align="center">
<i>(It is highly recommended to replace the image above with a GIF showcasing your app!)</i>
</p>

<p align="center">
<img alt="Python" src="https://www.google.com/search?q=https://img.shields.io/badge/Python-3.10%252B-blue%3Fstyle%3Dfor-the-badge%26logo%3Dpython">
<img alt="Streamlit" src="https://www.google.com/search?q=https://img.shields.io/badge/Streamlit-1.30.0%252B-red%3Fstyle%3Dfor-the-badge%26logo%3Dstreamlit">
<img alt="Framework" src="https://www.google.com/search?q=https://img.shields.io/badge/Framework-FAISS-brightgreen%3Fstyle%3Dfor-the-badge">
<img alt="Database" src="https://www.google.com/search?q=https://img.shields.io/badge/Database-SQLite-blueviolet%3Fstyle%3Dfor-the-badge%26logo%3Dsqlite">
</p>

✨ Core Features

👋 Personalized Dashboard: Connects to your Stack Overflow account via your User ID to load your profile picture and top tags, creating a personalized welcome experience.

🔎 Hybrid Search Engine: A powerful search that combines:

Exact Match: Guarantees a perfect 1.0 relevance score for questions copied directly from the dataset.

Semantic Search: Uses sentence-transformers and FAISS to find conceptually similar questions, even if the wording is different.

💡 Adaptive Recommendations: A dedicated "Recommendations" page that analyzes your search history to rank relevant topics. It prioritizes your most recent interests and suggests "next-step" questions you haven't seen before.

📚 Structured Learning Paths: Allows you to manually explore topics based on your saved profile tags, providing a structured, library-like experience.

🌐 Live Stack Overflow Answers: Fetches the top-voted or accepted answer for any recommended question directly from the live Stack Overflow API in real-time.

💾 Persistent User Database: All your data—saved tags, saved questions, and search history—is stored in a local SQLite database, so your progress and preferences are always saved between sessions.

👤 Profile Management: A full-featured profile page where you can manually add or remove interest tags and manage your list of saved-for-later questions.

🛠️ How It Works: System Architecture

The project uses a robust two-stage architecture to separate heavy data processing from the real-time web application.

1. Offline Processing (in Google Colab)

Data: A dataset of 60,000 Stack Overflow questions is loaded.

Preprocessing: Text is cleaned (HTML tags, stopwords, etc.) and lemmatized.

Embedding: The all-MiniLM-L6-v2 model converts each question into a vector embedding.

Indexing: All vectors are indexed into a FAISS (faiss_index.bin) file for high-speed similarity search.

Output: The final artifacts are the FAISS index and a processed_data.parquet file.

2. Real-Time Web App (Streamlit)

Frontend: A multi-page Streamlit application serves as the user interface.

Backend: Python scripts handle user login, API calls, and database logic.

Database: A local SQLite database (users.db) stores all persistent user data.

Live Data: The app makes live API calls to Stack Overflow to fetch user profiles and real-time answers, blending our static dataset with live data.

⚙️ Setup and Installation

Follow these steps to get the project running on your local machine.

1. Clone the Repository

git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME


2. Set Up a Virtual Environment (Recommended)

# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate


3. Install Dependencies

Install all required libraries using the requirements.txt file.

pip install -r requirements.txt


4. Get the Data Files

This project requires two large data files that are not stored in the Git repository:

faiss_index.bin

processed_data.parquet

You must generate these files yourself by running the provided Google Colab notebook. Once generated, place both files in the root directory of this project.

5. Run the Application

Once the setup is complete, launch the Streamlit app. The database file (users.db) will be created automatically on the first run.

streamlit run app.py


The application should now be open and running in your web browser!

📂 Project Structure

.
├── 📄 .gitignore
├── 📄 app.py                    # Main app: Welcome/Dashboard
├── 📄 db_functions.py           # SQLite database helper functions
├── 📄 deployment_setup.py       # (Optional) For Streamlit Cloud deployment
├── 📄 README.md                 # This file
├── 📄 requirements.txt          # Python library dependencies
│
├── 📁 pages/
│   ├── 📄 1_Search.py           # Hybrid search page
│   ├── 📄 2_Learning_Path.py    # Tag-based exploration page
│   ├── 📄 3_Profile.py          # User profile & saved items page
│   └── 📄 4_Recommendations.py  # Adaptive recommendations page
│
├── 📦 Data files (Must be generated/downloaded)
│   ├── 🗂️ faiss_index.bin
│   └── 📊 processed_data.parquet
│
└── 💾 Database (Generated on first run)
    └── 🗃️ users.db
