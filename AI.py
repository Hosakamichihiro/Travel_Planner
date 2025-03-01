from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
import pandas as pd
from  streamlit_folium import st_folium
import folium
from langchain_community.tools import DuckDuckGoSearchRun
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim  
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io
from reportlab.lib.utils import simpleSplit
from fpdf import FPDF
import warnings
import datetime



def main():
    llm = ChatOpenAI(temperature=0)

    st.set_page_config(
        page_title="Travel Planner",
        page_icon="🧳"
    )
    st.header("Travel Planner")
    st.text("・このサイトは、皆さんのバカンスを最高なものにするために開発されました。")
    st.text("・まずは目的地.グルメ.観光地などの気になる条件から入力してみましょう！")
    # Sidebarの選択肢を定義する
    options = ["⌂ HOME","Plan your travel", "AI_plus","TRAFFIC", "DESTINATION","MAP","EXIT"]
    choice = st.sidebar.selectbox("Select an option", options)
    # Mainコンテンツの表示を変える
    if choice == "MAP":
        st.write("You selected MAP")
        MAP()
    elif choice == "⌂ HOME":
        st.write("Home Screen")
        HOME()
    elif choice == "Plan your travel":
        st.write("Strat planning your travel")
        condition()
        AI()
    elif choice == "AI_plus":
        st.write("You selected AI_plus")
        AI_plus()
    elif choice == "TRAFFIC":
        st.write("You selected WEB")
        DUCK_airplane()
    elif choice == "DESTINATION":
        st.write("You selected DESTINATION")
        DUCK_DESTINATION()
    else:
        st.write("You selected EXIT")
        redirect()

def redirect():
    st.markdown("""
        <meta http-equiv="refresh" content="0; url=https://www.google.com">
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

    # 地図をクリックしたときの処理
    st_data = st_folium(m, width=725, height=500)
    if st_data and st_data["last_clicked"] is not None:
        clicked_lat = st_data["last_clicked"]["lat"]
        clicked_lng = st_data["last_clicked"]["lng"]
        st.session_state.map_data["location"] = [clicked_lat, clicked_lng]
        st.session_state.map_data["markers"].append([clicked_lat, clicked_lng])
        st.write(f"Clicked Location: Latitude {clicked_lat}, Longitude {clicked_lng}")

    # 観光地検索フォームを表示
    st.write("観光名所を検索")
    location_name = st.text_input("観光名所名または都市名を入力してください:")

    # 観光地の検索ボタン
    if st.button("検索してマップに追加"):
        if location_name.strip():
            geolocator = Nominatim(user_agent="my_trip_planner_app")  # ユニークなuser_agentを設定
            try:
                location = geolocator.geocode(location_name, language="ja")
                if location:
                    lat, lon = location.latitude, location.longitude
                    st.session_state.map_data["location"] = [lat, lon]
                    st.session_state.map_data["markers"].append([lat, lon])
                    st.success(f"Location found: {location_name} ({lat}, {lon})")
                else:
                    st.error(f"Location '{location_name}' not found. Please check the spelling or try another location.")
            except Exception as e:
                st.error(f"An error occurred while fetching the location: {e}")
        else:
            st.warning("Please enter a location name.")
    
def web():
    # 商品名またはブランドを入力してくださいというフィールドを定義する
    user_input_web = st.text_input("国名または都市名を入力してください.入力することで、行きたい国について、少し知ることができます.詳しく知りたい場合は、下の、'Enter your question'に.")
    
    # ユーザーが入力した値があれば検索をする
    if user_input_web:
        search = DuckDuckGoSearchRun()

        # DuckDuckGoSearchRunのrunメソッドにユーザーの入力を辞書で渡す
        response = search.run({"query": user_input_web, "language": "jp"})
        st.write(response)

# CSSファイルを読み込む関数
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def HOME():
    load_css()
    # セッション状態の初期化
    if "selected_button" not in st.session_state:
        st.session_state.selected_button = None

    # CSSを適用
    load_css()

    # 画像を表示
    #st.image("Oirasekeiryu.jpg", use_container_width=True)

    # ボタンを横並びにする
    cols = st.columns(6)  # 6つのボタン用のカラムを作成

    # 各ボタンの処理
    button_labels = ["AI", "AI_plus", "TRAFFIC", "DESTINATION", "MAP", "EXIT"]
    functions = [lambda: (condition(), AI()), AI_plus, DUCK_airplane, DUCK_DESTINATION, MAP, redirect]

    for i, label in enumerate(button_labels):
        with cols[i]:
            if st.button(label):
                st.session_state.selected_button = i  # 押されたボタンの番号を記憶

    # 記憶されたボタンの関数を実行
    if st.session_state.selected_button is not None:
        functions[st.session_state.selected_button]()


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

def AI_plus():
    # ユーザーの入力を監視
    llm = ChatOpenAI(temperature=0)

    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a travel planner. You should provide great travel plans.")
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
    
def condition():
    st.header("滞在条件の設定")
    destination_type = st.radio("国内旅行か海外旅行か選んでください", ['国内', '海外'])

    if destination_type == '国内':
        todofuken = ["北海道", "東北地方", "関東地方", "中部地方", "近畿地方", "中国地方", "四国地方", "九州地方", "沖縄県"]
        region = st.radio("行きたい地方", todofuken)
    else:
        states = ["アジア", "アフリカ", "ヨーロッパ", "北アメリカ", "南アメリカ", "オセアニア"]  # 例としていくつかの国を追加
        region = st.radio("States I want to visit", states)# デフォルトを「日本」に設定
    
    min_date = datetime.date(2025, 1, 1)
    max_date = datetime.date(2030, 12, 31)
    date = st.date_input('出発日', datetime.date(2025, 1, 1), min_value=min_date, max_value=max_date)
    Departure_point = st.text_input('出発地を入力')
    days = st.slider('滞在日数', 1, 14, 1)
    time = st.time_input("出発時間を入力", value=None)
    people = st.radio('人数', ['1人', '2人', '3人', '4人', 'それ以上'])
    traffic = st.radio('交通', ["飛行機", "船", "新幹線", "タクシー", "レンタカー", "自家用車"])
    cost = st.number_input("予算（円）", min_value=1000, max_value=100000000, value=100000, step=1000)
    st.write(destination_type,"旅行を選択しています")
    st.write("行きたい場所は、", region)
    st.write("出発日は、",date)
    st.write("出発地は、",Departure_point)
    st.write("出発時間は、",time)
    st.write("滞在日数は、",days)
    st.write("人数は、",people)
    st.write("交通手段は、",traffic)
    st.write("予算は、",cost)
    st.write("以上の条件で検索しますか。検索する場合は下のボタンを押してください。")
    if st.button("検索する"):
        # 入力された国を検索条件に追加
        sentence = f"{destination_type}旅行を計画しています。行きたい場所は{region},出発日は{date},出発地は{Departure_point},出発時間は{time},滞在日数は{days}日, 人数は{people}, 予算は{cost}円, 交通機関は{traffic}の旅行プランを計画してください。"
        question(sentence)

def condition_web():
    st.header("交通手段の検索")
    global sentence_duck
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
    global AI_messages
    user_input = sentence+"please response in japanese. 応答は必ず日本語で生成してください"
    #print(user_input)
    st.write("この条件で検索しています・・・")
    llm = ChatOpenAI(temperature=0)
    if user_input := sentence:
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("ChatGPT is typing ..."):
            response = llm.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))
        

    messages = st.session_state.get('messages', [])
    for message in messages:
        if isinstance(message, AIMessage):
            with st.chat_message('assistant'):
                st.markdown(message.content)
                AI_messages = message.content
        elif isinstance(message, HumanMessage):
            with st.chat_message('user'):
                st.markdown(message.content)
        else:  # isinstance(message, SystemMessage):
            st.write(f"System message: {message.content}")   
   
    

# URLの中身を取得してテキストを表示する関数
def display_url_content(url):
    global sentence_duck
    try:
        # URLからウェブページのコンテンツを取得する
        response = requests.get(url)
        response.raise_for_status()  # エラーがあれば例外を投げる
        #print(response)
        # HTMLを解析する
        soup = BeautifulSoup(response.content, 'html.parser')

        # ここでは例としてすべてのテキストを抽出していますが、
        # より詳細な情報が必要であれば、HTMLの特定の部分を指定することもできます
        text = soup.get_text()

        # テキストを表示する
        
        sentence_duck_2 = f"{text}を踏まえて{sentence_duck}"
        question(sentence_duck_2)  # このテキストをChatGPTに渡すことができます
        
    except requests.RequestException as e:
        # HTTPリクエストでエラーが発生した場合の処理
        st.write("エラーが発生しました。")
        st.write(e)

# 抽出したテキストをChatGPTに入力として使用するためには、
# 関数を実装してChatGPT APIにリクエストを送信し、
# 結果を取得して表示するロジックを追加する必要があります。

def DUCK_DESTINATION():
    st.header("目的地の検索")
    people = st.radio( '人数', ['1人', '2人', '3人',"4人","それ以上"])
    cost = st.text_input("予算",placeholder="(単位も表記してください。)")
    place = st.text_input("目的地",placeholder="沖縄県,フランス")
    other1 = st.text_area("他にもリクエストがある場合はここに記入してください。特になければ、[なし]にチェックを入れてください。",placeholder="羽田空港発で、出来れば早朝の便は避けたいです。")
    other2 = st.checkbox("なし")

    if other1:
        other0 = other1
    else:
        other0 = "なし"

    st.write("人数：",people)
    st.write("予算：",cost)
    st.write("目的地：",place)
    st.write("リクエスト：",other0)

    if st.button("検索する"):
        sentence_destination = f"人数は{people},予算は{cost},目的地は{place},リクエストは{other0}です。最適な過ごし方を考えてください"
        duckduckgo(sentence_destination)


def DUCK_airplane():
    st.header("交通手段の検索")
    min_date = datetime.date(2025, 2, 1)
    max_date = datetime.date(2030, 12, 31)
    date = st.date_input('出発日', datetime.date(2025, 2, 1), min_value=min_date, max_value=max_date)
    min_date = datetime.date(2025, 2, 1)
    max_date = datetime.date(2030, 12, 31)
    date2 = st.date_input('到着日', datetime.date(2025, 2, 1), min_value=min_date, max_value=max_date)
    traffic = st.radio( "交通", ["飛行機","船","新幹線","タクシー","レンタカー","自家用車"])  
    region = st.text_input("出発地",placeholder="成田空港")
    place = st.text_input("目的地",placeholder="沖縄県,フランス")

    st.write("日程：",date,"~",date2)
    st.write("交通手段：",traffic)
    st.write("出発地：",region)
    st.write("目的地：",place)
   
    if st.button("検索する"):
        sentence_traffic = f"出発日は{date},到着日は{date2},交通手段は{traffic},出発地は{region},目的地は{place}です。最適な行き方を考えてください"
        duckduckgo(sentence_traffic)


def duckduckgo(sentence_duck):
    st.title("duckduckgo 検索結果")

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
            #display_url_content(href)
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

def MEMO():

    # セッションステートにリストを初期化する
    if 'my_list' not in st.session_state:
        st.session_state.my_list = []

    # ユーザーが入力した値を追加する
    new_value = st.text_area('メモを入力してください。')

    if st.button("追加"):
        if new_value:
            st.session_state.my_list.append(new_value)

    # 現在のリストを表示
    st.write('保存したメモ:', st.session_state.my_list)

if __name__ == '__main__':
    main()