"use client";

import { useEffect, useState } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { Card } from "@/components/ui/card";

interface ScraperConfig {
  name: string;
  id: number;
  enabled: boolean;
}

export function ScraperCardTable() {
  const [scrapers, setScrapers] = useState<ScraperConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [nocflipkart,setNocflipkart] = useState(0);
  const [nocamazon,setNocamazon] = useState(0);

  // Fetch scraper configs on mount
  useEffect(() => {
    fetch("http://localhost:8000/admin/scrapers")
      .then((res) => res.json())
      .then((data) => {
        setScrapers(data.configs || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Failed to fetch scrapers:", error);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    fetch("http://localhost:8000/products/noc/flipkart")
      .then((res) => res.json())
      .then((data) => {
        setNocflipkart(data.number_of_clicks || 0);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Failed to fetch scrapers:", error);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    fetch("http://localhost:8000/products/noc/amazon")
      .then((res) => res.json())
      .then((data) => {
        setNocamazon(data.number_of_clicks || 0);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Failed to fetch scrapers:", error);
        setLoading(false);
      });
  }, []);

  const handleToggle = async (scraperName: string, newState: boolean) => {
    try {
      await fetch(
        `http://localhost:8000/admin/scrapers/${scraperName}/${newState ? "enable" : "disable"}`,
        {
          method: "POST",
          headers: { accept: "application/json" },
        }
      );
      setScrapers((prev) =>
        prev.map((scraper) =>
          scraper.name === scraperName ? { ...scraper, enabled: newState } : scraper
        )
      );
    } catch (error) {
      console.error("Failed to toggle scraper:", error);
    }
  };

  if (loading) return <div>Loading scrapers...</div>;

  return (
    <Card className="bg-gray-200 p-4 w-full mx-auto">
      {/* Table Header */}
      <div className="grid grid-cols-3 gap-4 font-semibold text-gray-900 border-b border-gray-300 pb-2">
        <div>Scraper Name</div>
        <div>Total No.</div>
        <div>Off / On</div>
      </div>

      {/* Table Rows */}
      {scrapers.map((scraper) => (
        <ScraperRow
          key={scraper.id}
          scraperName={scraper.name}
          totalNoc={scraper.id=== 1 ? nocflipkart : nocamazon}
          isActive={scraper.enabled}
          onToggle={(isActive) => handleToggle(scraper.name, isActive)}
        />
      ))}
    </Card>
  );
}

function ScraperRow({
  scraperName = "—",
  totalNoc = 0,
  isActive = false,
  onToggle,
}: {
  scraperName?: string;
  totalNoc?: number;
  isActive?: boolean;
  onToggle?: (isActive: boolean) => void;
}) {
  const [isChecked, setIsChecked] = useState(isActive);

  useEffect(() => {
    setIsChecked(isActive);
  }, [isActive]);

  const handleToggle = () => {
    const newState = !isChecked;
    setIsChecked(newState);
    onToggle?.(newState);
  };

  return (
    <div className="grid grid-cols-3 gap-4 items-center py-2">
      <div className="text-gray-800 capitalize">{scraperName}</div>
      <div className="text-gray-800">{totalNoc}</div>
      <Checkbox
        checked={isChecked}
        onCheckedChange={handleToggle}
        className="data-[state=checked]:bg-sky-500 bg-gray-200 border-gray-400 hover:bg-sky-500 hover:border-sky-500 focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 focus:ring-offset-gray-200 rounded"
      />
    </div>
  );
}
