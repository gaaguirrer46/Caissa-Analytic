import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Suspense } from "react";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Caissa Analytic — Plataforma de Rendimiento Ajedrecístico",
  description: "Sistema analítico integral para atletas y entrenadores de ajedrez.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-100">
        <Suspense fallback={<div className="h-16 border-b border-slate-800 bg-slate-950" />}>
          <Navbar />
        </Suspense>
        <Suspense fallback={<div className="p-8 text-center text-slate-500">Cargando...</div>}>
          {children}
        </Suspense>
      </body>
    </html>
  );
}
