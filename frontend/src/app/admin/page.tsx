// app/admin/page.tsx
import ProductDashboard from "@/components/admin/Product-dashboard";
import LayoutWithSidebar from "@/components/LayoutWithSidebar";

export default async function AdminPage() {
  return (
    <LayoutWithSidebar>
      <ProductDashboard />
    </LayoutWithSidebar>
  );
}
