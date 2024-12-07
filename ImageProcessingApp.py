import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
st.set_page_config(
    page_title="Image Processing App", 
    page_icon="🧳"
)
# Streamlitアプリの設定
st.title("画像処理アプリ:Theme")
st.subheader("画像をアップロードして処理を試してみてください。")

# サイドバーで操作の種類を選択
option = st.sidebar.selectbox(
    "操作を選択してください",
    ["オリジナル", "グレースケール", "ぼかし", "エッジ検出", "解像度アップ"]
)
# 画像アップロード
uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # PILで画像を読み込む
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)
    image_np = np.array(image)
    image_cv2 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    # OpenCV形式に変換
    image_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # 処理する画像の初期化
    processed_image = image_cv2

    # 選択された操作に応じて処理
    if option == "元の画像を表示":
        st.write("元の画像を表示しています。")
        processed_image = image_cv2
    elif option == "オリジナル":
        processed_image = image_np
    elif option == "グレースケール":
        processed_image = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)

    elif option == "ぼかし":
        # 奇数カーネルサイズを設定
        ksize = st.sidebar.slider("ぼかしの強さ (奇数のみ)", 1, 21, 5, step=2)
        processed_image = cv2.GaussianBlur(image_cv2, (ksize, ksize), 0)

    elif option == "エッジ検出":
        threshold1 = st.sidebar.slider("閾値1", 0, 255, 50)
        threshold2 = st.sidebar.slider("閾値2", 0, 255, 150)
        processed_image = cv2.Canny(image_cv2, threshold1, threshold2)

    elif option == "画像解像度を上げる":
        # 解像度を上げる（2倍に拡大）
        upscale_factor = st.sidebar.slider("拡大倍率", 1, 4, 2)
        width = image_cv2.shape[1] * upscale_factor
        height = image_cv2.shape[0] * upscale_factor
        processed_image = cv2.resize(image_cv2, (width, height), interpolation=cv2.INTER_CUBIC)

    # OpenCV形式をPIL形式に変換
    processed_image_pil = Image.fromarray(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))

    # 加工後の画像を表示
    st.image(processed_image_pil, caption="加工後の画像", use_column_width=True)

    # ダウンロード機能を追加
    buf = io.BytesIO()
    processed_image_pil.save(buf, format="PNG")
    byte_image = buf.getvalue()

    st.download_button(
        label="加工後の画像をダウンロード",
        data=byte_image,
        file_name="processed_image.png",
        mime="image/png"
    )
else:
    st.write("画像をアップロードしてください。")