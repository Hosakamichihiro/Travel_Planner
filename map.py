import streamlit as st
import json
from urllib.parse import urlencode, parse_qs

# 旅行プラン共有アプリ
def main():
    st.title("旅行プラン共有アプリ")

    # ページモード切り替え
    mode = st.sidebar.selectbox("モードを選択", ["プラン作成", "プラン閲覧"])

    if mode == "プラン作成":
        st.subheader("旅行プランを作成")

        # ユーザーが入力するプラン情報
        trip_title = st.text_input("旅行のタイトルを入力してください", placeholder="例: 京都旅行プラン")
        start_date = st.date_input("開始日を選択")
        end_date = st.date_input("終了日を選択")
        destinations = st.text_area("訪問先を入力（1行に1つ）", placeholder="例:\n清水寺\n金閣寺\n祇園")

        # プラン保存ボタン
        if st.button("プランを保存して共有リンクを生成"):
            if not trip_title or not destinations:
                st.warning("タイトルと訪問先を入力してください。")
            elif start_date > end_date:
                st.warning("終了日は開始日以降の日付を選択してください。")
            else:
                # プランをJSON形式で保存
                trip_plan = {
                    "title": trip_title,
                    "start_date": str(start_date),
                    "end_date": str(end_date),
                    "destinations": destinations.splitlines()
                }
                plan_json = json.dumps(trip_plan)
                encoded_plan = urlencode({"plan": plan_json})

                # 共有リンクを生成
                base_url = "https://share.streamlit.io/your_app_name"
                share_url = f"{base_url}?{encoded_plan}"
                st.success("プランが保存されました！以下のリンクを共有してください。")
                st.text_input("共有リンク", value=share_url, disabled=True)

    elif mode == "プラン閲覧":
        st.subheader("共有された旅行プランを表示")

        # URLパラメータからプランを取得
        query_params = st.experimental_get_query_params()
        if "plan" in query_params:
            try:
                plan_json = query_params["plan"][0]
                trip_plan = json.loads(plan_json)

                # プランを表示
                st.write(f"### {trip_plan['title']}")
                st.write(f"**開始日**: {trip_plan['start_date']}")
                st.write(f"**終了日**: {trip_plan['end_date']}")
                st.write("**訪問先**:")
                for destination in trip_plan["destinations"]:
                    st.write(f"- {destination}")
            except Exception as e:
                st.error(f"プランの読み込み中にエラーが発生しました: {e}")
        else:
            st.info("共有リンクを使用して旅行プランを表示してください。")

if __name__ == "__main__":
    main()