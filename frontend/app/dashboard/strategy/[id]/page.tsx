"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { ArrowLeft, MapPin, Building, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import DashboardLayout from "@/components/dashboard-layout"
import markdownToHtml from "@/app/dashboard/strategy/[id]/markdown" // Adjust path as needed

export default function StrategyDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(true)
  const [strategy, setStrategy] = useState<any>(null)
  const [strategyHtml, setStrategyHtml] = useState<string>("")
  const strategyId = params.id

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
      return
    }

    fetchFormattedStrategy()
  }, [router, strategyId])

  const fetchFormattedStrategy = async () => {
    if (!strategyId) return

    setIsLoading(true)
    try {
      const token = localStorage.getItem("token")
      const response = await fetch(`http://localhost:5000/strategies/${strategyId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch strategy")
      }

      const data = await response.json()
      setStrategy(data)

      const html = await markdownToHtml(data.strategy)
      setStrategyHtml(html)
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch strategy",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <Button variant="ghost" className="mb-6" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>

        {isLoading ? (
          <div className="flex justify-center items-center p-12">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
          </div>
        ) : strategy ? (
          <>
            <div className="mb-8">
              <h1 className="text-3xl font-bold mb-2">{strategy.business_type} Strategy</h1>
              <div className="flex items-center text-gray-500">
                <MapPin className="h-4 w-4 mr-1" />
                {strategy.location_name}
                <span className="mx-2">•</span>
                Created on {formatDate(strategy.created_at)}
              </div>
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              <div className="md:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Business Strategy</CardTitle>
                    <CardDescription>
                      AI-generated strategy for your {strategy.business_type} in {strategy.location_name}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div
                      className="prose max-w-none"
                      dangerouslySetInnerHTML={{ __html: strategyHtml }}
                    />
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Business Information</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Business Type</h3>
                        <div className="flex items-center mt-1">
                          <Building className="h-4 w-4 mr-2 text-emerald-600" />
                          <span className="font-medium">{strategy.business_type}</span>
                        </div>
                      </div>

                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Location</h3>
                        <div className="flex items-center mt-1">
                          <MapPin className="h-4 w-4 mr-2 text-emerald-600" />
                          <span>{strategy.location_name}</span>
                        </div>
                      </div>

                      <div>
                        <h3 className="text-sm font-medium text-gray-500">Coordinates</h3>
                        <div className="mt-1 text-sm">{strategy.location_coords}</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {strategy.trend_data && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Market Trends</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {strategy.trend_data.top_categories && (
                          <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-2">Top Business Categories</h3>
                            <ul className="space-y-1">
                              {strategy.trend_data.top_categories.map((item: any, index: number) => (
                                <li key={index} className="flex justify-between text-sm">
                                  <span>{item[0]}</span>
                                  <span className="font-medium">{item[1]}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {strategy.trend_data.untapped_categories && (
                          <div>
                            <h3 className="text-sm font-medium text-gray-500 mb-2">Untapped Opportunities</h3>
                            <ul className="space-y-1">
                              {strategy.trend_data.untapped_categories.map((item: any, index: number) => (
                                <li key={index} className="flex justify-between text-sm">
                                  <span>{item[0]}</span>
                                  <span className="font-medium">{item[1]}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </>
        ) : (
          <div className="text-center p-12">
            <p className="text-gray-500">Strategy not found</p>
            <Button variant="link" className="mt-2" onClick={() => router.push("/dashboard")}>
              Return to Dashboard
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
