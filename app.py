import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd
import pyperclip

# Create a connection object.
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
df_index = df.index

# Print results.
st.title("Twitample")
    
st.dataframe(df)

msg_idx = st.radio("✅ Select tweet :", df_index, horizontal=True)
init_msg = f"{df.loc[msg_idx, 'title']}\n{df.loc[msg_idx, 'text']}\n\n{df.loc[msg_idx, 'tag']}"
message = st.text_area("📝 Edit tweet :", value=init_msg, height=200)

if st.button('🐤 Copy to Clipboard 🚀'):
    pyperclip.copy(message)
