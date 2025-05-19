"use client";

import { IconCirclePlusFilled, IconMail, type Icon } from "@tabler/icons-react";

import { Button } from "@/components/ui/button";
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import Link from "next/link";
import { usePriceRangeStore } from "@/store/usePricerangestore";
import { Slider } from "@/components/ui/slider";
export function NavMain({
  items,
}: {
  items: {
    title: string;
    url: string;
    icon?: Icon;
  }[];
}) {
  const { priceRange, onPriceChange } = usePriceRangeStore();
  return (
    <SidebarGroup>
      <SidebarGroupContent className="flex flex-col gap-2">
        <SidebarMenu>
          {items.map((item) => (
            <Link key={item.url} href={item.url}>
              {/* <SidebarMenuItem className="flex items-center gap-2"> */}

              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton tooltip={item.title}>
                  {item.icon && <item.icon />}
                  <span>{item.title}</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </Link>
          ))}
        </SidebarMenu>
        <SidebarMenu>
          <div>
            <h3 className="font-semibold mb-4">Price Range</h3>
            <Slider
              min={0}
              max={10000}
              step={10}
              value={priceRange}
              onValueChange={(value: [number, number]) =>
                onPriceChange(value as [number, number])
              }
            />
            <div className="flex justify-between text-sm mt-2">
              <span>${priceRange[0].toLocaleString()}</span>
              <span>$5{priceRange[1].toLocaleString()}</span>
            </div>
          </div>
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
