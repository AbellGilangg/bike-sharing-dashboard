import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

def load_data():
    day_df = pd.read_csv("main_data.csv")
    hour_df = pd.read_csv("hour.csv")
    
    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    hour_df["dteday"] = pd.to_datetime(hour_df["dteday"])
    
    season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
    weather_map = {1: "Clear", 2: "Mist", 3: "Light Snow/Rain", 4: "Heavy Rain"}
    
    day_df["season_label"] = day_df["season"].map(season_map)
    day_df["weather_label"] = day_df["weathersit"].map(weather_map)
    hour_df["season_label"] = hour_df["season"].map(season_map)
    
    return day_df, hour_df

day_df, hour_df = load_data()

st.title("🚲 Bike Sharing Data Analytics Dashboard")

# Sidebar
st.sidebar.header("Filter Dashboard")
st.sidebar.markdown("Analisis data penyewaan sepeda tahun 2012")

# --- Pertanyaan 1 ---
st.subheader("1. Performa Penyewaan Berdasarkan Musim (2012)")
day_2012 = day_df[day_df["yr"] == 1]
season_avg = day_2012.groupby("season_label")["cnt"].mean().reset_index().sort_values("cnt", ascending=False)

fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(x="cnt", y="season_label", data=season_avg, palette="viridis", ax=ax1)
ax1.set_xlabel("Rata-rata Penyewaan")
ax1.set_ylabel(None)
st.pyplot(fig1)

with st.expander("Lihat Insight Musim"):
    st.write("Di tahun 2012, musim Fall (Gugur) mencatat rata-rata penyewaan tertinggi. Strategi stok maksimal harus diterapkan pada musim ini.")

# --- Pertanyaan 2 ---
st.subheader("2. Puncak Jam Kerja (Q4 2012)")
hour_q4 = hour_df[(hour_df["yr"] == 1) & (hour_df["mnth"].isin([10, 11, 12])) & (hour_df["workingday"] == 1)]
hourly_trend = hour_q4.groupby("hr")["cnt"].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(12, 5))
sns.lineplot(x="hr", y="cnt", data=hourly_trend, marker="o", color="blue", ax=ax2)
ax2.set_xticks(range(0, 24))
ax2.set_xlabel("Jam (0-23)")
ax2.set_ylabel("Rata-rata Penyewaan")
ax2.grid(True, linestyle="--", alpha=0.5)
st.pyplot(fig2)

with st.expander("Lihat Insight Jam Puncak"):
    st.write("Terdapat lonjakan tajam pada jam 08:00 dan 17:00. Ini adalah waktu komuter utama di kuartal terakhir tahun 2012.")

# --- Pertanyaan 3 ---
st.subheader("3. Dampak Cuaca di Akhir Pekan Musim Panas (2012)")
summer_weekend = day_2012[(day_2012["season_label"] == "Summer") & (day_2012["workingday"] == 0)]
weather_impact = summer_weekend.groupby("weather_label")["cnt"].sum().reset_index()

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(x="weather_label", y="cnt", data=weather_impact, palette="mako", ax=ax3)
ax3.set_xlabel("Kondisi Cuaca")
ax3.set_ylabel("Total Penyewaan")
st.pyplot(fig3)

with st.expander("Lihat Insight Cuaca"):
    st.write("Cuaca 'Clear' (Cerah) sangat mendominasi penyewaan akhir pekan. Penyewaan turun drastis saat cuaca buruk.")

st.caption("Copyright (c) Abel 2026")
