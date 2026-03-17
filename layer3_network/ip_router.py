"""
ip_router.py
============
Layer 3: Network Layer
ทำหน้าที่จัดการที่อยู่หมายเลขไอพี (IP Address), การหาเส้นทาง (Routing) 
และทำการส่งแพ็กเก็ตข้อมูลข้ามเครือข่ายผ่าน UDP Socket ของจริง
"""

import socket
import json

class IPRouter:
    def __init__(self, cloud_ip="127.0.0.1", cloud_port=9999, edge_ip="192.168.1.50"):
        """
        กำหนดค่า IP Address ปลายทาง (Cloud) และต้นทาง (Edge)
        (ในกรณีรันทดสอบในเครื่องตัวเอง จะใช้ 127.0.0.1 (Localhost))
        """
        self.cloud_ip = cloud_ip
        self.cloud_port = cloud_port
        self.edge_ip = edge_ip
        
        # สร้าง UDP Socket สำหรับใช้ส่งข้อมูลข้ามเครือข่าย
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def attach_header_and_send(self, encoded_payload: str, session_id: str) -> bool:
        """
        ห่อหุ้มข้อมูล (Encapsulation) ด้วย IP Header (src_ip, dst_ip)
        พร้อมแนบ Session ID และทำการส่งออกไปยังปลายทาง
        """
        # 1. จัดทำซองจดหมาย (IP Packet)
        packet = {
            "src_ip": self.edge_ip,
            "dst_ip": self.cloud_ip,
            "session_id": session_id,
            "data": encoded_payload  # ข้อมูลที่ถูกเข้ารหัส Base64 แล้วจาก Layer 6
        }
        
        print(f"[L3 - Network] 🌐 แนบ IP Header | ขากลับ: {self.edge_ip} -> ปลายทาง: {self.cloud_ip}:{self.cloud_port}")
        
        # 2. ทำการส่งข้อมูล (Transmission)
        try:
            # แปลง Packet (Dict) ให้เป็น Bytes เพื่อให้ส่งผ่าน Socket ได้
            packet_bytes = json.dumps(packet).encode('utf-8')
            
            # ยิงข้อมูลผ่าน UDP Socket ไปยัง Cloud
            self.sock.sendto(packet_bytes, (self.cloud_ip, self.cloud_port))
            print(f"[L3 - Network] 🚀 ส่งแพ็กเก็ตขึ้นสู่ระบบ Cloud เรียบร้อยแล้ว!")
            return True
            
        except Exception as e:
            print(f"[L3 - Network] ❌ เกิดข้อผิดพลาดในการส่งข้อมูล: {e}")
            return False

    def close_connection(self):
        """
        ปิดพอร์ต Socket เมื่อเลิกใช้งาน
        """
        self.sock.close()