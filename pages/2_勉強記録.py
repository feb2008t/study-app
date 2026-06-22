import streamlit as st
import pandas as pd
from supabase_config import supabase

if "user_id" not in st.session_state:
    st.warning("先にログインしてください")
    st.stop()

st.title("勉強記録")

response = (
    supabase
    .table("study_logs")
    .select("*")
    .eq("user_id", st.session_state["user_id"])
    .execute()
)

records = response.data

if records:
    data = pd.DataFrame(records)

    display_data = data[["date", "subject", "minutes"]]
    st.dataframe(display_data)

    total = data["minutes"].sum()
    st.write("合計勉強時間：", round(total / 60, 1), "時間")

    choices = {}

    for i, row in data.iterrows():
        text = f"{row['date']}:{row['subject']}:{row['minutes']}分"
        choices[text] = row["id"]

    selected = st.selectbox("削除する行を選択", list(choices.keys()))

    if st.button("削除"):
        selected_id = choices[selected]

        (
            supabase
            .table("study_logs")
            .delete()
            .eq("id", selected_id)
            .eq("user_id", st.session_state["user_id"])
            .execute()
        )

        st.rerun()

else:
    st.write("まだ記録がありません")