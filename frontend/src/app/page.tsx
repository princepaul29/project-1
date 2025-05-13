import ProductSearch from "@/components/product-search";
import LayoutWithSidebar from "@/components/LayoutWithSidebar";

export default async function HomePage() {
  return (
    <LayoutWithSidebar>
      <ProductSearch />
    </LayoutWithSidebar>
  );
}