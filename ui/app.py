import streamlit as st
import asyncio
import threading
import time
import json
import os

from ui.api_client import APIClient
from ui.mission_builder import MissionBuilder
from ui.session_replay import SessionReplay
from agent.config import Config # Import Config for paths

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Chimera Overlord - Mission Control",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open("ui/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Initialize Session State ---
if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient()
    st.session_state.api_client.connect()

if "mission_builder" not in st.session_state:
    st.session_state.mission_builder = MissionBuilder()

if "session_replay" not in st.session_state:
    st.session_state.session_replay = SessionReplay()

if "mission_status_updates" not in st.session_state:
    st.session_state.mission_status_updates = {}

if "mission_history" not in st.session_state:
    st.session_state.mission_history = st.session_state.mission_builder.get_mission_history()

# --- RabbitMQ Status Consumer (Background Thread) ---
def start_status_consumer(api_client: APIClient):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    api_client.start_consuming_status_updates()

if "status_consumer_thread" not in st.session_state:
    st.session_state.status_consumer_thread = threading.Thread(
        target=start_status_consumer,
        args=(st.session_state.api_client,),
        daemon=True
    )
    st.session_state.status_consumer_thread.start()

# --- UI Functions ---
def display_mission_status():
    st.subheader("สถานะภารกิจปัจจุบัน")
    if not st.session_state.mission_status_updates:
        st.info("ยังไม่มีภารกิจที่กำลังดำเนินการอยู่.")
        return

    for mission_id, status_data in st.session_state.mission_status_updates.items():
        st.markdown(f"### ภารกิจ ID: `{mission_id}`")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**สถานะ:** <span class=\"status-{status_data.get("status", "unknown")}\">{status_data.get("status", "N/A").replace("_", " ").title()}</span>", unsafe_allow_html=True)
        with col2:
            st.write(f"**ผลลัพธ์:** <span class=\"status-{status_data.get("outcome", "unknown")}\">{status_data.get("outcome", "N/A").replace("_", " ").title()}</span>", unsafe_allow_html=True)
        with col3:
            st.write(f"**ข้อความ:** {status_data.get("message", "ไม่มี")}")
        
        if status_data.get("trace_file") and status_data.get("status") == "failed":
            if st.button(f"ดู Trace สำหรับ {mission_id}", key=f"trace_btn_{mission_id}"):
                st.session_state.session_replay.replay_trace(status_data["trace_file"])
                st.success(f"กำลังเปิด Playwright Trace Viewer สำหรับ {mission_id}...")
        st.markdown("--- รหัสลับ ---")

def display_mission_history():
    st.subheader("ประวัติภารกิจ")
    if not st.session_state.mission_history:
        st.info("ยังไม่มีประวัติภารกิจ.")
        return

    # Reverse history to show most recent first
    sorted_history = sorted(st.session_state.mission_history, key=lambda x: x.get("start_time", ""), reverse=True)

    for mission in sorted_history:
        with st.expander(f"ภารกิจ {mission.get("mission_id", "N/A")} - {mission.get("target_website", "N/A")} ({mission.get("status", "N/A").title()})"):
            st.json(mission)
            if mission.get("trace_file") and mission.get("status") == "failed":
                if st.button(f"ดู Trace สำหรับ {mission.get("mission_id")}", key=f"hist_trace_btn_{mission.get("mission_id")}"):
                    st.session_state.session_replay.replay_trace(mission["trace_file"])
                    st.success(f"กำลังเปิด Playwright Trace Viewer สำหรับ {mission.get("mission_id")}...")

def display_card_management():
    st.subheader("จัดการบัตรเครดิต")

    with st.form("add_card_form", clear_on_submit=True):
        st.write("เพิ่มบัตรเครดิตใหม่")
        card_number = st.text_input("หมายเลขบัตร (ตัวอย่าง: 1234-5678-9012-3456)")
        card_expiry = st.text_input("วันหมดอายุ (MM/YY)")
        card_cvv = st.text_input("CVV")
        card_type = st.selectbox("ประเภทบัตร", ["Visa", "MasterCard", "American Express", "Discover", "Other"])
        card_nickname = st.text_input("ชื่อเล่นบัตร (เช่น: บัตรหลัก, บัตรสำรอง)")

        submitted = st.form_submit_button("เพิ่มบัตร")
        if submitted:
            if card_number and card_expiry and card_cvv and card_nickname:
                card_details = {
                    "number": card_number.replace("-", "").strip(),
                    "expiry": card_expiry.strip(),
                    "cvv": card_cvv.strip(),
                    "type": card_type,
                    "nickname": card_nickname.strip()
                }
                card_id = st.session_state.mission_builder.add_new_card(card_details)
                st.success(f"เพิ่มบัตร \"{card_nickname}\" (ID: {card_id}) เรียบร้อยแล้ว!")
            else:
                st.error("กรุณากรอกข้อมูลบัตรให้ครบถ้วน.")

    st.markdown("--- รหัสลับ ---")
    st.write("บัตรเครดิตที่มีอยู่")
    available_cards = st.session_state.mission_builder.get_available_cards()
    if not available_cards:
        st.info("ยังไม่มีบัตรเครดิตที่บันทึกไว้.")
    else:
        for card_id, card_ref in available_cards.items():
            st.write(f"- **{card_ref.get("nickname", "N/A")}** (ID: `{card_id}`) - {card_ref.get("card_type", "N/A")}, ลงท้ายด้วย {card_ref.get("last4", "N/A")}")

def display_profile_management():
    st.subheader("จัดการโปรไฟล์")
    st.write("โปรไฟล์ปัจจุบัน: `default_profile`")
    profile_info = st.session_state.mission_builder.get_profile_info("default_profile")
    st.write(f"**Trust Score:** {profile_info.get("trust_score", "N/A")}")
    st.info("ฟังก์ชันการจัดการโปรไฟล์ขั้นสูงจะถูกเพิ่มเข้ามาในอนาคต.")

# --- Main App Layout ---
st.title("🚀 Chimera Overlord - Mission Control")

# Sidebar for navigation
st.sidebar.title("เมนู")
page_selection = st.sidebar.radio(
    "",
    ["เริ่มภารกิจใหม่", "สถานะภารกิจ", "ประวัติภารกิจ", "จัดการบัตรเครดิต", "จัดการโปรไฟล์"]
)

# Main content area based on selection
if page_selection == "เริ่มภารกิจใหม่":
    st.header("เริ่มภารกิจใหม่")
    with st.form("new_mission_form"):
        st.write("รายละเอียดภารกิจ")
        target_website = st.text_input("เว็บไซต์เป้าหมาย (เช่น: https://www.apple.com/th/)",
                                        value="https://www.apple.com/th/")
        product_identifier = st.text_input("สินค้าที่ต้องการ (เช่น: iPhone 15 Pro Max 256GB)",
                                            value="iPhone 15 Pro Max 256GB")
        
        available_cards = st.session_state.mission_builder.get_available_cards()
        card_options = {f"{v.get("nickname", k)} (***{v.get("last4", "N/A")})": k for k, v in available_cards.items()}
        
        primary_card_display = st.selectbox("บัตรเครดิตหลัก", list(card_options.keys()))
        primary_card_id = card_options.get(primary_card_display)

        secondary_card_display = st.selectbox("บัตรเครดิตรอง (ไม่บังคับ)", ["ไม่มี"] + list(card_options.keys()))
        secondary_card_id = card_options.get(secondary_card_display) if secondary_card_display != "ไม่มี" else None

        force_warmup = st.checkbox("บังคับ Warmup Turbo ก่อนเริ่มภารกิจ (แนะนำหาก Trust Score ต่ำ)", value=False)

        submitted = st.form_submit_button("เริ่มภารกิจ")
        if submitted:
            if not primary_card_id:
                st.error("กรุณาเพิ่มบัตรเครดิตหลักก่อนเริ่มภารกิจ.")
            elif not target_website or not product_identifier:
                st.error("กรุณากรอกเว็บไซต์เป้าหมายและสินค้าที่ต้องการ.")
            else:
                mission_request = st.session_state.mission_builder.build_mission_request(
                    target_website=target_website,
                    product_identifier=product_identifier,
                    primary_card_id=primary_card_id,
                    secondary_card_id=secondary_card_id,
                    force_warmup=force_warmup
                )
                
                def mission_status_callback(status_data):
                    st.session_state.mission_status_updates[status_data["mission_id"]] = status_data
                    st.experimental_rerun() # Rerun to update UI with new status

                try:
                    mission_id = st.session_state.api_client.send_mission_request(mission_request, mission_status_callback)
                    st.success(f"ภารกิจ \"{mission_id}\" เริ่มต้นแล้ว! ตรวจสอบสถานะได้ที่แท็บ \"สถานะภารกิจ\".")
                    st.session_state.mission_status_updates[mission_id] = {"mission_id": mission_id, "status": "queued", "outcome": "pending", "message": "กำลังรอการประมวลผล..."}
                    st.experimental_rerun()
                except ConnectionError as e:
                    st.error(f"ไม่สามารถเชื่อมต่อกับ Agent ได้: {e}. โปรดตรวจสอบว่า Docker Compose ทำงานอยู่.")

elif page_selection == "สถานะภารกิจ":
    display_mission_status()
    # Auto-refresh mechanism (optional, can be heavy)
    # time.sleep(5)
    # st.experimental_rerun()

elif page_selection == "ประวัติภารกิจ":
    display_mission_history()

elif page_selection == "จัดการบัตรเครดิต":
    display_card_management()

elif page_selection == "จัดการโปรไฟล์":
    display_profile_management()


# --- Footer ---
st.markdown("""
<br><br><br>
<hr>
<p style="text-align: center; color: gray;">Chimera Overlord - สร้างสรรค์โดย Manus AI</p>
""", unsafe_allow_html=True)

# Refresh mission history on page load/rerun to ensure it's up-to-date
st.session_state.mission_history = st.session_state.mission_builder.get_mission_history()




