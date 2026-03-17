"""
dtn_buffer.py
=============
Layer 4: Transport Layer (DTN - Delay-Tolerant Networking)
ทำหน้าที่รับประกันการส่งข้อมูล (Reliability) โดยใช้หลักการ Store-and-Forward
เมื่อเครือข่ายล่ม จะนำข้อมูลไปฝากไว้ที่ Local Database 
และเมื่อเครือข่ายกลับมาใช้งานได้ จะทำการดึงข้อมูลที่ค้างอยู่ทั้งหมดไปส่งต่อ
"""

# Import ระบบฐานข้อมูลที่เราสร้างไว้
from local_database.sqlite_manager import DatabaseManager

class DTNBuffer:
    def __init__(self):
        # เรียกใช้งาน Database Manager
        self.db = DatabaseManager()
        
    def store_data(self, payload: dict):
        """
        เมื่อส่งข้อมูลไม่สำเร็จ (เน็ตหลุด) Layer 4 จะนำข้อมูลมาพักไว้ที่นี่
        และสั่งให้ Database เขียนลง Disk ทันที
        """
        print(f"[L4 - Transport] 📦 เครือข่ายขัดข้อง! กำลังนำข้อมูลเข้าสู่ระบบ DTN Buffer (Store-and-Forward)")
        
        # ส่งต่อให้ Database จัดการเซฟลงไฟล์
        self.db.save_offline_log(payload)

    def forward_data(self):
        """
        เมื่อเครือข่ายกลับมาปกติ (เน็ตมา) Layer 4 จะไปกวาดข้อมูลที่ค้างอยู่ใน Database 
        ออกมาเพื่อเตรียมส่งขึ้น Cloud ในรวดเดียว
        """
        # ดึงข้อมูลที่ค้างส่งและล้างคิวใน Database
        pending_logs = self.db.get_and_clear_pending_logs()
        
        if len(pending_logs) > 0:
            print(f"[L4 - Transport] 🔄 กู้คืนการเชื่อมต่อสำเร็จ! ดึงข้อมูลออฟไลน์ {len(pending_logs)} รายการเตรียม Sync ขึ้น Cloud")
            return pending_logs
        else:
            # ถ้าไม่มีข้อมูลค้างเลย ก็ไม่ต้องทำอะไร
            return None

    def close(self):
        """
        ปิดการเชื่อมต่อฐานข้อมูล
        """
        self.db.close_connection()