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
  Cell,
} from 'recharts';
import { useState } from 'react';
import { ChartDataPoint, TimeRange } from '@/lib/chartDataProcessors';
import { useChartData } from '@/hooks/useChartData';
import { useNavigation } from '@/hooks/useNavigation';
import { getPeriodLabel } from '@/lib/periodLabels';

interface BatteryChartProps {
  data: ChartDataPoint[];
  loading?: boolean;
}

export const BatteryChart = ({ data, loading }: BatteryChartProps) => {
  const [timeRange, setTimeRange] = useState<TimeRange>('all');
  const [offset, setOffset] = useState(0);
  const [showDetailed, setShowDetailed] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedWeek, setSelectedWeek] = useState<string | null>(null);

  const chartData = useChartData({
    data,
    timeRange,
    offset,
    showDetailed,
    selectedDate,
    selectedWeek,
  });

  const { canNavigateNext, canNavigatePrev } = useNavigation({
    data,
    timeRange,
    offset,
    showDetailed,
    selectedDate,
  });

  const periodLabel = getPeriodLabel(
    timeRange,
    data,
    offset,
    showDetailed,
    selectedDate,
    selectedWeek
  );

  const handleTimeRangeChange = (value: TimeRange) => {
    setTimeRange(value);
    setOffset(0);
    if (value !== 'day') {
      setSelectedDate(null);
    }
    if (value !== 'week') {
      setSelectedWeek(null);
    }
  };

  const handleBarClick = (entry: {
    date?: string;
    fullDate?: string;
    weekLabel?: string;
    batteries?: number;
  }) => {
    if (!entry) return;

    if (timeRange === 'week') {
      const targetDate = entry.fullDate || entry.date;
      if (!targetDate) return;
      setSelectedDate(targetDate);
      setTimeRange('day');
    } else if (timeRange === 'month') {
      if (!entry.date) return;
      if (showDetailed) {
        if (entry.weekLabel) {
          setSelectedWeek(entry.weekLabel);
          setTimeRange('week');
          setShowDetailed(false);
        }
      } else {
        setSelectedWeek(entry.date);
        setTimeRange('week');
        setShowDetailed(false);
      }
    } else if (timeRange === 'all') {
      if (!entry.date) return;
      if (showDetailed) {
        setSelectedDate(entry.date);
        setTimeRange('day');
      } else {
        const [monthStr, yearStr] = entry.date.split(' ');
        const monthDate = new Date(`${monthStr} 1, ${yearStr}`);
        const now = new Date();
        const monthsDiff =
          (monthDate.getFullYear() - now.getFullYear()) * 12 +
          (monthDate.getMonth() - now.getMonth());
        setOffset(monthsDiff);
        setTimeRange('month');
      }
    }
  };

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

          {timeRange !== 'day' && (
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
                {timeRange !== 'all' && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setOffset(offset - 1)}
                      disabled={!canNavigatePrev}
                    >
                      <ChevronLeft className="h-4 w-4 mr-1" />
                      Previous
                    </Button>
                  </>
                )}

                <span className="text-sm font-medium whitespace-nowrap">
                  {periodLabel}
                </span>

                {timeRange !== 'all' && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setOffset(offset + 1)}
                      disabled={!canNavigateNext}
                    >
                      Next
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </>
                )}
              </div>
            </div>
          )}

          {timeRange === 'day' && (
            <div className="flex flex-col space-y-3 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
              {selectedDate && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    if (selectedWeek) {
                      setTimeRange('week');
                    } else {
                      setTimeRange('week');
                      setShowDetailed(true);
                    }
                    setSelectedDate(null);
                  }}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Back to Week
                </Button>
              )}

              <div className="flex items-center justify-between sm:justify-end space-x-3 ml-auto">
                {!selectedDate && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setOffset(offset - 1)}
                      disabled={!canNavigatePrev}
                    >
                      <ChevronLeft className="h-4 w-4 mr-1" />
                      Previous
                    </Button>
                  </>
                )}

                <span className="text-sm font-medium whitespace-nowrap">
                  {periodLabel}
                </span>

                {!selectedDate && (
                  <>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setOffset(offset + 1)}
                      disabled={!canNavigateNext}
                    >
                      Next
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </>
                )}
              </div>
            </div>
          )}

          {timeRange === 'week' && selectedWeek && (
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setTimeRange('month');
                  setSelectedWeek(null);
                }}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back to Month
              </Button>

              <span className="text-sm font-medium">{periodLabel}</span>
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
                cursor={
                  timeRange === 'week' ||
                  timeRange === 'month' ||
                  timeRange === 'all'
                    ? 'pointer'
                    : 'default'
                }
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    onClick={() => handleBarClick(entry)}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
};
