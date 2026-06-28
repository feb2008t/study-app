import streamlit as st

import pandas as pd
from datetime import date
from supabase_config import supabase

from analysis import get_weekly_summary
from analysis import show_weekly_bar_chart
from analysis import show_subject_pie_chart
from analysis import show_goal_input
from analysis import show_goal_progress

if "user_id" not in st.session_state:
    st.warning("ログイン情報がありません。もう一度ログインしてください。")
    st.stop()

user_id = st.session_state["user_id"]

if (
    "access_token" not in st.session_state
    or
    "refresh_token" not in st.session_state
):
    st.warning("ログイン情報がありません。もう一度ログインしてください。")
    st.stop()

supabase.auth.set_session(
    st.session_state["access_token"],
    st.session_state["refresh_token"]
)

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

    # 日付をdate型に変換
    data["date"] = pd.to_datetime(data["date"]).dt.date

    # 新しい順に並び替え
    data = (
        data
        .sort_values(by=["date", "id"], ascending=False)
        .reset_index(drop=True)
    )

    today = date.today()

    # ----------------------------
    # 今日の記録
    # ----------------------------

    st.subheader("📝 今日の記録")

    today_data = data[data["date"] == today]

    if len(today_data) > 0:

        # 表を先に表示
        st.dataframe(
            today_data[["date", "subject", "minutes"]],
            use_container_width=True
        )

        # 削除
        choices = {}

        for _, row in today_data.iterrows():
            text = f"{row['subject']}：{row['minutes']}分"
            choices[text] = row["id"]

        selected = st.selectbox(
            "削除する今日の記録",
            list(choices.keys())
        )

        if st.button("今日の記録を削除"):

            (
                supabase
                .table("study_logs")
                .delete()
                .eq("id", choices[selected])
                .eq("user_id", st.session_state["user_id"])
                .execute()
            )

            st.rerun()

    else:
        st.write("今日はまだ記録がありません。")

    # ----------------------------
    # 過去の記録
    # ----------------------------

    with st.expander("📚 過去の記録を見る"):

        # 削除を先に配置
        choices = {}

        for _, row in data.iterrows():
            text = f"{row['date']}：{row['subject']}：{row['minutes']}分"
            choices[text] = row["id"]

        selected = st.selectbox(
            "削除する記録を選んでください",
            list(choices.keys()),
            key="history_delete"
        )

        if st.button(
            "削除する",
            key="history_delete_button"
        ):

            (
                supabase
                .table("study_logs")
                .delete()
                .eq("id", choices[selected])
                .eq("user_id", st.session_state["user_id"])
                .execute()
            )

            st.rerun()

        # 表を最後に表示
        st.dataframe(
            data[["date", "subject", "minutes"]],
            use_container_width=True
        )
    st.divider()

    st.subheader("📊 今週の分析")

    daily_summary, subject_summary = get_weekly_summary(records)

    show_weekly_bar_chart(daily_summary)

    show_subject_pie_chart(subject_summary)
    

    show_goal_progress(
        supabase,
        st.session_state["user_id"],
        daily_summary,
        subject_summary
    )

    show_goal_input(
    supabase,
    st.session_state["user_id"]
)
    

else:
    st.write("まだ記録がありません")