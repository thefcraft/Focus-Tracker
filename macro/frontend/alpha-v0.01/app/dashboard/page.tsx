"use client";
import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { CheckCircle2, Clock, Target, TrendingUp, AlertCircle, Calendar, PlusCircle, Monitor } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

// Mock data for application usage
const appUsageData = [
  { program_name: 'Chrome', window_title: 'Google - Work Research', timestamp: '2023-06-10 09:15', duration: 45, category: 'Productivity' },
  { program_name: 'VS Code', window_title: 'project.js - MyProject', timestamp: '2023-06-10 10:00', duration: 120, category: 'Development' },
  { program_name: 'Slack', window_title: 'Team Chat - #general', timestamp: '2023-06-10 12:30', duration: 15, category: 'Communication' },
  { program_name: 'Photoshop', window_title: 'banner-design.psd', timestamp: '2023-06-10 13:00', duration: 60, category: 'Design' },
  { program_name: 'Excel', window_title: 'Q2 Report.xlsx', timestamp: '2023-06-10 14:30', duration: 90, category: 'Productivity' },
]

const timeDistributionData = [
  { program_name: 'Chrome', time: 120 },
  { program_name: 'VS Code', time: 180 },
  { program_name: 'Slack', time: 45 },
  { program_name: 'Photoshop', time: 90 },
  { program_name: 'Excel', time: 60 },
]

const applicationUsageTimeline = [
  { time: '08:00', 'Chrome': 20, 'VS Code': 0, 'Slack': 5, 'Photoshop': 0, 'Excel': 0 },
  { time: '10:00', 'Chrome': 15, 'VS Code': 45, 'Slack': 10, 'Photoshop': 0, 'Excel': 0 },
  { time: '12:00', 'Chrome': 30, 'VS Code': 30, 'Slack': 15, 'Photoshop': 25, 'Excel': 0 },
  { time: '14:00', 'Chrome': 25, 'VS Code': 50, 'Slack': 5, 'Photoshop': 20, 'Excel': 30 },
  { time: '16:00', 'Chrome': 30, 'VS Code': 55, 'Slack': 10, 'Photoshop': 45, 'Excel': 30 },
]

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']

export default function EnhancedDashboard() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Productivity Dashboard</h1>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Productivity Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">78%</div>
            <p className="text-xs text-muted-foreground">+2% from last week</p>
            <Progress value={78} className="mt-2" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tasks Completed</CardTitle>
            <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">64/80</div>
            <p className="text-xs text-muted-foreground">80% completion rate</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Focus Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">5h 23m</div>
            <p className="text-xs text-muted-foreground">Average: 4h 45m</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Applications</CardTitle>
            <Monitor className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8</div>
            <p className="text-xs text-muted-foreground">Across 4 categories</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Time Distribution by Application</CardTitle>
            <CardDescription>How you've spent your time across different applications</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={timeDistributionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="time"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {timeDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Application Usage Timeline</CardTitle>
            <CardDescription>Usage patterns throughout the day</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={applicationUsageTimeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                {Object.keys(applicationUsageTimeline[0]).filter(key => key !== 'time').map((key, index) => (
                  <Area key={key} type="monotone" dataKey={key} stackId="1" stroke={COLORS[index % COLORS.length]} fill={COLORS[index % COLORS.length]} />
                ))}
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Application Usage</CardTitle>
            <CardDescription>Your latest application activities</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              {appUsageData.map((app, index) => (
                <li key={index} className="flex items-center space-x-4">
                  <Avatar className="h-9 w-9">
                    <AvatarImage src={`/placeholder.svg?text=${app.program_name[0]}`} alt={app.program_name} />
                    <AvatarFallback>{app.program_name[0]}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium leading-none">{app.program_name}</p>
                    <p className="text-sm text-muted-foreground">{app.window_title}</p>
                    <p className="text-xs text-muted-foreground">{app.timestamp} | Duration: {app.duration} min</p>
                  </div>
                  <div className="rounded-full bg-muted px-2 py-1 text-xs font-medium">
                    {app.category}
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Most Used Applications</CardTitle>
            <CardDescription>Top 5 apps by usage time</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              {timeDistributionData.sort((a, b) => b.time - a.time).slice(0, 5).map((app, index) => (
                <li key={index} className="flex items-center space-x-4">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={`/placeholder.svg?text=${app.program_name[0]}`} alt={app.program_name} />
                    <AvatarFallback>{app.program_name[0]}</AvatarFallback>
                  </Avatar>
                  <div className="flex-1 space-y-1">
                    <p className="text-sm font-medium leading-none">{app.program_name}</p>
                    <p className="text-sm text-muted-foreground">{app.time} minutes</p>
                  </div>
                  <Progress value={(app.time / Math.max(...timeDistributionData.map(a => a.time))) * 100} className="w-[60px]" />
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 mb-8">
        <Card>
          <CardHeader>
            <CardTitle>Upcoming Deadlines</CardTitle>
            <CardDescription>Tasks and projects due soon</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              <li className="flex items-center justify-between">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
                  <span>Quarterly Report</span>
                </div>
                <span className="text-sm text-muted-foreground">Tomorrow</span>
              </li>
              <li className="flex items-center justify-between">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 text-yellow-500 mr-2" />
                  <span>Team Presentation</span>
                </div>
                <span className="text-sm text-muted-foreground">In 3 days</span>
              </li>
              <li className="flex items-center justify-between">
                <div className="flex items-center">
                  <AlertCircle className="h-5 w-5 text-green-500 mr-2" />
                  <span>Project Milestone</span>
                </div>
                <span className="text-sm text-muted-foreground">Next week</span>
              </li>
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Productivity Tips</CardTitle>
            <CardDescription>Boost your efficiency with these tips</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              <li className="flex items-center">
                <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center mr-2">
                  <span className="text-blue-500 font-bold">1</span>
                </div>
                <span>Use the Pomodoro Technique for better focus</span>
              </li>
              <li className="flex items-center">
                <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center mr-2">
                  <span className="text-green-500 font-bold">2</span>
                </div>
                <span>Take regular breaks to maintain productivity</span>
              </li>
              <li className="flex items-center">
                <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center mr-2">
                  <span className="text-purple-500 font-bold">3</span>
                </div>
                <span>Prioritize tasks using the Eisenhower Matrix</span>
              </li>
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Frequently used productivity actions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <Button className="w-full">
                <PlusCircle className="mr-2 h-4 w-4" /> New Task
              </Button>
              <Button className="w-full">
                <Clock className="mr-2 h-4 w-4" /> Start Timer
              </Button>
              <Button className="w-full">
                <Target className="mr-2 h-4 w-4" /> Set Goal
              </Button>
              <Button className="w-full">
                <Calendar className="mr-2 h-4 w-4" /> Schedule
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}