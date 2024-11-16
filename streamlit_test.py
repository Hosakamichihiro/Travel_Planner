import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (SystemMessage, HumanMessage, AIMessage)
from streamlit_folium import st_folium
import folium
from langchain_community.tools import DuckDuckGoSearchRun
from duckduckgo_search import DDGS

def main():
    st.set_page_config(page_title="Trip Planner", page_icon="🧳")
    st.header("Trip Planner")
    st.text("Make the most of your vacation with our trip planner.")

    options = ["START", "WEB", "MAP", "MEMO", "EXIT"]
    choice = st.sidebar.selectbox("Select an option", options)

    if choice == "START":
        st.write("You selected START")
        web_search()
        trip_plan()
        ai_chat
    elif choice == "WEB":
        st.write("You selected WEB")
        web_search()
    elif choice == "MAP":
        st.write("You selected MAP")
        display_map()
    elif choice == "MEMO":
        st.write("You selected MEMO")
        ai_chat()
    else:
        st.write("You selected EXIT")
        st.markdown("""<meta http-equiv="refresh" content="0; url=https://www.google.com">""", unsafe_allow_html=True)

def display_map():
    m = folium.Map(location=[35.6812378, 139.7669852], zoom_start=16)
    m.add_child(folium.LatLngPopup())
    st_data = st_folium(m, width=725, height=500)

    if st_data["last_clicked"] is not None:
        clicked_lat = st_data["last_clicked"]["lat"]
        clicked_lng = st_data["last_clicked"]["lng"]
        st.write(f"Coordinates: Latitude {clicked_lat}, Longitude {clicked_lng}")

        folium.Marker(location=[clicked_lat, clicked_lng], popup=f"Latitude: {clicked_lat}, Longitude: {clicked_lng}").add_to(m)
        st_folium(m, width=725, height=500)

def web_search():
    user_input = st.text_input("Enter a country or city to explore:")
    if user_input:
        search = DuckDuckGoSearchRun()
        response = search.run({"query": user_input, "language": "jp"})
        st.write(response)

def ai_chat():
    llm = ChatOpenAI(temperature=0)
    if "messages" not in st.session_state:
        st.session_state.messages = [SystemMessage(content="You are a trip planner.")]

    if user_input := st.chat_input("Enter your question:"):
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.spinner("ChatGPT is typing ..."):
            response = llm.invoke(st.session_state.messages)
        st.session_state.messages.append(AIMessage(content=response.content))

    for message in st.session_state.get('messages', []):
        if isinstance(message, AIMessage):
            st.markdown(f"**Assistant:** {message.content}")
        elif isinstance(message, HumanMessage):
            st.markdown(f"**You:** {message.content}")

def trip_plan():
    destination_type = st.radio("Select trip type", ['Domestic', 'International'])
    region_options = ["Hokkaido", "Tohoku", "Kanto", "Chubu", "Kinki", "Chugoku", "Shikoku", "Kyushu", "Okinawa"] if destination_type == 'Domestic' else ["Asia", "Africa", "Europe", "North America", "South America", "Oceania"]
    region = st.radio("Choose a region", region_options)
    days = st.slider('Days', 1, 14, 1)
    people = st.radio('Number of people', ['1', '2', '3', '4', 'More'])
    traffic = st.radio('Transportation', ["Flight", "Ship", "Shinkansen", "Taxi", "Rental Car", "Private Car"])
    cost = st.sidebar.number_input("Budget (JPY)", min_value=1000, max_value=100000000, value=10000, step=1000)

    if st.button("Search"):
        query = f"Planning a {destination_type.lower()} trip to {region} for {days} days with {people} person(s), budget {cost} JPY, using {traffic}. Respond in Japanese."
        

if __name__ == '__main__':
    main()