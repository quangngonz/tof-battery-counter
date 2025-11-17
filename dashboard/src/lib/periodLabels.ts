import { ChartDataPoint, TimeRange } from '@/lib/chartDataProcessors';
import { getStartOfWeek, getWeekLabel, formatDate } from '@/lib/dateUtils';

export const getPeriodLabel = (
  timeRange: TimeRange,
  data: ChartDataPoint[],
  offset: number,
  showDetailed: boolean,
  selectedDate: string | null,
  selectedWeek: string | null
): string => {
  const now = new Date();

  switch (timeRange) {
    case 'day': {
      if (selectedDate) {
        return selectedDate;
      }
      if (data && data.length > 0) {
        const newestDate = new Date(
          Math.max(...data.map((d) => new Date(d.timestamp).getTime()))
        );
        newestDate.setDate(newestDate.getDate() + offset);
        return formatDate(newestDate, {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        });
      }
      return 'No data';
    }
    case 'week': {
      if (showDetailed) {
        const endDate = new Date(now);
        endDate.setDate(endDate.getDate() + offset);
        const startDate = new Date(endDate);
        startDate.setDate(startDate.getDate() - 29);
        return `${formatDate(startDate, {
          month: 'short',
          day: 'numeric',
        })} - ${formatDate(endDate, {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        })}`;
      }
      if (selectedWeek) {
        return selectedWeek;
      }
      const weekStart = getStartOfWeek(now);
      weekStart.setDate(weekStart.getDate() + offset * 7);
      return getWeekLabel(weekStart);
    }
    case 'month': {
      const date = new Date(now);
      date.setMonth(date.getMonth() + offset);
      return formatDate(date, {
        month: 'long',
        year: 'numeric',
      });
    }
    case 'all':
      return 'All Time';
  }
};
