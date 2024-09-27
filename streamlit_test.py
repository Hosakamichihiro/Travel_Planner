import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
import pandas as pd

def main():
    llm = ChatOpenAI(temperature=0)

    st.set_page_config(
        page_title="Trip Planner",
        page_icon="🧳"
    )
    st.header("旅行プランナー")
    st.text("・このサイトは、皆さんのバカンスを最高なものにするために開発されました。")
    st.text("・まずは目的地.グルメ.観光地などの気になる条件から入力してみましょう！")
    
    # Sidebarの選択肢を定義する
    options = ["MAP", "MEMO", "EXIT"]
    choice = st.sidebar.selectbox("Select an option", options)
    # Mainコンテンツの表示を変える
    if choice == "MAP":
        st.write("You selected MAP")
        MAP()
    elif choice == "MEMO":
        st.write("You selected MEMO")
        AI()
        condition()
    else:
        st.write("You selected EXIT")
        redirect()
    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a trip plannner.You should provide great trip plan.")
      ]


def redirect():
    st.markdown("""
        <meta http-equiv="refresh" content="0; url=https://www.google.com">
        <p>リダイレクトしています...</p>
    """, unsafe_allow_html=True)

def MAP():
    # 緯度と経度を設定
    latitude = 55 # 例として東京駅の緯度
    longitude = -3 # 例として東京駅の経度

    # 緯度と経度から地図用のデータフレームを作成
    data = pd.DataFrame({
        'lat': [latitude],
        'lon': [longitude]
    })
    st.map(data)
# 地図を表示

def AI():
    # ユーザーの入力を監視
    llm = ChatOpenAI(temperature=0)
    if user_input := st.chat_input("聞きたいことを入力して下さい"):
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("ChatGPT is typing ..."):
            response = llm(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))

    # チャット履歴の表示
    messages = st.session_state.get('messages', [])
    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message('assistant'):
                st.markdown(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message('user'):
                st.markdown(message.content)
        else:  # isinstance(message, SystemMessage):
            st.write(f"System message: {message.content}")
    #st.image("c:/Users/junakimichi/Pictures/Saved Picture/IMG_0356.JPG", use_column_width=True)


def condition():
    value = st.slider('宿泊日数', 1, 14, 1) # min, max, default
    people = st.radio(
        '人数', 
        ['1人', '2人', '3人',"4人","それ以上"]
    )
    traffic = st.radio(
        "交通",
        ["飛行機","船","新幹線","タクシー","レンタカー","自家用車"]
    )
    cost = st.radio(
        "予算",
        ["e","f","g","h"]    
    )
    if st.button("検索する"):
        question()
        st.session_state["value"]=value
        st.session_state["people"]=people
        st.session_state["traffic"]=traffic
        st.session_state["cost"]=cost

def question():
    st.write("選択した条件一覧")

if __name__ == '__main__':
    main()

    options = ["START","MAP", "MEMO", "EXIT"]
    choice = st.sidebar.selectbox("Select an option", options)
    budget = st.sidebar.number_input("予算（円）", min_value=1000, max_value=100000000, value=10000, step=1000)
    date = st.date_input("Pick a date")
    days = st.radio(
        'How many days will you stay?', 
        ['1', '2', '3', '4', '5']
    )
    traffic = st.radio(
        'Which transportation', 
        ['飛行機', '船', '新幹線', 'タクシー', 'レンタカー','マイカー']
    )
    num_of_people = st.radio(
        'How many people?', 
        ['1', '2', '3', '4', '5']
    )      
    budget = st.sidebar.number_input("予算（円）", min_value=1000, max_value=100000000, value=10000, step=1000)