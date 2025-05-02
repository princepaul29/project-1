import Link from "next/link"
import { Home, LogIn, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider";

interface SidebarProps {
  priceRange: [number, number];
  onPriceChange: (value: [number, number]) => void;
}

export default function Sidebar({ priceRange, onPriceChange }: SidebarProps) {
  return (
    <div className="flex flex-col h-full p-4">
      <div className="space-y-2 flex-1">
        <Button variant="ghost" className="w-full justify-start" asChild>
          <Link href="/">
            <Home className="mr-2 h-5 w-5" />
            Home
          </Link>
        </Button>
        <Button variant="ghost" className="w-full justify-start" asChild>
          <Link href="/login">
            <LogIn className="mr-2 h-5 w-5" />
            Login
          </Link>
        </Button>
      </div>
      <div className="p-4 space-y-6">
      <div>
        <h3 className="font-semibold mb-4">Price Range</h3>
        <Slider 
          min={0}
          max={100000}
          step={1000}
          value={priceRange}
          onValueChange={(value: [number, number]) => onPriceChange(value as [number, number])}
        />
        <div className="flex justify-between text-sm mt-2">
          <span>₹{priceRange[0].toLocaleString()}</span>
          <span>₹{priceRange[1].toLocaleString()}</span>
        </div>
      </div>
    </div>
      <div className="pt-4 border-t">
        <Button variant="outline" className="w-full justify-start">
          <User className="mr-2 h-5 w-5" />
          User Details
        </Button>
      </div>
    </div>
  )
}
