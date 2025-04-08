# Web tabanlı canlı grafik için Streamlit uygulaması
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Canlı Altın Grafiği", layout="wide")
st_autorefresh(interval=60 * 1000, key="otomatik_yenileme")  # 60 saniyede bir yenileme
st.title("📈 Canlı Gram Altın ve Ons Altın Grafiği")

# Veri çekme fonksiyonu
def veri_cek():
    url = "https://altin.in/fiyat/gram-altin"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    try:
        gram_altin = float(soup.find("span", id="spot_value").text.replace(",", "."))
    except:
        gram_altin = None

    try:
        ons_altin = float(soup.find("span", id="ons_value").text.replace(",", "."))
    except:
        ons_altin = None

    return gram_altin, ons_altin

# Session state ile veri saklama
if "veri" not in st.session_state:
    st.session_state.veri = pd.DataFrame(columns=["Zaman", "GramAltin", "OnsAltin"])

# Otomatik veri çekme
gram, ons = veri_cek()
zaman = pd.Timestamp.now()

if gram is not None and ons is not None:
    yeni_veri = pd.DataFrame([[zaman, gram, ons]], columns=["Zaman", "GramAltin", "OnsAltin"])
    st.session_state.veri = pd.concat([st.session_state.veri, yeni_veri]).tail(100)

# Grafik çizimi
grafik_df = st.session_state.veri.melt("Zaman", var_name="Tür", value_name="Fiyat")

if not grafik_df.empty:
    chart = alt.Chart(grafik_df).mark_line().encode(
        x="Zaman:T",
        y="Fiyat:Q",
        color="Tür:N"
    ).properties(
        width=800,
        height=400,
        title="Gram Altın ve Ons Altın"
    )
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Henüz veri bulunamadı. Lütfen sayfayı yenileyin.")
