"""
edge_ai_logic.py
================
Edge AI Rules Engine powered by DAFT (Dyadic Attention Field Theory).
ทำหน้าที่ประเมินค่าเซนเซอร์หน้างานและตัดสินใจสั่งการฮาร์ดแวร์ (เช่น พัดลม)
โดยอิงจากการจัดกลุ่มสถานะของ DAFT Classifier 
"""

from .daft_core import DAFTField

# 1. สร้าง Instance ของโมเดล DAFT (ใช้ค่าเริ่มต้น alpha=1.0, lambda=3)
daft = DAFTField(alpha=1.0, lambda_res=3)

def process_sensor_daft(current_temp: float) -> dict:
    """
    รับค่าอุณหภูมิปัจจุบันและประเมินแอคชันที่ต้องทำด้วย DAFT
    """
    optimal_temp = 25.0  # อุณหภูมิเป้าหมายที่โกดังควรจะรักษาไว้ (สมดุล)
    
    # 2. Domain Mapping: แปลงข้อมูลโลกจริงให้เข้ากับสมการ DAFT
    # xi (ค่าติดลบ): ตัวแทนของค่าที่เกิดขึ้นจริงหน้างาน
    # xj (ค่าบวก): ตัวแทนของเป้าหมาย หรือเกณฑ์มาตรฐาน
    xi = -(current_temp / optimal_temp) 
    xj = 1.0                             
    
    # 3. ให้ DAFT คำนวณความไม่สมดุล (O4) และจัดกลุ่มสถานะ (State)
    state = daft.classify(xi, xj)
    O4_asymmetry = daft.O4(xi, xj)
    O6_separation = daft.O6(xi, xj)
    
    # 4. Rules Engine: กำหนดการทำงานของฮาร์ดแวร์ตาม DAFT State
    action = "none"
    
    if state == "PURE":
        # สมดุลสมบูรณ์แบบ (|xi| == |xj|) -> อุณหภูมิ 25 องศาพอดี
        action = "maintain"
        icon = "✅"
        msg = "อุณหภูมิสมดุล (PURE) รักษาสถานะฮาร์ดแวร์"
        
    elif state == "DESTRUCTIVE":
        # พลังงานหน้างานสูงกว่าเป้าหมาย (|xi| > |xj| -> O4 > 0) -> ร้อนเกินไป
        action = "fan_on"
        icon = "🚨"
        msg = "ความร้อนเกินพิกัด! (DESTRUCTIVE) -> สั่งเปิดพัดลมระบายอากาศ"
        
    elif state == "CONSTRUCTIVE":
        # พลังงานหน้างานต่ำกว่าเป้าหมาย (|xi| < |xj| -> O4 < 0) -> เย็นเกินไป/ปกติ
        action = "fan_off"
        icon = "❄️"
        msg = "อุณหภูมิต่ำกว่าเกณฑ์ (CONSTRUCTIVE) -> สั่งปิดพัดลม"
        
    else:
        # BOUNDARY (มีค่าใดค่าหนึ่งเป็น 0 หรือใกล้เคียง 0 มากๆ) เซนเซอร์อาจพัง
        action = "alert_maintenance"
        icon = "⚠️"
        msg = "เซนเซอร์อาจมีปัญหา (BOUNDARY) -> แจ้งเตือนซ่อมบำรุง"

    # พิมพ์ Log เพื่อให้เห็นการตัดสินใจที่หน้าจอ Edge Node
    print(f"[L7 - App (DAFT)] {icon} อุณหภูมิ: {current_temp:.1f}°C | State: {state:<12} | O4: {O4_asymmetry:+.2f} | {msg}")
    
    # ส่งคืนข้อมูล (Payload) เพื่อส่งต่อไปยัง Layer 6 (Presentation)
    return {
        "timestamp": "2026-03-17T10:44:00Z", # สมมติเวลาที่บันทึก
        "sensor": "temp_zone_A",
        "temp": round(current_temp, 1),
        "daft_state": state,
        "O4_asymmetry": round(O4_asymmetry, 4),
        "O6_separation": round(O6_separation, 4),
        "action": action
    }