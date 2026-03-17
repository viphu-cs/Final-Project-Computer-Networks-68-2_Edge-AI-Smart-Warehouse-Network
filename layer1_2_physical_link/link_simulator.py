"""
link_simulator.py
=================
Layer 1 & 2: Physical and Data Link Layer
จำลองสถานะทางกายภาพของเครือข่าย (เช่น สาย LAN หลวม, Wi-Fi สัญญาณขาดหาย)
ทำหน้าที่สุ่มตัดการเชื่อมต่อเพื่อทดสอบระบบ Offline Resilience ของคลังสินค้า
"""

import random
import time

class LinkSimulator:
    def __init__(self, failure_rate: float = 0.25):
        """
        กำหนดโอกาสที่เน็ตจะหลุด (failure_rate)
        ค่าเริ่มต้นคือ 0.25 (มีโอกาส 25% ที่สายสัญญาณจะขาดในแต่ละรอบ)
        """
        self.failure_rate = failure_rate
        self.is_connected = True

    def check_connection(self) -> bool:
        """
        ตรวจสอบสถานะการเชื่อมต่อ (Link Status)
        จำลองการทำงานของ Data Link Layer ในการเช็ค Heartbeat ของสายสัญญาณ
        """
        # สุ่มตัวเลข 0.0 ถึง 1.0 ถ้าได้น้อยกว่า failure_rate ถือว่าเน็ตหลุด
        if random.random() < self.failure_rate:
            self.is_connected = False
            print("-" * 60)
            print("[L1/L2 - Physical/Link] ❌ สายสัญญาณขาด! (Link Failure Detected)")
            print("[L1/L2 - Physical/Link] ⚠️ ไม่สามารถส่ง Frame ข้อมูลไปยัง Router ได้")
        else:
            self.is_connected = True
            print("-" * 60)
            print("[L1/L2 - Physical/Link] ✅ สัญญาณเครือข่าย (Physical Link) ทำงานปกติ")
            
        return self.is_connected

    def set_failure_rate(self, new_rate: float):
        """
        ปรับเปลี่ยนโอกาสเน็ตหลุดได้ระหว่างรันโปรแกรม (ถ้าต้องการทดสอบแบบ Custom)
        """
        self.failure_rate = max(0.0, min(1.0, new_rate))