export interface TT20ParamDetail {
  ma_thong_so?: string;
  ten_thong_so?: string;
  phan_loai?: string;
  dinh_bien?: string;
  dinh_muc_cong_str?: string;
  dinh_muc_cong?: number;
  tieu_chuan?: string;
  tools?: any[];
  equipment?: any[];
  materials?: any[];
}

export interface TT20GroupData {
  coreCode?: string;
  sec_id?: string;
  name?: string;
  standard?: string;
  field?: TT20ParamDetail | null;
  lab?: TT20ParamDetail | null;
  single?: TT20ParamDetail | null;
}

export interface PaktItem {
  id: number;
  stt: string;
  nhom: string;
  khu_vuc: string;
  moi_truong: string;
  thong_so: string;
  dvt: string;
  so_vi_tri: number;
  so_lan: number;
  so_luong_mau: number;
  vi_tri: string;
  sec_id: string;
  ma_gop: string;
  tt20_data?: TT20GroupData | null;
}

export interface FilterState {
  search: string;
  program: string;
  plant: string;
  environment: string;
}

export interface LaborRowData {
  item: PaktItem;
  fieldRank: string;
  fieldNorm: number;
  fieldTotal: number;
  labRank: string;
  labNorm: number;
  labTotal: number;
  grandTotal: number;
}
