from __future__ import annotations


def calculateAreaM2(largura: float | None, comprimento: float | None) -> float | None:
    """Calculate the area in square meters from centimeter measures."""
    if not largura or not comprimento:
        return None

    return (largura / 100.0) * (comprimento / 100.0)


def calculatePrecoPorM2(
    valorUnitario: float | None,
    areaM2: float | None,
) -> float | None:
    """Calculate the historical price per square meter safely."""
    if not valorUnitario or not areaM2 or areaM2 <= 0:
        return None

    return valorUnitario / areaM2
