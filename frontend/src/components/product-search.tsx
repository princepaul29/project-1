"use client";

import type React from "react";
import { useEffect, useState } from "react";
import { Menu, Search, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import ProductCard from "@/components/product-card";
import Sidebar from "@/components/sidebar";
import RatingPanel from "@/components/rating-panel";
import { Skeleton } from "@/components/ui/skeleton";
import { usePriceRangeStore } from "@/store/usePricerangestore";
interface ProductCardProps {
  review_count: any;
  url: string;
  name: string;
  id: any;
  description: string;
  image: string;
  source: any;
  price: any;
  rating: any;
  product: {
    id: string;
    name: string;
    price: string;
    info: string;
    review: string;
    image: string;
  };
  onRateClick: () => void;
}

interface Product {
  id: string;
  name: string;
  price: number;
  rating: number;
  description: string;
  image?: string;
  source: string;
}

export default function ProductSearch() {
  const [searchQuery, setSearchQuery] = useState("");
  const [products, setProducts] = useState<ProductCardProps[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);
  const [showRating, setShowRating] = useState(false);
  const [sortOption, setSortOption] = useState<
    "rating" | "price-asc" | "price-desc" | "none"
  >("none");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // const [priceRange, setPriceRange] = useState<[number, number]>([0, 0]);
  const { priceRange } = usePriceRangeStore();
  const connectWebSocket = (searchId: string) => {
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws?search_id=${searchId}`);

    ws.onopen = () => {
      console.log("WebSocket connection opened");
      setProducts([]); // clear previous results
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("WebSocket message received:", data);
        console.log("WebSocket message data: -.", data.data?.results);

        const newProducts = data.data?.results;

        if (Array.isArray(newProducts)) {
          setProducts((prev) => [...prev,...newProducts]);
          setLoading(false);
        } else {
          console.warn("No results to update products with.");
        }
      } catch (err) {
        console.error("WebSocket message error:", err);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket error", err);
      setError("WebSocket error. Please try again.");
      setLoading(false);
    };

    ws.onclose = () => {
      console.log("WebSocket closed");
      setLoading(false);
    };
  };

 

  const fetchProducts = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        query: searchQuery,
        min_price: priceRange[0].toString(),
        max_price: priceRange[1].toString(),
      });

      const response = await fetch(`http://127.0.0.1:8000/search?${params}`);
      if (!response.ok) throw new Error("Failed to fetch results");

      const data = await response.json();
      console.log("Initial search response ->", data);

      if (data.status === "cached") {
        // const combinedResults = [
        //   ...(data.flipkart_results || []).map((p: any) => ({
        //     ...p,
        //     source: "flipkart",
        //     price: parseFloat(p.price),
        //     rating: parseFloat(p.rating),
        //   })),
        //   ...(data.amazon_results || []).map((p: any) => ({
        //     ...p,
        //     source: "amazon",
        //     price: parseFloat(p.price),
        //     rating: parseFloat(p.rating),
        //   })),
        // ];
        // setProducts(combinedResults);
        setLoading(false);
      } else if (data.status === "pending") {
        connectWebSocket(data.search_id);
        
      }
    } catch (err) {
      setError("Failed to fetch products. Please try again.");
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      fetchProducts();
      setHasSearched(true);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
  };

  const getSortedProducts = () => {
    const sorted = [...products];
    switch (sortOption) {
      case "rating":
        return sorted.sort((a, b) => b.rating - a.rating);
      case "price-asc":
        return sorted.sort((a, b) => a.price - b.price);
      case "price-desc":
        return sorted.sort((a, b) => b.price - a.price);
      default:
        return sorted;
    }
  };
console.log("Products ->", products); 
  return (
    <>
      <div className="flex w-full">
        {/* Sidebar - visible on desktop */}
        {/* <div className="hidden md:block w-64 border-r min-h-screen">
          <Sidebar priceRange={priceRange} onPriceChange={setPriceRange} />
        </div> */}

        {/* Main content */}
        <div className="flex-1">
  
          <div
            className={`${
              hasSearched
                ? ""
                : "flex justify-center items-center p-4 min-h-screen"
            }`}
          >
            {/* Search Section */}
            <div className={`p-4 ${hasSearched ? "border-b" : ""}`}>
              <div className="flex justify-center">
                <div className="flex gap-2 w-full max-w-3xl min-w-2xl relative">
                  <TypewriterInput
                    searchQuery={searchQuery}
                    setSearchQuery={setSearchQuery}
                    handleKeyPress={handleKeyPress}
                  />
                  <Button onClick={handleSearch} variant="ghost">
                    <Search className="h-5 w-5" />
                  </Button>
                </div>
              </div>

              {!hasSearched && (
                <div className="mt-8 p-6 border rounded-lg max-w-3xl mx-auto">
                  <div className="space-y-4">
                    {[...Array(4)].map((_, i) => (
                      <Skeleton key={i} className="h-4 w-full rounded" />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
          {/* Results Section */}
          {hasSearched && (
            <div className="p-4">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Search Results</h2>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      <Filter className="h-4 w-4 mr-2" />
                      Filter
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => setSortOption("rating")}>
                      Sort by Rating (High → Low)
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => setSortOption("price-asc")}
                    >
                      Sort by Price (Low → High)
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => setSortOption("price-desc")}
                    >
                      Sort by Price (High → Low)
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => setSortOption("none")}>
                      Clear Sort
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              {loading ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[...Array(6)].map((_, i) => (
                    <Skeleton key={i} className="h-64 w-full rounded-lg" />
                  ))}
                </div>
              ) : error ? (
                <div className="text-center py-8 text-red-500">{error}</div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[calc(100vh-200px)] overflow-y-auto">
                  {getSortedProducts().map((product: { source: any; id: any; }, key: any) => (
                    <ProductCard
                      key={`${product.source}-${product.id}-${key}`}
                      product={product}
                      onRateClick={() => {
                        setSelectedProduct(`${product.source}-${product.id}`);
                        setShowRating(true);
                      }}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

const suggestions = [
  "Search products...",
  "Search books...",
  "Search electronics...",
  "Search deals...",
  "Search clothing...",
];

const TypewriterInput = ({
  searchQuery,
  setSearchQuery,
  handleKeyPress,
}: any) => {
  const [placeholder, setPlaceholder] = useState("");
  const [textIndex, setTextIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentText = suggestions[textIndex];
    const timeout = setTimeout(
      () => {
        if (!isDeleting) {
          setPlaceholder(currentText.slice(0, charIndex + 1));
          setCharIndex((prev) => prev + 1);

          if (charIndex + 1 === currentText.length) {
            setTimeout(() => setIsDeleting(true), 1500); // pause before deleting
          }
        } else {
          setPlaceholder(currentText.slice(0, charIndex - 1));
          setCharIndex((prev) => prev - 1);

          if (charIndex === 0) {
            setIsDeleting(false);
            setTextIndex((prev) => (prev + 1) % suggestions.length);
          }
        }
      },
      isDeleting ? 30 : 100
    ); // typing and deleting speeds

    return () => clearTimeout(timeout);
  }, [charIndex, isDeleting, textIndex]);

  return (
    <Input
      placeholder={placeholder}
      value={searchQuery}
      onChange={(e) => setSearchQuery(e.target.value)}
      onKeyDown={handleKeyPress}
      className="pr-10"
    />
  );
};
