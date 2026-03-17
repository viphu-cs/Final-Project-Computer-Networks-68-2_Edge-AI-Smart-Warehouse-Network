"""
session_manager.py
==================
Layer 5: Session Layer
ทำหน้าที่ควบคุม ดูแล และจัดการการเชื่อมต่อ (Session) ระหว่าง Edge Node และ Cloud
รวมถึงการสร้าง Session ID เพื่อยืนยันช่องทางการสื่อสาร
"""

import uuid
from datetime import datetime

class SessionLayer:
    def __init__(self):
        # เก็บสถานะว่าตอนนี้มี Session ที่ใช้งานอยู่หรือไม่
        self.current_session_id = None
        self.session_start_time = None

    def establish_session(self) -> str:
        """
        สร้าง Session ใหม่เมื่อมีการเชื่อมต่อเครือข่ายสำเร็จ
        ถ้ามี Session อยู่แล้ว จะใช้ตัวเดิมเพื่อรักษาความต่อเนื่อง
        """
        if self.current_session_id is None:
            # สุ่มสร้าง ID ความยาว 8 ตัวอักษร
            self.current_session_id = str(uuid.uuid4())[:8]
            self.session_start_time = datetime.now()
            
            print(f"[L5 - Session] 🤝 เริ่มการเชื่อมต่อใหม่ | Session ID: [{self.current_session_id}]")
        else:
            # พิมพ์บอกแค่ว่ายังใช้ Session เดิมอยู่ (ลดความรกของหน้าจอ)
            print(f"[L5 - Session] 🔄 ใช้งาน Session เดิม: [{self.current_session_id}]")
            
        return self.current_session_id

    def terminate_session(self):
        """
        ทำลาย Session ทิ้งเมื่อตรวจพบว่าสายสัญญาณขาด หรือเครือข่ายมีปัญหา
        เพื่อให้ระบบรู้ว่าต้องสร้าง Session ใหม่เมื่อเน็ตกลับมา
        """
        if self.current_session_id is not None:
            duration = datetime.now() - self.session_start_time
            print(f"[L5 - Session] 🚫 เน็ตหลุด! ทำลาย Session: [{self.current_session_id}] (อายุการใช้งาน: {duration.seconds} วินาที)")
            
            # เคลียร์ค่าทิ้ง
            self.current_session_id = None
            self.session_start_time = None

    def get_current_session(self):
        """
        ดึงค่า Session ปัจจุบัน (ใช้สำหรับแนบไปกับ Header ใน Layer 3)
        """
        return self.current_session_id