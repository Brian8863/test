import streamlit as st
import pandas as pd

st.set_page_config(page_title="📘 題庫練習器", layout="centered")
st.title("📘 題庫練習器")

uploaded_file = st.file_uploader("📥 請上傳 Excel 題庫檔（檔名請改英文，需含：ID、題目、答案、選項1~4、可選圖片欄）", type=["xlsx"],accept_multiple_files=False)

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    max_count = len(df)
    num_questions = st.number_input("📌 請輸入想作答的題數：", min_value=1, max_value=max_count, value=min(10, max_count), step=1)

    if st.button("🎲 開始作答") or "questions_loaded" not in st.session_state:
        sampled_df = df.sample(n=num_questions).reset_index(drop=True)
        st.session_state["sampled_df"] = sampled_df
        st.session_state["user_answers"] = [{} for _ in range(num_questions)]
        st.session_state["submitted"] = False
        st.session_state["questions_loaded"] = True

if "sampled_df" in st.session_state:
    df = st.session_state["sampled_df"]
    user_answers = st.session_state["user_answers"]

    st.divider()
    for i, row in df.iterrows():
        st.markdown(f"### 第 {i+1} 題")
        st.write(row["題目"])

        if "圖片" in row and pd.notna(row["圖片"]):
            try:
                st.image(row["圖片"])
            except:
                st.warning("⚠️ 圖片無法載入")

        options = {
            "1": row["選項1"],
            "2": row["選項2"],
            "3": row["選項3"],
            "4": row["選項4"]
        }

        answer_keys = list(str(row["答案"]))
        is_multiple = len(answer_keys) > 1

        selected = set()
        if is_multiple:
            for key, value in options.items():
                if pd.notna(value):
                    checked = st.checkbox(f"{value}", key=f"q_{i}_{key}")
                    if checked:
                        selected.add(value)
        else:
            valid_options = [v for v in options.values() if pd.notna(v)]
            selected_val = st.radio(
                "請選擇：",
                options=valid_options,
                key=f"q_{i}_radio",
                index=None  # ✅ 不預設任何選項
            )
            if selected_val:
                selected.add(selected_val)

        user_answers[i] = selected

    st.divider()
    if st.button("✅ 交卷"):
        st.session_state["submitted"] = True

if st.session_state.get("submitted", False):
    st.markdown("## 🎯 結果分析")
    total_score = 0
    score_per_question = round(100 / len(st.session_state["sampled_df"]), 2)

    for i, row in df.iterrows():
        options = {
            "1": row["選項1"],
            "2": row["選項2"],
            "3": row["選項3"],
            "4": row["選項4"]
        }
        correct_keys = list(str(row["答案"]))
        correct_set = set(options[k] for k in correct_keys if k in options and pd.notna(options[k]))
        user_set = user_answers[i]
        is_correct = user_set == correct_set

        if is_correct:
            total_score += score_per_question

        st.markdown(f"### 第 {i+1} 題：{'✅ 正確' if is_correct else '❌ 錯誤'}")
        st.write(f"題目：{row['題目']}")
        st.write(f"你的答案：{'& '.join(user_set) if user_set else '（未作答）'}")
        st.markdown(f"正確答案：\n"+{"\n".join(correct_set)}")
        st.markdown("---")

    st.markdown(f"## 🧮 你的總分：{round(total_score, 2)} / 100")

    if st.button("🔁 重新作答"):
        for key in list(st.session_state.keys()):
            if key.startswith("q_") or key in ("sampled_df", "user_answers", "questions_loaded", "submitted"):
                del st.session_state[key]
