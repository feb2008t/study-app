import streamlit as st
import pandas as pd
from datetime import date, timedelta
from supabase_config import supabase

st.set_page_config(page_title="学習ダッシュボード", layout="wide")

st.title("📚 学習ダッシュボード")

# 未ログインならログイン画面
if "user_id" not in st.session_state:
    st.header("ログイン")

    email = st.text_input("メールアドレス")
    password = st.text_input("パスワード", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("新規登録"):
            try:
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })

                st.session_state["user_id"] = response.user.id
                st.session_state["access_token"] = response.session.access_token
                st.session_state["refresh_token"] = response.session.refresh_token

                st.success("登録成功")
                st.rerun()

            except Exception:
                st.error("登録に失敗しました。メールアドレスやパスワードを確認してください。")

    with col2:
        if st.button("ログイン"):
            try:
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                st.session_state["user_id"] = response.user.id
                st.session_state["access_token"] = response.session.access_token
                st.session_state["refresh_token"] = response.session.refresh_token

                st.success("ログイン成功")
                st.rerun()

            except Exception:
                st.error("メールアドレスまたはパスワードが違います。")

    st.stop()

user_id = st.session_state["user_id"]

# データ取得
response = supabase.table("study_logs").select("*").eq("user_id", user_id).execute()
logs = response.data

df = pd.DataFrame(logs)

today = date.today()
week_start = today - timedelta(days=today.weekday())

# 初期値
today_minutes = 0
week_minutes = 0
week_hours = 0
total_minutes = 0
total_hours = 0
goal_exists = False
goal_hours = 0
achievement = 0

if not df.empty:
    df["date"] = pd.to_datetime(df["date"]).dt.date

    today_minutes = df[df["date"] == today]["minutes"].sum()
    week_minutes = df[df["date"] >= week_start]["minutes"].sum()
    week_hours = week_minutes / 60

    total_minutes = df["minutes"].sum()
    total_hours = total_minutes / 60

# 今週の目標取得
goal_response = (
    supabase.table("weekly_goals")
    .select("*")
    .eq("user_id", user_id)
    .eq("week_start_date", week_start.isoformat())
    .execute()
)

goal_df = pd.DataFrame(goal_response.data)

if goal_df.empty:
    goal_exists = False
    goal_hours = 0
else:
    goal_exists = True
    goal_hours = goal_df["target_minutes"].sum() / 60

if goal_hours > 0:
    achievement = week_hours / goal_hours
else:
    achievement = 0

# 上部カード
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔥 今日", f"{today_minutes} 分")

with col2:
    st.metric("📅 今週", f"{week_hours:.1f} 時間")

with col3:
    st.metric("📖 累計", f"{total_hours:.1f} 時間")

st.subheader("🎯 今週の目標")

if not goal_exists:
    st.info("今週の目標は設定されませんでした。")
else:
    st.progress(min(achievement, 1.0))
    st.write(f"**{week_hours:.1f} / {goal_hours:.1f} 時間**")
    st.write(f"達成率：{achievement*100:.0f}%")