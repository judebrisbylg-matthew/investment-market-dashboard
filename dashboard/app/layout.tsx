import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "每日综合大看板 2.0｜投资研究中心",
  description: "以数据质量、风险闸门、行业排序、跨市场验证、事件复核与持仓映射为主线的量化投资研究看板。",
  icons: { icon: "/investment-market-dashboard/favicon.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body>{children}</body></html>;
}
