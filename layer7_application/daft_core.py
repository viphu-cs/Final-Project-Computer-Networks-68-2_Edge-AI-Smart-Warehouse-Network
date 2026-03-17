"""
daft_core.py
============
Core DAFT operator algebra. Implements all six operators, state
classifier, field computation, and quantum corrections.

Usage
-----
    from daft_core import DAFTField
    field = DAFTField(alpha=1.0, lambda_res=3)
    state = field.classify(xi=-0.5, xj=0.5)
"""

import numpy as np
from dataclasses import dataclass
from typing import Literal

StateType = Literal["PURE", "CONSTRUCTIVE", "DESTRUCTIVE", "BOUNDARY"]

@dataclass
class DAFTField:
    """
    DAFT field with the six operators and quantum extensions.

    Parameters
    ----------
    alpha      : dyadic coupling constant (default 1.0)
    lambda_res : resolution cutoff λ (default 3)
    """
    alpha: float = 1.0
    lambda_res: int = 3

    # ── Derived quantum quantities ─────────────────────────────────────────
    @property
    def hbar(self) -> float:
        """DAFT quantum of action ħ_DAFT = α²/λ."""
        return self.alpha**2 / self.lambda_res

    @property
    def c_daft(self) -> float:
        """DAFT effective speed of light = α/λ."""
        return self.alpha / self.lambda_res

    @property
    def field_levels(self) -> list:
        """The (λ+1) potential levels: α/2ⁿ for n=0..λ."""
        return [self.alpha / 2**n for n in range(self.lambda_res + 1)]

    # ── The six operators ──────────────────────────────────────────────────
    def O_plus(self, xi: float, xj: float) -> float:
        """O+ : inner product (force / recognition)."""
        return xi * xj

    def O_star(self, xi: float, xj: float) -> np.ndarray:
        """O* : outer product (field / structure). Returns rank-1 tensor."""
        return np.outer([xi], [xj])

    def O_minus(self, xi: float, xj: float) -> float:
        """O- : boundary operator (conservation). Zero under constraint."""
        return xi - xj

    def O4(self, xi: float, xj: float) -> float:
        """O4 : magnitude difference (classification driver)."""
        return abs(xi) - abs(xj)

    def O5(self, xi: float) -> float:
        """O5 : self-reference (identity). Always zero."""
        return abs(xi - xi)  # = 0 by definition

    def O6(self, xi: float, xj: float) -> float:
        """O6 : metric distance (total separation)."""
        return abs(xi - xj)

    # ── State classifier ───────────────────────────────────────────────────
    def classify(self, xi: float, xj: float) -> StateType:
        """
        Classify a pair (xi, xj) into one of four DAFT states.
        O(1) complexity.
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
        """Eccentricity ratio ρ = O6 / |O4|. ρ→∞ for PURE, ρ=1 for BOUNDARY."""
        o4 = self.O4(xi, xj)
        o6 = self.O6(xi, xj)
        return o6 / abs(o4) if abs(o4) > 1e-10 else float("inf")

    # ── Core field ─────────────────────────────────────────────────────────
    def Phi(self, x: float) -> float:
        """DAFT core field: Φ(x) = Σ O(±α/2ⁿ) for n=0..λ."""
        return sum(x / 2**n for n in range(self.lambda_res + 1))

    # ── Dynamics ───────────────────────────────────────────────────────────
    def asymmetry_decay(self, O4_0: float, t: np.ndarray) -> np.ndarray:
        """Classical O4(t) = O4(0)·exp(−t). Universal decay law."""
        return O4_0 * np.exp(-t)

    def resolution_growth(self, lambda_0: float, O6: float,
                          t: np.ndarray) -> np.ndarray:
        """λ(t) = sqrt(λ₀² + O6·t). DAFT diffusion / learning law."""
        return np.sqrt(lambda_0**2 + O6 * t)

    # ── Beta function ──────────────────────────────────────────────────────
    def beta_one_loop(self, O6: float) -> float:
        """One-loop beta function β(α) = -α²·O6/2λ². Always negative."""
        return -self.alpha**2 * O6 / (2 * self.lambda_res**2)

    def beta_two_loop(self, O6: float) -> float:
        """Two-loop beta function with ln(2) correction."""
        b1 = self.beta_one_loop(O6)
        correction = 1 + (self.alpha**2 * np.log(2)) / (2 * np.pi * self.lambda_res)
        return b1 * correction

    def alpha_running(self, lambda_target: float, O6: float = 1.0) -> float:
        """Running coupling α(λ) from one-loop RG equation."""
        denom = 1 + (self.alpha * O6 / (2 * self.lambda_res**2)) * np.log(
            lambda_target / self.lambda_res)
        return self.alpha / denom if denom > 0 else float("inf")

    # ── Quantum potential ──────────────────────────────────────────────────
    def yukawa_length(self, O6: float) -> float:
        """Screening length ξ = √λ·O6 / √(λ·O6² + α²)."""
        return (np.sqrt(self.lambda_res) * O6
                / np.sqrt(self.lambda_res * O6**2 + self.alpha**2))

    def V_quantum(self, O6: float) -> float:
        """Yukawa-screened quantum potential V = -12/O6 · exp(-O6/ξ)."""
        xi = self.yukawa_length(O6)
        return -12 * self.alpha / O6 * np.exp(-O6 / xi)