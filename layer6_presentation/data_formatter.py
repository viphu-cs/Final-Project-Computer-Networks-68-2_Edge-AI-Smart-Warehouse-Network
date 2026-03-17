"""
data_formatter.py
=================
Layer 6: Presentation Layer
รับหน้าที่แปลงรูปแบบข้อมูล (Data Formatting) และเข้ารหัส (Encryption) 
ก่อนส่งข้ามเครือข่าย เพื่อความปลอดภัยของข้อมูลคลังสินค้า
"""

import json
import base64

class PresentationLayer:
    @staticmethod
    def encode_payload(data_dict: dict) -> str:
        """
        แปลง Dictionary จาก Layer 7 เป็น JSON และเข้ารหัสด้วย Base64
        (จำลองการทำ Data Encryption)
        """
        # 1. แปลงโครงสร้างข้อมูล (Formatting: Dict -> JSON String)
        json_str = json.dumps(data_dict)
        
        # 2. เข้ารหัสข้อมูลเพื่อความปลอดภัย (Encryption: String -> Base64)
        encoded_bytes = base64.b64encode(json_str.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        
        # แสดงตัวอย่างข้อมูลที่ถูกเข้ารหัสแล้ว (โชว์แค่ 30 ตัวอักษรแรกเพื่อความสวยงาม)
        print(f"[L6 - Presentation] 🔐 เข้ารหัสข้อมูล (Base64): {encoded_str[:30]}...")
        
        return encoded_str

    @staticmethod
    def decode_payload(encoded_str: str) -> dict:
        """
        ถอดรหัส Base64 และแปลง JSON กลับเป็น Dictionary 
        (ฟังก์ชันนี้จะถูกเรียกใช้ที่ฝั่งเซิร์ฟเวอร์ Cloud เพื่ออ่านข้อมูล)
        """
        try:
            # 1. ถอดรหัสข้อมูล (Decryption: Base64 -> String)
            decoded_bytes = base64.b64decode(encoded_str.encode('utf-8'))
            
            # 2. แปลงกลับเป็นโครงสร้างเดิม (Parsing: JSON String -> Dict)
            data_dict = json.loads(decoded_bytes.decode('utf-8'))
            
            return data_dict
            
        except Exception as e:
            print(f"[L6 - Presentation] ❌ ถอดรหัสล้มเหลว: {e}")
            return {}