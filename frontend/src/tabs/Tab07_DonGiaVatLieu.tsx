import React, { useState, useMemo, useEffect, useCallback } from 'react';
import { 
  Search, X, Save, FileSpreadsheet, 
  Layers, CheckCircle2, Eye, ShieldCheck,
  TrendingDown, Sparkles
} from 'lucide-react';
import type { MaterialPriceItem, MaterialPricingDatabase, PaktItem } from '../types';

interface Tab07DonGiaVatLieuProps {
  paktItems: PaktItem[];
  onSelectDrawerItem?: (item: PaktItem) => void;
}

export const Tab07_DonGiaVatLieu: React.FC<Tab07DonGiaVatLieuProps> = ({ paktItems, onSelectDrawerItem }) => {
  const [items, setItems] = useState<MaterialPriceItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedMaterialForDetail, setSelectedMaterialForDetail] = useState<MaterialPriceItem | null>(null);
  const [saveToast, setSaveToast] = useState<string | null>(null);

  // 1. Nạp dữ liệu đơn giá vật liệu từ Backend / Static fallback
  const fetchPricing = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/material-pricing');
      if (!res.ok) throw new Error('API failed');
      const data: MaterialPricingDatabase = await res.json();
      setItems(data.items || []);
    } catch (err) {
      console.warn('Backend /api/material-pricing not reachable, loading fallback static:', err);
      try {
        const fbRes = await fetch('/material_pricing.json');
        const fbData: MaterialPricingDatabase = await fbRes.json();
        setItems(fbData.items || []);
      } catch (fbErr) {
        console.error('Failed to load material pricing:', fbErr);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPricing();
  }, [fetchPricing]);

  // 2. Cập nhật đơn giá duyệt cục bộ
  const handleUpdatePrice = (id: string, newPrice: number) => {
    setItems(prev => prev.map(item => {
      if (item.id === id) {
        return {
          ...item,
          approved_price: Math.max(0, newPrice),
          approval_basis: 'Điều chỉnh thẩm định trực tiếp'
        };
      }
      return item;
    }));
  };

  // 3. Các thao tác gán giá nhanh hàng loạt (Bulk actions)
  const applyMinQuotes = () => {
    setItems(prev => prev.map(item => ({
      ...item,
      approved_price: Math.min(item.quote_1, item.quote_2, item.quote_3),
      approval_basis: 'Min 03 Báo giá cạnh tranh (Khoản 2 Điều 16 NĐ 24/2024/NĐ-CP)'
    })));
  };

  const applyHd71 = () => {
    setItems(prev => prev.map(item => ({
      ...item,
      approved_price: item.price_hd71,
      approval_basis: 'Kế thừa HĐ số 71/2025/HĐ-DV của NMNĐ Vĩnh Tân 4'
    })));
  };

  const applyAvgQuotes = () => {
    setItems(prev => prev.map(item => ({
      ...item,
      approved_price: Math.round((item.quote_1 + item.quote_2 + item.quote_3) / 3),
      approval_basis: 'Bình quân 03 Báo giá cạnh tranh'
    })));
  };

  // 4. Lưu lại CSDL vào Backend và OneDrive
  const handleSaveToBackend = async () => {
    setIsSaving(true);
    try {
      const payload: MaterialPricingDatabase = {
        metadata: {
          total_items: items.length,
          currency: 'VND',
          vat_included: false,
          waste_factor_statutory: 1.08,
          legal_basis: [
            'Khoản 4.4 Thông tư 20/2017/TT-BTNMT (+8% hao hụt vụn vặt)',
            'Quyết định số 80/2026/QĐ-UBND ngày 19/10/2026 của UBND TP.HCM',
            'Điều 16 Nghị định số 24/2024/NĐ-CP (Tối thiểu 3 báo giá cạnh tranh)',
            'Hợp đồng số 71/2025/HĐ-DV của NMNĐ Vĩnh Tân 4'
          ],
          last_updated: new Date().toISOString().split('T')[0]
        },
        items: items
      };

      const res = await fetch('/api/material-pricing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Failed to save to backend');
      setSaveToast('Đã lưu thành công CSDL Đơn giá Vật liệu vào hệ thống!');
      setTimeout(() => setSaveToast(null), 4000);
    } catch (err) {
      console.error('Error saving pricing:', err);
      alert('Không thể lưu vào backend. Vui lòng kiểm tra kết nối API.');
    } finally {
      setIsSaving(false);
    }
  };

  // 5. Danh sách lọc
  const filteredList = useMemo(() => {
    return items.filter(it => {
      if (selectedCategory !== 'all' && it.category !== selectedCategory) return false;
      if (searchQuery.trim()) {
        const q = searchQuery.trim().toLowerCase();
        const mName = it.name.toLowerCase().includes(q);
        const mUnit = it.unit.toLowerCase().includes(q);
        const mId = it.id.toLowerCase().includes(q);
        if (!mName && !mUnit && !mId) return false;
      }
      return true;
    });
  }, [items, selectedCategory, searchQuery]);

  // 6. Tính toán tổng hợp KPI toàn bộ danh mục vật tư
  const kpis = useMemo(() => {
    let rawCost = 0;
    let costWithWaste = 0;
    let ktatCost = 0;

    items.forEach(it => {
      const lineRaw = it.total_quantity_raw * it.approved_price;
      const lineWaste = lineRaw * 1.08;
      const lineKtat = it.total_quantity_raw * it.price_ktat * 1.08;

      rawCost += lineRaw;
      costWithWaste += lineWaste;
      ktatCost += lineKtat;
    });

    const diffSavings = ktatCost - costWithWaste;

    return {
      totalItemsCount: items.length,
      rawCost: Math.round(rawCost),
      wasteAmount: Math.round(costWithWaste - rawCost),
      costWithWaste: Math.round(costWithWaste),
      ktatCost: Math.round(ktatCost),
      diffSavings: Math.round(diffSavings)
    };
  }, [items]);

  // 7. Tìm danh sách các thông số PAKT sử dụng vật liệu đang chọn
  const paramsUsingSelectedMaterial = useMemo(() => {
    if (!selectedMaterialForDetail) return [];
    const targetName = selectedMaterialForDetail.name.trim().toLowerCase();
    const targetUnit = selectedMaterialForDetail.unit.trim().toLowerCase();

    const result: { item: PaktItem; normRaw: number; totalQty: number }[] = [];

    paktItems.forEach(pakt => {
      const N = pakt.so_luong_mau || 1;
      const tt = pakt.tt20_data;
      if (!tt) return;

      let foundNorm = 0;
      for (const k of ['field', 'lab', 'single'] as const) {
        const sub = tt[k];
        if (sub && sub.materials) {
          for (const m of sub.materials) {
            const mName = String(m.name || '').trim().toLowerCase();
            const mUnit = String(m.unit || '').trim().toLowerCase();
            if (mName === targetName && (!targetUnit || mUnit === targetUnit)) {
              foundNorm += Number(m.norm || 0);
            }
          }
        }
      }

      if (foundNorm > 0) {
        result.push({
          item: pakt,
          normRaw: foundNorm,
          totalQty: Number((foundNorm * 1.08 * N).toFixed(4))
        });
      }
    });

    return result;
  }, [selectedMaterialForDetail, paktItems]);

  const getCategoryBadge = (cat: string) => {
    switch (cat) {
      case 'hoa_chat':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blue-950 text-blue-300 border border-blue-800/50">Hóa chất tinh khiết</span>;
      case 'chuan':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-purple-950 text-purple-300 border border-purple-800/50">Chất chuẩn / Vi sinh</span>;
      case 'vat_tu_tieu_hao':
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-950 text-amber-300 border border-amber-800/50">Vật tư tiêu hao / Lọc</span>;
      default:
        return <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700/60">Thông dụng / Bảo quản</span>;
    }
  };

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-400 bg-slate-950">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-ping"></span>
          <span className="text-sm font-medium">Đang tải CSDL Đơn giá Vật liệu & 3 Báo giá...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-slate-950 text-slate-100 select-none">
      {/* Toast Alert */}
      {saveToast && (
        <div className="absolute top-16 right-6 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-lg shadow-xl flex items-center space-x-2 text-xs font-semibold animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-200" />
          <span>{saveToast}</span>
        </div>
      )}

      {/* 1. Header Toolbar */}
      <div className="p-3 bg-slate-900 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Input */}
          <div className="relative min-w-[240px]">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm theo tên hóa chất, dung dịch chuẩn, ĐVT..."
              className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-9 pr-7 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Category Dropdown */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 outline-none focus:border-blue-500 font-medium"
          >
            <option value="all">Tất cả Phân nhóm (173 loại)</option>
            <option value="hoa_chat">Hóa chất tinh khiết (AR/PA/HPLC)</option>
            <option value="chuan">Dung dịch chuẩn & Vi sinh</option>
            <option value="vat_tu_tieu_hao">Vật tư tiêu hao / Phin lọc</option>
            <option value="thong_dung">Vật tư thông dụng & Bảo quản</option>
          </select>
        </div>

        {/* Action Buttons: Apply Presets & Save */}
        <div className="flex items-center space-x-1.5 text-xs">
          <button
            onClick={applyMinQuotes}
            className="px-2.5 py-1.5 bg-blue-900/40 hover:bg-blue-800/60 text-blue-200 border border-blue-700/50 rounded-lg font-semibold transition active:scale-95 flex items-center space-x-1"
            title="Áp dụng giá thấp nhất trong 03 Báo giá cạnh tranh (NĐ 24/2024)"
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-400" />
            <span>Min 3 Báo giá</span>
          </button>

          <button
            onClick={applyHd71}
            className="px-2.5 py-1.5 bg-purple-900/40 hover:bg-purple-800/60 text-purple-200 border border-purple-700/50 rounded-lg font-semibold transition active:scale-95"
            title="Kế thừa theo Hợp đồng số 71/2025/HĐ-DV của VT4"
          >
            Kế thừa HĐ 71
          </button>

          <button
            onClick={applyAvgQuotes}
            className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 rounded-lg font-semibold transition active:scale-95"
            title="Áp dụng giá bình quân 3 Báo giá"
          >
            Bình quân
          </button>

          <button
            onClick={handleSaveToBackend}
            disabled={isSaving}
            className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold shadow-md shadow-emerald-600/30 transition active:scale-95 flex items-center space-x-1.5 ml-2"
          >
            <Save className="w-3.5 h-3.5" />
            <span>{isSaving ? 'Đang lưu...' : 'Lưu Đơn Giá'}</span>
          </button>
        </div>
      </div>

      {/* 2. Top Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2.5 p-3 bg-slate-900/60 border-b border-slate-800 text-xs">
        {/* Card 1: Tổng danh mục */}
        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
            <Layers className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Danh Mục Hóa Chất</div>
            <div className="text-base font-bold text-white tabular-nums">{kpis.totalItemsCount} <span className="text-xs font-normal text-slate-400">loại</span></div>
          </div>
        </div>

        {/* Card 2: Chi phí trước hao hụt */}
        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
            <FileSpreadsheet className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-400">Chi Phí Gốc (Trước +8%)</div>
            <div className="text-sm font-bold text-indigo-300 tabular-nums">
              {kpis.rawCost.toLocaleString('vi-VN')} <span className="text-[10px] font-normal text-indigo-200/60">đ</span>
            </div>
          </div>
        </div>

        {/* Card 3: Chi phí +8% hao hụt quy định */}
        <div className="bg-slate-800/70 border border-slate-700/60 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-amber-500/20 text-amber-400 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-amber-400">+8% Hao Hụt (K4.4 TT20)</div>
            <div className="text-sm font-bold text-amber-300 tabular-nums">
              +{kpis.wasteAmount.toLocaleString('vi-VN')} <span className="text-[10px] font-normal text-amber-200/60">đ</span>
            </div>
          </div>
        </div>

        {/* Card 4: Tổng Chi Phí Vật Liệu Sau Hao Hụt */}
        <div className="bg-gradient-to-r from-blue-950/60 to-indigo-950/60 border border-blue-500/40 rounded-lg p-2.5 flex items-center space-x-2.5 shadow-sm">
          <div className="w-8 h-8 rounded-md bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-md">
            <FileSpreadsheet className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-blue-300">Tổng Chi Phí Vật Liệu (C_VL)</div>
            <div className="text-base font-black text-white tabular-nums">
              {kpis.costWithWaste.toLocaleString('vi-VN')} <span className="text-xs font-normal text-blue-300">đ</span>
            </div>
          </div>
        </div>

        {/* Card 5: Giá trị Tiết kiệm / Giảm trừ so với KTAT */}
        <div className="bg-emerald-950/40 border border-emerald-600/40 rounded-lg p-2.5 flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-md bg-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
            <TrendingDown className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-emerald-400">Tiết Kiệm So Với KTAT</div>
            <div className="text-base font-black text-emerald-300 tabular-nums">
              -{kpis.diffSavings.toLocaleString('vi-VN')} <span className="text-xs font-normal text-emerald-200/60">đ</span>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Main Data Table */}
      <div className="flex-1 overflow-auto bg-slate-950">
        <table className="w-full text-left border-collapse text-xs">
          <thead className="sticky top-0 bg-slate-900 border-b border-slate-700/80 text-slate-300 font-bold z-10 shadow-sm text-[11px]">
            {/* Multi-tier header */}
            <tr className="border-b border-slate-800">
              <th colSpan={4} className="py-1.5 px-3 text-center bg-slate-900 border-r border-slate-800 text-slate-400 uppercase tracking-wider">
                1. Danh mục & Khối lượng tổng (Từ Tab 3)
              </th>
              <th colSpan={5} className="py-1.5 px-3 text-center bg-blue-950/30 text-blue-300 border-r border-slate-800 uppercase tracking-wider">
                2. Ma trận Đối soát Đơn giá Đa nguồn (Điều 16 NĐ 24/2024)
              </th>
              <th colSpan={4} className="py-1.5 px-3 text-center bg-emerald-950/30 text-emerald-300 uppercase tracking-wider">
                3. Đơn giá Thẩm định Duyệt & Thành tiền (+8% Khoản 4.4 TT20)
              </th>
            </tr>
            <tr>
              <th className="py-2 px-2.5 w-12 text-center">STT</th>
              <th className="py-2 px-3 min-w-[200px]">Tên Hóa chất / Vật liệu</th>
              <th className="py-2 px-2 w-16 text-center">ĐVT</th>
              <th className="py-2 px-3 w-28 text-right tabular-nums border-r border-slate-800">Tổng Nhu Cầu</th>

              {/* Quotes */}
              <th className="py-2 px-2.5 w-24 text-right bg-slate-900/50 text-slate-400 tabular-nums">KTAT Đề xuất</th>
              <th className="py-2 px-2.5 w-24 text-right bg-blue-950/20 text-slate-300 tabular-nums">Báo giá 1</th>
              <th className="py-2 px-2.5 w-24 text-right bg-blue-950/20 text-slate-300 tabular-nums">Báo giá 2</th>
              <th className="py-2 px-2.5 w-24 text-right bg-blue-950/20 text-slate-300 tabular-nums">Báo giá 3</th>
              <th className="py-2 px-2.5 w-24 text-right bg-purple-950/20 text-purple-300 tabular-nums border-r border-slate-800">HĐ 71/2025</th>

              {/* Approved Price & Totals */}
              <th className="py-2 px-3 w-32 text-right bg-emerald-950/20 text-emerald-300 tabular-nums">ĐG Duyệt (đ)</th>
              <th className="py-2 px-3 min-w-[160px] bg-emerald-950/20 text-slate-300">Căn cứ Thẩm định</th>
              <th className="py-2 px-3 w-28 text-right bg-emerald-950/20 text-slate-400 tabular-nums">Tiền gốc</th>
              <th className="py-2 px-3 w-32 text-right bg-emerald-950/20 text-emerald-300 tabular-nums font-black">
                +8% TT20 (đ)
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-300 font-mono text-[11px]">
            {filteredList.map((item, idx) => {
              const lineRaw = item.total_quantity_raw * item.approved_price;
              const lineWithWaste = lineRaw * 1.08;

              return (
                <tr key={item.id} className="hover:bg-slate-900/60 transition group">
                  <td className="py-2 px-2.5 text-center text-slate-500">{idx + 1}</td>
                  <td className="py-2 px-3 font-sans">
                    <div className="flex items-center space-x-1.5">
                      <span className="font-semibold text-white">{item.name}</span>
                      <button
                        onClick={() => setSelectedMaterialForDetail(item)}
                        className="text-slate-500 hover:text-blue-400 p-0.5 rounded transition"
                        title="Xem danh sách các thông số quan trắc sử dụng hóa chất này"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </div>
                    <div className="mt-0.5 flex items-center space-x-1">
                      {getCategoryBadge(item.category)}
                      <span className="text-[10px] text-slate-500">({item.param_count} thông số dùng)</span>
                    </div>
                  </td>
                  <td className="py-2 px-2 text-center text-slate-400 font-sans">{item.unit}</td>
                  <td className="py-2 px-3 text-right font-bold text-blue-300 tabular-nums border-r border-slate-800">
                    {item.total_quantity_raw.toLocaleString('vi-VN', { maximumFractionDigits: 3 })}
                  </td>

                  {/* Multi-source quotes */}
                  <td className="py-2 px-2.5 text-right text-slate-400 tabular-nums bg-slate-900/30">
                    {item.price_ktat.toLocaleString('vi-VN')}
                  </td>
                  <td className="py-2 px-2.5 text-right text-slate-300 tabular-nums bg-blue-950/10">
                    {item.quote_1.toLocaleString('vi-VN')}
                  </td>
                  <td className="py-2 px-2.5 text-right text-slate-300 tabular-nums bg-blue-950/10">
                    {item.quote_2.toLocaleString('vi-VN')}
                  </td>
                  <td className="py-2 px-2.5 text-right text-slate-300 tabular-nums bg-blue-950/10">
                    {item.quote_3.toLocaleString('vi-VN')}
                  </td>
                  <td className="py-2 px-2.5 text-right text-purple-300 tabular-nums bg-purple-950/10 border-r border-slate-800">
                    {item.price_hd71.toLocaleString('vi-VN')}
                  </td>

                  {/* Approved Price Input */}
                  <td className="py-1 px-2 text-right bg-emerald-950/10">
                    <input
                      type="number"
                      value={item.approved_price}
                      onChange={(e) => handleUpdatePrice(item.id, Number(e.target.value))}
                      className="w-full text-right bg-slate-800 border border-slate-700 rounded px-2 py-1 text-emerald-300 font-bold font-mono focus:border-emerald-500 outline-none"
                    />
                  </td>

                  <td className="py-2 px-3 text-slate-400 font-sans text-[10px] truncate max-w-[160px] bg-emerald-950/10" title={item.approval_basis}>
                    {item.approval_basis}
                  </td>

                  <td className="py-2 px-3 text-right text-slate-400 tabular-nums bg-emerald-950/10">
                    {Math.round(lineRaw).toLocaleString('vi-VN')}
                  </td>

                  <td className="py-2 px-3 text-right font-black text-emerald-300 tabular-nums bg-emerald-950/20">
                    {Math.round(lineWithWaste).toLocaleString('vi-VN')} đ
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* 4. Drawer chi tiết: Xem hóa chất này được dùng ở đâu trong 253 dòng PAKT */}
      {selectedMaterialForDetail && (
        <div className="fixed inset-0 z-50 overflow-hidden flex justify-end bg-black/50 backdrop-blur-xs transition-opacity animate-in fade-in">
          <div className="w-full max-w-xl bg-slate-900 border-l border-slate-700 h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
            {/* Drawer Header */}
            <div className="p-4 border-b border-slate-800 flex items-start justify-between bg-slate-950/80">
              <div>
                <span className="text-[10px] uppercase font-bold text-blue-400">
                  Truy vết ngược xuôi (Bậc 4 $\rightarrow$ Bậc 1)
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">
                  {selectedMaterialForDetail.name} ({selectedMaterialForDetail.unit})
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Đơn giá duyệt: <strong className="text-emerald-400">{selectedMaterialForDetail.approved_price.toLocaleString('vi-VN')} đ/{selectedMaterialForDetail.unit}</strong> • Đã gồm +8% hao hụt TT20
                </p>
              </div>
              <button
                onClick={() => setSelectedMaterialForDetail(null)}
                className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Drawer Body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 text-xs">
              <div className="text-[11px] font-semibold text-slate-300">
                Có <strong>{paramsUsingSelectedMaterial.length}</strong> thông số quan trắc sử dụng loại hóa chất/vật tư này:
              </div>

              <div className="divide-y divide-slate-800 border border-slate-800 rounded-lg overflow-hidden bg-slate-950/60">
                {paramsUsingSelectedMaterial.map((entry, idx) => (
                  <div 
                    key={idx} 
                    onClick={() => onSelectDrawerItem && onSelectDrawerItem(entry.item)}
                    className={`p-2.5 flex items-center justify-between hover:bg-slate-800/40 transition ${onSelectDrawerItem ? 'cursor-pointer' : ''}`}
                  >
                    <div>
                      <div className="font-semibold text-white">
                        {entry.item.thong_so}
                      </div>
                      <div className="text-[10px] text-slate-400">
                        {entry.item.khu_vuc} • {entry.item.moi_truong} • Số mẫu N: {entry.item.so_luong_mau}
                      </div>
                    </div>
                    <div className="text-right font-mono">
                      <div className="text-blue-300 font-bold">
                        {entry.totalQty.toLocaleString('vi-VN')} {selectedMaterialForDetail.unit}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        ({entry.normRaw} đm/mẫu × 1,08)
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Drawer Footer */}
            <div className="p-3 border-t border-slate-800 bg-slate-950 flex justify-end">
              <button
                onClick={() => setSelectedMaterialForDetail(null)}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
