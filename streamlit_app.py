import streamlit as st
import pandas as pd

df = pd.read_csv('aa.csv', encoding='cp949')

df.head()

st.title("🎈 My new app")
st.write(
    "한글은 Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
