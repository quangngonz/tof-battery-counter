import { useMemo } from 'react';
import { ChartDataPoint, TimeRange } from '@/lib/chartDataProcessors';
import { getStartOfWeek } from '@/lib/dateUtils';

interface UseNavigationParams {
  data: ChartDataPoint[];
  timeRange: TimeRange;
  offset: number;
  showDetailed: boolean;
  selectedDate: string | null;
}

export const useNavigation = ({
  data,
  timeRange,
  offset,
  showDetailed,
  selectedDate,
}: UseNavigationParams) => {
  const canNavigateNext = offset < 0;

  const canNavigatePrev = useMemo(() => {
    if (!data || data.length === 0) return false;

    const oldestDate = new Date(
      Math.min(...data.map((d) => new Date(d.timestamp).getTime()))
    );
    const now = new Date();

    switch (timeRange) {
      case 'day': {
        if (selectedDate) return false;
        const targetDate = new Date(
          Math.max(...data.map((d) => new Date(d.timestamp).getTime()))
        );
        targetDate.setDate(targetDate.getDate() + offset - 1);
        return targetDate >= oldestDate;
      }
      case 'week': {
        if (showDetailed) {
          const endDate = new Date(now);
          endDate.setDate(endDate.getDate() + offset - 30);
          return endDate >= oldestDate;
        }
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
  }, [data, timeRange, offset, showDetailed, selectedDate]);

  return { canNavigateNext, canNavigatePrev };
};
