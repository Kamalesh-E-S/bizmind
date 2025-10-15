import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, BarChart3, MapPin, Users, FileText } from "lucide-react"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="bg-gradient-to-r from-teal-500 to-emerald-600 text-white">
        <div className="container mx-auto px-4 py-16 md:py-24">
          <nav className="flex justify-between items-center mb-16">
            <div className="flex items-center gap-2">
              <BarChart3 className="h-8 w-8" />
              <span className="text-2xl font-bold">BizMind</span>
            </div>
            <div className="space-x-2">
              <Link href="/login">
                <Button variant="outline" className="text-white border-white hover:bg-white/10">
                  Login
                </Button>
              </Link>
              <Link href="/register">
                <Button className="bg-white text-emerald-600 hover:bg-white/90">Sign Up</Button>
              </Link>
            </div>
          </nav>

          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">AI-Powered Market Research & Business Strategy</h1>
            <p className="text-xl mb-8 text-white/90">
              Make data-driven business decisions with our comprehensive location analysis, competitor insights, and
              AI-generated business strategies.
            </p>
            <Link href="/register">
              <Button size="lg" className="bg-white text-emerald-600 hover:bg-white/90">
                Get Started <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Powerful Features</h2>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="h-12 w-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
                <MapPin className="h-6 w-6 text-emerald-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Location Analysis</h3>
              <p className="text-gray-600">
                Analyze business trends and opportunities in any location with our heatmap visualization and landmark
                analysis.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="h-12 w-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-emerald-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Competitor Insights</h3>
              <p className="text-gray-600">
                Get detailed information about competitors in your area, including ratings, reviews, and business types.
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md">
              <div className="h-12 w-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-4">
                <FileText className="h-6 w-6 text-emerald-600" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Strategy Generation</h3>
              <p className="text-gray-600">
                Receive AI-generated business strategies tailored to your specific location and business type.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>

          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="h-12 w-12 rounded-full bg-emerald-600 text-white flex items-center justify-center mx-auto mb-4">
                1
              </div>
              <h3 className="font-semibold mb-2">Create Account</h3>
              <p className="text-gray-600">Sign up and tell us about your business</p>
            </div>

            <div className="text-center">
              <div className="h-12 w-12 rounded-full bg-emerald-600 text-white flex items-center justify-center mx-auto mb-4">
                2
              </div>
              <h3 className="font-semibold mb-2">Select Location</h3>
              <p className="text-gray-600">Choose your target business location</p>
            </div>

            <div className="text-center">
              <div className="h-12 w-12 rounded-full bg-emerald-600 text-white flex items-center justify-center mx-auto mb-4">
                3
              </div>
              <h3 className="font-semibold mb-2">Analyze Data</h3>
              <p className="text-gray-600">Get insights on competitors and trends</p>
            </div>

            <div className="text-center">
              <div className="h-12 w-12 rounded-full bg-emerald-600 text-white flex items-center justify-center mx-auto mb-4">
                4
              </div>
              <h3 className="font-semibold mb-2">Generate Strategy</h3>
              <p className="text-gray-600">Receive AI-powered business recommendations</p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16 bg-emerald-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to grow your business?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Join thousands of business owners making data-driven decisions with MarketSense.
          </p>
          <Link href="/register">
            <Button size="lg" className="bg-white text-emerald-600 hover:bg-white/90">
              Get Started Today
            </Button>
          </Link>
        </div>
      </section>

      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between">
            <div className="mb-8 md:mb-0">
              <div className="flex items-center gap-2 mb-4">
                <BarChart3 className="h-6 w-6" />
                <span className="text-xl font-bold">MarketSense</span>
              </div>
              <p className="text-gray-400 max-w-md">
                AI-powered market research and business strategy platform for data-driven decisions.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
              <div>
                <h3 className="font-semibold mb-4">Product</h3>
                <ul className="space-y-2 text-gray-400">
                  <li><a href="#" className="hover:text-white">Features</a></li>
                  <li><a href="#" className="hover:text-white">Pricing</a></li>
                  <li><a href="#" className="hover:text-white">Case Studies</a></li>
                </ul>
              </div>

              <div>
                <h3 className="font-semibold mb-4">Company</h3>
                <ul className="space-y-2 text-gray-400">
                  <li><a href="#" className="hover:text-white">About</a></li>
                  <li><a href="#" className="hover:text-white">Blog</a></li>
                  <li><a href="#" className="hover:text-white">Careers</a></li>
                </ul>
              </div>

              <div>
                <h3 className="font-semibold mb-4">Support</h3>
                <ul className="space-y-2 text-gray-400">
                  <li><a href="#" className="hover:text-white">Help Center</a></li>
                  <li><a href="#" className="hover:text-white">Contact</a></li>
                  <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                </ul>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-700 mt-12 pt-8 text-center text-gray-400">
            <p>© {new Date().getFullYear()} MarketSense. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
