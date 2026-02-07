"use client";

import { Banknote, ArrowRight } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCurrency } from "@/lib/format";
import type { CurrencyResult, ToolResultData } from "@/types";

interface CurrencyCardProps {
  data: ToolResultData;
}

export function CurrencyCard({ data }: CurrencyCardProps) {
  const currencyData = data as CurrencyResult;

  return (
    <Card className="border-currency/20 bg-currency/5">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <Banknote className="h-4 w-4 text-currency" />
          <CardTitle className="text-sm">Currency Exchange</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-center gap-3 py-2">
          <div className="text-center">
            <p className="text-2xl font-bold">{currencyData.from}</p>
            {currencyData.amount && (
              <p className="text-sm text-muted-foreground">
                {formatCurrency(currencyData.amount, currencyData.from)}
              </p>
            )}
          </div>
          <ArrowRight className="h-5 w-5 text-currency" />
          <div className="text-center">
            <p className="text-2xl font-bold">{currencyData.to}</p>
            {currencyData.convertedAmount && (
              <p className="text-sm text-muted-foreground">
                {formatCurrency(
                  currencyData.convertedAmount,
                  currencyData.to
                )}
              </p>
            )}
          </div>
        </div>
        <div className="mt-2 text-center">
          <p className="text-lg font-semibold text-currency">
            1 {currencyData.from} = {currencyData.rate.toFixed(4)}{" "}
            {currencyData.to}
          </p>
          <p className="text-xs text-muted-foreground">
            Last updated: {currencyData.lastUpdated}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
