import streamlit as st
from PIL import Image, ImageFilter
import requests
import io
import numpy as np

st.set_page_config(page_title="Filter Image App", layout="wide")

st.title("🎨 Filter Image App")

# -------------------------
# Filters
# -------------------------

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
    arr[:, :, 0] = np.clip(arr[:, :, 0] * 1.2 + 20, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] * 1.1 + 10, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] * 0.85, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))


def filter_grayscale(img):
    return img.convert("L").convert("RGB")


def filter_edge(img):
    return img.filter(ImageFilter.FIND_EDGES)


filters = {
    "No Filter": None,
    "Vintage": filter_vintage,
    "Black & White": filter_bw,
    "Sharp": filter_sharp,
    "Blur": filter_blur,
    "Warm": filter_warm,
    "Grayscale": filter_grayscale,
    "Edge Detection": filter_edge,
}

# -------------------------
# Inputs
# -------------------------

api_key = st.text_input("Enter Remove.bg API Key", type="password")

bg_file = st.file_uploader(
    "Upload Background",
    type=["png", "jpg", "jpeg"]
)

uploaded = st.file_uploader(
    "Upload Person Image",
    type=["png", "jpg", "jpeg"]
)

# -------------------------
# Process
# -------------------------

if uploaded and bg_file:

    if not api_key:
        st.warning("Please enter your Remove.bg API key.")
        st.stop()

    with st.spinner("Removing background..."):

        try:
            response = requests.post(
                "https://api.remove.bg/v1.0/removebg",
                files={
                    "image_file": (
                        uploaded.name,
                        uploaded.getvalue(),
                        uploaded.type,
                    )
                },
                data={"size": "auto"},
                headers={"X-Api-Key": api_key},
                timeout=60,
            )

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error:\n{e}")
            st.stop()

    if response.status_code != 200:
        st.error("Background removal failed.")
        st.code(response.text)
        st.stop()

    st.success("Background removed successfully!")

    person = Image.open(io.BytesIO(response.content)).convert("RGBA")
    background = Image.open(bg_file).convert("RGBA")

    scale = st.slider("Scale (%)", 10, 200, 100)

    ratio = scale / 100

    new_width = int(person.width * ratio)
    new_height = int(person.height * ratio)

    person = person.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS,
    )

    max_x = max(0, background.width - person.width)
    max_y = max(0, background.height - person.height)

    pos_x = st.slider("Horizontal Position", 0, max_x, 0)
    pos_y = st.slider("Vertical Position", 0, max_y, 0)

    final = background.copy()
    final.paste(person, (pos_x, pos_y), person)

    choice = st.selectbox(
        "Choose Filter",
        list(filters.keys())
    )

    result = final.convert("RGB")

    if filters[choice] is not None:
        result = filters[choice](result)

    col1, col2 = st.columns(2)

    with col1:
        st.image(background, caption="Background")

    with col2:
        st.image(result, caption="Final Image")

    buffer = io.BytesIO()
    result.save(buffer, format="PNG")
    buffer.seek(0)

    st.download_button(
        label="Download Image",
        data=buffer,
        file_name="FilteredImage.png",
        mime="image/png",
    )
