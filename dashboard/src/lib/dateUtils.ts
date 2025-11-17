export const getStartOfWeek = (date: Date): Date => {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day;
  return new Date(d.setDate(diff));
};

export const getWeekLabel = (startDate: Date): string => {
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

export const formatDate = (
  date: Date,
  options: Intl.DateTimeFormatOptions
): string => {
  return date.toLocaleDateString('en-US', options);
};

export const formatTime = (
  date: Date,
  options: Intl.DateTimeFormatOptions
): string => {
  return date.toLocaleTimeString('en-US', options);
};
