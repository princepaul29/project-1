"use client"

import Image from "next/image"
import { Star } from "lucide-react"
import { Card, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/router"

interface ProductCardProps {
  product: {
    id: number
    name: string
    price: string
    info: string
    review: string
    url: string
  }
  onRateClick: () => void
}

export default function ProductCard({ product, onRateClick }: ProductCardProps) {
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-0">
        {/* <div className="relative h-48 w-full">
          <Image src={product.image || "/placeholder.svg"} alt={product.name} fill className="object-cover" />
        </div> */}
        <div className="p-4">
          <div className="grid gap-1">
            <h3 className="font-semibold text-sm text-primary">{product?.name}</h3>
            <p className="text-sm font-medium">{product?.price}</p>
            <p className="text-xs text-muted-foreground line-clamp-2">{product?.info}</p>
            <div className="flex items-center mt-1">
              <Star className="h-3 w-3 fill-primary text-primary mr-1" />
              <span className="text-xs">{product?.review}</span>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0">
        <Button variant="outline" size="sm" className="w-full" onClick={() => { window.open(product.url, "_blank")
        }}>
          go to product
        </Button>
      </CardFooter>
    </Card>
  )
}
