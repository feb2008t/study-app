import streamlit as st
import pandas as pd
import os

st.title("勉強記録")

CSV_FILE = "study_log.csv"

if os.path.exists(CSV_FILE):
    data = pd.read_csv(CSV_FILE)
    st.dataframe(data)

    total = data["minutes"].sum()
    st.write("合計勉強時間：", round(total / 60, 1), "時間")
else:
    st.write("まだ記録がありません")
if os.path.exists(CSV_FILE):
    dt=pd.read_csv(CSV_FILE)
    choices={}
    for i,row in dt.iterrows():
        text=f"{row['date']}:{row['subject']}:{row['minutes']}"
        choices[text]=i
    selected=st.selectbox("削除する行を選択",list(choices.keys()))
    if st.button("削除"):
        s=choices[selected]
        dt=dt.drop(s)
        dt=dt.reset_index(drop=True)
        dt.to_csv(CSV_FILE,index=False)
        st.rerun()
else:
    st.warning("まだ記録がありません")