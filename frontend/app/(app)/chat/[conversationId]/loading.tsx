import { Skeleton } from "@/components/ui/skeleton";

export default function ChatLoading() {
  return (
    <div className="flex h-full flex-col">
      {/* Message skeletons */}
      <div className="flex-1 space-y-6 p-4">
        {/* User message skeleton */}
        <div className="flex justify-end gap-3">
          <div className="space-y-2">
            <Skeleton className="ml-auto h-10 w-64 rounded-2xl" />
            <Skeleton className="ml-auto h-3 w-16" />
          </div>
          <Skeleton className="h-8 w-8 rounded-full" />
        </div>

        {/* Assistant message skeleton */}
        <div className="flex gap-3">
          <Skeleton className="h-8 w-8 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-20 w-80 rounded-2xl" />
            <Skeleton className="h-32 w-72 rounded-lg" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>

        {/* Another user message */}
        <div className="flex justify-end gap-3">
          <div className="space-y-2">
            <Skeleton className="ml-auto h-10 w-48 rounded-2xl" />
            <Skeleton className="ml-auto h-3 w-16" />
          </div>
          <Skeleton className="h-8 w-8 rounded-full" />
        </div>
      </div>

      {/* Input skeleton */}
      <div className="border-t p-4">
        <div className="mx-auto flex max-w-3xl items-end gap-2">
          <Skeleton className="h-12 flex-1 rounded-xl" />
          <Skeleton className="h-12 w-12 rounded-xl" />
        </div>
      </div>
    </div>
  );
}
