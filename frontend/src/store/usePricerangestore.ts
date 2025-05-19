// store/usePriceRangeStore.ts
import { create } from 'zustand';

type PriceRangeState = {
  priceRange: [number, number];
  onPriceChange: (value: [number, number]) => void;
};

export const usePriceRangeStore = create<PriceRangeState>((set) => ({
  priceRange: [0, 0], // default values
  onPriceChange: (value: [number, number]) =>
    set({ priceRange: value }),
}));
