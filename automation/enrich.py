import requests
from deep_translator import GoogleTranslator

STRAPI_URL = "https://gezi-rehberi-backend-f4qi.onrender.com"
STRAPI_TOKEN = "4527e21d54eac7d9d81a7d03b899835447603c3ee445f0bb2bd0a4b9f67a821b1819802ce54afc61664a3bf738c7d19322305e9fc3a8611e20623e199e02710c90ca37fcafef986984a200ae046a03ed38b5aeb5020f1380ddc5189375b45f0c4879c7192391896009c4fba60564fa223770cc43f28d2cc0a194736d800c221a"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {STRAPI_TOKEN}"
}

def get_places():
    response = requests.get(f"{STRAPI_URL}/api/places?populate=*&locale=tr")
    if response.status_code == 200:
        return response.json()["data"]
    else:
        print(f"Hata: {response.status_code}")
        return []

def translate_to_english(text):
    try:
        translator = GoogleTranslator(source='tr', target='en')
        return translator.translate(text)
    except Exception as e:
        print(f"Çeviri hatası: {e}")
        return text

def generate_image_url(place_name):
    prompt = f"Tourist attraction {place_name}, scenic landscape photography"
    encoded_prompt = requests.utils.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"

def update_place_english(document_id, english_name, english_desc):
    data = {
        "data": {
            "name": english_name,
            "description": english_desc,
        }
    }
    response = requests.put(
        f"{STRAPI_URL}/api/places/{document_id}",
        json=data,
        headers=headers,
        params={"locale": "en"}
    )
    if response.status_code in [200, 201]:
        print(f"✅ İngilizce kaydedildi!")
    else:
        print(f"❌ Hata: {response.status_code} - {response.text[:100]}")

def enrich_places():
    places = get_places()
    print(f"{len(places)} mekan bulundu\n")
    
    for place in places:
        document_id = place["documentId"]
        name = place["name"]
        description = place["description"]
        
        print(f"İşleniyor: {name}")
        
        english_name = translate_to_english(name)
        english_desc = translate_to_english(description)
        print(f"İngilizce isim: {english_name}")
        print(f"İngilizce açıklama: {english_desc[:60]}...")
        
        image_url = generate_image_url(name)
        print(f"Görsel URL üretildi ✅")
        
        update_place_english(document_id, english_name, english_desc)
        print()

if __name__ == "__main__":
    enrich_places()