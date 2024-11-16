import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
from streamlit_folium import st_folium
import folium
from langchain_community.tools import DuckDuckGoSearchRun

class TravelPlannerApp:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0)
        self.initialize_session_state()

    def initialize_session_state(self):
        if "messages" not in st.session_state:
            st.session_state.messages = [
                SystemMessage(content="You are a trip planner. You should provide great trip plans.")
            ]
        if "map_data" not in st.session_state:
            st.session_state.map_data = {
                "location": [35.6812378, 139.7669852],  # Default location
                "markers": []  # List of markers
            }

    def run(self):
        st.set_page_config(page_title="Trip Planner", page_icon="🧳")
        st.title("Trip Planner")
        st.write("・This site was developed to help you make the most of your vacation.")
        st.write("・First, enter the conditions you are interested in, such as your destination, gourmet food, tourist spots, etc.")

        # Sidebar options
        options = ["START", "WEB", "MAP", "MEMO", "EXIT"]
        choice = st.sidebar.selectbox("Select an option", options)

        if choice == "START":
            self.start_page()
        elif choice == "WEB":
            self.web_page()
        elif choice == "MAP":
            self.map_page()
        elif choice == "MEMO":
            self.memo_page()
        elif choice == "EXIT":
            self.exit_page()

    def start_page(self):
        st.write("You selected START")
        self.web()
        self.ai()
        self.condition()

    def web_page(self):
        st.write("You selected WEB")
        self.ai()
        self.condition_web()

    def map_page(self):
        st.write("You selected MAP")
        self.display_map()

    def memo_page(self):
        st.write("You selected MEMO")
        self.ai()

    def exit_page(self):
        st.markdown("""
            <meta http-equiv="refresh" content="0; url=https://www.google.com">
            <p>Redirecting...</p>
        """, unsafe_allow_html=True)

    def display_map(self):
        # Initialize map
        m = folium.Map(location=st.session_state.map_data["location"], zoom_start=16)
        m.add_child(folium.LatLngPopup())

        # Add existing markers
        for marker in st.session_state.map_data["markers"]:
            folium.Marker(location=marker, popup=f"Latitude: {marker[0]}, Longitude: {marker[1]}").add_to(m)

        # Display map and get user interaction
        st_data = st_folium(m, width=725, height=500)

        if st_data["last_clicked"] is not None:
            clicked_lat = st_data["last_clicked"]["lat"]
            clicked_lng = st_data["last_clicked"]["lng"]

            # Update session state
            st.session_state.map_data["location"] = [clicked_lat, clicked_lng]
            st.session_state.map_data["markers"] = [[clicked_lat, clicked_lng]]

            st.write(f"Coordinates: Latitude {clicked_lat}, Longitude {clicked_lng}")

            # Update map
            m = folium.Map(location=st.session_state.map_data["location"], zoom_start=16)
            folium.Marker(location=[clicked_lat, clicked_lng], popup=f"Latitude: {clicked_lat}, Longitude: {clicked_lng}").add_to(m)
            st_folium(m, width=725, height=500)

    def web(self):
        user_input_web = st.text_input("Enter a country or city to learn more about it.")
        if user_input_web:
            search = DuckDuckGoSearchRun()
            response = search.run({"query": user_input_web, "language": "jp"})
            st.write(response)

    def ai(self):
        if user_input := st.chat_input("Enter your question:"):
            st.session_state.messages.append(HumanMessage(content=user_input))
            with st.spinner("ChatGPT is typing ..."):
                response = self.llm.invoke(st.session_state.messages)
            st.session_state.messages.append(AIMessage(content=response.content))

        messages = st.session_state.get("messages", [])
        for message in messages:
            if isinstance(message, AIMessage):
                st.markdown(f"**Assistant:** {message.content}")
            elif isinstance(message, HumanMessage):
                st.markdown(f"**You:** {message.content}")

    def condition(self):
        destination_type = st.radio("国内旅行か海外旅行か選んでください", ['国内', '海外'])
        region = st.radio("行きたい地方", self.get_region_options(destination_type))
        days = st.slider('宿泊日数', 1, 14, 1)
        people = st.radio('人数', ['1人', '2人', '3人', '4人', 'それ以上'])
        traffic = st.radio('交通', ["飛行機", "船", "新幹線", "タクシー", "レンタカー", "自家用車"])
        cost = st.sidebar.number_input("予算（円）", min_value=1000, max_value=100000000, value=10000, step=1000)

        if st.button("検索する"):
            query = (f"{destination_type}旅行を計画しています。行きたい場所は{region}, "
                     f"滞在日数は{days}日, 人数は{people}, 予算は{cost}円, "
                     f"交通機関は{traffic}の旅行プランを計画してください。")
            self.question(query)

    def condition_web(self):
        destination_type = st.radio("国内旅行か海外旅行か選んでください", ['国内', '海外'])
        region = st.radio("行きたい地方", self.get_region_options(destination_type))
        days = st.slider('宿泊日数', 1, 14, 1)
        people = st.radio('人数', ['1人', '2人', '3人', '4人', 'それ以上'])
        traffic = st.radio('交通', ["飛行機", "船", "新幹線", "タクシー", "レンタカー", "自家用車"])
        cost = st.sidebar.number_input("予算（円）", min_value=1000, max_value=100000000, value=10000, step=1000)
        other = st.text_area("他にもリクエストがある場合はここに記入してください。", placeholder="例: 羽田空港発で、早朝の便は避けたい")
        if st.button("検索する"):
            query = (f"{destination_type}旅行を計画しています。行きたい場所は{region}, "
                     f"滞在日数は{days}日, 人数は{people}, 予算は{cost}円, "
                     f"交通機関は{traffic}, 他のリクエストは「{other}」。")
            self.duckduckgo(query)

    def question(self, query):
        user_input = f"{query} 応答は必ず日本語で生成してください"
        st.write("この条件で検索しています・・・")
        if user_input:
            st.session_state.messages.append(HumanMessage(content=user_input))
            with st.spinner("ChatGPT is typing ..."):
                response = self.llm.invoke(st.session_state.messages)
            st.session_state.messages.append(AIMessage(content=response.content))

        messages = st.session_state.get("messages", [])
        for message in messages:
            if isinstance(message, AIMessage):
                st.markdown(f"**Assistant:** {message.content}")

    def duckduckgo(self, query):
        st.header("DuckDuckGo 検索結果")
        st.write(f"検索クエリ: {query}")
        # Implement actual search logic if needed

    @staticmethod
    def get_region_options(destination_type):
        if destination_type == '国内':
            return ["北海道", "東北地方", "関東地方", "中部地方", "近畿地方", "中国地方", "四国地方", "九州地方", "沖縄県"]
        else:
            return ["アジア", "アフリカ", "ヨーロッパ", "北アメリカ", "南アメリカ", "オセアニア"]

if __name__ == '__main__':
    app = TravelPlannerApp()
    app.run()