import streamlit as st
from  streamlit_folium import st_folium
import folium

# 地図の表示箇所とズームレベルを指定してマップデータを作成
# attr（アトリビュート）は地図右下に表示する文字列。
# デフォルトマップの場合は省略可能

def main():
    # タイトル。最もサイズが大きい。ページタイトル向け
    st.title('Map')
    # ヘッダ。２番目に大きい。項目名向け
    st.header('Streamlit')

    m = folium.Map(
        location=[35.17081269026154, 137.0339428258054],
        zoom_start=16,
        attr='Folium map'
    )

    # 地図上のクリックした場所にポップアップを表示する
    m.add_child(folium.LatLngPopup())

    # ユーザーのクリック情報を取得
    st_data = st_folium(m, width=725, height=500)

    # ユーザーが地図上をクリックした場合の処理
    if st_data["last_clicked"] is not None:
        clicked_lat = st_data["last_clicked"]["lat"]
        clicked_lng = st_data["last_clicked"]["lng"]

        st.write(f"クリックした場所の座標: 緯度 {clicked_lat}, 経度 {clicked_lng}")

        # 新しい地図を作成してクリックした場所にマーカーを追加
        m = folium.Map(
            location=[clicked_lat, clicked_lng],
            zoom_start=16,
            attr='Folium map'
        )

        # マーカーをクリックした場所に追加
        folium.Marker(
            location=[clicked_lat, clicked_lng],
            popup=f"Latitude: {clicked_lat}, Longitude: {clicked_lng}",
            tooltip="Click me!"
        ).add_to(m)

        # マップを再表示
        st_folium(m, width=725, height=500)


    
    lang_dict = {

    "error": "エラーメッセージ。赤文字に薄赤背景",
    "warning": "警告メッセージ。黄色文字に薄黄色背景",
    "info": "情報メッセージ。青文字に薄青背景",
    "success" : "成功メッセージ。緑文字に薄緑背景",
    "exception(Exception('Ooops!'))" : "例外メッセージ。Exception部分が太字の赤文字・薄赤背景"
   
    }

    st.subheader("Choose a widget")
    #streamlitのセレクトボックスを使って、辞書からアイテムを選びます。
    lang = st.selectbox(label="Streamlit widget",options=lang_dict)

    st.write("You selected", lang,".")

    st.write("explanation:", lang_dict[lang]) #キーを指定して、説明を取り出します。
    
    st.image("hakonetozantetsudo.jpg", width=300)

if __name__ == '__main__':
  main()