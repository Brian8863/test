import streamlit as st
import pandas as pd

st.title("📘 題庫練習器（隨機 50 題，一次交卷）")

uploaded_file = st.file_uploader("請上傳 Excel 題庫檔（需含欄位：ID, 答案, 題目, 選項一～四）", type=["xlsx"])

if uploaded_file:
    if "questions_loaded" not in st.session_state:
        df = pd.read_excel(uploaded_file)

        # 隨機抽 50 題（最多）
        num_questions = min(30, len(df))
        sampled_df = df.sample(n=num_questions).reset_index(drop=True)

        st.session_state["sampled_df"] = sampled_df
        st.session_state["user_answers"] = [set() for _ in range(num_questions)]
        st.session_state["questions_loaded"] = True
        st.session_state["submitted"] = False

    df = st.session_state["sampled_df"]
    user_answers = st.session_state["user_answers"]

    for i, row in df.iterrows():
        st.markdown(f"### 第 {i+1} 題")
        st.write(row["題目"])

        options = {
            "1": row["選項1"],
            "2": row["選項2"],
            "3": row["選項3"],
            "4": row["選項4"]
        }

        # 顯示選項（可複選）
        selected = st.multiselect(
            label="請選擇正確答案（可複選）：",
            options=list(options.values()),
            default=list(user_answers[i]),
            key=f"q_{row['ID']}"  # ✅ 用 ID 當 key，避免題目重複出錯
        )
        user_answers[i] = set(selected)

    if st.button("✅ 交卷"):
        st.session_state["submitted"] = True

    if st.session_state.get("submitted", False):
        st.markdown("## 🎯 結果分析")
        total_score = 0
        for i, row in df.iterrows():
            options = {
                "1": row["選項1"],
                "2": row["選項2"],
                "3": row["選項3"],
                "4": row["選項4"]
            }
            correct_keys = list(str(row["答案"]))
            correct_set = set(options[k] for k in correct_keys if k in options)
            user_set = user_answers[i]

            is_correct = user_set == correct_set
            if is_correct:
                total_score += 3.33

            st.markdown(f"### 第 {i+1} 題：{'✅ 正確' if is_correct else '❌ 錯誤'}")
            st.write(f"題目：{row['題目']}")
            st.write(f"你的答案：{', '.join(user_set) if user_set else '（未作答）'}")
            st.write(f"正確答案：{', '.join(correct_set)}")
            st.markdown("---")

        st.markdown(f"## 🧮 你的總分：{total_score} / 100")

    if st.button("🔁 重新抽題"):
        for key in list(st.session_state.keys()):
            if key.startswith("q_") or key in ("sampled_df", "user_answers", "questions_loaded", "submitted"):
                del st.session_state[key]
