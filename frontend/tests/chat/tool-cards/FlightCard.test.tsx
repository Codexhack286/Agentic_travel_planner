import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { FlightCard } from "@/components/chat/tool-cards/FlightCard";
import type { FlightResult } from "@/types";

describe("FlightCard", () => {
  it("renders flight data correctly", () => {
    const flightData: FlightResult = {
      origin: "JFK",
      destination: "LAX",
      departureDate: "2026-02-15",
      flights: [
        {
          airline: "Delta",
          flightNumber: "DL123",
          duration: "5h 30m",
          stops: 0,
          price: {
            amount: 299,
            currency: "USD",
          },
        },
        {
          airline: "United",
          flightNumber: "UA456",
          duration: "6h 15m",
          stops: 1,
          price: {
            amount: 249,
            currency: "USD",
          },
        },
      ],
    };

    render(<FlightCard data={flightData} />);

    // Check header with origin/destination
    expect(screen.getByText(/Flights: JFK/)).toBeInTheDocument();
    expect(screen.getByText(/LAX/)).toBeInTheDocument();

    // Check departure date badge
    expect(screen.getByText("2026-02-15")).toBeInTheDocument();

    // Check first flight details
    expect(screen.getByText("Delta DL123")).toBeInTheDocument();
    expect(screen.getByText("5h 30m")).toBeInTheDocument();
    expect(screen.getByText("$299")).toBeInTheDocument();

    // Check second flight details
    expect(screen.getByText("United UA456")).toBeInTheDocument();
    expect(screen.getByText("6h 15m")).toBeInTheDocument();
    expect(screen.getByText("$249")).toBeInTheDocument();
    expect(screen.getByText("· 1 stop")).toBeInTheDocument();
  });

  it("shows +N more options when there are more than 3 flights", () => {
    const flightData: FlightResult = {
      origin: "SFO",
      destination: "NYC",
      departureDate: "2026-03-01",
      flights: [
        {
          airline: "Delta",
          flightNumber: "DL1",
          duration: "5h 00m",
          stops: 0,
          price: { amount: 350, currency: "USD" },
        },
        {
          airline: "United",
          flightNumber: "UA2",
          duration: "5h 30m",
          stops: 1,
          price: { amount: 300, currency: "USD" },
        },
        {
          airline: "American",
          flightNumber: "AA3",
          duration: "6h 00m",
          stops: 1,
          price: { amount: 280, currency: "USD" },
        },
        {
          airline: "JetBlue",
          flightNumber: "B64",
          duration: "6h 15m",
          stops: 2,
          price: { amount: 250, currency: "USD" },
        },
        {
          airline: "Southwest",
          flightNumber: "WN5",
          duration: "6h 30m",
          stops: 2,
          price: { amount: 230, currency: "USD" },
        },
      ],
    };

    render(<FlightCard data={flightData} />);

    // Should show first 3 flights
    expect(screen.getByText("Delta DL1")).toBeInTheDocument();
    expect(screen.getByText("United UA2")).toBeInTheDocument();
    expect(screen.getByText("American AA3")).toBeInTheDocument();

    // Should NOT show the 4th and 5th flights
    expect(screen.queryByText("JetBlue B64")).not.toBeInTheDocument();
    expect(screen.queryByText("Southwest WN5")).not.toBeInTheDocument();

    // Should show "+N more options" message
    expect(screen.getByText("+2 more options")).toBeInTheDocument();
  });
});
