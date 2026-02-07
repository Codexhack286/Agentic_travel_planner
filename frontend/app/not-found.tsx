import Link from "next/link";
import { MapPinOff } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex h-dvh items-center justify-center p-8">
      <div className="text-center">
        <MapPinOff className="mx-auto h-16 w-16 text-muted-foreground" />
        <h1 className="mt-4 text-3xl font-bold">Lost in transit</h1>
        <p className="mt-2 text-muted-foreground">
          This page doesn&apos;t exist. Let&apos;s get you back on track.
        </p>
        <Button className="mt-6" asChild>
          <Link href="/chat">Back to chat</Link>
        </Button>
      </div>
    </div>
  );
}
