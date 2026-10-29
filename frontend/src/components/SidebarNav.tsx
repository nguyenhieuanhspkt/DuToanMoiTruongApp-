import React from 'react';
import { 
  FileSpreadsheet, Users, Layers, Wrench, Cpu, 
  Coins, ShoppingCart, Activity, Percent, PieChart,
  ChevronLeft, ChevronRight
} from 'lucide-react';

interface SidebarNavProps {
  activeTab: number;
  onTabChange: (tabIndex: number) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const SidebarNav: React.FC<SidebarNavProps> = ({
  activeTab,
  onTabChange,
  isCollapsed,
  onToggleCollapse
}) => {
  const normTabs = [
    { id: 1, label: 'Khối lượng', icon: FileSpreadsheet, badge: '253 dòng' },
    { id: 2, label: 'Nhân công', icon: Users, badge: '+20% TT' },
    { id: 3, label: 'Vật liệu', icon: Layers, badge: '+8% TT' },
    { id: 4, label: 'Dụng cụ', icon: Wrench, badge: '+10% TT' },
    { id: 5, label: 'Thiết bị', icon: Cpu, badge: '250/500 ca' },
  ];

  const pricingTabs = [
    { id: 6, label: 'ĐG Nhân công', icon: Coins, badge: 'Lương TT56' },
    { id: 7, label: 'ĐG Vật liệu', icon: ShoppingCart, badge: '173 loại' },
    { id: 8, label: 'ĐG Dụng cụ, Thiết bị', icon: Activity, badge: '158 DC + 72 TB' },
    { id: 9, label: 'Chi phí gián tiếp', icon: Percent, badge: '+38,23%' },
    { id: 10, label: 'Tổng hợp kinh phí', icon: PieChart, badge: '3 PAKT' },
  ];

  return (
    <aside
      className={`h-[calc(100vh-3.5rem-3rem)] bg-slate-900 border-r border-slate-800 flex flex-col justify-between transition-all duration-300 z-20 ${
        isCollapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
        {/* Group 1: Bóc tách Kỹ thuật Định mức */}
        <div>
          {!isCollapsed && (
            <div className="px-2.5 mb-1.5 flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <span>Định mức Kỹ thuật</span>
              <span className="text-[9px] bg-blue-900/40 text-blue-300 px-1.5 py-0.2 rounded border border-blue-700/30">
                1 - 5
              </span>
            </div>
          )}
          <nav className="space-y-1">
            {normTabs.map((t) => {
              const Icon = t.icon;
              const isActive = activeTab === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => onTabChange(t.id)}
                  title={isCollapsed ? t.label : undefined}
                  className={`w-full flex items-center ${
                    isCollapsed ? 'justify-center px-0' : 'justify-between px-3'
                  } py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    {!isCollapsed && <span className="truncate">{t.id}. {t.label}</span>}
                  </div>
                  {!isCollapsed && (
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-normal ${
                        isActive
                          ? 'bg-blue-700 text-blue-100'
                          : 'bg-slate-800 text-slate-400 border border-slate-700/60'
                      }`}
                    >
                      {t.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Group 2: Đơn giá & Tổng hợp Kinh phí */}
        <div>
          {!isCollapsed && (
            <div className="px-2.5 mb-1.5 flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <span>Đơn giá & Kinh phí</span>
              <span className="text-[9px] bg-emerald-900/40 text-emerald-300 px-1.5 py-0.2 rounded border border-emerald-700/30">
                6 - 10
              </span>
            </div>
          )}
          <nav className="space-y-1">
            {pricingTabs.map((t) => {
              const Icon = t.icon;
              const isActive = activeTab === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => onTabChange(t.id)}
                  title={isCollapsed ? t.label : undefined}
                  className={`w-full flex items-center ${
                    isCollapsed ? 'justify-center px-0' : 'justify-between px-3'
                  } py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                    {!isCollapsed && <span className="truncate">{t.id}. {t.label}</span>}
                  </div>
                  {!isCollapsed && (
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-normal ${
                        isActive
                          ? 'bg-emerald-700 text-emerald-100'
                          : 'bg-slate-800 text-slate-400 border border-slate-700/60'
                      }`}
                    >
                      {t.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Collapse Toggle Footer */}
      <div className="p-2 border-t border-slate-800 flex items-center justify-center bg-slate-950/40">
        <button
          onClick={onToggleCollapse}
          className="w-full flex items-center justify-center py-1.5 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition"
          title={isCollapsed ? 'Mở rộng Sidebar' : 'Thu gọn Sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          {!isCollapsed && <span className="ml-1.5 text-[11px] font-medium">Thu gọn thanh điều hướng</span>}
        </button>
      </div>
    </aside>
  );
};
