"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { MapPin, Search, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import DashboardLayout from "@/components/dashboard-layout"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

// This would normally be loaded from a proper Maps library
// For this demo, we'll create a simplified version
const HeatmapVisualizer = ({ coordinates, center }: { coordinates: any[]; center: any }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    if (!canvasRef.current || !coordinates.length) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Set canvas dimensions
    canvas.width = 600
    canvas.height = 400

    // Calculate bounds
    const lats = coordinates.map((c) => c.lat)
    const lngs = coordinates.map((c) => c.lng)
    const minLat = Math.min(...lats)
    const maxLat = Math.max(...lats)
    const minLng = Math.min(...lngs)
    const maxLng = Math.max(...lngs)

    // Add padding
    const latPadding = (maxLat - minLat) * 0.1
    const lngPadding = (maxLng - minLng) * 0.1

    // Draw center point
    const centerX = ((center.lng - minLng) / (maxLng - minLng + 2 * lngPadding)) * canvas.width
    const centerY = ((maxLat - center.lat) / (maxLat - minLat + 2 * latPadding)) * canvas.height

    ctx.fillStyle = "blue"
    ctx.beginPath()
    ctx.arc(centerX, centerY, 8, 0, 2 * Math.PI)
    ctx.fill()
    ctx.fillStyle = "white"
    ctx.font = "10px Arial"
    ctx.textAlign = "center"
    ctx.fillText("You", centerX, centerY + 4)

    // Draw heatmap points
    coordinates.forEach((coord) => {
      const x = ((coord.lng - minLng) / (maxLng - minLng + 2 * lngPadding)) * canvas.width
      const y = ((maxLat - coord.lat) / (maxLat - minLat + 2 * latPadding)) * canvas.height

      ctx.fillStyle = "rgba(255, 0, 0, 0.5)"
      ctx.beginPath()
      ctx.arc(x, y, 10, 0, 2 * Math.PI)
      ctx.fill()
    })

    // Draw legend
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)"
    ctx.fillRect(10, 10, 150, 60)

    ctx.fillStyle = "white"
    ctx.font = "12px Arial"
    ctx.textAlign = "left"
    ctx.fillText("Legend:", 20, 30)

    ctx.fillStyle = "blue"
    ctx.beginPath()
    ctx.arc(30, 50, 6, 0, 2 * Math.PI)
    ctx.fill()

    ctx.fillStyle = "white"
    ctx.fillText("Your location", 45, 55)

    ctx.fillStyle = "rgba(255, 0, 0, 0.5)"
    ctx.beginPath()
    ctx.arc(30, 75, 6, 0, 2 * Math.PI)
    ctx.fill()

    ctx.fillStyle = "white"
    ctx.fillText("Competitor", 45, 80)
  }, [coordinates, center])

  return (
    <div className="border rounded-md overflow-hidden bg-white">
      <canvas ref={canvasRef} width={600} height={400} className="w-full h-auto" />
    </div>
  )
}

export default function HeatmapPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [location, setLocation] = useState("")
  const [category, setCategory] = useState("")
  const [heatmapData, setHeatmapData] = useState<any>(null)

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
    }
  }, [router])

  const handleGenerateHeatmap = async () => {
    if (!location || !category) {
      toast({
        title: "Missing information",
        description: "Please provide both location and business category",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)

    try {
      const token = localStorage.getItem("token")
      const response = await fetch(
        `http://localhost:5000/heatmap?location=${encodeURIComponent(location)}&category=${encodeURIComponent(category)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      if (!response.ok) {
        throw new Error("Failed to generate heatmap")
      }

      const data = await response.json()
      setHeatmapData(data)

      toast({
        title: "Heatmap generated",
        description: `Found ${data.count} locations for ${category} in the area`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate heatmap",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const businessCategories = [
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
          <h1 className="text-3xl font-bold mb-2">Business Heatmap</h1>
          <p className="text-gray-500">Visualize competitor density in your target area</p>
        </div>

        {/* Heatmap Generator */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Generate Heatmap</CardTitle>
            <CardDescription>Enter a location and business category to visualize competitor density</CardDescription>
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
                <label htmlFor="category" className="text-sm font-medium">
                  Business Category
                </label>
                <Select value={category} onValueChange={setCategory}>
                  <SelectTrigger id="category">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {businessCategories.map((type) => (
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
                  onClick={handleGenerateHeatmap}
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
                      Generate Heatmap
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Heatmap Visualization */}
        {heatmapData && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">
              Heatmap for {category} in {location}
            </h2>

            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <HeatmapVisualizer coordinates={heatmapData.coordinates} center={heatmapData.center} />
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Heatmap Analysis</CardTitle>
                  <CardDescription>Insights based on competitor density</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-medium mb-1">Competitor Count</h3>
                      <p className="text-3xl font-bold text-emerald-600">{heatmapData.count}</p>
                      <p className="text-sm text-gray-500">businesses found in this area</p>
                    </div>

                    <div>
                      <h3 className="font-medium mb-1">Density Analysis</h3>
                      <p className="text-gray-700">
                        {heatmapData.count > 10
                          ? "High competition in this area. Consider differentiation strategies."
                          : heatmapData.count > 5
                            ? "Moderate competition. Good balance of demand and supply."
                            : "Low competition. Potential opportunity or low demand area."}
                      </p>
                    </div>

                    <div>
                      <h3 className="font-medium mb-1">Next Steps</h3>
                      <ul className="list-disc pl-5 text-gray-700 space-y-1">
                        <li>Generate a business strategy for this location</li>
                        <li>Analyze competitor insights for more details</li>
                        <li>Check landmark data for foot traffic potential</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
