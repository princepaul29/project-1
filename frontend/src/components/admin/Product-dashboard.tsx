"use client";
import React, { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowDown, ArrowUp } from "lucide-react";
import { Calendar } from "@/components/ui/calendar";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { ScraperCardTable } from "./scraper-card";


const sampleData = [
  {
    name: "Product C",
    prize: 90,
    rating: 4.9,
    url: "https://c.com",
    noc: 10,
  },
  {
    name: "Product A",
    prize: 100,
    rating: 4.5,
    url: "https://a.com",
    noc: 5,
  },
  {
    name: "Product B",
    prize: 150,
    rating: 3.8,
    url: "https://b.com",
    noc: 2,
  },
  {
    name: "Product C",
    prize: 90,
    rating: 4.9,
    url: "https://c.com",
    noc: 10,
  },
];

const columns = ["name", "price", "rating", "url", "noc"];

// Define the Product type
interface Product {
  price: string;
  name: string;
  prize: number;
  rating: number;
  url: string;
  noc: number;
}

export default function ProductDashboard() {
  const [data, setData] = useState<Product[] | null>(null);
  const [sortConfig, setSortConfig] = useState<{
    key: keyof Product;
    direction: "asc" | "desc";
  } | null>(null);

  // Fetch data on mount
  useEffect(() => {
    fetch("http://localhost:8000/products")
      .then((res) => res.json())
      .then((data) => setData(data.results))
      .catch((err) => console.error("Error fetching products:", err));
  }, []);

  // Sort effect: whenever data or sortConfig changes, re-sort
  useEffect(() => {
    if (!data || !sortConfig) return;

    const { key, direction } = sortConfig;

    const sorted = [...data].sort((a, b) => {
      const aVal = a[key];
      const bVal = b[key];

      if (typeof aVal === "number" && typeof bVal === "number") {
        return direction === "asc" ? aVal - bVal : bVal - aVal;
      }
      return direction === "asc"
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });

    setData(sorted);
  }, [sortConfig, data]);

  // Handler just updates sortConfig
  const handleSort = (key: any) => {
    let direction: "asc" | "desc" = "asc";
    if (
      sortConfig &&
      sortConfig.key === key &&
      sortConfig.direction === "asc"
    ) {
      direction = "desc";
    }
    setSortConfig({ key, direction });
  };

  const getSortIcon = (key: string) => {
    if (sortConfig?.key !== key) return null;
    return sortConfig.direction === "asc" ? (
      <ArrowUp className="inline w-4 h-4 ml-1" />
    ) : (
      <ArrowDown className="inline w-4 h-4 ml-1" />
    );
  };

  const [count, setCount] = useState(null);
  const [totalApi, setTotalApi] = useState(null);
  const [totalNoc, setTotalNoc] = useState(0);
  useEffect(() => {
    fetch("http://localhost:8000/visitors/count")
      .then((res) => res.json())
      .then((data) => setCount(data.total_visitors))
      .catch((err) => console.error("Error fetching count:", err));
  }, []);
  useEffect(() => {
    fetch("http://localhost:8000/api-requests/amazon_search/count")
      .then((res) => res.json())
      .then((data) => setTotalApi(data.count))
      .catch((err) => console.error("Error fetching count:", err));
  }, []);
  const [flipkartEnabled, setFlipkartEnabled] = useState(false);
  const [amazonEnabled, setAmazonEnabled] = useState(false);
  const [loading, setLoading] = useState(true);
   useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch('http://localhost:8000/admin/scrapers');
        const data = await res.json();

        const flipkart = data.configs.find((s: any) => s.name === 'flipkart');
        const amazon = data.configs.find((s: any) => s.name === 'amazon');

        if (flipkart) setFlipkartEnabled(flipkart.enabled);
        if (amazon) setAmazonEnabled(amazon.enabled);
      } catch (error) {
        console.error('Failed to fetch scraper status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  const toggleScraper = async (platform: 'flipkart' | 'amazon') => {
    const isEnabled = platform === 'flipkart' ? flipkartEnabled : amazonEnabled;
    const action = isEnabled ? 'disable' : 'enable';
    const url = `http://localhost:8000/admin/scrapers/${platform}/${action}`;

    try {
      const res = await fetch(url, {
        method: 'POST',
      });

      if (!res.ok) throw new Error(`Failed to ${action} ${platform} scraper`);

      if (platform === 'flipkart') {
        setFlipkartEnabled(!flipkartEnabled);
      } else {
        setAmazonEnabled(!amazonEnabled);
      }
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="p-6 space-y-6 flex flex-col justify-between">
      <div className="flex gap-4">
        <ScraperCardTable  />
      </div>
      <div className="bg-gray-200 rounded-xl p-4 h-[75vh] ">
        <div className="overflow-auto max-h-full scrollbar-custom">
          <Table className="w-full table-fixed border border-gray-300 border-collapse">
            <TableHeader>
              <TableRow className="border border-gray-300">
                {columns.map((col) => (
                  <TableHead
                    key={col}
                    className="cursor-pointer text-black border border-gray-300 max-w-[100px] truncate"
                    onClick={() => handleSort(col)}
                  >
                    {col} {getSortIcon(col)}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data &&
                data.map((item, index) => (
                  <TableRow key={index} className="border border-gray-300">
                    <TableCell className="border border-gray-300 px-2 py-1 truncate">
                      {item.name}
                    </TableCell>
                    <TableCell className="border border-gray-300 px-2 py-1">
                      {item.price}
                    </TableCell>
                    <TableCell className="border border-gray-300 px-2 py-1">
                      {item.rating}
                    </TableCell>
                    <TableCell className="border border-gray-300 px-2 py-1">
                      <a
                        href={item.url}
                        className="text-blue-600 underline truncate text-wrap"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {item.url}
                      </a>
                    </TableCell>
                    <TableCell className="border border-gray-300 px-2 py-1">
                      {item.noc}
                    </TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Footer Cards */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-gray-200">
          <CardContent className="p-4 text-center font-semibold text-black">
            visitors - <span>{count}</span>
          </CardContent>
        </Card>
        <Popover>
          <PopoverTrigger>
        <Card className="bg-gray-200">
          <CardContent className="p-4 text-center font-semibold text-black">
            no of api request - <span>{totalApi}</span>
          </CardContent>

        </Card>
        </PopoverTrigger>
        <PopoverContent><ApiRequestCount /></PopoverContent>
        </Popover>
        <Card className="bg-gray-200">
          <CardContent className="p-4 text-center font-semibold text-black">
            total noc - <span>{totalNoc}</span>
          </CardContent>
        </Card>
      </div>
      
    </div>
  );
}



const  ApiRequestCount = () => {
    const [startDate, setStartDate] = useState<Date | undefined>(undefined);
  const [endDate, setEndDate] = useState<Date | undefined>(undefined);
  const [count, setCount] = useState<number | null>(null);

  const endpointName = "amazon_search";

  const fetchCount = async () => {
    if (!startDate || !endDate) {
      alert("Please select both start and end dates");
      return;
    }

    const startISO = format(startDate, "yyyy-MM-dd");
    const endISO = format(endDate, "yyyy-MM-dd");

    const params = new URLSearchParams({
      start_date: startISO,
      end_date: endISO,
    });

    try {
      const res = await fetch(`http://127.0.0.1:8000/api-requests/${endpointName}/count?${params.toString()}`);
      const data = await res.json();
      setCount(data.count);
    } catch (error) {
      alert("Failed to fetch count");
      console.error(error);
    }
  };

  return (
    <div className="max-w-md mx-auto p-4 space-y-6">

      {/* Start Date Picker */}
      <div>
        <label className="block mb-2 font-medium">Start Date:</label>
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" className="w-full">
              {startDate ? startDate.toLocaleDateString() : "Select Start Date"}
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" className="p-0">
            <Calendar
              mode="single"
              selected={startDate}
              onSelect={(date) => setStartDate(date || undefined)}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      {/* End Date Picker */}
      <div>
        <label className="block mb-2 font-medium">End Date:</label>
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="outline" className="w-full">
              {endDate ? endDate.toLocaleDateString() : "Select End Date"}
            </Button>
          </PopoverTrigger>
          <PopoverContent align="start" className="p-0">
            <Calendar
              mode="single"
              selected={endDate}
              onSelect={(date) => setEndDate(date || undefined)}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      </div>

      <Button onClick={fetchCount} className="w-full" disabled={!startDate || !endDate}>
        Get Count
      </Button>

      {count !== null && (
        <div className="mt-4 p-3 bg-green-100 text-green-800 rounded">
          API Request Count: {count}
        </div>
      )}
    </div>
  );
};