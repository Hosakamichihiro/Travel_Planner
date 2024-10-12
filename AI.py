import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
import pandas as pd
import datetime
import pydeck as pdk
#master→main
def main():
    llm = ChatOpenAI(temperature=0)

    st.set_page_config(
        page_title="Trip Planner",
        page_icon="🧳"
    )
    st.header("Trip Planner")
    st.text("・This site was developed to help you make the most of your vacation.")
    st.text("・First, enter the conditions you are interested in,")
    st.text("    such as your destination, gourmet food, tourist spots, etc.")
    # Sidebarの選択肢を定義する
    options = ["START","MAP", "MEMO", "EXIT"]
    choice = st.sidebar.selectbox("Select an option", options)

    if choice == "START":
        st.write("You selected START")
        AI()
        condition()
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
    # 初期マップの表示設定
    view_state = pdk.ViewState(
        latitude=35.6804,  # 初期表示する緯度
        longitude=139.7690,  # 初期表示する経度
        zoom=10,  # ズームレベル
        pitch=50
    )

    # マップのレイヤー設定（何も表示しないベースマップ）
    layer = pdk.Layer(
        "ScatterplotLayer",  # シンプルなマップ表示
        data=[],  # 初期データなし
        get_position='[lon, lat]',  # 緯度経度を設定するフィールド
        get_color='[200, 30, 0, 160]',
        get_radius=200,
    )

    # Pydeckマップを表示
    map = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Click on the map to get the coordinates!"}
    )

    # Pydeckでマップを表示
    map_output = st.pydeck_chart(map)

    # 地図上のクリックイベントを処理するためのインタラクション
    if st.button("クリックした場所の緯度経度を取得"):
        # 現在の地図の状態を取得して、クリックした座標を取得（仮のロジック）
        # Note: Streamlit自体で直接クリック位置を取得する機能はないため、Pydeckの拡張や外部ツールが必要
        st.write("緯度経度を取得しました！(ダミー値: 緯度 35.6804, 経度 139.7690)")  # 仮の値を表示


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
    days = st.slider('宿泊日数', 1, 14, 1)
    people = st.radio('人数', ['1人', '2人', '3人', '4人', 'それ以上'])
    traffic = st.radio('交通', ["飛行機", "船", "新幹線", "タクシー", "レンタカー", "自家用車"])
    cost = st.sidebar.number_input("予算（円）", min_value=1000, max_value=100000000, value=10000, step=1000)

    if st.button("検索する"):
        # 入力された情報を検索条件に追加
        sentence = f"{destination_type}旅行を計画しています。出発日は、{date}行きたい場所は{region}, 滞在日数は{days}日, 人数は{people}, 予算は{cost}円, 交通機関は{traffic}の旅行プランを作成してください。"
        question(sentence)

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


if __name__ == '__main__':
    main()