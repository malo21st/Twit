import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd
import tweepy
from io import BytesIO, BufferedReader
from PIL import Image
import pyperclip

PIC_WIDTH = 500
consumer_key    = st.secrets["API_KEY"]
consumer_secret = st.secrets["API_SECRET"]
access_token    = st.secrets["ACCESS_TOKEN"]
access_token_secret = st.secrets["ACCESS_TOKEN_SECRET"]

# OAuth process, using the keys and tokens
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

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
st.title("Caster - tweet so easy -")
picture_data = st.file_uploader("🎉 Select a picture :", type=['png', 'jpg', 'jpeg'])
if picture_data:
    img = Image.open(picture_data)
    #リサイズ&圧縮
    width, height = img.size
    img_resize = img.resize((PIC_WIDTH, int(height / width * PIC_WIDTH)))
    #写真表示
    st.image(img_resize)
    # Save image in-memory
    b = BytesIO()
    img_resize.save(b, "PNG")
    b.seek(0)
    fp = BufferedReader(b)
    
st.dataframe(df)

msg_idx = st.radio("✅ Select tweet :", df_index, horizontal=True)
init_msg = f"{df.loc[msg_idx, 'title']}\n{df.loc[msg_idx, 'text']}\n\n{df.loc[msg_idx, 'tag']}"
message = st.text_area("📝 Edit tweet :", value=init_msg, height=200)

if st.button('🐤 tweet 🚀'):
    if picture_data:
        media = api.media_upload(filename="dummy.png", file=fp)
        api.update_status(message, media_ids=[media.media_id])
    else:
        api.update_status(message)

text_to_be_copied = 'The text to be copied to the clipboard.'
pyperclip.copy(text_to_be_copied)
