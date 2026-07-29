import streamlit as st
from PIL import Image, ImageFilter
from rembg import remove
import io
import numpy as np

st.set_page_config(page_title="Filter Image App", layout="wide")

st.title("🎨 Filter Image App")

# ---------------- Filters ---------------- #

def filter_vintage(img):
    arr = np.array(img, dtype=np.float32)
    arr[:,:,0] = np.clip(arr[:,:,0]*1.1+20,0,255)
    arr[:,:,1] = np.clip(arr[:,:,1]*0.9+10,0,255)
    arr[:,:,2] = np.clip(arr[:,:,2]*0.75,0,255)
    return Image.fromarray(arr.astype(np.uint8))

def filter_bw(img):
    return img.convert("L").convert("RGB")

def filter_sharp(img):
    return img.filter(ImageFilter.SHARPEN)

def filter_blur(img):
    return img.filter(ImageFilter.BLUR)

def filter_warm(img):
    arr=np.array(img,dtype=np.float32)
    arr[:,:,0]=np.clip(arr[:,:,0]*1.2+20,0,255)
    arr[:,:,1]=np.clip(arr[:,:,1]*1.1+10,0,255)
    arr[:,:,2]=np.clip(arr[:,:,2]*0.85,0,255)
    return Image.fromarray(arr.astype(np.uint8))

def filter_gray(img):
    return img.convert("L").convert("RGB")

def filter_edge(img):
    return img.filter(ImageFilter.FIND_EDGES)

filters={
    "No Filter":None,
    "Vintage":filter_vintage,
    "Black & White":filter_bw,
    "Sharp":filter_sharp,
    "Blur":filter_blur,
    "Warm":filter_warm,
    "Grayscale":filter_gray,
    "Edge Detection":filter_edge
}

# ---------------- Upload ---------------- #

bg_file=st.file_uploader(
    "Upload Background",
    type=["jpg","jpeg","png"]
)

person_file=st.file_uploader(
    "Upload Person Image",
    type=["jpg","jpeg","png"]
)

if bg_file and person_file:

    with st.spinner("Removing background..."):

        person_bytes=remove(person_file.getvalue())

    person=Image.open(io.BytesIO(person_bytes)).convert("RGBA")
    background=Image.open(bg_file).convert("RGBA")

    scale=st.slider(
        "Scale (%)",
        10,
        100,
        50
    )

    ratio=scale/100

    new_w=int(person.width*ratio)
    new_h=int(person.height*ratio)

    try:
        resample=Image.Resampling.LANCZOS
    except AttributeError:
        resample=Image.LANCZOS

    person=person.resize((new_w,new_h),resample)

    # Make sure person fits background
    if person.width>background.width or person.height>background.height:

        fit=min(
            background.width/person.width,
            background.height/person.height
        )*0.9

        person=person.resize(
            (
                int(person.width*fit),
                int(person.height*fit)
            ),
            resample
        )

    max_x=max(0,background.width-person.width)
    max_y=max(0,background.height-person.height)

    pos_x=st.slider(
        "Horizontal Position",
        0,
        max_x,
        max_x//2
    )

    pos_y=st.slider(
        "Vertical Position",
        0,
        max_y,
        max_y//2
    )

    final=background.copy()
    final.paste(person,(pos_x,pos_y),person)

    choice=st.selectbox(
        "Choose Filter",
        list(filters.keys())
    )

    result=final.convert("RGB")

    if filters[choice]:
        result=filters[choice](result)

    col1,col2=st.columns(2)

    with col1:
        st.image(background,caption="Background")

    with col2:
        st.image(result,caption="Final Image")

    buffer=io.BytesIO()
    result.save(buffer,format="PNG")

    st.download_button(
        "⬇ Download Image",
        data=buffer.getvalue(),
        file_name="FinalImage.png",
        mime="image/png"
    )
