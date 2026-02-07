"use client";

import { useEffect, useRef, useCallback } from "react";

export function useAutoScroll(dependency: unknown) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const isUserScrolledUp = useRef(false);

  const handleScroll = useCallback(() => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    // User is "scrolled up" if more than 100px from bottom
    isUserScrolledUp.current = scrollHeight - scrollTop - clientHeight > 100;
  }, []);

  useEffect(() => {
    if (!isUserScrolledUp.current && scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [dependency]);

  return { scrollRef, handleScroll };
}
