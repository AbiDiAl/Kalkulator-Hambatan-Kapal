import streamlit as st
import math
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Marine Analytics Pro", page_icon="⚓", layout="wide")

st.title("⚓ Naval Arch: Advanced Resistance & Propulsion Calculator")
st.markdown("---")

# --- SIDEBAR INPUT ---
st.sidebar.header("Dimensi Utama Kapal")
L = st.sidebar.number_input("Panjang (Lwl) [m]", value=20.0)
B = st.sidebar.number_input("Lebar (B) [m]", value=8.0)
T = st.sidebar.number_input("Sarat (T) [m]", value=3.5)
Cb = st.sidebar.slider("Block Coefficient (Cb)", 0.4, 0.9, 0.7)

st.sidebar.header("Operasional")
v_knot = st.sidebar.slider("Kecepatan Target (Knots)", 5, 25, 11)

# --- LOGIKA PERHITUNGAN TEKNIK ---
def kalkulasi_marine(L, B, T, Cb, v_knot):
    # Konstanta
    rho = 1025  # Massa jenis air laut (kg/m3)
    nu = 1.188e-6 # Viskositas
    v = v_knot * 0.5144 # konversi ke m/s
    
    # 1. Wetted Surface Area (S)
    S = L * (2 * T + B) * math.sqrt(Cb)
    
    # 2. Koefisien Gesek (Cf) - ITTC 1957
    if v > 0:
        Re = (v * L) / nu
        Cf = 0.075 / (math.log10(Re) - 2)**2
    else:
        Cf = 0
        
    # 3. Hambatan Gesek (Rf)
    Rf = 0.5 * rho * S * (v**2) * Cf
    
    # 4. Faktor Bentuk & Hambatan Total (Rt)
    k_factor = 0.12 + (0.11 * (B/L)) 
    Rt = Rf * (1 + k_factor) * 1.25 # Estimasi hambatan gelombang
    
    return Rf/1000, Rt/1000 # Return dalam kN

# --- EKSEKUSI PERHITUNGAN ---
rf_kn, rt_kn = kalkulasi_marine(L, B, T, Cb, v_knot)
ehp_kw = rt_kn * (v_knot * 0.5144)

# --- ANALISA PROPULSI (BHP) ---
eta_transmission = 0.97 # Gearbox/Shaft
eta_propeller = 0.55    # Baling-baling
eta_hull = 1.05         # Interaksi lambung
total_efficiency = eta_transmission * eta_propeller * eta_hull

sea_margin = 1.15 # Cadangan cuaca 15%
bhp_kw = (ehp_kw / total_efficiency) * sea_margin
bhp_hp = bhp_kw / 0.7457 # Konversi ke Horsepower

# --- TAMPILAN DASHBOARD UTAMA ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Frictional Resistance (Rf)", f"{round(rf_kn, 2)} kN")
with col2:
    st.metric("Total Resistance (Rt)", f"{round(rt_kn, 2)} kN")
with col3:
    st.metric("Effective Power (EHP)", f"{round(ehp_kw, 2)} kW")

st.markdown("---")

# --- REKOMENDASI MESIN ---
st.subheader("⚙️ Rekomendasi Spesifikasi Mesin (Brake Horse Power)")
c1, c2 = st.columns(2)
with c1:
    st.success(f"### Kapasitas Mesin: {round(bhp_hp, 1)} HP")
    st.caption(f"Atau setara dengan {round(bhp_kw, 2)} kW")
with c2:
    with st.expander("Lihat Rincian Kehilangan Daya (Losses)"):
        st.write(f"- **Efisiensi Baling-baling:** {eta_propeller*100}%")
        st.write(f"- **Efisiensi Transmisi:** {eta_transmission*100}%")
        st.write(f"- **Sea Margin:** 15% (Cadangan cuaca)")
        st.write(f"**Total Efisiensi Sistem:** {round(total_efficiency*100, 2)}%")

st.info(f"💡 Untuk mencapai {v_knot} Knots, belilah mesin dengan rating kontinu (MCR) minimal **{round(bhp_hp, 1)} HP**.")

# --- GRAFIK ANALISA KECEPATAN ---
st.subheader("📈 Kurva Hambatan Kapal (Resistance Curve)")

data_grafik = []
for speed in range(5, 26):
    res_frictional, res_total = kalkulasi_marine(L, B, T, Cb, speed)
    data_grafik.append({
        "Kecepatan (Knots)": speed, 
        "Hambatan Total (kN)": round(res_total, 2),
        "Hambatan Gesek (Rf)": round(res_frictional, 2)
    })

# Membuat DataFrame
df_grafik = pd.DataFrame(data_grafik).set_index("Kecepatan (Knots)")

# Menampilkan Line Chart hanya untuk Hambatan
st.line_chart(df_grafik)

st.caption("Sumbu X: Kecepatan (Knots) | Sumbu Y: Gaya Hambatan (kN)")

# --- FOOTER ---
st.write("---")
st.caption("Developed by Abi Dimas Alfian & AI | Naval Arch UNDIP 2012")
