import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)
conn = connect(credentials=credentials)

@st.cache()
def run_query(query):
    rows = conn.execute(query, headers=1)
    rows = rows.fetchall()
    return rows

sheet_url = st.secrets["private_gsheets_url"]
rows = run_query(f'SELECT * FROM "{sheet_url}"')
df = pd.DataFrame(rows, columns=["title", "text", "tag"])
pd.set_option('display.max_colwidth', 10)

# Contents
st.title("Tweet Template")
st.dataframe(df)
tweet_idx = st.radio("✅ ツイートを選んで下さい :", df.index, horizontal=True)
init_tweet = f"{df.loc[tweet_idx, 'title']}\n{df.loc[tweet_idx, 'text']}\n\n{df.loc[tweet_idx, 'tag']}"
st.code(init_tweet, language="txt")
tweet = init_tweet.replace("\n", "%0A").replace(" ", "%20").replace("#", "%23")
link = f'[これをベースにツイート](https://twitter.com/intent/tweet?text={tweet})'
st.markdown(link, unsafe_allow_html=True)
