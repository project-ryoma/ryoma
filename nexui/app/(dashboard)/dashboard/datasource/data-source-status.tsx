"use client";
export function DataSourceStatus({ status }: { status: string }) {
  return (
    <div className="flex items-center space-x-2">
      <span
        className={`text-xs font-semibold ${
          status === "connected"
            ? "text-green-500"
            : status === "disconnected"
            ? "text-red-500"
            : status === "connecting"
            ? "text-blue-500"
            : "text-yellow-500"
        }`}
      >
        {status}
      </span>
    </div>
  );
}