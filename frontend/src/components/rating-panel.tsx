"use client"

import { X, Star } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useState } from "react"

interface RatingPanelProps {
  onClose: () => void
  productId: number | null
}

export default function RatingPanel({ onClose, productId }: RatingPanelProps) {
  const [rating, setRating] = useState<number | null>(null)
  const [review, setReview] = useState("")

  const handleSubmit = () => {
    // Here you would submit the rating and review
    console.log({ productId, rating, review })
    onClose()
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-semibold">Rate & Review</h3>
        <Button variant="ghost" size="icon" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <div className="space-y-6 flex-1">
        <div>
          <p className="mb-2 text-sm">Rate</p>
          <div className="flex gap-4 items-center">
            <div className="flex">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star
                  key={star}
                  className={`h-6 w-6 cursor-pointer ${
                    rating && star <= rating ? "fill-primary text-primary" : "text-muted-foreground"
                  }`}
                  onClick={() => setRating(star)}
                />
              ))}
            </div>
            <div className="text-sm">→</div>
            <div className="h-4 w-4 rounded-full bg-red-500"></div>
          </div>
        </div>

        <div>
          <p className="mb-2 text-sm">Review</p>
          <div className="flex gap-4 items-center">
            <div className="h-4 w-4 rounded-full bg-red-500"></div>
            <div className="text-sm">→</div>
            <div className="h-4 w-4 rounded-full bg-gray-300"></div>
          </div>
          <Textarea
            className="mt-2"
            placeholder="Write your review here..."
            value={review}
            onChange={(e) => setReview(e.target.value)}
          />
        </div>
      </div>

      <div className="mt-auto pt-4">
        <Button className="w-full" onClick={handleSubmit}>
          Submit Review
        </Button>
      </div>
    </div>
  )
}
