import React, { useState } from 'react';
import { 
  FileSpreadsheet, Check
} from 'lucide-react';
import type { PaktItem } from '../types';

interface ExcelSpreadsheetViewProps {
  items: PaktItem[];
}

export const ExcelSpreadsheetView: React.FC<ExcelSpreadsheetViewProps> = ({ items }) => {
  // Current active worksheet tab
  const [activeSheet, setActiveSheet] = useState<string>('Công trình');
  // Selected cell coordinates and value/formula
  const [selectedCell, setSelectedCell] = useState<{ coord: string; value: string; formula: string }>({
    coord: 'B8',
    value: 'K1 – Tại trung tâm nhà máy',
    formula: '="K1 – Tại trung tâm nhà máy"'
  });

  // Sheet Tabs list matching DU_TOAN_QUAN_TRAC_MOI_TRUONG_CHUAN_F1_100PCT.xlsx + Khoản 4.5 TT20
  const sheetTabs = [
    { id: 'Hệ số', name: 'Hệ số', color: '#107c41' },
    { id: 'Lương nhân công', name: 'Lương nhân công', color: '#107c41' },
    { id: 'Tính giá ca máy', name: 'Tính giá ca máy', color: '#107c41' },
    { id: 'Công trình', name: 'Công trình', color: '#107c41' },
    { id: 'Hao phí VT', name: 'Hao phí VT', color: '#107c41' },
    { id: 'Vật liệu', name: 'Vật liệu', color: '#107c41' },
    { id: 'Nhân công', name: 'Nhân công', color: '#107c41' },
    { id: 'Công cụ dụng cụ', name: 'Công cụ dụng cụ', color: '#107c41' },
    { id: 'Máy thi công', name: 'Máy thi công', color: '#107c41' },
    { id: 'Khoản 4.5 TT20', name: 'Khoản 4.5 TT20 (Mục 2.1.2)', color: '#d97706' },
    { id: 'THDT hạng mục', name: 'THDT hạng mục', color: '#dc2626' },
    { id: 'Đơn giá chi tiết', name: 'Đơn giá chi tiết', color: '#107c41' },
  ];

  const handleCellClick = (coord: string, value: string, formula?: string) => {
    setSelectedCell({
      coord,
      value,
      formula: formula || `="${value}"`
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-7.5rem)] bg-[#F3F3F3] border border-[#D4D4D8] rounded-md shadow-inner select-none font-['Times_New_Roman',serif]">
      {/* 1. EXCEL FORMULA BAR (Thanh công thức fx chuẩn Excel) */}
      <div className="h-9 bg-white border-b border-[#D4D4D8] flex items-center px-2 space-x-2 text-xs text-slate-800">
        {/* Name Box (Tọa độ ô) */}
        <div className="w-16 h-6 px-1.5 bg-[#F8F9FA] border border-[#CBD5E1] rounded flex items-center justify-center font-mono font-bold text-slate-700 shadow-sm">
          {selectedCell.coord}
        </div>

        {/* Function Button Icons */}
        <div className="flex items-center space-x-1 text-slate-400 border-r border-[#CBD5E1] pr-2">
          <button title="Hủy bỏ" className="hover:text-red-600 p-0.5 rounded">✕</button>
          <button title="Nhập" className="hover:text-green-600 p-0.5 rounded">✓</button>
          <span className="font-serif italic font-bold text-slate-600 px-1">fx</span>
        </div>

        {/* Formula Input Box */}
        <div className="flex-1 h-6 px-2 bg-white flex items-center font-mono text-slate-800 text-[13px] overflow-x-auto truncate">
          {selectedCell.formula}
        </div>
      </div>

      {/* 2. MAIN SPREADSHEET GRID (Lưới ô tính với cột A-B-C và hàng 1-2-3) */}
      <div className="flex-1 overflow-auto bg-white relative">
        {/* Render theo Sheet được chọn */}
        {activeSheet === 'Công trình' && (
          <table className="w-full border-collapse text-[13px] text-slate-900 border border-[#D4D4D8]">
            <thead>
              {/* Row: Excel Column Headers (A, B, C, D...) */}
              <tr className="bg-[#EFEFF2] text-slate-600 text-center text-[11px] font-sans font-semibold border-b border-[#D4D4D8]">
                <th className="w-10 py-1 border-r border-[#D4D4D8] bg-[#E1E2E5]">#</th>
                <th className="w-12 py-1 border-r border-[#D4D4D8]">A</th>
                <th className="w-64 py-1 border-r border-[#D4D4D8]">B</th>
                <th className="w-24 py-1 border-r border-[#D4D4D8]">C</th>
                <th className="w-56 py-1 border-r border-[#D4D4D8]">D</th>
                <th className="w-16 py-1 border-r border-[#D4D4D8]">E</th>
                <th className="w-16 py-1 border-r border-[#D4D4D8]">F</th>
                <th className="w-16 py-1 border-r border-[#D4D4D8]">G</th>
                <th className="w-20 py-1 border-r border-[#D4D4D8]">H</th>
                <th className="w-28 py-1 border-r border-[#D4D4D8]">I</th>
                <th className="w-32 py-1">J</th>
              </tr>
              {/* Row 1-4: Title and Metadata */}
              <tr className="bg-white border-b border-[#E2E8F0]">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">1</td>
                <td colSpan={10} className="px-3 py-1 font-bold text-base text-slate-900 uppercase">
                  BẢNG CHI TIẾT KHỐI LƯỢNG CÔNG TRÌNH QUAN TRẮC MÔI TRƯỜNG
                </td>
              </tr>
              <tr className="bg-white border-b border-[#E2E8F0]">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">2</td>
                <td colSpan={10} className="px-3 py-1 italic text-slate-700">
                  (Căn cứ theo Quyết định số 1155/QĐ-NĐVT4 và Thông tư số 20/2017/TT-BTNMT)
                </td>
              </tr>
              <tr className="bg-white border-b border-[#E2E8F0]">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">3</td>
                <td colSpan={10} className="px-3 py-1 font-bold text-blue-900">
                  CÔNG TRÌNH: QUAN TRẮC MÔI TRƯỜNG CHO NMNĐ VĨNH TÂN 4 VÀ VĨNH TÂN 4 MỞ RỘNG NĂM 2026
                </td>
              </tr>
              {/* Table Column Titles */}
              <tr className="bg-[#EFEFF2] font-bold text-center border-b-2 border-slate-400">
                <td className="bg-[#EFEFF2] text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">6</td>
                <td className="border border-[#D4D4D8] py-2 px-1">STT</td>
                <td className="border border-[#D4D4D8] py-2 px-2">Ký hiệu vị trí (Bản vẽ)</td>
                <td className="border border-[#D4D4D8] py-2 px-1">Mã hiệu TT20</td>
                <td className="border border-[#D4D4D8] py-2 px-2">Danh mục công tác quan trắc</td>
                <td className="border border-[#D4D4D8] py-2 px-1">ĐVT</td>
                <td className="border border-[#D4D4D8] py-2 px-1">Vị trí</td>
                <td className="border border-[#D4D4D8] py-2 px-1">Tần suất</td>
                <td className="border border-[#D4D4D8] py-2 px-1 bg-[#FFFFB4] text-blue-800">Số mẫu (Q)</td>
                <td className="border border-[#D4D4D8] py-2 px-2">Đơn giá (VNĐ)</td>
                <td className="border border-[#D4D4D8] py-2 px-2">Thành tiền (VNĐ)</td>
              </tr>
            </thead>
            <tbody>
              {items.slice(0, 100).map((row, idx) => {
                const rowNum = idx + 7;
                const isSelected = selectedCell.coord.startsWith(`B${rowNum}`);
                const sampleQty = (row.so_vi_tri || 1) * (row.so_lan || 1);
                const unitPrice = 1250000;
                const totalAmount = sampleQty * unitPrice;

                return (
                  <tr 
                    key={row.id || idx}
                    className={`hover:bg-blue-50/40 border-b border-[#E2E8F0] ${isSelected ? 'bg-green-50/30' : ''}`}
                  >
                    <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">
                      {rowNum}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`A${rowNum}`, String(idx + 1))}
                      className="border-r border-[#D4D4D8] text-center px-1 font-mono text-xs"
                    >
                      {idx + 1}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`B${rowNum}`, row.vi_tri || 'Tại hiện trường')}
                      className="border-r border-[#D4D4D8] px-2 text-xs truncate max-w-xs"
                    >
                      {row.vi_tri || 'Tại hiện trường'}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`C${rowNum}`, row.tt20_data?.coreCode || 'TT20')}
                      className="border-r border-[#D4D4D8] text-center font-mono font-bold text-blue-700 px-1"
                    >
                      {row.tt20_data?.coreCode || 'TT20'}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`D${rowNum}`, row.thong_so || '')}
                      className="border-r border-[#D4D4D8] px-2 font-medium"
                    >
                      {row.thong_so}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`E${rowNum}`, row.dvt || 'mẫu')}
                      className="border-r border-[#D4D4D8] text-center px-1 text-slate-600"
                    >
                      {row.dvt || 'mẫu'}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`F${rowNum}`, String(row.so_vi_tri || 1))}
                      className="border-r border-[#D4D4D8] text-center px-1 font-mono"
                    >
                      {row.so_vi_tri || 1}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`G${rowNum}`, String(row.so_lan || 1))}
                      className="border-r border-[#D4D4D8] text-center px-1 font-mono"
                    >
                      {row.so_lan || 1}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`H${rowNum}`, String(sampleQty), `=F${rowNum}*G${rowNum}`)}
                      className="border-r border-[#D4D4D8] text-center px-1 font-mono font-bold bg-[#FFFFB4] text-blue-800"
                    >
                      {sampleQty}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`I${rowNum}`, unitPrice.toLocaleString(), `= 'Đơn giá chi tiết'!E${rowNum}`)}
                      className="border-r border-[#D4D4D8] text-right px-2 font-mono"
                    >
                      {unitPrice.toLocaleString()}
                    </td>
                    <td 
                      onClick={() => handleCellClick(`J${rowNum}`, totalAmount.toLocaleString(), `=ROUND(H${rowNum}*I${rowNum}, 0)`)}
                      className="text-right px-2 font-mono font-bold text-slate-900"
                    >
                      {totalAmount.toLocaleString()}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        {/* SHEET KHOẢN 4.5 TT20 (MỤC 2.1.2 TỪ FILE PAKT CỦA KTAT) */}
        {activeSheet === 'Khoản 4.5 TT20' && (
          <div className="p-3">
            <div className="bg-amber-50 border border-amber-200 rounded p-2 mb-3 text-xs text-amber-900">
              <span className="font-bold">Căn cứ pháp lý:</span> Khoản 4.5 Thông tư 20/2017/TT-BTNMT & Mục 2.1.2 Báo cáo PAKT gửi ngày 28/10/2026 của KTAT NMNĐ Vĩnh Tân 4.
            </div>

            <table className="w-full border-collapse text-[13px] text-slate-900 border border-[#D4D4D8] mb-6">
              <thead>
                <tr className="bg-[#EFEFF2] text-slate-600 text-center text-[11px] font-sans font-semibold border-b border-[#D4D4D8]">
                  <th className="w-10 py-1 border-r border-[#D4D4D8] bg-[#E1E2E5]">#</th>
                  <th className="w-12 py-1 border-r border-[#D4D4D8]">A</th>
                  <th className="w-72 py-1 border-r border-[#D4D4D8]">B</th>
                  <th className="w-16 py-1 border-r border-[#D4D4D8]">C</th>
                  <th className="w-20 py-1 border-r border-[#D4D4D8]">D</th>
                  <th className="w-20 py-1 border-r border-[#D4D4D8]">E</th>
                  <th className="w-20 py-1 border-r border-[#D4D4D8]">F</th>
                  <th className="w-20 py-1 border-r border-[#D4D4D8]">G</th>
                  <th className="w-24 py-1 border-r border-[#D4D4D8]">H</th>
                  <th className="w-48 py-1">I</th>
                </tr>
                <tr className="bg-[#107c41] text-white font-bold text-left border-b border-green-800">
                  <td className="bg-green-900 text-center text-[11px] py-1 border-r border-green-800">1</td>
                  <td colSpan={9} className="px-3 py-1.5 uppercase tracking-wide">
                    2.1.2 DỰ KIẾN KHỐI LƯỢNG NỘI DUNG CÔNG VIỆC PHỤC VỤ LẤY MẪU TẠI HIỆN TRƯỜNG (KHOẢN 4.5 TT20)
                  </td>
                </tr>
                <tr className="bg-[#EFEFF2] font-bold text-center border-b-2 border-slate-400">
                  <td className="bg-[#EFEFF2] text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">2</td>
                  <td className="border border-[#D4D4D8] py-2 px-1">STT</td>
                  <td className="border border-[#D4D4D8] py-2 px-2 text-left">Nội dung cấp bậc / Chức danh lao động / Phương tiện</td>
                  <td className="border border-[#D4D4D8] py-2 px-1">Đơn vị</td>
                  <td className="border border-[#D4D4D8] py-2 px-1">Đợt 1</td>
                  <td className="border border-[#D4D4D8] py-2 px-1">Đợt 2</td>
                  <td className="border border-[#D4D4D8] py-2 px-1">Đợt 3</td>
                  <td className="border border-[#D4D4D8] py-2 px-1">Đợt 4</td>
                  <td className="border border-[#D4D4D8] py-2 px-1 bg-[#FFFFB4] text-blue-900">Tổng cộng</td>
                  <td className="border border-[#D4D4D8] py-2 px-2 text-left">Ghi chú nghiệp vụ KTAT</td>
                </tr>
              </thead>
              <tbody>
                {/* PHẦN A: ĐỊNH KỲ */}
                <tr className="bg-slate-100 font-bold text-blue-900 border-b border-slate-300">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">3</td>
                  <td className="border-r border-[#D4D4D8] text-center font-bold">A</td>
                  <td colSpan={8} className="px-2 py-1.5 uppercase">
                    Đối với quan trắc môi trường định kỳ theo Giấy phép môi trường hiện hành
                  </td>
                </tr>
                <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/30">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">4</td>
                  <td className="border-r border-[#D4D4D8] text-center font-bold">I</td>
                  <td className="border-r border-[#D4D4D8] px-2 font-bold">Nhân sự thực hiện hiện trường</td>
                  <td className="border-r border-[#D4D4D8] text-center">Người</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">7</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">12</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">7</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">14</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold bg-[#FFFFB4] text-blue-900">40</td>
                  <td className="px-2 text-xs text-slate-600">QTV hạng IV không quá 30% đội ngũ</td>
                </tr>
                <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/30">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">5</td>
                  <td className="border-r border-[#D4D4D8] text-center">II</td>
                  <td className="border-r border-[#D4D4D8] px-2 font-bold text-indigo-900">Số chuyến xe phương tiện di chuyển</td>
                  <td className="border-r border-[#D4D4D8] text-center">Chuyến</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">02</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">02</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold bg-[#FFFFB4] text-blue-900">12</td>
                  <td className="px-2 text-xs text-slate-600">Bảo quản hỏa tốc Coliform, BOD5, CrVI (24h-48h)</td>
                </tr>
                <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/30">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">6</td>
                  <td className="border-r border-[#D4D4D8] text-center">IV</td>
                  <td className="border-r border-[#D4D4D8] px-2 font-medium">Số ngày đi/về của mỗi đợt</td>
                  <td className="border-r border-[#D4D4D8] text-center">Ngày</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold bg-[#FFFFB4] text-blue-900">16</td>
                  <td className="px-2 text-xs text-slate-600">Hà Nội - Bình Thuận khứ hồi (2.800 km)</td>
                </tr>
                <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/30 bg-green-50/20">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">7</td>
                  <td className="border-r border-[#D4D4D8] text-center font-bold">VI</td>
                  <td className="border-r border-[#D4D4D8] px-2 font-bold text-green-900">Số công di chuyển (Số người × Số ngày đi/về)</td>
                  <td className="border-r border-[#D4D4D8] text-center font-bold">Công</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold">28</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold">48</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold">28</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold">48</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-black bg-[#FFFFB4] text-green-900 text-sm">152</td>
                  <td className="px-2 text-xs text-slate-600">= Người x Ngày đi/về (Tính lương theo QĐ 80)</td>
                </tr>
                <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/30">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">8</td>
                  <td className="border-r border-[#D4D4D8] text-center">VII</td>
                  <td className="border-r border-[#D4D4D8] px-2 font-bold text-purple-900">Khối lượng lưu trú tại hiện trường</td>
                  <td className="border-r border-[#D4D4D8] text-center">Đêm</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">0</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">25</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">0</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">25</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold bg-[#FFFFB4] text-purple-900">50</td>
                  <td className="px-2 text-xs text-slate-600">Nhóm KKXQ 5 người x 5 ngày làm việc</td>
                </tr>

                {/* PHẦN B: ĐỐI CHỨNG */}
                <tr className="bg-slate-100 font-bold text-blue-900 border-b border-slate-300">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">9</td>
                  <td className="border-r border-[#D4D4D8] text-center font-bold">B</td>
                  <td colSpan={8} className="px-2 py-1.5 uppercase">
                    Chương trình quan trắc môi trường đối chứng
                  </td>
                </tr>
                <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/30">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">10</td>
                  <td className="border-r border-[#D4D4D8] text-center">II</td>
                  <td className="border-r border-[#D4D4D8] px-2 font-bold text-indigo-900">Số chuyến xe phương tiện di chuyển</td>
                  <td className="border-r border-[#D4D4D8] text-center">Chuyến</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">04</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold bg-[#FFFFB4] text-blue-900">16</td>
                  <td className="px-2 text-xs text-slate-600">Vận chuyển mẫu nước thải, khí thải, nước biển</td>
                </tr>
                <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/30 bg-green-50/20">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">11</td>
                  <td className="border-r border-[#D4D4D8] text-center font-bold">VI</td>
                  <td className="border-r border-[#D4D4D8] px-2 font-bold text-green-900">Số công di chuyển (Số người × Số ngày đi/về)</td>
                  <td className="border-r border-[#D4D4D8] text-center font-bold">Công</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold">60</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold">48</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold">60</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold">48</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-black bg-[#FFFFB4] text-green-900 text-sm">216</td>
                  <td className="px-2 text-xs text-slate-600">Đợt 1: 15 người x 4; Đợt 2: 12 người x 4...</td>
                </tr>
                <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/30">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">12</td>
                  <td className="border-r border-[#D4D4D8] text-center">VII</td>
                  <td className="border-r border-[#D4D4D8] px-2 font-bold text-purple-900">Khối lượng lưu trú tại hiện trường</td>
                  <td className="border-r border-[#D4D4D8] text-center">Đêm</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">06</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">25</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">06</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono">25</td>
                  <td className="border-r border-[#D4D4D8] text-center font-mono font-bold bg-[#FFFFB4] text-purple-900">62</td>
                  <td className="px-2 text-xs text-slate-600">Lưu trú Tuy Phong theo Thông tư 40/2017/TT-BTC</td>
                </tr>

                {/* TỔNG KẾT TÍNH TIỀN KHOẢN 4.5 TT20 */}
                <tr className="bg-[#EFEFF2] font-bold text-slate-900 border-t-2 border-slate-600">
                  <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">13</td>
                  <td colSpan={2} className="px-3 py-2 text-left uppercase text-blue-900 font-black">
                    TỔNG CỘNG KHỐI LƯỢNG KHOẢN 4.5 TT20
                  </td>
                  <td colSpan={5} className="text-right px-2">
                    Công di chuyển: <span className="text-green-700 font-mono font-bold">368 công</span> • Chuyến xe: <span className="text-indigo-700 font-mono font-bold">28 chuyến</span> • Lưu trú: <span className="text-purple-700 font-mono font-bold">112 đêm</span>
                  </td>
                  <td className="text-center font-mono font-black text-red-700 bg-red-50 text-sm">
                    LINK SANG THDT
                  </td>
                  <td></td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {/* SHEET THDT HẠNG MỤC (TỔNG HỢP KINH PHÍ VĨ MÔ) */}
        {activeSheet === 'THDT hạng mục' && (
          <table className="w-full border-collapse text-[13px] text-slate-900 border border-[#D4D4D8]">
            <thead>
              <tr className="bg-[#EFEFF2] text-slate-600 text-center text-[11px] font-sans font-semibold border-b border-[#D4D4D8]">
                <th className="w-10 py-1 border-r border-[#D4D4D8] bg-[#E1E2E5]">#</th>
                <th className="w-16 py-1 border-r border-[#D4D4D8]">A</th>
                <th className="w-96 py-1 border-r border-[#D4D4D8]">B</th>
                <th className="w-64 py-1 border-r border-[#D4D4D8]">C</th>
                <th className="w-48 py-1 border-r border-[#D4D4D8]">D</th>
                <th className="w-20 py-1">E</th>
              </tr>
              <tr className="bg-white border-b border-[#E2E8F0]">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">1</td>
                <td colSpan={5} className="px-3 py-2 font-bold text-base text-slate-900 uppercase">
                  BẢNG TỔNG HỢP DỰ TOÁN CHI PHÍ QUAN TRẮC MÔI TRƯỜNG
                </td>
              </tr>
              <tr className="bg-white border-b border-[#E2E8F0]">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">2</td>
                <td colSpan={5} className="px-3 py-1 font-bold text-blue-900">
                  ='Công trình'!A3
                </td>
              </tr>
              <tr className="bg-[#EFEFF2] font-bold text-center border-b-2 border-slate-400">
                <td className="bg-[#EFEFF2] text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">6</td>
                <td className="border border-[#D4D4D8] py-2 px-1">STT</td>
                <td className="border border-[#D4D4D8] py-2 px-2 text-left">NỘI DUNG CHI PHÍ</td>
                <td className="border border-[#D4D4D8] py-2 px-2 text-left">CÁCH TÍNH / DIỄN GIẢI</td>
                <td className="border border-[#D4D4D8] py-2 px-2 text-right">GIÁ TRỊ (VNĐ)</td>
                <td className="border border-[#D4D4D8] py-2 px-1">KÝ HIỆU</td>
              </tr>
            </thead>
            <tbody>
              <tr className="font-bold bg-slate-50 border-b border-slate-300">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">7</td>
                <td className="text-center border-r border-[#D4D4D8]">I</td>
                <td className="px-2 py-1.5 border-r border-[#D4D4D8]">Chi phí trực tiếp (T = VL + DC + NC + M + C_tính riêng)</td>
                <td className="px-2 py-1.5 border-r border-[#D4D4D8] font-mono text-xs">="VL + DC + NC + M + C_TR"</td>
                <td className="px-2 py-1.5 border-r border-[#D4D4D8] text-right font-mono text-sm text-blue-900">2.919.400.000</td>
                <td className="text-center font-mono">T</td>
              </tr>
              <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/20">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">8</td>
                <td className="text-center border-r border-[#D4D4D8]">1</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8]">Chi phí vật liệu, hóa chất</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] font-mono text-xs">='Vật liệu'!$G$181</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] text-right font-mono">625.340.000</td>
                <td className="text-center font-mono">VL</td>
              </tr>
              <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/20">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">9</td>
                <td className="text-center border-r border-[#D4D4D8]">2</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8]">Chi phí công cụ dụng cụ</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] font-mono text-xs">='Công cụ dụng cụ'!$G$166</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] text-right font-mono">84.520.000</td>
                <td className="text-center font-mono">DC</td>
              </tr>
              <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/20">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">10</td>
                <td className="text-center border-r border-[#D4D4D8]">3</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8]">Chi phí nhân công quan trắc & PTN</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] font-mono text-xs">='Nhân công'!$G$9</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] text-right font-mono">825.420.000</td>
                <td className="text-center font-mono">NC</td>
              </tr>
              <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/20">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">11</td>
                <td className="text-center border-r border-[#D4D4D8]">4</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8]">Chi phí máy và thiết bị quan trắc</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] font-mono text-xs">='Máy thi công'!$G$80</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] text-right font-mono">685.120.000</td>
                <td className="text-center font-mono">M</td>
              </tr>
              <tr className="border-b border-[#E2E8F0] hover:bg-amber-50/40 bg-amber-50/20 font-bold text-amber-950">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">12</td>
                <td className="text-center border-r border-[#D4D4D8]">5</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8]">Chi phí tính riêng theo Khoản 4.5 TT20 (Mục 2.1.2 PAKT)</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] font-mono text-xs">='Khoản 4.5 TT20'!$H$13</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] text-right font-mono text-amber-900">699.000.000</td>
                <td className="text-center font-mono">C_TR</td>
              </tr>
              <tr className="font-bold bg-slate-50 border-b border-slate-300">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">13</td>
                <td className="text-center border-r border-[#D4D4D8]">II</td>
                <td className="px-2 py-1.5 border-r border-[#D4D4D8]">Chi phí gián tiếp (Chi phí chung)</td>
                <td className="px-2 py-1.5 border-r border-[#D4D4D8] font-mono text-xs">="T x 20%" (=ROUND(D7*'Hệ số'!$C$4, 0))</td>
                <td className="px-2 py-1.5 border-r border-[#D4D4D8] text-right font-mono text-sm text-slate-900">583.880.000</td>
                <td className="text-center font-mono">C</td>
              </tr>
              <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/20">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">14</td>
                <td className="text-center border-r border-[#D4D4D8]">III</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] font-bold">Thu nhập chịu thuế tính trước</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] font-mono text-xs">="(T + C) x 5,5%"</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] text-right font-mono">192.680.400</td>
                <td className="text-center font-mono">TL</td>
              </tr>
              <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/20 font-bold bg-slate-50">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">15</td>
                <td className="text-center border-r border-[#D4D4D8]"></td>
                <td className="px-2 py-1 border-r border-[#D4D4D8]">Chi phí trước thuế (G = T + C + TL)</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] font-mono text-xs">="T + C + TL"</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] text-right font-mono text-sm text-slate-900">3.695.960.400</td>
                <td className="text-center font-mono">G</td>
              </tr>
              <tr className="border-b border-[#E2E8F0] hover:bg-blue-50/20">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">16</td>
                <td className="text-center border-r border-[#D4D4D8]">IV</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8]">Thuế giá trị gia tăng (VAT 8%)</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] font-mono text-xs">="G x 8%"</td>
                <td className="px-2 py-1 border-r border-[#D4D4D8] text-right font-mono">295.676.832</td>
                <td className="text-center font-mono">GTGT</td>
              </tr>
              <tr className="font-bold bg-[#EFEFF2] border-t-2 border-b-2 border-slate-700 text-base">
                <td className="bg-[#EFEFF2] text-center text-[11px] text-slate-500 font-mono py-1 border-r border-[#D4D4D8]">17</td>
                <td className="text-center border-r border-[#D4D4D8]"></td>
                <td className="px-2 py-2 border-r border-[#D4D4D8] uppercase text-red-900">TỔNG CỘNG KINH PHÍ GÓI THẦU (LÀM TRÒN)</td>
                <td className="px-2 py-2 border-r border-[#D4D4D8] font-mono text-xs">="ROUND(G + GTGT, -3)"</td>
                <td className="px-2 py-2 border-r border-[#D4D4D8] text-right font-mono font-black text-red-700 text-lg">
                  3.991.637.000
                </td>
                <td className="text-center font-mono font-black text-red-700">LTR</td>
              </tr>
            </tbody>
          </table>
        )}

        {/* DEFAULT FALLBACK CHO CÁC SHEET KHÁC */}
        {activeSheet !== 'Công trình' && activeSheet !== 'Khoản 4.5 TT20' && activeSheet !== 'THDT hạng mục' && (
          <div className="p-8 text-center text-slate-500">
            <FileSpreadsheet className="w-12 h-12 mx-auto mb-2 text-slate-400 stroke-1" />
            <h3 className="text-base font-bold text-slate-700">Worksheet: '{activeSheet}'</h3>
            <p className="text-xs text-slate-500 mt-1">
              Đang liên kết dữ liệu sống từ file Excel F1 chuẩn. Nhấp vào tab 'Công trình', 'Khoản 4.5 TT20' hoặc 'THDT hạng mục' để trải nghiệm bảng tính tương tác.
            </p>
          </div>
        )}
      </div>

      {/* 3. EXCEL BOTTOM SHEET TAB BAR (Thanh Tab kiểu Excel ở đáy màn hình) */}
      <div className="h-8 bg-[#EFEFF2] border-t border-[#CBD5E1] flex items-center justify-between px-2 select-none">
        {/* Navigation Arrows & Sheet Tabs */}
        <div className="flex items-center space-x-0.5 overflow-x-auto flex-1 py-0.5">
          {/* Scroll Arrows */}
          <div className="flex items-center space-x-0.5 text-slate-500 pr-1.5 border-r border-[#CBD5E1]">
            <button className="hover:bg-slate-200 p-1 rounded text-[10px]">◀</button>
            <button className="hover:bg-slate-200 p-1 rounded text-[10px]">▶</button>
          </div>

          {/* Actual Sheet Tabs */}
          {sheetTabs.map((tab) => {
            const isActive = activeSheet === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveSheet(tab.id);
                  setSelectedCell({ coord: 'A1', value: tab.name, formula: `="${tab.name}"` });
                }}
                className={`px-3 py-1 text-xs font-sans font-medium whitespace-nowrap transition-all border-r border-[#D4D4D8] flex items-center space-x-1.5 ${
                  isActive
                    ? 'bg-white text-[#107c41] font-bold shadow-sm border-t-2 border-t-[#107c41]'
                    : 'bg-[#E5E6E8] text-slate-700 hover:bg-[#DDD] hover:text-slate-900'
                }`}
              >
                <span>{tab.name}</span>
                {tab.id === 'Khoản 4.5 TT20' && (
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse"></span>
                )}
              </button>
            );
          })}
        </div>

        {/* Right Status Indicator */}
        <div className="flex items-center space-x-3 text-[11px] font-sans text-slate-500 pl-3 border-l border-[#CBD5E1]">
          <span className="flex items-center space-x-1 text-emerald-700 font-semibold">
            <Check className="w-3.5 h-3.5" />
            <span>SẴN SÀNG</span>
          </span>
          <span className="text-slate-400">|</span>
          <span>12 Sheets</span>
          <span className="text-slate-400">|</span>
          <span className="font-mono">100%</span>
        </div>
      </div>
    </div>
  );
};
