"""
daft_core.py
============
พีชคณิตตัวดำเนินการหลักของ DAFT (Core DAFT operator algebra) 
ซึ่งประกอบด้วยตัวดำเนินการทั้ง 6 ตัว, การจำแนกสถานะ (state classifier), 
การคำนวณสนาม (field computation) และการแก้ไขทางควอนตัม (quantum corrections)

การใช้งาน
-----
    from daft_core import DAFTField
    field = DAFTField(alpha=1.0, lambda_res=3)
    state = field.classify(xi=-0.5, xj=0.5)
"""

import numpy as np
from dataclasses import dataclass
from typing import Literal

# ประเภทสถานะ: "PURE" (บริสุทธิ์), "CONSTRUCTIVE" (เสริมกัน), "DESTRUCTIVE" (หักล้างกัน), "BOUNDARY" (ขอบเขต)
StateType = Literal["PURE", "CONSTRUCTIVE", "DESTRUCTIVE", "BOUNDARY"]

@dataclass
class DAFTField:
    """
    สนาม DAFT ที่มีตัวดำเนินการ 6 ตัวและส่วนขยายทางควอนตัม

    พารามิเตอร์ (Parameters)
    ----------
    alpha      : ค่าคงที่การควบคู่ไดอาดิก (dyadic coupling constant) (ค่าเริ่มต้น 1.0)
    lambda_res : ค่าจำกัดความละเอียด λ (resolution cutoff) (ค่าเริ่มต้น 3)
    """
    alpha: float = 1.0
    lambda_res: int = 3

    # ── ปริมาณทางควอนตัมที่คำนวณได้ (Derived quantum quantities) ──────────
    @property
    def hbar(self) -> float:
        """ควอนตัมของการกระทำของ DAFT (DAFT quantum of action) ħ_DAFT = α²/λ"""
        return self.alpha**2 / self.lambda_res

    @property
    def c_daft(self) -> float:
        """ความเร็วแสงประสิทธิผลของ DAFT (DAFT effective speed of light) = α/λ"""
        return self.alpha / self.lambda_res

    @property
    def field_levels(self) -> list:
        """ระดับศักย์ (λ+1) ระดับ: α/2ⁿ สำหรับ n=0..λ"""
        return [self.alpha / 2**n for n in range(self.lambda_res + 1)]

    # ── ตัวดำเนินการทั้ง 6 (The six operators) ─────────────────────────────
    def O_plus(self, xi: float, xj: float) -> float:
        """O+ : ผลคูณภายใน (แรง / การรับรู้)"""
        return xi * xj

    def O_star(self, xi: float, xj: float) -> np.ndarray:
        """O* : ผลคูณภายนอก (สนาม / โครงสร้าง) คืนค่าเป็นเทนเซอร์อันดับ 1 (rank-1 tensor)"""
        return np.outer([xi], [xj])

    def O_minus(self, xi: float, xj: float) -> float:
        """O- : ตัวดำเนินการขอบเขต (การอนุรักษ์) เป็นศูนย์ภายใต้ข้อจำกัด"""
        return xi - xj

    def O4(self, xi: float, xj: float) -> float:
        """O4 : ผลต่างของขนาด (ตัวขับเคลื่อนการจำแนกสถานะ)"""
        return abs(xi) - abs(xj)

    def O5(self, xi: float) -> float:
        """O5 : การอ้างอิงตนเอง (เอกลักษณ์) เป็นศูนย์เสมอ"""
        return abs(xi - xi)  # = 0 ตามนิยาม

    def O6(self, xi: float, xj: float) -> float:
        """O6 : ระยะทางเมตริก (การแยกกันทั้งหมด)"""
        return abs(xi - xj)

    # ── การจำแนกสถานะ (State classifier) ───────────────────────────────────
    def classify(self, xi: float, xj: float) -> StateType:
        """
        จำแนกคู่ (xi, xj) ออกเป็นหนึ่งในสี่สถานะของ DAFT 
        มีความซับซ้อนเชิงเวลาเป็น O(1)
        """
        o4 = self.O4(xi, xj)
        o6 = self.O6(xi, xj)

        if o6 < 1e-10:
            return "BOUNDARY"
        if abs(xi) < 1e-10 or abs(xj) < 1e-10:
            return "BOUNDARY"
        if abs(o4) < 1e-8 * o6:
            return "PURE"
        if o4 < 0:
            return "CONSTRUCTIVE"
        return "DESTRUCTIVE"

    def eccentricity(self, xi: float, xj: float) -> float:
        """อัตราส่วนความเยื้องศูนย์กลาง (Eccentricity ratio) ρ = O6 / |O4| โดย ρ→∞ สำหรับ PURE, ρ=1 สำหรับ BOUNDARY"""
        o4 = self.O4(xi, xj)
        o6 = self.O6(xi, xj)
        return o6 / abs(o4) if abs(o4) > 1e-10 else float("inf")

    # ── สนามหลัก (Core field) ─────────────────────────────────────────────
    def Phi(self, x: float) -> float:
        """สนามหลักของ DAFT: Φ(x) = Σ O(±α/2ⁿ) สำหรับ n=0..λ"""
        return sum(x / 2**n for n in range(self.lambda_res + 1))

    # ── พลวัต (Dynamics) ──────────────────────────────────────────────────
    def asymmetry_decay(self, O4_0: float, t: np.ndarray) -> np.ndarray:
        """การสลายตัวแบบอสมมาตร (Classical O4(t) = O4(0)·exp(−t)) เป็นกฎการสลายตัวสากล"""
        return O4_0 * np.exp(-t)

    def resolution_growth(self, lambda_0: float, O6: float,
                          t: np.ndarray) -> np.ndarray:
        """การเติบโตของความละเอียด λ(t) = sqrt(λ₀² + O6·t) เป็นกฎการแพร่หรือการเรียนรู้ของ DAFT"""
        return np.sqrt(lambda_0**2 + O6 * t)

    # ── ฟังก์ชันเบต้า (Beta function) ──────────────────────────────────────
    def beta_one_loop(self, O6: float) -> float:
        """ฟังก์ชันเบต้าแบบวงรอบเดียว (One-loop beta function) β(α) = -α²·O6/2λ² มีค่าเป็นลบเสมอ"""
        return -self.alpha**2 * O6 / (2 * self.lambda_res**2)

    def beta_two_loop(self, O6: float) -> float:
        """ฟังก์ชันเบต้าแบบสองวงรอบพร้อมการแก้ไขค่า ln(2)"""
        b1 = self.beta_one_loop(O6)
        correction = 1 + (self.alpha**2 * np.log(2)) / (2 * np.pi * self.lambda_res)
        return b1 * correction

    def alpha_running(self, lambda_target: float, O6: float = 1.0) -> float:
        """ค่าการควบคู่แบบแปรผัน (Running coupling) α(λ) จากสมการ RG แบบวงรอบเดียว"""
        denom = 1 + (self.alpha * O6 / (2 * self.lambda_res**2)) * np.log(
            lambda_target / self.lambda_res)
        return self.alpha / denom if denom > 0 else float("inf")

    # ── ศักย์ควอนตัม (Quantum potential) ───────────────────────────────────
    def yukawa_length(self, O6: float) -> float:
        """ระยะคัดกรอง (Screening length) ξ = √λ·O6 / √(λ·O6² + α²)"""
        return (np.sqrt(self.lambda_res) * O6
                / np.sqrt(self.lambda_res * O6**2 + self.alpha**2))

    def V_quantum(self, O6: float) -> float:
        """ศักย์ควอนตัมที่ถูกคัดกรองแบบยูกาวะ (Yukawa-screened quantum potential) V = -12/O6 · exp(-O6/ξ)"""
        xi = self.yukawa_length(O6)
        return -12 * self.alpha / O6 * np.exp(-O6 / xi)
