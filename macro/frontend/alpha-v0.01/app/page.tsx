"use client";
import React, { useState, useMemo, useEffect } from "react";
import { Bell, Calendar, Home, Moon, Settings, Sun, User, SettingsIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle,
  CardDescription,
  CardFooter, } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Pie, PieChart } from "recharts"
import { TrendingUp } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import { BarChart, Clock, Download, FileSpreadsheet, File, } from 'lucide-react'
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"

const api = "http://127.0.0.1:8000";

const formatTime = (seconds: number) => {
  const minutes = Math.max(Math.floor(seconds / 60), 1);
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours == 0) return `${mins}m`;
  return `${hours}h ${mins}m`;
};
const CategoryIcon = ({ category }: {category: string}) => {
  switch (category) {
    case 'IDE':
      return <FileSpreadsheet className="w-6 h-6 text-blue-500" />
    // case 'Browser':
    //   return <Globe className="w-6 h-6 text-green-500" />
    // case 'Communication':
    //   return <MessageSquare className="w-6 h-6 text-purple-500" />
    // case 'Design':
    //   return <Palette className="w-6 h-6 text-orange-500" />
    default:
      return <File className="w-6 h-6 text-gray-500" />
  }
}




export default function Dashboard() {
  const [darkMode, setDarkMode] = useState(true);

  interface ProgramSummary {
    [key: string]: number;
  }
  interface ProgramData {
    program_name: string;
    window_title: string;
    timestamp: string;
    duration: number;
  }
  interface State {
    data: ProgramData[];
    summary: ProgramSummary;
    loading: boolean;
    error: string | null;
  }

  const [state, setState] = useState<State>({
    data: [],
    summary: {},
    loading: true,
    error: null
  });
  
  const Timeline = ({ data }: {data: ProgramData[]}) => (
    <div className="space-y-2">
      {data.map((item, index) => (
        <div key={index} className="flex items-center space-x-4 p-4 bg-card rounded-lg shadow-sm">
          <img
            src={api + `/icon/${item.program_name}.png`}
            alt={item.program_name}
            className="w-6 h-6 mr-2"
          />
          <div className="flex-grow">
            <h3 className="font-semibold">{item.program_name}</h3>
            <p className="text-sm text-muted-foreground">{item.window_title}</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium">{item.timestamp}</p>
            <p className="text-sm text-muted-foreground">{formatTime(item.duration)}</p>
          </div>
        </div>
      ))}
    </div>
  )

  const Chart = ({ summary }: {summary: ProgramSummary}) => {
    
    interface NameDuration {
      program_name: string;
      duration: number;
    }
    var nameDuration: NameDuration[] = Object.entries(summary).map(([program_name, duration], index) => (
      {
        program_name: program_name,
        duration: duration
      }
    ))
    nameDuration.sort((a, b) => b.duration-a.duration);
    const topPrograms = nameDuration.slice(0, 5);
    // Calculate the sum of durations of other programs
    const otherDurationSum = nameDuration.slice(5).reduce((acc, program) => acc + program.duration, 0);
    if (otherDurationSum !== 0) {
      let other: NameDuration = {
        program_name: "others",
        duration: otherDurationSum
      }
      topPrograms.push(other);
    }
    
    const maxDuration = topPrograms.reduce((acc, program) => acc + program.duration, 0) + otherDurationSum;

    const colors = ["red", "green", "yellow", "blue", "gray", "white"];

    const chartData = topPrograms.map((program: NameDuration, index) => {
      return { name: program.program_name, percentage: parseFloat((program.duration / 60).toFixed(2)), fill: colors[index] };
    })
    const chartConfig = {} satisfies ChartConfig
    return (
      <Card className="flex flex-col w-full">
        <CardHeader className="items-center pb-0  w-full">
          <CardTitle>Pie Chart - Label</CardTitle>
          <CardDescription>2024-09-14</CardDescription>
        </CardHeader>
        <CardContent className="flex-1 pb-0  w-full">
          <ChartContainer
            config={chartConfig}
            className="mx-auto aspect-square max-h-[250px] pb-0 [&_.recharts-pie-label-text]:fill-foreground w-full"
          >
            <PieChart>
              <ChartTooltip content={<ChartTooltipContent hideLabel />} />
              <Pie data={chartData} dataKey="percentage" label nameKey="name" className=" w-full"/>
            </PieChart>
          </ChartContainer>
        </CardContent>
        <CardFooter className="flex-col gap-2 text-sm">
          <div className="flex items-center gap-2 font-medium leading-none">
            Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
          </div>
          <div className="leading-none text-muted-foreground">
            Showing total visitors for the last 6 months
          </div>
        </CardFooter>
      </Card>
    );
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(api + "/summary/");
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        const response_data = await fetch(api + "/data/");
        if (!response_data.ok) {
          throw new Error("Network response was not ok");
        }
        const result: ProgramSummary = await response.json();
        const data: ProgramData[] = await response_data.json();
        setState({
          data: data,
          summary: result,
          loading: false,
          error: null
        });
      } catch (error: any) {
        setState({
          data: [],
          summary: {},
          loading: false,
          error: (error as Error).message
        });
      }
    };

    fetchData();
  }, []); // Empty dependency array means this useEffect runs once on mount
  
  const { data, summary, loading, error } = state;
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  

  const totalScreenTime = Object.entries(summary).map(([program, duration], index) => duration).reduce((acc, duration) => acc + duration, 0);

  return (
    <div className={`min-h-screen ${darkMode ? "dark" : ""}`}>
      <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
        {/* Sidebar */}
        <aside className="w-64 bg-white dark:bg-gray-800 p-4">
          <div className="flex items-center mb-8">
            <img
              src="/placeholder.svg?height=32&width=32"
              alt="Logo"
              className="h-8 w-8 mr-2"
            />
            <h1 className="text-xl font-bold">DigitalBalance</h1>
          </div>
          <nav className="space-y-2">
            <Button variant="ghost" className="w-full justify-start">
              <Home className="mr-2 h-4 w-4" /> Dashboard
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Calendar className="mr-2 h-4 w-4" /> Insights
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              <Settings className="mr-2 h-4 w-4" /> Settings
            </Button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8 overflow-auto">
          {/* Header */}
          <header className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold">Digital Wellbeing Dashboard</h2>
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setDarkMode(!darkMode)}
              >
                {darkMode ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </Button>
              <Button variant="ghost" size="icon">
                <Bell className="h-5 w-5" />
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <User className="h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>Profile</DropdownMenuItem>
                  <DropdownMenuItem>Settings</DropdownMenuItem>
                  <DropdownMenuItem>Logout</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </header>

          {/* Screen Time Overview */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Today's Screen Time</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div className="text-4xl font-bold">
                  {formatTime(totalScreenTime)}
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">
                    Daily Goal: 5h
                  </p>
                  <p className="text-sm text-green-500">
                    {formatTime(300*60 - totalScreenTime)} left
                  </p>
                </div>
              </div>
              <Progress
                value={(totalScreenTime / 60 / 300) * 100}
                className="mt-4"
              />
            </CardContent>
          </Card>

          {/* App Usage Breakdown */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>App Usage Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                
              {Object.entries(summary).map(([program, duration], index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center"
                  >
                    <div className="flex items-center">
                      <img
                        src={api + `/icon/${program}.png`}
                        alt={program}
                        className="w-6 h-6 mr-2"
                      />
                      <span>{program}</span>
                    </div>
                    <span>{formatTime(duration)}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Digital Wellbeing Score */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Digital Wellbeing Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center">
                <div className="relative w-48 h-48">
                  <svg className="w-full h-full" viewBox="0 0 100 100">
                    <circle
                      className="text-gray-200 stroke-current"
                      strokeWidth="10"
                      cx="50"
                      cy="50"
                      r="40"
                      fill="transparent"
                    ></circle>
                    <circle
                      className="text-blue-600 progress-ring stroke-current"
                      strokeWidth="10"
                      strokeLinecap="round"
                      cx="50"
                      cy="50"
                      r="40"
                      fill="transparent"
                      strokeDasharray="251.2"
                      strokeDashoffset="50.24"
                      transform="rotate(-90 50 50)"
                    ></circle>
                    <text
                      x="50"
                      y="50"
                      fontFamily="Verdana"
                      fontSize="20"
                      textAnchor="middle"
                      alignmentBaseline="middle"
                      fill="currentColor"
                    >
                      80%
                    </text>
                  </svg>
                </div>
              </div>
              <p className="text-center mt-4">
                Great job! Your digital habits are balanced.
              </p>
            </CardContent>
          </Card>

          <div className="my-8">
            <h2 className="text-xl font-semibold mb-4">Time Distribution</h2>
            <Chart summary={summary} />
          </div>

          {/* Digital Wellbeing Tips */}
          <Card>
            <CardHeader>
              <CardTitle>Wellbeing Tips</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                <li className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center mr-2">
                    <span className="text-blue-600 text-sm">1</span>
                  </div>
                  <p>
                    Take a 5-minute break every hour to reduce eye strain and
                    improve focus.
                  </p>
                </li>
                <li className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center mr-2">
                    <span className="text-blue-600 text-sm">2</span>
                  </div>
                  <p>
                    Enable night mode on your devices to improve sleep quality.
                  </p>
                </li>
                <li className="flex items-start">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center mr-2">
                    <span className="text-blue-600 text-sm">3</span>
                  </div>
                  <p>
                    Practice the 20-20-20 rule: Every 20 minutes, look at
                    something 20 feet away for 20 seconds.
                  </p>
                </li>
              </ul>
            </CardContent>
          </Card>

          
            
          <div className="flex justify-between items-center mt-8 mb-4">
            <h2 className="text-xl font-semibold">Activity Timeline</h2>
            <Input type="date" className="w-auto" />
          </div>
          <Timeline data={data} />
          <div className="mt-8 flex justify-between items-center">
            <h2 className="text-xl font-semibold">Reports</h2>
            <div className="space-x-2">
              <Button variant="outline">
                <FileSpreadsheet className="mr-2 h-4 w-4" />
                Export CSV
              </Button>
              <Button variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Download PDF
              </Button>
            </div>
          </div>

        </main>
      </div>
    </div>
  );
}
