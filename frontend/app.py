import streamlit as st
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(
    page_title="YZ Destekli Gezi Rehberi",
    page_icon="🌍",
    layout="wide"
)

STRAPI_URL = "https://gezi-rehberi-backend-f4qi.onrender.com"

PLACE_IMAGES = {
    "Eyfel Kulesi": "https://picsum.photos/id/318/800/500",
    "Louvre Müzesi": "https://picsum.photos/id/188/800/500",
    "Senso-ji Tapınağı": "https://picsum.photos/id/164/800/500",
    "Ayasofya": "https://picsum.photos/id/162/800/500",
    "Central Park": "https://picsum.photos/id/15/800/500",
    "Kolezyum": "https://picsum.photos/id/395/800/500",
}

@st.cache_data
def load_image(url):
    try:
        r = requests.get(url, timeout=15)
        return Image.open(BytesIO(r.content))
    except:
        return None

def get_cities():
    response = requests.get(f"{STRAPI_URL}/api/cities?locale=tr")
    if response.status_code == 200:
        return response.json()["data"]
    return []

def get_places(city_name, locale="tr"):
    response = requests.get(f"{STRAPI_URL}/api/places?populate=*&locale={locale}")
    if response.status_code == 200:
        places = response.json()["data"]
        return [p for p in places if p.get("city") and p["city"].get("name") == city_name]
    return []

st.title("🌍 YZ Destekli Gezi Rehberi")
st.markdown("Dünya'nın en güzel şehirlerini keşfet!")

col1, col2 = st.columns([3, 1])
with col2:
    lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English"])
    locale = "tr" if lang == "Türkçe" else "en"

cities = get_cities()

if not cities:
    st.error("Şehirler yüklenemedi!")
else:
    city_names = [c["name"] for c in cities]
    with col1:
        selected_city = st.selectbox("🏙️ Şehir Seç", city_names)
    
    selected_city_data = next((c for c in cities if c["name"] == selected_city), None)
    if selected_city_data:
        st.markdown(f"### 📍 {selected_city_data['name']} - {selected_city_data['country']}")
        st.info(selected_city_data["description"])
    
    st.divider()
    places = get_places(selected_city, locale)
    
    if not places:
        st.warning("Bu şehir için mekan bulunamadı.")
    else:
        st.markdown(f"### 🗺️ {selected_city} - Gezilecek Yerler")
        cols = st.columns(3)
        for i, place in enumerate(places):
            with cols[i % 3]:
                name = place["name"]
                description = place["description"]
                rating = place.get("rating", 0)
                url = PLACE_IMAGES.get(name, f"https://picsum.photos/id/{abs(hash(name)) % 200 + 1}/800/500")
                img = load_image(url)
                if img:
                    st.image(img, use_container_width=True)
                st.markdown(f"**{name}**")
                st.markdown(f"⭐ {rating}/5")
                st.markdown(description)
                st.divider()