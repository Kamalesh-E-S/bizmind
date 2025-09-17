"use client"

import type React from "react"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { BarChart3, LayoutDashboard, Map, Users, FileText, Settings, LogOut, Menu, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useToast } from "@/hooks/use-toast"
import { useMobile } from "@/hooks/use-mobile"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const pathname = usePathname()
  const router = useRouter()
  const { toast } = useToast()
  const isMobile = useMobile()
  const [menuOpen, setMenuOpen] = useState(false)
  const [username, setUsername] = useState("")
  const [businessName, setBusinessName] = useState("")

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
      return
    }

    // Get user info from localStorage
    const storedUsername = localStorage.getItem("username")
    const storedBusinessName = localStorage.getItem("business_name")

    if (storedUsername) {
      setUsername(storedUsername)
    }

    if (storedBusinessName) {
      setBusinessName(storedBusinessName)
    }
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem("token")
    localStorage.removeItem("user_id")
    localStorage.removeItem("username")
    localStorage.removeItem("business_name")

    toast({
      title: "Logged out",
      description: "You have been successfully logged out.",
    })

    router.push("/login")
  }

  const navItems = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/dashboard/heatmap", label: "Heatmap", icon: Map },
    { href: "/dashboard/competitors", label: "Competitors", icon: Users },
    { href: "/dashboard/reports", label: "Reports", icon: FileText },
    { href: "/dashboard/settings", label: "Settings", icon: Settings },
  ]

  const toggleMenu = () => {
    setMenuOpen(!menuOpen)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Mobile Header */}
      <div className="md:hidden bg-white border-b p-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-6 w-6 text-emerald-600" />
          <span className="font-bold">MarketSense</span>
        </div>
        <Button variant="ghost" size="icon" onClick={toggleMenu}>
          {menuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </Button>
      </div>

      {/* Sidebar */}
      <aside
        className={`
          ${menuOpen || !isMobile ? "block" : "hidden"} 
          ${isMobile ? "absolute inset-0 z-50 bg-white" : "w-64 border-r"} 
          md:block
        `}
      >
        <div className="p-6">
          <div className="flex items-center gap-2 mb-6">
            <BarChart3 className="h-6 w-6 text-emerald-600" />
            <span className="font-bold">MarketSense</span>
          </div>

          {/* User info */}
          <div className="mb-6 pb-6 border-b">
            <p className="font-medium">{username}</p>
            {businessName && <p className="text-sm text-gray-500">{businessName}</p>}
          </div>

          {/* Navigation */}
          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              const Icon = item.icon

              return (
                <Link key={item.href} href={item.href} onClick={() => isMobile && setMenuOpen(false)}>
                  <div
                    className={`
                      flex items-center gap-3 px-3 py-2 rounded-md text-sm
                      ${isActive ? "bg-emerald-50 text-emerald-600 font-medium" : "text-gray-700 hover:bg-gray-100"}
                    `}
                  >
                    <Icon className="h-5 w-5" />
                    {item.label}
                  </div>
                </Link>
              )
            })}
          </nav>

          {/* Logout button */}
          <div style={{ width: "200px" }} className="mt-auto pt-6 border-t absolute bottom-6 left-6 right-6">
            <Button
              variant="outline"
              className="w-full justify-start text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
              onClick={handleLogout}
            >
              <LogOut className="mr-2 h-4 w-4" style={{ width: "10px" }}/>
              Log out
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  )
}
