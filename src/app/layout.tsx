import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-jakarta",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Pairfect — Ingredients that taste great together, and why",
  description: "Pick any two ingredients to discover their flavor pairing score, the aromatic compounds they share, and the science behind why they work. Free, easy to use, no cooking experience needed.",
  applicationName: "Pairfect",
  authors: [{ name: "Astrolabe" }],
  keywords: ["food pairing", "flavor pairing", "ingredient pairing", "cooking", "recipes", "flavor chemistry", "what goes with"],
  openGraph: {
    title: "Pairfect — Ingredients that taste great together",
    description: "Pick any two ingredients to discover the flavor pairing score and the science behind why they work.",
    type: "website",
    siteName: "Pairfect",
  },
  twitter: {
    card: "summary_large_image",
    title: "Pairfect — Ingredients that taste great together",
    description: "Discover surprising flavor pairings, backed by science.",
  },
  icons: {
    icon: [
      { url: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E🍴%3C/text%3E%3C/svg%3E", type: "image/svg+xml" },
    ],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={jakarta.variable}>
      <body>{children}</body>
    </html>
  );
}
