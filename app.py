import streamlit as st
from PIL import Image, ImageFilter
import requests
import io
import numpy as np

st.title("Filter Image App")

def filter_vintage(img):
    arr = np.array(img, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.1 + 20, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] * 0.9 + 10, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.75, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def filter_bw(img):
    return img.convert("L").convert("RGB")

def filter_sharp(img):
    return img.filter(ImageFilter.SHARPEN)

def filter_blur(img):
    return img.filter(ImageFilter.BLUR)

def filter_warm(img):
    arr = np.array(img, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.20 + 20, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.10 + 10, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.85, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def filter_grayscale(img):
    return img.convert("L").convert("RGB")

def filter_edge(img):
    return img.filter(ImageFilter.FIND_EDGES)

filters = {
    "No filter": None,
    "Vintage": filter_vintage,
    "Black & White": filter_bw,
    "Sharp": filter_sharp,
    "Blur": filter_blur,
    "Warm": filter_warm,
    "Grayscale": filter_grayscale,
    "Edge Detection": filter_edge
}

api_key = st.text_input("Enter your API", type="password")

bg_file = st.file_uploader("Upload your background", type=["png", "jpg"])
uploaded = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded and bg_file:
    # Remove background using remove.bg
    with st.spinner("Removing the bg..."):
        uploaded.seek(0)
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": uploaded},
            data={"size": "auto"},
            headers={"X-Api-Key": api_key}
        )

    if response.status_code == 200:
        

        # Sliders
        scale = st.slider("Image Scale", 10, 100, 50)
        pos_x = st.slider("Image Position x", 0, 500, 50)
        pos_y = st.slider("Image Position y", 0, 500, 70)
        person_no_bg = Image.open(io.BytesIO(response.content)).convert("RGBA")

        # Resize person image based on background height
        bg_img = Image.open(bg_file).convert("RGB")
        bg_w, bg_h = bg_img.size

        new_h = int(bg_h * scale / 100)
        ratio = new_h / person_no_bg.size[1]
        new_w = int(person_no_bg.size[0] * ratio)

        person_resized = person_no_bg.resize((new_w, new_h), Image.LANCZOS)

    else:
        st.error("Error removing background")
        st.stop()

    col1, col2 = st.columns(2)
    col1.image(person_resized, caption="Person (Resized)")
    col2.image(bg_img, caption="Background")

    choice = st.selectbox("Choose a filter", list(filters.keys()))

    if filters[choice] is None:
        result = person_resized
    else:
        result = filters[choice](person_resized)

    st.image(result, caption=f"Filtered: {choice}")

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    buf.seek(0)

    st.download_button("Download Image", buf, file_name="FilteredImage.png", mime="image/png")
