import { IoBarChartOutline } from "react-icons/io5";

export default function TopNav() {
  return (
    <header
      className="h-12 shrink-0 flex items-center px-5 select-none"
      style={{
        background: "var(--bg-sidebar)",
        borderBottom: "1px solid var(--border-subtle)",
      }}
    >
      <div className="flex items-center gap-2.5">
        <div
          className="w-7 h-7 rounded-md flex items-center justify-center"
          style={{ background: "var(--bg-icon)" }}
        >
          <IoBarChartOutline style={{ color: "var(--text-secondary)" }} size={15} />
        </div>
        <span
          className="font-medium text-sm tracking-tight"
          style={{ color: "var(--text-primary)" }}
        >
          股票AI助手
        </span>
      </div>
    </header>
  );
}
