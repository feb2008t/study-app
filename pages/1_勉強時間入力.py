import streamlit as st
from datetime import date
from supabase_config import supabase

if "user_id" not in st.session_state:
    st.warning("先にログインしてください")
    st.stop()

st.title("勉強時間入力")

study_date = st.date_input("日付", value=date.today())
subject = st.text_input("科目")
minutes = st.number_input("勉強時間（分）", min_value=0, step=10)

if st.button("記録する"):
    if subject == "" or minutes == 0:
        st.warning("科目と勉強時間を入力してください")
    else:
        supabase.table("study_logs").insert(
            {
                "user_id": st.session_state["user_id"],
                "date": str(study_date),
                "subject": subject,
                "minutes": minutes
            }
        ).execute()

        st.success("記録しました！")