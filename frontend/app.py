import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import os

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
    "Eiffel Tower": "eyfel kulesi.jpg",
    "Louvre Museum": "Louvre Müzesi.jpg",
    "Senso-ji Temple": "Senso-ji Tapınağı.jpg",
    "hagia sophia": "Ayasofya.jpg",
    "coliseum": "kolezyum.jpg",
}

PLACE_IMAGES_FALLBACK = {
    "Eyfel Kulesi": "https://picsum.photos/id/318/800/500",
    "Louvre Müzesi": "https://picsum.photos/id/188/800/500",
    "Senso-ji Tapınağı": "https://picsum.photos/id/164/800/500",
    "Ayasofya": "https://picsum.photos/id/162/800/500",
    "Central Park": "https://picsum.photos/id/15/800/500",
    "Kolezyum": "https://picsum.photos/id/395/800/500",
    "Eiffel Tower": "https://picsum.photos/id/318/800/500",
    "Louvre Museum": "https://picsum.photos/id/188/800/500",
    "Senso-ji Temple": "https://picsum.photos/id/164/800/500",
    "hagia sophia": "https://picsum.photos/id/162/800/500",
    "coliseum": "https://picsum.photos/id/395/800/500",
}

TRANSLATIONS = {
    "tr": {
        "places_title": "Gezilecek Yerler",
        "no_places": "Bu şehir için mekan bulunamadı.",
        "no_cities": "Şehirler yüklenemedi!",
    },
    "en": {
        "places_title": "Places to Visit",
        "no_places": "No places found for this city.",
        "no_cities": "Could not load cities!",
    }
}

@st.cache_data
def load_image_from_url(url):
    try:
        r = requests.get(url, timeout=15)
        return Image.open(BytesIO(r.content))
    except:
        return None

def get_image(name):
    local_path = PLACE_IMAGES.get(name)
    if local_path and os.path.exists(local_path):
        try:
            return Image.open(local_path)
        except:
            pass
    url = PLACE_IMAGES_FALLBACK.get(name, f"https://picsum.photos/id/{abs(hash(name)) % 200 + 1}/800/500")
    return load_image_from_url(url)

@st.cache_data
def get_cities(locale="tr"):
    response = requests.get(f"{STRAPI_URL}/api/cities?locale={locale}")
    if response.status_code == 200:
        return response.json()["data"]
    return []

def get_places(city_name, locale="tr"):
    tr_response = requests.get(f"{STRAPI_URL}/api/places?populate=*&locale=tr")
    tr_places = tr_response.json()["data"] if tr_response.status_code == 200 else []
    tr_doc_ids = [p["documentId"] for p in tr_places if p.get("city") and p["city"].get("name") == city_name]

    if locale == "tr":
        return [p for p in tr_places if p["documentId"] in tr_doc_ids]

    en_response = requests.get(f"{STRAPI_URL}/api/places?populate=*&locale=en")
    en_places = en_response.json()["data"] if en_response.status_code == 200 else []
    return [p for p in en_places if p["documentId"] in tr_doc_ids]

st.title("🌍 YZ Destekli Gezi Rehberi")
st.markdown("Dünya'nın en güzel şehirlerini keşfet!")

# Session state başlat
if "city_index" not in st.session_state:
    st.session_state.city_index = 0

col1, col2 = st.columns([3, 1])
with col2:
    lang = st.selectbox("🌐 Dil / Language", ["Türkçe", "English"])
    locale = "tr" if lang == "Türkçe" else "en"

t = TRANSLATIONS[locale]

# TR şehirleri her zaman ana referans
tr_cities = get_cities("tr")
locale_cities = get_cities(locale)
if not locale_cities:
    locale_cities = tr_cities

if not tr_cities:
    st.error(t["no_cities"])
else:
    tr_city_names = [c["name"] for c in tr_cities]
    locale_city_names = [c["name"] for c in locale_cities]

    with col1:
        selected_city = st.selectbox(
            "🏙️ Şehir Seç",
            locale_city_names,
            index=st.session_state.city_index
        )
        st.session_state.city_index = locale_city_names.index(selected_city)

    # TR karşılığını bul
    tr_city_name = tr_city_names[st.session_state.city_index]

    selected_city_data = locale_cities[st.session_state.city_index]
    if selected_city_data:
        st.markdown(f"### 📍 {selected_city_data['name']} - {selected_city_data['country']}")
        st.info(selected_city_data["description"])

    st.divider()

    places = get_places(tr_city_name, locale)

    if not places:
        st.warning(t["no_places"])
    else:
        st.markdown(f"### 🗺️ {selected_city} - {t['places_title']}")
        cols = st.columns(3)
        for i, place in enumerate(places):
            with cols[i % 3]:
                name = place["name"]
                description = place["description"]
                rating = place.get("rating", 0)
                img = get_image(name)
                if img:
                    st.image(img, use_container_width=True)
                st.markdown(f"**{name}**")
                st.markdown(f"⭐ {rating}/5")
                st.markdown(description)
                st.divider()