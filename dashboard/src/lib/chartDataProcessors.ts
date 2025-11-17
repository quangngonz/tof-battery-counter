import {
  getStartOfWeek,
  getWeekLabel,
  formatDate,
  formatTime,
} from './dateUtils';

export interface ChartDataPoint {
  timestamp: string;
  amount: number;
}

export interface ProcessedChartData {
  date: string;
  fullDate?: string;
  weekLabel?: string;
  batteries: number;
}

export type TimeRange = 'day' | 'week' | 'month' | 'all';

export const processDayData = (
  data: ChartDataPoint[],
  targetDate: string | null
): ProcessedChartData[] => {
  if (!targetDate) return [];

  return data
    .filter((item) => {
      const itemDate = new Date(item.timestamp);
      const dateKey = formatDate(itemDate, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
      return dateKey === targetDate;
    })
    .sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )
    .map((item) => ({
      date: formatTime(new Date(item.timestamp), {
        hour: 'numeric',
        minute: '2-digit',
      }),
      batteries: item.amount,
    }));
};

export const processWeekDetailedData = (
  data: ChartDataPoint[],
  startDate: Date,
  endDate: Date
): ProcessedChartData[] => {
  const dailyData: { [key: string]: number } = {};

  data.forEach((item) => {
    const itemDate = new Date(item.timestamp);
    if (itemDate >= startDate && itemDate <= endDate) {
      const dateKey = formatDate(itemDate, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
      dailyData[dateKey] = (dailyData[dateKey] || 0) + item.amount;
    }
  });

  const result: ProcessedChartData[] = [];
  const currentDate = new Date(startDate);
  while (currentDate <= endDate) {
    const dateKey = formatDate(currentDate, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
    result.push({
      date: dateKey,
      batteries: dailyData[dateKey] || 0,
    });
    currentDate.setDate(currentDate.getDate() + 1);
  }

  return result;
};

export const processWeekData = (
  data: ChartDataPoint[],
  weekStart: Date,
  weekEnd: Date
): ProcessedChartData[] => {
  const weekData: { [key: string]: { count: number; fullDate: string } } = {};

  data.forEach((item) => {
    const itemDate = new Date(item.timestamp);
    if (itemDate >= weekStart && itemDate < weekEnd) {
      const fullDate = formatDate(itemDate, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
      const dayName = formatDate(itemDate, { weekday: 'short' });
      if (!weekData[dayName]) {
        weekData[dayName] = { count: 0, fullDate };
      }
      weekData[dayName].count += item.amount;
    }
  });

  const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  return daysOfWeek.map((day) => ({
    date: day,
    fullDate: weekData[day]?.fullDate,
    batteries: weekData[day]?.count || 0,
  }));
};

export const processMonthDetailedData = (
  data: ChartDataPoint[],
  monthStart: Date,
  monthEnd: Date
): ProcessedChartData[] => {
  return data
    .filter((item) => {
      const itemDate = new Date(item.timestamp);
      return itemDate >= monthStart && itemDate <= monthEnd;
    })
    .sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )
    .map((item) => {
      const itemDate = new Date(item.timestamp);
      const weekStart = getStartOfWeek(itemDate);
      const weekLabel = getWeekLabel(weekStart);
      return {
        date: formatDate(itemDate, {
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
        }),
        weekLabel: weekLabel,
        batteries: item.amount,
      };
    });
};

export const processMonthData = (
  data: ChartDataPoint[],
  monthStart: Date,
  monthEnd: Date
): ProcessedChartData[] => {
  const weeklyData: { [key: string]: number } = {};

  data.forEach((item) => {
    const itemDate = new Date(item.timestamp);
    if (itemDate >= monthStart && itemDate <= monthEnd) {
      const weekStart = getStartOfWeek(itemDate);
      const weekLabel = getWeekLabel(weekStart);
      weeklyData[weekLabel] = (weeklyData[weekLabel] || 0) + item.amount;
    }
  });

  return Object.entries(weeklyData)
    .map(([date, batteries]) => ({ date, batteries }))
    .sort((a, b) => {
      const dateA = new Date(a.date.split(' - ')[0]);
      const dateB = new Date(b.date.split(' - ')[0]);
      return dateA.getTime() - dateB.getTime();
    });
};

export const processAllDetailedData = (
  data: ChartDataPoint[]
): ProcessedChartData[] => {
  return data
    .sort(
      (a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )
    .map((item) => ({
      date: formatDate(new Date(item.timestamp), {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      }),
      batteries: item.amount,
    }));
};

export const processAllData = (
  data: ChartDataPoint[]
): ProcessedChartData[] => {
  const monthlyData: { [key: string]: number } = {};

  data.forEach((item) => {
    const itemDate = new Date(item.timestamp);
    const monthKey = formatDate(itemDate, {
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
};
