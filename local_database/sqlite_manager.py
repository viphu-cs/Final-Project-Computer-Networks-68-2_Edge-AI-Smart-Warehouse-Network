"""
sqlite_manager.py
=================
Local Database Manager
จัดการฐานข้อมูล SQLite ภายในตัว Edge Node (โกดัง) 
ทำหน้าที่เป็นพื้นที่เก็บข้อมูลถาวร (Persistent Storage) เมื่อเครือข่ายล่ม
ป้องกันข้อมูลสูญหายกรณีที่อุปกรณ์ Edge เกิดไฟดับหรือรีสตาร์ท
"""

import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="warehouse_offline_logs.db"):
        self.db_name = db_name
        # เชื่อมต่อกับไฟล์ฐานข้อมูล (ถ้าไม่มีไฟล์นี้ ระบบจะสร้างขึ้นมาให้ใหม่ทันที)
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # สร้างตารางสำหรับเก็บ Log ถ้ายังไม่มีตารางนี้อยู่
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daft_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                payload TEXT,
                status TEXT
            )
        ''')
        self.conn.commit()

    def save_offline_log(self, payload_dict: dict):
        """
        บันทึกข้อมูล (Payload) ลงฐานข้อมูล พร้อมประทับเวลาและสถานะ 'pending' (รอส่ง)
        """
        # แปลง Dictionary เป็น JSON String ก่อนเซฟลงฐานข้อมูล
        payload_str = json.dumps(payload_dict)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute(
            "INSERT INTO daft_logs (timestamp, payload, status) VALUES (?, ?, 'pending')", 
            (current_time, payload_str)
        )
        self.conn.commit()
        
        print(f"[Database] 💾 เขียนข้อมูลลง Disk สำเร็จ (SQLite) | ป้องกันข้อมูลสูญหายเมื่อไฟดับ")

    def get_and_clear_pending_logs(self) -> list:
        """
        ดึงข้อมูลที่ค้างอยู่ (pending) ทั้งหมดออกมาส่งเมื่อเน็ตกลับมา 
        และทำการลบข้อมูลนั้นทิ้งเพื่อไม่ให้ส่งซ้ำ
        """
        # 1. ดึงข้อมูลที่รอส่ง
        self.cursor.execute("SELECT id, payload FROM daft_logs WHERE status='pending'")
        rows = self.cursor.fetchall()
        
        if not rows:
            return [] # ไม่มีข้อมูลค้างส่ง
            
        # 2. แปลงข้อมูลกลับเป็น Dictionary
        pending_logs = []
        ids_to_delete = []
        
        for row in rows:
            row_id = row[0]
            payload_str = row[1]
            try:
                pending_logs.append(json.loads(payload_str))
                ids_to_delete.append(row_id)
            except json.JSONDecodeError:
                continue
                
        # 3. ล้างข้อมูลเก่าที่กำลังจะถูกนำไปส่ง เพื่อคืนพื้นที่
        if ids_to_delete:
            # สร้างเงื่อนไขลบตาม ID เช่น (1, 2, 3)
            placeholders = ', '.join(['?'] * len(ids_to_delete))
            self.cursor.execute(f"DELETE FROM daft_logs WHERE id IN ({placeholders})", ids_to_delete)
            self.conn.commit()
            
            print(f"[Database] 🧹 ดึงข้อมูลค้างส่ง {len(pending_logs)} รายการ และล้างคิวใน Database แล้ว")
            
        return pending_logs

    def close_connection(self):
        """
        ปิดการเชื่อมต่อฐานข้อมูลเมื่อเลิกใช้งาน
        """
        self.conn.close()