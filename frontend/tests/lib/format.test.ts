import { describe, it, expect } from "vitest";
import {
  formatCurrency,
  formatDuration,
  formatTemperature,
} from "@/lib/format";

describe("formatCurrency", () => {
  it("formats USD amount correctly", () => {
    const result = formatCurrency(1250, "USD");
    expect(result).toContain("1,250");
    expect(result).toContain("$");
  });

  it("formats EUR amount correctly", () => {
    const result = formatCurrency(99.5, "EUR");
    expect(result).toContain("99.5");
  });

  it("omits decimals for whole numbers", () => {
    const result = formatCurrency(500, "USD");
    expect(result).toBe("$500");
  });
});

describe("formatDuration", () => {
  it("formats hours and minutes", () => {
    expect(formatDuration("PT14H30M")).toBe("14h 30m");
  });

  it("formats hours only", () => {
    expect(formatDuration("PT14H")).toBe("14h");
  });

  it("formats minutes only", () => {
    expect(formatDuration("PT45M")).toBe("45m");
  });

  it("returns original string for invalid format", () => {
    expect(formatDuration("invalid")).toBe("invalid");
  });
});

describe("formatTemperature", () => {
  it("formats celsius", () => {
    expect(formatTemperature(22.4, "celsius")).toBe("22°C");
  });

  it("formats fahrenheit", () => {
    expect(formatTemperature(72.6, "fahrenheit")).toBe("73°F");
  });
});
