import { useQuery } from '@tanstack/react-query';
import { Battery, Droplets, Leaf } from 'lucide-react';
import { DashboardHeader } from '@/components/DashboardHeader';
import { StatCard } from '@/components/StatCard';
import { BatteryChart } from '@/components/BatteryChart';
import { toast } from 'sonner';

// Check if development environment
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';
// const API_BASE_URL = 'https://asep-battery-counter.vercel.app/api';
// const API_BASE_URL = 'http://localhost:3000';

interface StatsData {
  totalBatteries: number;
  soilSaved: number;
  waterSaved: number;
}

interface LogEntry {
  timestamp: string;
  amount: number;
}

const fetchStats = async (): Promise<StatsData> => {
  const response = await fetch(`${API_BASE_URL}/stats`);
  if (!response.ok) {
    throw new Error('Failed to fetch stats');
  }
  return response.json();
};

const fetchLogs = async (): Promise<LogEntry[]> => {
  const response = await fetch(`${API_BASE_URL}/log`);
  if (!response.ok) {
    throw new Error('Failed to fetch logs');
  }
  return response.json();
};

const Index = () => {
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    retry: 1,
  });

  const {
    data: logs,
    isLoading: logsLoading,
    error: logsError,
  } = useQuery({
    queryKey: ['logs'],
    queryFn: fetchLogs,
    retry: 1,
  });

  // Show error toast if API calls fail
  if (statsError || logsError) {
    toast.error('Unable to fetch data. Please check your API URL.');
  }

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-4 py-8">
        {/* Stats Grid */}
        <div className="mb-8 grid gap-4 md:grid-cols-3">
          <StatCard
            title="Total Batteries Collected"
            value={stats?.totalBatteries?.toLocaleString() || '0'}
            icon={Battery}
            loading={statsLoading}
          />
          <StatCard
            title="Soil Saved (kg)"
            value={stats?.soilSaved?.toLocaleString() || '0'}
            icon={Leaf}
            loading={statsLoading}
          />
          <StatCard
            title="Water Saved (L)"
            value={stats?.waterSaved?.toLocaleString() || '0'}
            icon={Droplets}
            loading={statsLoading}
          />
        </div>

        {/* Chart Section */}
        <BatteryChart data={logs || []} loading={logsLoading} />
      </main>
    </div>
  );
};

export default Index;
