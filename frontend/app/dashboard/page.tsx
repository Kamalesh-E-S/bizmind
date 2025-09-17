"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { MapPin, Search, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import DashboardLayout from "@/components/dashboard-layout"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function Dashboard() {
  const router = useRouter()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [strategies, setStrategies] = useState<any[]>([])
  const [location, setLocation] = useState("")
  const [businessType, setBusinessType] = useState("")

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
      return
    }

    // Fetch user's strategies
    fetchStrategies()
  }, [router])

  const fetchStrategies = async () => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("http://localhost:5000/strategies", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch strategies")
      }

      const data = await response.json()
      setStrategies(data.strategies || [])
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch strategies",
        variant: "destructive",
      })
    }
  }

  const handleGenerateStrategy = async () => {
    if (!location || !businessType) {
      toast({
        title: "Missing information",
        description: "Please provide both location and business type",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)

    try {
      const token = localStorage.getItem("token")
      const response = await fetch("http://localhost:5000/generate-strategy", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          location,
          business_type: businessType,
        }),
      })

      if (!response.ok) {
        throw new Error("Failed to generate strategy")
      }

      await response.json()

      toast({
        title: "Strategy generated",
        description: "Your business strategy has been generated successfully",
      })

      // Refresh strategies
      fetchStrategies()

      // Clear form
      setLocation("")
      setBusinessType("")
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate strategy",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const businessTypes = [
    "Restaurant",
    "Cafe",
    "Retail Store",
    "Grocery Store",
    "Bakery",
    "Gym",
    "Salon",
    "Bookstore",
    "Pharmacy",
    "Clothing Store",
    "Electronics Store",
    "Hardware Store",
    "Pet Shop",
    "Flower Shop",
    "Jewelry Store",
    "Toy Store",
    "Furniture Store",
    "Art Gallery",
  ]

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-gray-500">Generate business strategies and analyze market data</p>
        </div>

        {/* Strategy Generator */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Generate Business Strategy</CardTitle>
            <CardDescription>
              Enter a location and business type to get AI-powered business recommendations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <label htmlFor="location" className="text-sm font-medium">
                  Location
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
                  <Input
                    id="location"
                    placeholder="City, State or Lat,Lng"
                    className="pl-10"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="business-type" className="text-sm font-medium">
                  Business Type
                </label>
                <Select value={businessType} onValueChange={setBusinessType}>
                  <SelectTrigger id="business-type">
                    <SelectValue placeholder="Select business type" />
                  </SelectTrigger>
                  <SelectContent>
                    {businessTypes.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-end">
                <Button
                  className="w-full bg-emerald-600 hover:bg-emerald-700"
                  onClick={handleGenerateStrategy}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-4 w-4" />
                      Generate Strategy
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Strategies */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Recent Strategies</h2>

          {strategies.length === 0 ? (
            <Card>
              <CardContent className="p-6 text-center text-gray-500">
                <p>You haven&apos;t generated any strategies yet.</p>
                <p className="text-sm mt-1">Use the form above to create your first business strategy.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {strategies.slice(0, 6).map((strategy) => (
                <Card key={strategy.id} className="overflow-hidden">
                  <CardHeader className="bg-emerald-50 border-b pb-3">
                    <CardTitle className="text-lg">{strategy.business_type}</CardTitle>
                    <CardDescription className="truncate">{strategy.location_name}</CardDescription>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="h-32 overflow-hidden text-sm text-gray-600">
                      {strategy.strategy.substring(0, 200)}...
                    </div>
                    <Button
                      variant="link"
                      className="p-0 h-auto text-emerald-600 mt-2"
                      onClick={() => router.push(`/dashboard/strategy/${strategy.id}`)}
                    >
                      View full strategy
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {strategies.length > 6 && (
            <div className="text-center mt-6">
              <Button variant="outline" onClick={() => router.push("/dashboard/strategies")}>
                View all strategies
              </Button>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
