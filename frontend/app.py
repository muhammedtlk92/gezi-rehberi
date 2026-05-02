import streamlit as st
import requests
from PIL import Image

st.set_page_config(
    page_title="YZ Destekli Gezi Rehberi",
    page_icon="🌍",
    layout="wide"
)

STRAPI_URL = "https://gezi-rehberi-backend-f4qi.onrender.com"

PLACE_IMAGES = {
    "Eyfel Kulesi": "eyfel kulesi.jpg",
    "Louvre Müzesi": "Louvre Müzesi.jpg",
    "Senso-ji Tapınağı": "Senso-ji Tapınağı.jpg",
    "Ayasofya": "Ayasofya.jpg",
    "Central Park": "centralpark.jpg",
    "Kolezyum": "kolezyum.jpg",
}

@st.cache_data
def load_image(filename):
    try:
        return Image.open(filename)
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
                filename = PLACE_IMAGES.get(name)
                img = load_image(filename) if filename else None
                if img:
                    st.image(img, use_container_width=True)
                st.markdown(f"**{name}**")
                st.markdown(f"⭐ {rating}/5")
                st.markdown(description)
                st.divider()