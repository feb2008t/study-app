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
                st.success("登録成功")
                st.session_state["user_id"] = response.user.id
                st.session_state["access_token"] = response.session.access_token
                st.session_state["refresh_token"] = response.session.refresh_token
                st.success("ログイン成功")
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
                st.success("ログイン成功")
                st.session_state["user_id"] = response.user.id
                st.session_state["access_token"] = response.session.access_token
                st.session_state["refresh_token"] = response.session.refresh_token
                st.success("登録成功")
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

if df.empty:
    today_minutes = 0
    week_minutes = 0
    total_minutes = 0
else:
    df["date"] = pd.to_datetime(df["date"]).dt.date

    today_minutes = df[df["date"] == today]["minutes"].sum()
    today_hours=today_minutes/60

    week_start = today - timedelta(days=today.weekday())
    week_minutes = df[df["date"] >= week_start]["minutes"].sum()
    week_hours=week_minutes/60

    total_minutes = df["minutes"].sum()
    total_hours = total_minutes / 60

# 上部カード
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("🔥 今日", f"{today_hours:1f} 時間")

with col2:
    st.metric("📅 今週", f"{week_hours:1f} 時間")

with col3:
    st.metric("📖 累計", f"{total_hours:.1f} 時間")

