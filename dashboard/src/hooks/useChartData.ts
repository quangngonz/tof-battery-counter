import { useMemo } from 'react';
import {
  ChartDataPoint,
  ProcessedChartData,
  TimeRange,
  processDayData,
  processWeekDetailedData,
  processWeekData,
  processMonthDetailedData,
  processMonthData,
  processAllDetailedData,
  processAllData,
} from '@/lib/chartDataProcessors';
import { getStartOfWeek, formatDate } from '@/lib/dateUtils';

interface UseChartDataParams {
  data: ChartDataPoint[];
  timeRange: TimeRange;
  offset: number;
  showDetailed: boolean;
  selectedDate: string | null;
  selectedWeek: string | null;
}

export const useChartData = ({
  data,
  timeRange,
  offset,
  showDetailed,
  selectedDate,
  selectedWeek,
}: UseChartDataParams): ProcessedChartData[] => {
  return useMemo(() => {
    if (!data || data.length === 0) return [];

    const now = new Date();

    switch (timeRange) {
      case 'day': {
        let targetDate: string | null;

        if (selectedDate) {
          targetDate = selectedDate;
        } else if (data.length > 0) {
          const newestDate = new Date(
            Math.max(...data.map((d) => new Date(d.timestamp).getTime()))
          );
          newestDate.setDate(newestDate.getDate() + offset);
          targetDate = formatDate(newestDate, {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          });
        } else {
          targetDate = null;
        }

        return processDayData(data, targetDate);
      }

      case 'week': {
        if (showDetailed) {
          const endDate = new Date(now);
          endDate.setDate(endDate.getDate() + offset);
          endDate.setHours(23, 59, 59, 999);
          const startDate = new Date(endDate);
          startDate.setDate(startDate.getDate() - 29);
          startDate.setHours(0, 0, 0, 0);

          return processWeekDetailedData(data, startDate, endDate);
        }

        let weekStart: Date, weekEnd: Date;

        if (selectedWeek) {
          const weekParts = selectedWeek.split(' ');
          const startDay = parseInt(weekParts[1]);
          const monthName = weekParts[0];

          const monthDate = new Date(now);
          monthDate.setMonth(monthDate.getMonth() + offset);
          const year = monthDate.getFullYear();

          weekStart = new Date(`${monthName} ${startDay}, ${year}`);
          weekEnd = new Date(weekStart);
          weekEnd.setDate(weekEnd.getDate() + 7);
        } else {
          weekStart = getStartOfWeek(now);
          weekStart.setDate(weekStart.getDate() + offset * 7);
          weekEnd = new Date(weekStart);
          weekEnd.setDate(weekEnd.getDate() + 7);
        }

        return processWeekData(data, weekStart, weekEnd);
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
          return processMonthDetailedData(data, monthStart, monthEnd);
        } else {
          return processMonthData(data, monthStart, monthEnd);
        }
      }

      case 'all': {
        if (showDetailed) {
          return processAllDetailedData(data);
        }
        return processAllData(data);
      }
    }
  }, [data, timeRange, offset, showDetailed, selectedDate, selectedWeek]);
};
