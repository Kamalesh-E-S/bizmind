"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { MapPin, Search, Loader2, Star, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import DashboardLayout from "@/components/dashboard-layout"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronDown, ChevronUp } from "lucide-react"

export default function CompetitorsPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [location, setLocation] = useState("")
  const [category, setCategory] = useState("")
  const [competitorData, setCompetitorData] = useState<any>(null)
  const [topExpanded, setTopExpanded] = useState<{ [key: number]: boolean }>({});
  const [leastExpanded, setLeastExpanded] = useState<{ [key: number]: boolean }>({});

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
    }
  }, [router])

  const handleAnalyzeCompetitors = async () => {
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
        `http://localhost:5000/competitor-insights?location=${encodeURIComponent(location)}&category=${encodeURIComponent(category)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        },
      )

      if (!response.ok) {
        throw new Error("Failed to analyze competitors")
      }

      const data = await response.json()
      setCompetitorData(data)

      toast({
        title: "Competitor analysis complete",
        description: `Found ${data.total} competitors in the area`,
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to analyze competitors",
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
          <h1 className="text-3xl font-bold mb-2">Competitor Analysis</h1>
          <p className="text-gray-500">Analyze competitors in your target area</p>
        </div>

        {/* Competitor Analysis Form */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Analyze Competitors</CardTitle>
            <CardDescription>Enter a location and business category to analyze competitors</CardDescription>
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
                  onClick={handleAnalyzeCompetitors}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-4 w-4" />
                      Analyze Competitors
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Competitor Analysis Results */}
        {competitorData && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">
              Competitor Analysis for {category} in {location}
            </h2>

            <div className="grid gap-6 md:grid-cols-3 mb-8">
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <Users className="h-8 w-8 text-emerald-600 mx-auto mb-2" />
                    <h3 className="text-lg font-medium mb-1">Total Competitors</h3>
                    <p className="text-3xl font-bold">{competitorData.total}</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <Star className="h-8 w-8 text-emerald-600 mx-auto mb-2" />
                    <h3 className="text-lg font-medium mb-1">Average Rating</h3>
                    <p className="text-3xl font-bold">
                      {competitorData.avg_rating} <span className="text-lg text-gray-500">/5</span>
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <Users className="h-8 w-8 text-emerald-600 mx-auto mb-2" />
                    <h3 className="text-lg font-medium mb-1">Average Reviews</h3>
                    <p className="text-3xl font-bold">{Math.round(competitorData.avg_reviews)}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
 <Card>
    <CardHeader>
      <CardTitle>Competitor Details</CardTitle>
      <CardDescription>Detailed information about competitors in the area</CardDescription>
    </CardHeader>
    <CardContent>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-50 text-left">
              <th className="p-3 border-b">Name</th>
              <th className="p-3 border-b">Rating</th>
              <th className="p-3 border-b">Reviews</th>
              <th className="p-3 border-b">Address</th>
              <th className="p-3 border-b">Reviews Details</th>
            </tr>
          </thead>
          <tbody>
            {competitorData.details.map((competitor: any, index: number) => (
              <tr key={index} className="border-b hover:bg-gray-50 align-top">
                <td className="p-3 font-medium">{competitor.name}</td>
                <td className="p-3">
                  <div className="flex items-center">
                    {competitor.rating || "N/A"}
                    {competitor.rating && <Star className="h-4 w-4 text-yellow-500 ml-1" />}
                  </div>
                </td>
                <td className="p-3">{competitor.user_ratings_total || 0}</td>
                <td className="p-3 text-gray-600">{competitor.vicinity}</td>
                <td className="p-3 min-w-[350px]">
                  <div className="flex flex-col gap-4">
                    {/* Top Reviews */}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-green-700">Top Reviews</span>
                        <button
                          className="p-1 rounded hover:bg-green-100 transition"
                          onClick={() =>
                            setTopExpanded((prev) => ({
                              ...prev,
                              [index]: !prev[index],
                            }))
                          }
                          aria-label={topExpanded[index] ? "Collapse" : "Expand"}
                        >
                          {topExpanded[index] ? (
                            <ChevronUp className="h-4 w-4 text-green-700" />
                          ) : (
                            <ChevronDown className="h-4 w-4 text-green-700" />
                          )}
                        </button>
                      </div>
                      <ul className="mt-1 space-y-2">
                        {(competitor.top_reviews && competitor.top_reviews.length > 0) ? (
                          (topExpanded[index]
                            ? competitor.top_reviews
                            : competitor.top_reviews.slice(0, 1)
                          ).map((review: any, i: number) => (
                            <li key={i} className="bg-green-50 rounded p-2 shadow-sm">
                              <div className="flex items-center gap-2">
                                <span className="font-medium">{review.author}</span>
                                <span className="text-yellow-600 flex items-center text-sm">
                                  <Star className="h-3 w-3 mr-0.5" /> {review.rating}
                                </span>
                                <span className="text-xs text-gray-400 ml-auto">
                                  {review.time ? new Date(review.time * 1000).toLocaleDateString() : ""}
                                </span>
                              </div>
                              <div className="text-gray-700 text-sm mt-1">{review.text}</div>
                            </li>
                          ))
                        ) : (
                          <li className="text-gray-400 text-sm">No top reviews</li>
                        )}
                      </ul>
                    </div>
                    {/* Least Reviews */}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-red-700">Least Reviews</span>
                        <button
                          className="p-1 rounded hover:bg-red-100 transition"
                          onClick={() =>
                            setLeastExpanded((prev) => ({
                              ...prev,
                              [index]: !prev[index],
                            }))
                          }
                          aria-label={leastExpanded[index] ? "Collapse" : "Expand"}
                        >
                          {leastExpanded[index] ? (
                            <ChevronUp className="h-4 w-4 text-red-700" />
                          ) : (
                            <ChevronDown className="h-4 w-4 text-red-700" />
                          )}
                        </button>
                      </div>
                      <ul className="mt-1 space-y-2">
                        {(competitor.least_reviews && competitor.least_reviews.length > 0) ? (
                          (leastExpanded[index]
                            ? competitor.least_reviews
                            : competitor.least_reviews.slice(0, 1)
                          ).map((review: any, i: number) => (
                            <li key={i} className="bg-red-50 rounded p-2 shadow-sm">
                              <div className="flex items-center gap-2">
                                <span className="font-medium">{review.author}</span>
                                <span className="text-yellow-600 flex items-center text-sm">
                                  <Star className="h-3 w-3 mr-0.5" /> {review.rating}
                                </span>
                                <span className="text-xs text-gray-400 ml-auto">
                                  {review.time ? new Date(review.time * 1000).toLocaleDateString() : ""}
                                </span>
                              </div>
                              <div className="text-gray-700 text-sm mt-1">{review.text}</div>
                            </li>
                          ))
                        ) : (
                          <li className="text-gray-400 text-sm">No least reviews</li>
                        )}
                      </ul>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </CardContent>
  </Card>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
