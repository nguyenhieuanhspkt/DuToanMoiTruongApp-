from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class NormDetail(BaseModel):
    ma_thong_so: Optional[str] = None
    ten_thong_so: Optional[str] = None
    nhan_cong: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    dung_cu: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    thiet_bi: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    vat_lieu: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class TT20GroupData(BaseModel):
    coreCode: Optional[str] = None
    sec_id: Optional[str] = None
    name: Optional[str] = None
    standard: Optional[str] = None
    field: Optional[Dict[str, Any]] = None
    lab: Optional[Dict[str, Any]] = None
    single: Optional[Dict[str, Any]] = None

class PaktItem(BaseModel):
    id: int
    stt: str
    nhom: str
    khu_vuc: str
    moi_truong: str
    thong_so: str
    dvt: str
    so_vi_tri: int
    so_lan: int
    so_luong_mau: int
    vi_tri: Optional[str] = ""
    sec_id: Optional[str] = ""
    ma_gop: Optional[str] = ""
    tt20_data: Optional[TT20GroupData] = None

class PricingConfig(BaseModel):
    labor_rates_3072: Dict[str, float]
    currency: str = "VND"
    last_updated: Optional[str] = None
    source: Optional[str] = None

class OverheadConfig(BaseModel):
    indirect_cost_rate: float = 0.15
    contingency_rate: float = 0.05
    vat_rate: float = 0.08
    source: Optional[str] = None
