"""
HTTP client for calling the ML Inference server.
Routes single readings to /predict, batches to /predict/batch.
"""

import httpx
import logging
from typing import Optional
from app.config import ML_INFERENCE_URL

logger = logging.getLogger("genai.ml_client")

TIMEOUT = 30  # seconds


def _url(path: str) -> str:
    return f"{ML_INFERENCE_URL.rstrip('/')}{path}"


def predict_single(
    inverter_id: str,
    dc_voltage: float,
    dc_current: float,
    ac_power: float,
    module_temp: float,
    ambient_temp: float,
    irradiation: float,
    alarm_code: int = 0,
    op_state: int = 5120,
    power_factor: Optional[float] = None,
    frequency: Optional[float] = None,
    include_shap: bool = True,
    include_plot: bool = False,
) -> dict:
    """Call ML inference /predict for a single inverter reading."""
    payload = {
        "inverter_id": inverter_id,
        "dc_voltage": dc_voltage,
        "dc_current": dc_current,
        "ac_power": ac_power,
        "module_temp": module_temp,
        "ambient_temp": ambient_temp,
        "irradiation": irradiation,
        "alarm_code": alarm_code,
        "op_state": op_state,
        "include_shap": include_shap,
        "include_plot": include_plot,
    }
    if power_factor is not None:
        payload["power_factor"] = power_factor
    if frequency is not None:
        payload["frequency"] = frequency

    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(_url("/predict"), json=payload)
        resp.raise_for_status()
        return resp.json()


def predict_batch(
    readings: list[dict],
    mode: str = "manual",
    include_shap: bool = True,
    include_plot: bool = False,
) -> dict:
    """
    Call ML inference /predict/batch for multiple inverter readings.

    Each reading in the list should have:
      { "inverter_id": "...", "features": { "dc_voltage": ..., ... } }
    """
    payload = {
        "readings": readings,
        "mode": mode,
        "include_shap": include_shap,
        "include_plot": include_plot,
    }

    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(_url("/predict/batch"), json=payload)
        resp.raise_for_status()
        return resp.json()


def health_check() -> dict:
    """Check if the ML inference server is reachable."""
    try:
        with httpx.Client(timeout=5) as client:
            resp = client.get(_url("/health"))
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.warning("ML inference health check failed: %s", e)
        return {"status": "unreachable", "error": str(e)}
