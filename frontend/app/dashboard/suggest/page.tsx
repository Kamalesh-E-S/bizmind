"use client";

import { useState } from "react";
import {
  MapPin,
  Search,
  Loader2,
  Map,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import DashboardLayout from "@/components/dashboard-layout";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { LoadScript, GoogleMap, Circle, Marker } from "@react-google-maps/api";

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
];

export default function LocationSuggestionPage() {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [location, setLocation] = useState("");
  const [category, setCategory] = useState("");
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [center, setCenter] = useState({ lat: 13.0827, lng: 80.2707 }); // Chennai default
  const [mapReady, setMapReady] = useState(false);

  const mapContainerStyle = {
    width: "100%",
    height: "400px",
    borderRadius: "12px",
  };

  // 🔍 Geocode function to convert LatLng to name
  const reverseGeocode = async (lat: number, lng: number) => {
    const geocoder = new google.maps.Geocoder();
    return new Promise<string>((resolve) => {
      geocoder.geocode({ location: { lat, lng } }, (results, status) => {
        if (status === "OK" && results[0]) {
          resolve(results[0].formatted_address);
        } else {
          resolve(`(${lat.toFixed(5)}, ${lng.toFixed(5)})`);
        }
      });
    });
  };

  // 🚀 Suggest locations (fetch + geocode)
  const handleSuggestLocations = async () => {
    if (!location || !category) {
      toast({
        title: "Missing information",
        description: "Please provide both location and business category",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(
        `http://localhost:5000/suggest-locations?location=${encodeURIComponent(
          location
        )}&category=${encodeURIComponent(category)}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Failed to fetch suggestions");

      // 🗺️ Convert coords → names
      const detailedSuggestions = await Promise.all(
        (data.suggested_zones || []).map(async (zone: any) => {
          const name = await reverseGeocode(zone.lat, zone.lng);
          return { ...zone, name };
        })
      );

      setSuggestions(detailedSuggestions);
      if (detailedSuggestions.length > 0) setCenter(detailedSuggestions[0]);
      toast({
        title: "Suggestions ready",
        description: `Found ${data.count} suggested locations.`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to fetch suggestions",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Location Suggestion</h1>
          <p className="text-gray-500">
            Find ideal locations with low competition for your business
          </p>
        </div>

        {/* Input Card */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Suggest Locations</CardTitle>
            <CardDescription>
              Enter a location and business category to get low-density suggestions
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
                  onClick={handleSuggestLocations}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Suggesting...
                    </>
                  ) : (
                    <>
                      <Search className="mr-2 h-4 w-4" />
                      Suggest Locations
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Google Map */}
        <LoadScript
          googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY!}
          onLoad={() => setMapReady(true)}
          libraries={["visualization", "places"]}
        >
          <GoogleMap
            mapContainerStyle={mapContainerStyle}
            center={center}
            zoom={13}
          >
            {mapReady &&
              suggestions.map((zone, idx) => (
                <Circle
                  key={idx}
                  center={{ lat: zone.lat, lng: zone.lng }}
                  radius={300}
                  options={{
                    fillColor: "#10B981",
                    fillOpacity: 0.3,
                    strokeColor: "#059669",
                    strokeOpacity: 0.7,
                    strokeWeight: 1,
                  }}
                />
              ))}
            {mapReady &&
              suggestions.map((zone, idx) => (
                <Marker
                  key={idx}
                  position={{ lat: zone.lat, lng: zone.lng }}
                  title={zone.name}
                />
              ))}
          </GoogleMap>
        </LoadScript>

        {/* Suggestions List */}
        {suggestions.length > 0 && (
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Suggested Locations</CardTitle>
              <CardDescription>Coordinates with low competition</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {suggestions.map((zone: any, idx: number) => (
                  <li
                    key={idx}
                    className="flex flex-col bg-emerald-50 rounded p-3"
                  >
                    <div className="flex items-center gap-3">
                      <Map className="text-emerald-600" />
                      <span className="font-mono text-sm">
                        {zone.lat}, {zone.lng}
                      </span>
                    </div>
                    <span className="text-sm text-gray-600 pl-8">{zone.name}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
