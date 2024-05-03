import BreadCrumb from "@/components/breadcrumb";
import { ProductForm } from "@/components/forms/product-form";
import { ScrollArea } from "@/components/ui/scroll-area";
import React from "react";

export default function Page() {
  const breadcrumbItems = [
    { title: "User", link: "/dashboard/user" },
    { title: "Create", link: "/dashboard/user/create" },
  ];
  return (
    <ScrollArea className="h-full">
      <div className="flex-1 space-y-4 p-5">
        <BreadCrumb items={breadcrumbItems} />
        <ProductForm
          categories={[
            { _id: "shirts", name: "shirts" },
            { _id: "pants", name: "pants" },
          ]}
          initialData={null}
          key={null}
        />
      </div>
    </ScrollArea>
  );
}

export const generateStaticParams = async () => {
  const userIds = await fetchUserIds(); // Implement this function to fetch user IDs
  return userIds.map(userId => ({ params: { userId } }));
};

async function fetchUserIds() {
  // Fetch user IDs from an API or database
  return ['123', '456', '789'];  // Example user IDs
}