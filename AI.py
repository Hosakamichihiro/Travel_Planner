import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
import pandas as pd
from  streamlit_folium import st_folium
import folium
from langchain_community.tools import DuckDuckGoSearchRun
from duckduckgo_search import DDGS


def main():
    llm = ChatOpenAI(temperature=0)

    st.set_page_config(
        page_title="Travel Planner",
        page_icon="🧳"
    )
    st.header("Travel Planner")
    st.text("・This site was developed to help you make the most of your vacation.")
    st.text("・First, enter the conditions you are interested in,")
    st.text("    such as your destination, gourmet food, tourist spots, etc.")
    # Sidebarの選択肢を定義する
    options = ["START","WEB","MAP", "MEMO", "EXIT"]
    choice = st.sidebar.selectbox("Select an option", options)

    if choice == "START":
        st.write("You selected START")
        AI()
        web()
        condition()
    elif choice == "WEB":
        st.write("You selected WEB")
        AI()
        condition_web()
    elif choice == "MAP":
        st.write("You selected MAP")
        MAP()
    elif choice == "MEMO":
        st.write("You selected MEMO")
        AI()
    else:
        st.write("You selected EXIT")
        redirect()

def redirect():
    st.markdown("""
        <meta http-equiv="refresh" content="0; url=https://www.google.com/">
        <p>Redirecting...</p>
    """, unsafe_allow_html=True)

def MAP():
        # セッション状態で地図データを管理
    if "map_data" not in st.session_state:
        st.session_state.map_data = {
            "location": [35.6812378, 139.7669852],  # 初期位置
            "markers": []  # マーカーのリスト
        }

    # 初期地図を生成
    m = folium.Map(location=st.session_state.map_data["location"], zoom_start=16)
    m.add_child(folium.LatLngPopup())

    # 既存のマーカーを地図に追加
    for marker in st.session_state.map_data["markers"]:
        folium.Marker(location=marker, popup=f"Latitude: {marker[0]}, Longitude: {marker[1]}").add_to(m)

    # ユーザーがクリックした地図の情報を取得
    st_data = st_folium(m, width=725, height=500)

    if st_data["last_clicked"] is not None:
        clicked_lat = st_data["last_clicked"]["lat"]
        clicked_lng = st_data["last_clicked"]["lng"]

        # 新しい座標をセッション状態に保存し、前のマーカーをクリア
        st.session_state.map_data["location"] = [clicked_lat, clicked_lng]
        st.session_state.map_data["markers"] = [[clicked_lat, clicked_lng]]

        st.write(f"Coordinates: Latitude {clicked_lat}, Longitude {clicked_lng}")

        # 新しい地図を再描画
        m = folium.Map(location=st.session_state.map_data["location"], zoom_start=16)
        folium.Marker(location=[clicked_lat, clicked_lng], popup=f"Latitude: {clicked_lat}, Longitude: {clicked_lng}").add_to(m)
        st_folium(m, width=725, height=500)

    # 地図上のクリックイベントを処理するためのインタラクション
    #if st.button("クリックした場所の緯度経度を取得"):
        #st.write(f"緯度経度を取得しました！ 緯度{clicked_lat}  経度 {clicked_lng}")  # 緯度経度を表示

def web():
    # 商品名またはブランドを入力してくださいというフィールドを定義する
    user_input_web = st.text_input("国名または都市名を入力してください.入力することで、行きたい国について、少し知ることができます.詳しく知りたい場合は、下の、'Enter your question'に.")
    
    # ユーザーが入力した値があれば検索をする
    if user_input_web:
        search = DuckDuckGoSearchRun()

        # DuckDuckGoSearchRunのrunメソッドにユーザーの入力を辞書で渡す
        response = search.run({"query": user_input_web, "language": "jp"})
        st.write(response)

def AI():
    llm = ChatOpenAI(temperature=0)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a trip planner. You should provide great trip plans.")
        ]

    if user_input := st.chat_input("Enter your question:"):
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("ChatGPT is typing ..."):
            response = llm.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))

    messages = st.session_state.get('messages', [])
    for message in messages:
        if isinstance(message, AIMessage):
            st.markdown(f"**Assistant:** {message.content}")
        elif isinstance(message, HumanMessage):
            st.markdown(f"**You:** {message.content}")

def condition():
    # 国内か海外か選択
    destination_type = st.radio("国内旅行か海外旅行か選んでください", ['国内', '海外'])

    if destination_type == '国内':
        # 国内の地方を選択
        todofuken = ["北海道", "東北地方", "関東地方", "中部地方", "近畿地方", "中国地方", "四国地方", "九州地方", "沖縄県"]
        region = st.radio("行きたい地方", todofuken)
    else:
        # 海外の州（または国）を選択
        states = ["アジア", "アフリカ", "ヨーロッパ", "北アメリカ", "南アメリカ", "オセアニア"]  # 例としていくつかの国を追加
        region = st.radio("States I want to visit", states)

    # 他の条件
    date = st.date_input('出発日を選択')
    Departure_point = st.text_input('出発地を入力')
    days = st.slider('滞在日数', 1, 14, 1)
    time = st.time_input("出発時間を入力", value=None)
    people = st.radio('人数', ['1人', '2人', '3人', '4人', 'それ以上'])
    traffic = st.radio('交通', ["飛行機", "船", "新幹線", "タクシー", "レンタカー", "自家用車"])
    cost = st.sidebar.number_input("予算（円）", min_value=1000, max_value=100000000, value=10000, step=1000)

    if st.button("検索する"):
        # 入力された情報を検索条件に追加
        sentence = f"{destination_type}旅行を計画しています。出発日は、{date}出発時間は{time},行きたい場所は{region},出発地点は{Departure_point},滞在日数は{days}日, 人数は{people}, 予算は{cost}円, 交通機関は{traffic}の旅行プランを作成してください。"
        question(sentence)

def condition_web():
    # 国を入力させるフィールドを追加
    # 国内か海外か選択
    destination_type = st.radio("国内旅行か海外旅行か選んでください", ['国内', '海外'])

    if destination_type == '国内':
        # 国内の地方を選択
        todofuken = ["北海道", "東北地方", "関東地方", "中部地方", "近畿地方", "中国地方", "四国地方", "九州地方", "沖縄県"]
        region = st.radio("行きたい地方", todofuken)
    else:
        # 海外の州（または国）を選択
        states = ["アジア", "アフリカ", "ヨーロッパ", "北アメリカ", "南アメリカ", "オセアニア"]  # 例としていくつかの国を追加
        region = st.radio("States I want to visit", states)# デフォルトを「日本」に設定
    days = st.slider('宿泊日数', 1, 14, 1)
    people = st.radio('人数', ['1人', '2人', '3人', '4人', 'それ以上'])
    traffic = st.radio('交通', ["飛行機", "船", "新幹線", "タクシー", "レンタカー", "自家用車"])
    cost = st.sidebar.number_input("予算（円）", min_value=1000, max_value=100000000, value=10000, step=1000)
    other1 = st.text_area("他にもリクエストがある場合はここに記入してください。特になければ、[なし]にチェックを入れてください。",placeholder="羽田空港発で、出来れば早朝の便は避けたいです。")
    other2 = st.checkbox("なし")

    if other1:
        other0 = other1
    else:
        other0 = "なし"
    if st.button("検索する"):
        # 入力された国を検索条件に追加
        sentence_duck = f"{destination_type}旅行を計画しています。行きたい場所は{region},滞在日数は{days}日, 人数は{people}, 予算は{cost}円, 交通機関は{traffic}の旅行プランを計画してください。他のリクエストは「{other0}」です。最適な旅行プランを考えて下さい。応答は必ず日本語でお願いします。"
        duckduckgo(sentence_duck)


def question(sentence):
    llm = ChatOpenAI(temperature=0)

    st.write("この条件で検索しています・・・")
    
    st.session_state.messages.append(HumanMessage(content=sentence))
    with st.spinner("ChatGPT is typing ..."):
        response = llm.invoke(st.session_state.messages)
    st.session_state.messages.append(AIMessage(content=response.content))

    for message in st.session_state.messages:
        if isinstance(message, AIMessage):
            st.markdown(f"**Assistant:** {message.content}")
        #elif isinstance(message, HumanMessage):
            #st.markdown(f"**You:** {message.content}")



def duckduckgo(sentence_duck):
    st.subheader("duckduckgo 検索結果")

    # 検索を実行する関数
    def search_duckduckgo(query):
        results = DDGS().text(query, region="jp-jp", max_results=5)
        # 検索結果があるかどうかチェックする
        if results:
            # 検索結果の最初の項目のタイトルとURLを取得する
            first_result = results[0]
            title = first_result['title']
            href = first_result['href']
            # タイトルとURLを表示する
            st.write(f"1: {title}")
            st.write(f"URL: {href}")
            # 検索結果の二番目の項目のタイトルとURLを取得する
            second_result = results[1]
            title2 = second_result['title']
            href2 = second_result['href']
            # タイトルとURLを表示する
            st.write(f"2: {title2}")
            st.write(f"URL: {href2}")
            # 検索結果の三番目の項目のタイトルとURLを取得する
            third_result = results[2]
            title3 = third_result['title']
            href3 = third_result['href']
            # タイトルとURLを表示する
            st.write(f"3: {title3}")
            st.write(f"URL: {href3}")
            anothersearch = st.button("もっと見る")
            if anothersearch:
                # 検索結果の四番目の項目のタイトルとURLを取得する
                four_result = results[3]
                title4 = four_result['title']
                href4 = four_result['href']
                # タイトルとURLを表示する
                st.write(f"4: {title4}")
                st.write(f"URL: {href4}")
                # 検索結果の四番目の項目のタイトルとURLを取得する
                five_result = results[4]
                title5 = five_result['title']
                href5 = five_result['href']
                # タイトルとURLを表示する
                st.write(f"5: {title5}")
                st.write(f"URL: {href5}")
        else:
            # 検索結果がなかった場合のメッセージを表示する
            st.write("検索結果が見つかりませんでした。")

    # 検索を実行する
    
    search_duckduckgo(sentence_duck)


if __name__ == '__main__':
    main()