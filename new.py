import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
import pandas as pd

flag = False 
sentence = "aaa"
def main():
    llm = ChatOpenAI(temperature=0)

    st.set_page_config(
        page_title="Trip Planner",
        page_icon="🧳"
    )
    st.header("Trip Planner")
    st.text("・This site was developed to help you make the most of your vacation.")
    st.text("・First, enter the conditions you are interested in,such as your destination, gourmet food, tourist spots, etc.")
    
    # Sidebarの選択肢を定義する
    options = ["START","MAP", "MEMO", "EXIT"]
    choice = st.sidebar.selectbox("Select an option", options)
    # Mainコンテンツの表示を変える
    if choice == "START":
        st.write("You selected START")
        AI()
        condition()
    elif choice == "MAP":
        st.write("You selected MEMO")
        MAP()

    elif choice == "MEMO":
        st.write("You selected MEMO")
        AI()
        
    else:
        st.write("You selected EXIT")
        redirect()
    


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

# チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a trip plannner.You should provide great trip plan.")
      ]

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
    global flag,sentence
    days = st.slider('宿泊日数', 1, 14, 1) # min, max, default
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
        st.session_state["days"]=days
        st.session_state["people"]=people
        st.session_state["traffic"]=traffic
        st.session_state["cost"]=cost
        flag = True
        sentence =  ("滞在日数は",days,"日,",
                              "人数は",people,"人,","予算は",cost,"円,",
                              "交通機関は",traffic,"の旅行プランを計画してください")
def question():
    global flag, sentence
    if flag == True:
        llm = ChatOpenAI(temperature=0)
        
        user_input = sentence
        print(user_input)
        st.write("この条件で検索しています・・・")
        
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("ChatGPT is typing ..."):
            response = llm(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))

    # ここで `messages` を取得
        messages = st.session_state.get('messages', [])

        # メッセージのループ処理
        for message in messages:
            if isinstance(message, AIMessage):
                with st.chat_message('assistant'):
                    st.markdown(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message('user'):
                    st.markdown(message.content)
            #else:  # SystemMessage の場合
                #st.write(f"System message: {message.content}")

    # フラグをリセット
    flag = False
if __name__ == '__main__':
    main()
    