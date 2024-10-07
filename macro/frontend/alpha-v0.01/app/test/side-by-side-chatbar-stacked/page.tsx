"use client"

import { TrendingUp } from "lucide-react"
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

export const description = "A stacked bar chart with a legend comparing current and last year's data"

const chartData = [
  { month: "Jan", desktop: 186, mobile: 80, lastYearDesktop: 150, lastYearMobile: 60 },
  { month: "Feb", desktop: 305, mobile: 200, lastYearDesktop: 280, lastYearMobile: 180 },
  { month: "Mar", desktop: 237, mobile: 120, lastYearDesktop: 220, lastYearMobile: 110 },
  { month: "Apr", desktop: 73, mobile: 190, lastYearDesktop: 70, lastYearMobile: 170 },
  { month: "May", desktop: 209, mobile: 130, lastYearDesktop: 190, lastYearMobile: 120 },
  { month: "Jun", desktop: 214, mobile: 140, lastYearDesktop: 200, lastYearMobile: 130 },
]

const chartConfig = {
  desktop: {
    label: "Desktop (This Year)",
    color: "hsl(var(--chart-1))",
  },
  mobile: {
    label: "Mobile (This Year)",
    color: "hsl(var(--chart-2))",
  },
  lastYearDesktop: {
    label: "Desktop (Last Year)",
    color: "hsl(var(--chart-3))",
  },
  lastYearMobile: {
    label: "Mobile (Last Year)",
    color: "hsl(var(--chart-4))",
  },
} satisfies ChartConfig

export default function Component() {
  return (
    <Card className="w-[64rem]">
      <CardHeader>
        <CardTitle>Bar Chart - Stacked + Legend (Year-over-Year Comparison)</CardTitle>
        <CardDescription>January - June 2023 vs 2024</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <BarChart accessibilityLayer data={chartData}>
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="month"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ChartLegend content={<ChartLegendContent />} />
            <Bar
              dataKey="desktop"
              stackId="thisYear"
              fill="var(--color-desktop)"
              radius={[0, 0, 0, 0]}
            />
            <Bar
              dataKey="mobile"
              stackId="thisYear"
              fill="var(--color-mobile)"
              radius={[4, 4, 0, 0]}
            />
            <Bar
              dataKey="lastYearDesktop"
              stackId="lastYear"
              fill="var(--color-lastYearDesktop)"
              radius={[0, 0, 0, 0]}
            />
            <Bar
              dataKey="lastYearMobile"
              stackId="lastYear"
              fill="var(--color-lastYearMobile)"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex gap-2 font-medium leading-none">
          Trending up by 5.2% compared to last year <TrendingUp className="h-4 w-4" />
        </div>
        <div className="leading-none text-muted-foreground">
          Showing total visitors for the last 6 months, comparing current year to previous year
        </div>
      </CardFooter>
    </Card>
  )
}