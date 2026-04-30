import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import Link from "next/link";
import { Activity, Beaker, LayoutDashboard } from "lucide-react";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Linq Autopilot QA",
  description: "Scenario-driven integration testing framework",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col`}
      >
        <header className="glass sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-primary" />
            <span className="font-bold text-xl tracking-tight">Linq Autopilot</span>
          </div>
          <nav className="flex items-center gap-6 text-sm font-medium text-muted-foreground">
            <Link href="/" className="hover:text-foreground transition-colors flex items-center gap-2">
              <LayoutDashboard className="h-4 w-4" /> Runs
            </Link>
            <Link href="/scenarios" className="hover:text-foreground transition-colors flex items-center gap-2">
              <Beaker className="h-4 w-4" /> Scenarios
            </Link>
          </nav>
        </header>
        <main className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-10">
          {children}
        </main>
      </body>
    </html>
  );
}
