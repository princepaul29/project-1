"use client";
import React, { useState } from "react";
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

const columns = ["name", "prize", "rating", "url", "noc"];

export default function ProductDashboard() {
  const [data, setData] = useState(sampleData);
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: "asc" | "desc";
  } | null>(null);

  const handleSort = (key: string) => {
    let direction: "asc" | "desc" = "asc";
    if (sortConfig?.key === key && sortConfig.direction === "asc") {
      direction = "desc";
    }
    setSortConfig({ key, direction });

    const sorted = [...data].sort((a, b) => {
      const aVal = a[key as keyof typeof a];
      const bVal = b[key as keyof typeof b];

      if (typeof aVal === "number" && typeof bVal === "number") {
        return direction === "asc" ? aVal - bVal : bVal - aVal;
      }

      return direction === "asc"
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });

    setData(sorted);
  };

  const getSortIcon = (key: string) => {
    if (sortConfig?.key !== key) return null;
    return sortConfig.direction === "asc" ? (
      <ArrowUp className="inline w-4 h-4 ml-1" />
    ) : (
      <ArrowDown className="inline w-4 h-4 ml-1" />
    );
  };

  return (
    <div className="p-6 space-y-6 h-screen flex flex-col justify-between">
      <div className="bg-gray-200 rounded-xl p-4 h-[75vh] ">
        <div className="overflow-auto max-h-full scrollbar-custom">
          <Table>
            <TableHeader>
              <TableRow>
                {columns.map((col) => (
                  <TableHead
                    key={col}
                    className="cursor-pointer text-black"
                    onClick={() => handleSort(col)}
                  >
                    {col} {getSortIcon(col)}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((item, index) => (
                <TableRow key={index}>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{item.prize}</TableCell>
                  <TableCell>{item.rating}</TableCell>
                  <TableCell>
                    <a
                      href={item.url}
                      className="text-blue-600 underline"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {item.url}
                    </a>
                  </TableCell>
                  <TableCell>{item.noc}</TableCell>
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
            no of visitors
          </CardContent>
        </Card>
        <Card className="bg-gray-200">
          <CardContent className="p-4 text-center font-semibold text-black">
            no of api request
          </CardContent>
        </Card>
        <Card className="bg-gray-200">
          <CardContent className="p-4 text-center font-semibold text-black">
            total noc
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
