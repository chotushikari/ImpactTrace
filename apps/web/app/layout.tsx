import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ImpactTrace",
  description: "Evidence intelligence for impact and sustainability media.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
