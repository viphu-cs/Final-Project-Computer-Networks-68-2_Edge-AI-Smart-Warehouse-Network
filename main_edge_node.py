"""
main_edge_node.py
=================
ไฟล์หลักสำหรับรันระบบ Smart Warehouse Edge AI (จำลอง OSI 7 Layers + DAFT)
ทำหน้าที่เป็นศูนย์กลางเชื่อมต่อทุก Layer ฝั่งอุปกรณ์ที่หน้างาน (Edge Node)
"""

import time
import random

# Import เลเยอร์ทั้งหมดที่เราสร้างไว้
from layer7_application.edge_ai_logic import process_sensor_daft
from layer6_presentation.data_formatter import PresentationLayer
from layer5_session.session_manager import SessionLayer
from layer4_transport.dtn_buffer import DTNBuffer
from layer3_network.ip_router import IPRouter
from layer1_2_physical_link.link_simulator import LinkSimulator

def run_edge_node():
    # 1. สร้าง Instance ของแต่ละเลเยอร์เตรียมไว้
    presentation = PresentationLayer()
    session = SessionLayer()
    dtn_buffer = DTNBuffer()
    router = IPRouter()
    
    # ตั้งค่าให้โอกาสเน็ตหลุดอยู่ที่ 30% เพื่อโชว์ความทนทานของระบบ
    link = LinkSimulator(failure_rate=0.30)

    print("=========================================================")
    print("🚀 เริ่มการจำลอง: Smart Warehouse Edge AI (OSI 7 Layers + DAFT)")
    print("=========================================================\n")

    try:
        while True:
            print("=" * 60)
            
            # จำลองอุณหภูมิหน้างาน (องศาเซลเซียส) ให้แกว่งอยู่ในช่วง 20 ถึง 38 องศา
            current_temp = round(random.uniform(20.0, 38.0), 1)
            
            # --- Layer 7: Application (ประมวลผลเซนเซอร์ และตัดสินใจด้วย DAFT) ---
            raw_payload = process_sensor_daft(current_temp)
            
            # --- Layer 6: Presentation (แปลงเป็น JSON และเข้ารหัส Base64) ---
            encoded_payload = presentation.encode_payload(raw_payload)
            
            # --- Layer 1/2: Physical & Data Link (เช็คสถานะสายแลน/Wi-Fi ก่อนส่ง) ---
            if link.check_connection():
                
                # --- Layer 5: Session (เปิดการเชื่อมต่อ) ---
                session_id = session.establish_session()
                
                # --- Layer 4: Transport (กวาดข้อมูลที่ค้างอยู่ใน Database ขึ้นมาส่งก่อน) ---
                buffered_data_list = dtn_buffer.forward_data()
                if buffered_data_list:
                    for idx, b_data in enumerate(buffered_data_list):
                        print(f"[Orchestrator] 🔄 กำลังส่งข้อมูลค้างส่ง (DTN Recovery) {idx+1}/{len(buffered_data_list)}...")
                        router.attach_header_and_send(b_data, session_id)
                
                # --- Layer 3: Network (แนบ IP และส่งข้อมูลปัจจุบันขึ้น Cloud) ---
                router.attach_header_and_send(encoded_payload, session_id)
                
            else:
                # กรณีเน็ตหลุด!
                
                # --- Layer 5: Session (ทำลายการเชื่อมต่อทิ้ง) ---
                session.terminate_session()
                
                # --- Layer 4: Transport (Offline Resilience - ฝากข้อมูลลง Local Database) ---
                dtn_buffer.store_data(encoded_payload)
                print("[Orchestrator] ⚠️ ระบบออฟไลน์: เครือข่ายล่ม แต่ระบบหน้างาน (Edge AI) ยังคุมพัดลมได้ และบันทึกข้อมูลเรียบร้อย")

            # หน่วงเวลา 5 วินาทีก่อนเริ่มรอบใหม่ (ให้ดูง่ายตอนพรีเซนต์)
            time.sleep(5) 
            
    except KeyboardInterrupt:
        print("\n[System] 🛑 กำลังปิดระบบ Edge Node...")
        router.close_connection()
        dtn_buffer.close()
        print("[System] ปิดระบบอย่างปลอดภัย")

if __name__ == "__main__":
    run_edge_node()