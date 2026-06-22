import streamlit as st
from supabase_config import supabase

st.title("ログイン")

email = st.text_input("メールアドレス")
password = st.text_input("パスワード", type="password")

if st.button("新規登録"):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        st.session_state["user_id"] = response.user.id

        st.success("登録成功")
        st.write("user_id:", st.session_state["user_id"])

    except Exception as e:
        st.error(e)

if st.button("ログイン"):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        st.session_state["user_id"] = response.user.id

        st.success("ログイン成功")
        st.write("user_id:", st.session_state["user_id"])

    except Exception as e:
        st.error(e)

if "user_id" in st.session_state:
    st.success("ログイン中")
    st.write("現在のuser_id:", st.session_state["user_id"])