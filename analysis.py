import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from debug import DEBUG


def get_week_range(today=None):
    """
    今週の月曜日と日曜日を返す
    """

    if today is None:
        today = date.today()

    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    return monday, sunday


def get_weekly_summary(records):
    """
    recordsから今週の曜日別・科目別集計を返す
    """

    df = pd.DataFrame(records)

    monday, sunday = get_week_range()

    week_dates = [monday + timedelta(days=i) for i in range(7)]

    weekday_map = {
        0: "月",
        1: "火",
        2: "水",
        3: "木",
        4: "金",
        5: "土",
        6: "日"
    }

    if df.empty:

        daily_summary = pd.DataFrame({
            "date": week_dates,
            "minutes": [0] * 7
        })

        daily_summary["weekday"] = [
            weekday_map[d.weekday()]
            for d in week_dates
        ]

        subject_summary = pd.DataFrame(
            columns=["subject", "minutes"]
        )

        return daily_summary, subject_summary

    df["date"] = pd.to_datetime(df["date"]).dt.date

    week_df = df[
        (df["date"] >= monday)
        &
        (df["date"] <= sunday)
    ]

    daily_summary = (
        week_df
        .groupby("date")["minutes"]
        .sum()
        .reindex(week_dates, fill_value=0)
        .reset_index()
    )

    daily_summary.columns = ["date", "minutes"]

    daily_summary["weekday"] = daily_summary["date"].apply(
        lambda d: weekday_map[d.weekday()]
    )

    subject_summary = (
        week_df
        .groupby("subject")["minutes"]
        .sum()
        .reset_index()
    )

    return daily_summary, subject_summary


def show_weekly_bar_chart(daily_summary):
    """
    曜日別学習時間棒グラフ
    """

    fig = px.bar(
        daily_summary,
        x="weekday",
        y="minutes",
        text="minutes",
        title="曜日別学習時間"
    )

    fig.update_traces(
        textposition="outside"
    )

    fig.update_layout(
        template="plotly_white",
        title_x=0.5,
        xaxis_title="",
        yaxis_title="勉強時間（分）"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def show_subject_pie_chart(subject_summary):
    """
    科目別学習割合円グラフ
    """

    if subject_summary.empty:
        st.info("今週の学習記録がありません。")
        return

    fig = px.pie(
        subject_summary,
        names="subject",
        values="minutes",
        title="科目別学習割合"
    )

    fig.update_layout(
        template="plotly_white",
        title_x=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

def get_next_week_monday():
    today = date.today()
    next_monday = today + timedelta(days=(7 - today.weekday()))
    return next_monday


def get_this_week_monday():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday


def save_weekly_goals(supabase, user_id, week_start_date, goals):
    # まず同じユーザー・同じ週の目標を全部削除
    supabase.table("weekly_goals") \
        .delete() \
        .eq("user_id", user_id) \
        .eq("week_start_date", str(week_start_date)) \
        .execute()

    # その後、今入力されている目標を新しく保存
    for subject, target_minutes in goals.items():
        if target_minutes > 0:
            supabase.table("weekly_goals").insert({
                "user_id": user_id,
                "week_start_date": str(week_start_date),
                "subject": subject,
                "target_minutes": target_minutes
            }).execute()


def get_weekly_goals(supabase, user_id, week_start_date):
    response = (
        supabase
        .table("weekly_goals")
        .select("*")
        .eq("user_id", user_id)
        .eq("week_start_date", str(week_start_date))
        .execute()
    )

    return response.data

def show_goal_input(supabase, user_id):
    today = date.today()

    if (today.weekday() != 6) and (not DEBUG):
        st.info("次週の目標設定は日曜日だけできます。")
        return

    st.subheader("🎯 次週の目標設定")

    if st.session_state.get("goal_saved"):
        st.success("次週の目標を保存しました。")
        st.session_state["goal_saved"] = False

    next_monday = get_next_week_monday()

    st.write(f"対象週：{next_monday} からの1週間")

    goals = {}

    total_hours = st.number_input(
        "合計目標時間（時間）",
        min_value=0.0,
        step=0.5
    )

    goals["合計"] = int(total_hours * 60)

    st.write("科目別目標")

    num_subjects = st.number_input(
        "科目数",
        min_value=0,
        max_value=20,
        value=3,
        step=1
    )

    for i in range(num_subjects):
        col1, col2 = st.columns([2, 1])

        with col1:
            subject = st.text_input(
                f"科目名 {i + 1}",
                key=f"goal_subject_{i}"
            )

        with col2:
            hours = st.number_input(
                f"時間 {i + 1}",
                min_value=0.0,
                step=0.5,
                key=f"goal_hours_{i}"
            )

        if subject.strip() != "" and hours > 0:
            goals[subject.strip()] = int(hours * 60)

    if st.button("次週の目標を保存"):
        save_weekly_goals(
            supabase,
            user_id,
            next_monday,
            goals
        )

        st.toast("次週の目標を保存しました。", icon="✅")
        
def show_goal_progress(supabase, user_id, daily_summary, subject_summary):
    st.subheader("🎯 今週の目標")

    this_monday = get_this_week_monday()

    goals = get_weekly_goals(
        supabase,
        user_id,
        this_monday
    )

    if len(goals) == 0:
        st.info("今週の目標は設定されていません。")
        return

    total_actual = daily_summary["minutes"].sum()

    for goal in goals:
        subject = goal["subject"]
        target = goal["target_minutes"]

        if subject == "合計":
            actual = total_actual
        else:
            matched = subject_summary[
                subject_summary["subject"] == subject
            ]

            if matched.empty:
                actual = 0
            else:
                actual = int(matched["minutes"].iloc[0])

        rate = actual / target if target > 0 else 0

        st.write(f"{subject}：{round(actual / 60, 1)} / {round(target / 60, 1)} 時間")

        st.progress(min(rate, 1.0))

        if rate >= 1:
            st.success("達成！")
        else:
            st.write(f"達成率：{round(rate * 100, 1)}%")