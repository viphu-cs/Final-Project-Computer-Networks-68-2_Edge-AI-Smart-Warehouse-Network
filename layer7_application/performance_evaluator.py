"""
performance_evaluator.py
========================
ระบบประเมินผลประสิทธิภาพ (System Evaluation & Metrics)
ทำหน้าที่เก็บสถิติการทำงานของทุก Layer เพื่อสรุปผลความทนทานและการทำงานของ AI
"""

class PerformanceEvaluator:
    def __init__(self):
        # สถิติเครือข่าย
        self.total_attempts = 0
        self.successful_sends = 0
        self.buffered_packets = 0
        self.recovered_packets = 0
        
        # สถิติ AI (DAFT)
        self.state_counts = {
            "PURE": 0,
            "CONSTRUCTIVE": 0,
            "DESTRUCTIVE": 0,
            "BOUNDARY": 0
        }
        
        # สถานะปัจจุบัน
        self.start_time = None

    def log_attempt(self, is_online: bool):
        """บันทึกความพยายามในการส่งข้อมูล"""
        self.total_attempts += 1
        if is_online:
            self.successful_sends += 1
        else:
            self.buffered_packets += 1

    def log_recovery(self, count: int):
        """บันทึกจำนวนข้อมูลที่กู้คืนมาได้"""
        self.recovered_packets += count

    def log_daft_state(self, state: str):
        """บันทึกสถานะที่ AI ตัดสินใจ"""
        if state in self.state_counts:
            self.state_counts[state] += 1

    def print_summary_report(self):
        """แสดงรายงานการประเมินผล (Final Evaluation Report)"""
        print("\n" + "="*30)
        print("📊 รายงานการประเมินผลระบบ (Evaluation Report)")
        print("="*30)
        
        # 1. ประเมินความทนทานเครือข่าย (Network Resilience Evaluation)
        reliability = (self.successful_sends / self.total_attempts * 100) if self.total_attempts > 0 else 0
        recovery_rate = (self.recovered_packets / self.buffered_packets * 100) if self.buffered_packets > 0 else 100
        
        print(f"[Network Efficiency]")
        print(f" - ความพยายามส่งทั้งหมด: {self.total_attempts} ครั้ง")
        print(f" - ส่งสำเร็จทันที: {self.successful_sends} ครั้ง ({reliability:.1f}%)")
        print(f" - ข้อมูลที่ต้องเก็บสำรอง: {self.buffered_packets} ครั้ง")
        print(f" - อัตราการกู้คืนข้อมูล (Recovery Rate): {recovery_rate:.1f}%")
        
        # 2. ประเมินการทำงานของ AI (Edge AI Evaluation)
        print(f"\n[AI Decision Summary]")
        for state, count in self.state_counts.items():
            percentage = (count / self.total_attempts * 100) if self.total_attempts > 0 else 0
            print(f" - {state:<12}: {count} ครั้ง ({percentage:.1f}%)")
            
        # 3. สรุปความคุ้มค่า
        print("\n[Conclusion]")
        if recovery_rate >= 100 and self.total_attempts > 0:
            print("✅ ระบบมีความทนทานสูง (High Resilience): ข้อมูลครบถ้วน 100%")
        else:
            print("⚠️ ระบบมีความเสี่ยงข้อมูลสูญหาย: ควรตรวจสอบหน่วยความจำสำรอง")
        print("="*30 + "\n")
