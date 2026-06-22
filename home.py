import streamlit as st
from supabase_config import supabase

st.title("ログインテスト")

email = st.text_input("メールアドレス")
password = st.text_input("パスワード", type="password")

if st.button("新規登録"):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        st.success("登録成功")
        st.write("user_id:", response.user.id)
    except Exception as e:
        st.error(e)

if st.button("ログイン"):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.success("ログイン成功")
        st.write("user_id:", response.user.id)

    except Exception as e:
        st.error(e)