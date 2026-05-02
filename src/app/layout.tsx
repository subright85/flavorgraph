import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FlavorGraph",
  description: "Discover ingredient pairings through flavor chemistry",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
