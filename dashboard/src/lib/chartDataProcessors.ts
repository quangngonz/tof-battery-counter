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

  // Filter data for the target date
  const filteredData = data.filter((item) => {
    const itemDate = new Date(item.timestamp);
    const dateKey = formatDate(itemDate, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
    return dateKey === targetDate;
  });

  // Aggregate data into 10-minute intervals
  const intervalData: { [key: string]: number } = {};

  filteredData.forEach((item) => {
    const itemDate = new Date(item.timestamp);
    const hours = itemDate.getHours();
    const minutes = itemDate.getMinutes();

    // Round down to nearest 10-minute interval
    const roundedMinutes = Math.floor(minutes / 10) * 10;

    // Create time key (e.g., "14:20")
    const timeKey = `${hours}:${roundedMinutes.toString().padStart(2, '0')}`;

    intervalData[timeKey] = (intervalData[timeKey] || 0) + item.amount;
  });

  // Convert to array and sort by time
  return Object.entries(intervalData)
    .map(([timeKey, batteries]) => {
      const [hour, minute] = timeKey.split(':').map(Number);
      const date = new Date();
      date.setHours(hour, minute);

      return {
        date: formatTime(date, {
          hour: 'numeric',
          minute: '2-digit',
        }),
        batteries,
        // Store numeric values for sorting
        _hour: hour,
        _minute: minute,
      };
    })
    .sort((a, b) => {
      // @ts-ignore - _hour and _minute are temporary sorting fields
      const timeA = a._hour * 60 + a._minute;
      // @ts-ignore
      const timeB = b._hour * 60 + b._minute;
      return timeA - timeB;
    })
    .map(({ date, batteries }) => ({ date, batteries }));
};

export const processWeekDetailedData = (
  data: ChartDataPoint[],
  startDate: Date,
  endDate: Date
): ProcessedChartData[] => {
  const hourlyData: { [key: string]: number } = {};

  data.forEach((item) => {
    const itemDate = new Date(item.timestamp);
    if (itemDate >= startDate && itemDate <= endDate) {
      // Group by hour
      const dateKey = formatDate(itemDate, {
        month: 'short',
        day: 'numeric',
      });
      const hour = itemDate.getHours();
      const timeKey = `${dateKey} ${hour}:00`;
      hourlyData[timeKey] = (hourlyData[timeKey] || 0) + item.amount;
    }
  });

  // Convert to array and sort by timestamp
  return Object.entries(hourlyData)
    .map(([timeKey, batteries]) => {
      const [datePart, timePart] = timeKey.split(' ');
      return {
        date: `${datePart} ${timePart}`,
        batteries,
        _sortKey: timeKey,
      };
    })
    .sort((a, b) => {
      const dateA = new Date(a._sortKey.replace(' ', ' 2025 '));
      const dateB = new Date(b._sortKey.replace(' ', ' 2025 '));
      return dateA.getTime() - dateB.getTime();
    })
    .map(({ date, batteries }) => ({ date, batteries }));
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
  const hourlyData: {
    [key: string]: { batteries: number; weekLabel: string };
  } = {};

  data.forEach((item) => {
    const itemDate = new Date(item.timestamp);
    if (itemDate >= monthStart && itemDate <= monthEnd) {
      // Group by hour
      const dateKey = formatDate(itemDate, {
        month: 'short',
        day: 'numeric',
      });
      const hour = itemDate.getHours();
      const timeKey = `${dateKey} ${hour}:00`;

      const weekStart = getStartOfWeek(itemDate);
      const weekLabel = getWeekLabel(weekStart);

      if (!hourlyData[timeKey]) {
        hourlyData[timeKey] = { batteries: 0, weekLabel };
      }
      hourlyData[timeKey].batteries += item.amount;
    }
  });

  // Convert to array and sort by timestamp
  return Object.entries(hourlyData)
    .map(([date, { batteries, weekLabel }]) => ({
      date,
      weekLabel,
      batteries,
      _sortKey: date,
    }))
    .sort((a, b) => {
      const dateA = new Date(
        a._sortKey.replace(' ', ` ${monthStart.getFullYear()} `)
      );
      const dateB = new Date(
        b._sortKey.replace(' ', ` ${monthStart.getFullYear()} `)
      );
      return dateA.getTime() - dateB.getTime();
    })
    .map(({ date, weekLabel, batteries }) => ({ date, weekLabel, batteries }));
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
  const dailyData: { [key: string]: number } = {};

  data.forEach((item) => {
    const itemDate = new Date(item.timestamp);
    const dateKey = formatDate(itemDate, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
    dailyData[dateKey] = (dailyData[dateKey] || 0) + item.amount;
  });

  return Object.entries(dailyData)
    .map(([date, batteries]) => ({
      date,
      batteries,
      _sortKey: new Date(date).getTime(),
    }))
    .sort((a, b) => a._sortKey - b._sortKey)
    .map(({ date, batteries }) => ({ date, batteries }));
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
