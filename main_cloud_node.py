"""
main_cloud_node.py
==================
ไฟล์หลักสำหรับรันระบบ Cloud Server (ส่วนกลาง)
ทำหน้าที่เปิดช่องทางการสื่อสาร (UDP Socket) รอรับแพ็กเก็ตข้อมูลจาก Edge Node
พร้อมทำการถอดรหัสและแสดงผลขึ้น Cloud Dashboard
"""

import socket
import json
import base64
from datetime import datetime

def run_cloud_node():
    # 1. ตั้งค่า IP และ Port สำหรับรับข้อมูล (ต้องตรงกับปลายทางใน ip_router.py)
    UDP_IP = "127.0.0.1"  # รันในเครื่องตัวเอง (Localhost)
    UDP_PORT = 9999       # พอร์ต 9999
    
    # 2. สร้าง Socket เพื่อเปิดช่องทางการสื่อสาร (Network Layer ฝั่งรับ)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    
    print("================================================================")
    print(f"☁️ Cloud Server Node พร้อมทำงาน! (Listening on {UDP_IP}:{UDP_PORT})")
    print("================================================================\n")
    print("รอรับข้อมูลจาก Smart Warehouse Edge Node...")

    try:
        while True:
            # 3. รอรับแพ็กเก็ตข้อมูลจากเครือข่าย (รับได้สูงสุด 4096 bytes ต่อรอบ)
            data, addr = sock.recvfrom(4096)
            receive_time = datetime.now().strftime("%H:%M:%S")
            
            # 4. แปลงข้อมูลที่รับมา (Bytes) กลับเป็น String
            packet_str = data.decode('utf-8')
            
            try:
                # 5. แกะซองจดหมาย IP Packet (Network Layer)
                packet = json.loads(packet_str)
                src_ip = packet.get("src_ip", "Unknown")
                session_id = packet.get("session_id", "No-Session")
                encoded_payload = packet.get("data", "")
                
                # 6. ถอดรหัสข้อมูล Base64 (Presentation Layer ฝั่งรับ)
                decoded_bytes = base64.b64decode(encoded_payload.encode('utf-8'))
                payload = json.loads(decoded_bytes.decode('utf-8'))
                
                # 7. แสดงผลข้อมูลลงบน Dashboard
                print("-" * 65)
                print(f"📥 [Cloud Dashboard] ได้รับข้อมูลเวลา: {receive_time}")
                print(f"   🌐 ต้นทาง: {src_ip} | 🔑 Session: {session_id}")
                
                # ดึงค่ามาแสดงผล (เปลี่ยนสี/ไอคอนตามสถานะ)
                temp = payload.get("temp")
                state = payload.get("daft_state")
                action = payload.get("action")
                o4 = payload.get("O4_asymmetry")
                
                status_icon = "✅" if state == "PURE" else ("🚨" if state == "DESTRUCTIVE" else ("❄️" if state == "CONSTRUCTIVE" else "⚠️"))
                
                print(f"   📊 สถานะโกดัง: {status_icon} {temp}°C | DAFT State: {state:<12} | O4: {o4}")
                print(f"   ⚙️ การสั่งการหน้างาน: {action}")
                print("-" * 65)
                
            except Exception as e:
                print(f"❌ [Error] ไม่สามารถประมวลผลแพ็กเก็ตจาก {addr} ได้: {e}")

    except KeyboardInterrupt:
        print("\n[System] 🛑 กำลังปิดระบบ Cloud Server...")
        sock.close()
        print("[System] ปิดระบบอย่างปลอดภัย")

if __name__ == "__main__":
    run_cloud_node()