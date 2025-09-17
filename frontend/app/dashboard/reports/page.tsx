"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { FileText, Download, Loader2, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import DashboardLayout from "@/components/dashboard-layout"

export default function ReportsPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [isGenerating, setIsGenerating] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [reports, setReports] = useState<any[]>([])

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
      return
    }

    // Fetch reports
    fetchReports()
  }, [router])

  const fetchReports = async () => {
    setIsLoading(true)
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("http://localhost:5000/reports", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!response.ok) {
        throw new Error("Failed to fetch reports")
      }

      const data = await response.json()
      setReports(data.reports || [])
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to fetch reports",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    setIsGenerating(true)
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("http://localhost:5000/generate-report", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      })

      if (!response.ok) {
        throw new Error("Failed to generate report")
      }

      await response.json()

      toast({
        title: "Report generated",
        description: "Your comprehensive market research report has been generated",
      })

      // Refresh reports list
      fetchReports()
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate report",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownloadReport = async (reportId: number) => {
    try {
      const token = localStorage.getItem("token")

      // Create a temporary anchor element to trigger the download
      const link = document.createElement("a")
      link.href = `http://localhost:5000/download-report/${reportId}?token=${token}`
      link.target = "_blank"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: "Download started",
        description: "Your report download has started",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to download report",
        variant: "destructive",
      })
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Reports</h1>
          <p className="text-gray-500">Generate and download comprehensive market research reports</p>
        </div>

        {/* Generate Report Button */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Generate New Report</CardTitle>
            <CardDescription>Create a comprehensive PDF report with all your market research data</CardDescription>
          </CardHeader>
          <CardContent>
            <Button
              className="bg-emerald-600 hover:bg-emerald-700"
              onClick={handleGenerateReport}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating Report...
                </>
              ) : (
                <>
                  <FileText className="mr-2 h-4 w-4" />
                  Generate New Report
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Reports List */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Your Reports</h2>

          {isLoading ? (
            <div className="flex justify-center items-center p-12">
              <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
            </div>
          ) : reports.length === 0 ? (
            <Card>
              <CardContent className="p-6 text-center text-gray-500">
                <p>You haven&apos;t generated any reports yet.</p>
                <p className="text-sm mt-1">Use the button above to create your first report.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {reports.map((report) => (
                <Card key={report.id} className="overflow-hidden">
                  <div className="flex items-center p-4">
                    <div className="h-12 w-12 bg-emerald-100 rounded-lg flex items-center justify-center mr-4">
                      <FileText className="h-6 w-6 text-emerald-600" />
                    </div>

                    <div className="flex-1">
                      <h3 />
                    </div>

                    <div className="flex-1">
                      <h3 className="font-medium">{report.report_name}</h3>
                      <div className="flex items-center text-sm text-gray-500">
                        <Calendar className="h-4 w-4 mr-1" />
                        {formatDate(report.created_at)}
                      </div>
                    </div>

                    <Button variant="outline" className="ml-4" onClick={() => handleDownloadReport(report.id)}>
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
