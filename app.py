import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd
import html

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

msg_idx = st.radio("✅ ツイートを選んで下さい :", df_index, horizontal=True)
init_msg = f"{df.loc[msg_idx, 'title']}" #\n{df.loc[msg_idx, 'text']}\n\n{df.loc[msg_idx, 'tag']}"
st.write("📋 下のエリアを選択すると右上のアイコンでコピーできます :")
message = st.text_area("📝 ツイート :", value=init_msg, height=200)
msg_html = html.unescape(message)
link = f'[この内容でツイートする](https://twitter.com/intent/tweet?text={msg_html}%0A改行)'
st.markdown(link, unsafe_allow_html=True)
