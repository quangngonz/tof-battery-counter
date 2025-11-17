import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useState, useMemo } from 'react';

interface ChartDataPoint {
  timestamp: string;
  amount: number;
}

interface BatteryChartProps {
  data: ChartDataPoint[];
  loading?: boolean;
}

type TimeRange = 'day' | 'week' | 'month' | 'all';

export const BatteryChart = ({ data, loading }: BatteryChartProps) => {
  const [timeRange, setTimeRange] = useState<TimeRange>('all');
  const [offset, setOffset] = useState(0);
  const [showDetailed, setShowDetailed] = useState(false);

  const getStartOfWeek = (date: Date) => {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day;
    return new Date(d.setDate(diff));
  };

  const getWeekLabel = (startDate: Date) => {
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + 6);

    const startMonth = startDate.toLocaleDateString('en-US', {
      month: 'short',
    });
    const endMonth = endDate.toLocaleDateString('en-US', { month: 'short' });
    const startDay = startDate.getDate();
    const endDay = endDate.getDate();

    if (startMonth === endMonth) {
      return `${startMonth} ${startDay}-${endDay}`;
    }
    return `${startMonth} ${startDay} - ${endMonth} ${endDay}`;
  };

  const getPeriodLabel = () => {
    const now = new Date();

    switch (timeRange) {
      case 'day': {
        const endDate = new Date(now);
        endDate.setDate(endDate.getDate() + offset);
        const startDate = new Date(endDate);
        startDate.setDate(startDate.getDate() - 29);
        return `${startDate.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        })} - ${endDate.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        })}`;
      }
      case 'week': {
        const weekStart = getStartOfWeek(now);
        weekStart.setDate(weekStart.getDate() + offset * 7);
        return getWeekLabel(weekStart);
      }
      case 'month': {
        const date = new Date(now);
        date.setMonth(date.getMonth() + offset);
        return date.toLocaleDateString('en-US', {
          month: 'long',
          year: 'numeric',
        });
      }
      case 'all':
        return 'All Time';
    }
  };

  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];

    const now = new Date();

    switch (timeRange) {
      case 'day': {
        // 30 day range
        const endDate = new Date(now);
        endDate.setDate(endDate.getDate() + offset);
        endDate.setHours(23, 59, 59, 999);
        const startDate = new Date(endDate);
        startDate.setDate(startDate.getDate() - 29);
        startDate.setHours(0, 0, 0, 0);

        if (showDetailed) {
          // Show individual entries for each day within the 30-day range
          return data
            .filter((item) => {
              const itemDate = new Date(item.timestamp);
              return itemDate >= startDate && itemDate <= endDate;
            })
            .sort(
              (a, b) =>
                new Date(a.timestamp).getTime() -
                new Date(b.timestamp).getTime()
            )
            .map((item) => ({
              date: new Date(item.timestamp).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
              }),
              batteries: item.amount,
            }));
        } else {
          // Show daily aggregates for 30 days
          const dailyData: { [key: string]: number } = {};

          data.forEach((item) => {
            const itemDate = new Date(item.timestamp);
            if (itemDate >= startDate && itemDate <= endDate) {
              const dateKey = itemDate.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
              });
              dailyData[dateKey] = (dailyData[dateKey] || 0) + item.amount;
            }
          });

          const result = [];
          const currentDate = new Date(startDate);
          while (currentDate <= endDate) {
            const dateKey = currentDate.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
            });
            result.push({
              date: dateKey,
              batteries: dailyData[dateKey] || 0,
            });
            currentDate.setDate(currentDate.getDate() + 1);
          }

          return result;
        }
      }

      case 'week': {
        const weekStart = getStartOfWeek(now);
        weekStart.setDate(weekStart.getDate() + offset * 7);
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekEnd.getDate() + 7);

        if (showDetailed) {
          // Show individual entries within the week
          return data
            .filter((item) => {
              const itemDate = new Date(item.timestamp);
              return itemDate >= weekStart && itemDate < weekEnd;
            })
            .sort(
              (a, b) =>
                new Date(a.timestamp).getTime() -
                new Date(b.timestamp).getTime()
            )
            .map((item) => ({
              date: new Date(item.timestamp).toLocaleDateString('en-US', {
                weekday: 'short',
                hour: 'numeric',
                minute: '2-digit',
              }),
              batteries: item.amount,
            }));
        } else {
          // Show daily aggregates for the week
          const weekData: { [key: string]: number } = {};

          data.forEach((item) => {
            const itemDate = new Date(item.timestamp);
            if (itemDate >= weekStart && itemDate < weekEnd) {
              const dayName = itemDate.toLocaleDateString('en-US', {
                weekday: 'short',
              });
              weekData[dayName] = (weekData[dayName] || 0) + item.amount;
            }
          });

          const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
          return daysOfWeek.map((day) => ({
            date: day,
            batteries: weekData[day] || 0,
          }));
        }
      }

      case 'month': {
        const monthDate = new Date(now);
        monthDate.setMonth(monthDate.getMonth() + offset);
        const monthStart = new Date(
          monthDate.getFullYear(),
          monthDate.getMonth(),
          1
        );
        const monthEnd = new Date(
          monthDate.getFullYear(),
          monthDate.getMonth() + 1,
          0
        );

        if (showDetailed) {
          // Show individual entries within the month
          return data
            .filter((item) => {
              const itemDate = new Date(item.timestamp);
              return itemDate >= monthStart && itemDate <= monthEnd;
            })
            .sort(
              (a, b) =>
                new Date(a.timestamp).getTime() -
                new Date(b.timestamp).getTime()
            )
            .map((item) => ({
              date: new Date(item.timestamp).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
              }),
              batteries: item.amount,
            }));
        } else {
          // Show weekly aggregates for the month
          const weeklyData: { [key: string]: number } = {};

          data.forEach((item) => {
            const itemDate = new Date(item.timestamp);
            if (itemDate >= monthStart && itemDate <= monthEnd) {
              const weekStart = getStartOfWeek(itemDate);
              const weekLabel = getWeekLabel(weekStart);
              weeklyData[weekLabel] =
                (weeklyData[weekLabel] || 0) + item.amount;
            }
          });

          return Object.entries(weeklyData)
            .map(([date, batteries]) => ({ date, batteries }))
            .sort((a, b) => {
              const dateA = new Date(a.date.split(' - ')[0]);
              const dateB = new Date(b.date.split(' - ')[0]);
              return dateA.getTime() - dateB.getTime();
            });
        }
      }

      case 'all': {
        const monthlyData: { [key: string]: number } = {};

        data.forEach((item) => {
          const itemDate = new Date(item.timestamp);
          const monthKey = itemDate.toLocaleDateString('en-US', {
            month: 'short',
            year: 'numeric',
          });
          monthlyData[monthKey] = (monthlyData[monthKey] || 0) + item.amount;
        });

        return Object.entries(monthlyData)
          .map(([date, batteries]) => ({ date, batteries }))
          .sort((a, b) => {
            const dateA = new Date(a.date);
            const dateB = new Date(b.date);
            return dateA.getTime() - dateB.getTime();
          });
      }
    }
  }, [data, timeRange, offset, showDetailed]);

  const handleTimeRangeChange = (value: TimeRange) => {
    setTimeRange(value);
    setOffset(0);
  };

  const canNavigateNext = offset < 0;
  const canNavigatePrev = useMemo(() => {
    if (!data || data.length === 0) return false;

    const oldestDate = new Date(
      Math.min(...data.map((d) => new Date(d.timestamp).getTime()))
    );
    const now = new Date();

    switch (timeRange) {
      case 'day': {
        const endDate = new Date(now);
        endDate.setDate(endDate.getDate() + offset - 30);
        return endDate >= oldestDate;
      }
      case 'week': {
        const weekStart = getStartOfWeek(now);
        weekStart.setDate(weekStart.getDate() + (offset - 1) * 7);
        return weekStart >= oldestDate;
      }
      case 'month': {
        const monthDate = new Date(now);
        monthDate.setMonth(monthDate.getMonth() + offset - 1);
        return monthDate >= oldestDate;
      }
      default:
        return false;
    }
  }, [data, timeRange, offset]);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col space-y-4">
          <div className="flex flex-col space-y-3 sm:flex-row sm:items-start sm:justify-between sm:space-y-0">
            <div>
              <CardTitle>Battery Collection Over Time</CardTitle>
              <CardDescription>
                Number of batteries collected per log entry
              </CardDescription>
            </div>
            <Tabs value={timeRange} onValueChange={handleTimeRangeChange}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="day">Day</TabsTrigger>
                <TabsTrigger value="week">Week</TabsTrigger>
                <TabsTrigger value="month">Month</TabsTrigger>
                <TabsTrigger value="all">All</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {timeRange !== 'all' && (
            <div className="flex flex-col space-y-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="show-detailed"
                  checked={showDetailed}
                  onCheckedChange={(checked) =>
                    setShowDetailed(checked as boolean)
                  }
                />
                <Label
                  htmlFor="show-detailed"
                  className="text-base font-medium cursor-pointer"
                >
                  Show individual entries
                </Label>
              </div>

              <div className="flex items-center justify-between sm:justify-end space-x-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setOffset(offset - 1)}
                  disabled={!canNavigatePrev}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>

                <span className="text-sm font-medium whitespace-nowrap">
                  {getPeriodLabel()}
                </span>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setOffset(offset + 1)}
                  disabled={!canNavigateNext}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-[300px] w-full animate-pulse rounded bg-muted" />
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                className="text-xs text-muted-foreground"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <YAxis
                className="text-xs text-muted-foreground"
                tick={{ fill: 'hsl(var(--muted-foreground))' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                }}
                labelStyle={{ color: 'hsl(var(--foreground))' }}
              />
              <Bar
                dataKey="batteries"
                fill="hsl(var(--primary))"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
};
