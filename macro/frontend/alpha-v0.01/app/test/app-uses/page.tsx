"use client"

import { TrendingUp } from "lucide-react"
import { CartesianGrid, Line, LineChart, XAxis, Area, AreaChart } from "recharts"
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
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
export const description = "A multiple line chart"
// const chartData = [
//   { month: "January", desktop: 186, mobile: 80 },
//   { month: "February", desktop: 305, mobile: 200 },
//   { month: "March", desktop: 237, mobile: 120 },
//   { month: "April", desktop: 73, mobile: 190 },
//   { month: "May", desktop: 209, mobile: 130 },
//   { month: "June", desktop: 214, mobile: 140 },
// ]
const chartData = [
    { date: "2024-04-01", desktop: 222, mobile: 222+150 },
    { date: "2024-04-02", desktop: 0, mobile: 0 },
    { date: "2024-04-03", desktop: 0, mobile:0 },
    { date: "2024-04-04", desktop: 0, mobile:0 },
    { date: "2024-04-05", desktop: 373, mobile:373+ 290 },
    { date: "2024-04-06", desktop: 301, mobile:301+ 340 },
    { date: "2024-04-07", desktop: 245, mobile:245+ 180 },
    { date: "2024-04-08", desktop: 409, mobile:409+ 320 },
    { date: "2024-04-09", desktop: 59, mobile: 59+110 },
    { date: "2024-04-10", desktop: 261, mobile:261+ 190 },
    { date: "2024-04-11", desktop: 327, mobile:327+ 350 },
    { date: "2024-04-12", desktop: 292, mobile:292+ 210 },
    { date: "2024-04-13", desktop: 342, mobile:342+ 380 },
    { date: "2024-04-14", desktop: 137, mobile:137+ 220 },
    { date: "2024-04-15", desktop: 120, mobile:120+ 170 },
    { date: "2024-04-16", desktop: 138, mobile:138+ 190 },
    { date: "2024-04-17", desktop: 446, mobile:446+ 360 },
    { date: "2024-04-18", desktop: 0, mobile:0 },
    { date: "2024-04-19", desktop: 243, mobile:243+ 180 },
    { date: "2024-04-20", desktop: 89, mobile: 89+150 },
    { date: "2024-04-21", desktop: 137, mobile:137+ 200 },
    { date: "2024-04-22", desktop: 224, mobile:224+ 170 },
    { date: "2024-04-23", desktop: 138, mobile:138+ 230 },
    { date: "2024-04-24", desktop: 387, mobile:387+ 290 },
    { date: "2024-04-25", desktop: 215, mobile:215+ 250 },
    { date: "2024-04-26", desktop: 75, mobile: 75+130 },
    { date: "2024-04-27", desktop: 383, mobile:383+ 420 },
    { date: "2024-04-28", desktop: 122, mobile:122+ 180 },
    { date: "2024-04-29", desktop: 315, mobile:315+ 240 },
    { date: "2024-04-30", desktop: 454, mobile:454+ 380 },
    { date: "2024-05-01", desktop: 165, mobile:165+ 220 },
  ]
  
const chartConfig = {
  desktop: {
    label: "Desktop",
    color: "hsl(var(--chart-1))",
  },
  mobile: {
    label: "Mobile",
    color: "hsl(var(--chart-2))",
  },
} satisfies ChartConfig

export default function () {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Area Chart - Stacked</CardTitle>
          <CardDescription>
            Showing total visitors for the last 6 months
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer config={chartConfig}>
            <AreaChart
              accessibilityLayer
              data={chartData}
              margin={{
                left: 12,
                right: 12,
              }}
            >
              <CartesianGrid vertical={false} />
              <XAxis
                dataKey="month"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                tickFormatter={(value) => value.slice(0, 3)}
              />
              <ChartTooltip
                cursor={false}
                content={<ChartTooltipContent indicator="dot" />}
              />
              <Area
                dataKey="mobile"
                type="natural"
                fill="var(--color-mobile)"
                fillOpacity={0.4}
                stroke="var(--color-mobile)"
                stackId="a"
              />
              <Area
                dataKey="desktop"
                type="natural"
                fill="var(--color-desktop)"
                fillOpacity={0.4}
                stroke="var(--color-desktop)"
                stackId="a"
              />
            </AreaChart>
          </ChartContainer>
        </CardContent>
        <CardFooter>
          <div className="flex w-full items-start gap-2 text-sm">
            <div className="grid gap-2">
              <div className="flex items-center gap-2 font-medium leading-none">
                Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
              </div>
              <div className="flex items-center gap-2 leading-none text-muted-foreground">
                January - June 2024
              </div>
            </div>
          </div>
        </CardFooter>
      </Card>
    )
  }
  

export  function Component() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Line Chart - Multiple</CardTitle>
        <CardDescription>January - June 2024</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer config={chartConfig}>
          <LineChart
            accessibilityLayer
            data={chartData}
            margin={{
              left: 12,
              right: 12,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="month"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
            <Line
              dataKey="desktop"
              type="monotone"
              stroke="var(--color-desktop)"
              strokeWidth={2}
              dot={false}
            />
            <Line
              dataKey="mobile"
              type="monotone"
              stroke="var(--color-mobile)"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ChartContainer>
      </CardContent>
      <CardFooter>
        <div className="flex w-full items-start gap-2 text-sm">
          <div className="grid gap-2">
            <div className="flex items-center gap-2 font-medium leading-none">
              Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-2 leading-none text-muted-foreground">
              Showing total visitors for the last 6 months
            </div>
          </div>
        </div>
      </CardFooter>
    </Card>
  )
}
