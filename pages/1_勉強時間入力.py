import streamlit as st
import pandas as pd
from datetime import date
import os

st.title("勉強時間入力")

CSV_FILE = "study_log.csv"

study_date = st.date_input("日付", value=date.today())
subject = st.text_input("科目")
minutes = st.number_input("勉強時間（分）", min_value=0, step=10)

if st.button("記録する"):
    if subject == "" or minutes == 0:
        st.warning("科目と勉強時間を入力してください")
    else:
        new_data = pd.DataFrame({
            "date": [str(study_date)],
            "subject": [subject],
            "minutes": [minutes]
        })

        if os.path.exists(CSV_FILE):
            old_data = pd.read_csv(CSV_FILE)
            data = pd.concat([old_data, new_data], ignore_index=True)
            data = data.groupby(["date", "subject"], as_index=False)["minutes"].sum()
        else:
            data = new_data

        data.to_csv(CSV_FILE, index=False)
        st.success("記録しました！")
