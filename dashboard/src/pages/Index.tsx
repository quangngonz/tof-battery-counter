import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Battery, Droplets, Leaf } from 'lucide-react';
import { DashboardHeader } from '@/components/DashboardHeader';
import { StatCard } from '@/components/StatCard';
import { BatteryChart } from '@/components/BatteryChart';
import { toast } from 'sonner';
import { supabase, type BatteryLog } from '@/lib/supabase';
import { useEffect } from 'react';

interface StatsData {
  total: number;
  soil: number;
  water: number;
}

interface LogEntry {
  timestamp: string;
  amount: number;
}

// Environmental impact constants
const SOIL_PER_BATTERY = 1; // in meter square
const WATER_PER_BATTERY = 500; // in L

const fetchStats = async (): Promise<StatsData> => {
  const { data, error } = await supabase.from('battery_logs').select('amount');

  if (error) {
    throw new Error('Failed to fetch stats');
  }

  const total = data.reduce((sum, log) => sum + log.amount, 0);

  return {
    total,
    soil: Math.round(total * SOIL_PER_BATTERY),
    water: Math.round(total * WATER_PER_BATTERY),
  };
};

const fetchLogs = async (): Promise<LogEntry[]> => {
  const { data, error } = await supabase
    .from('battery_logs')
    .select('timestamp, amount')
    .order('timestamp', { ascending: true });

  if (error) {
    throw new Error('Failed to fetch logs');
  }

  return data.map((log: BatteryLog) => ({
    timestamp: log.timestamp,
    amount: log.amount,
  }));
};

const Index = () => {
  const queryClient = useQueryClient();

  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError,
  } = useQuery({
    queryKey: ['stats'],
    queryFn: fetchStats,
    retry: 1,
    refetchInterval: 5000, // Auto-refresh every 5 seconds
  });

  const {
    data: logs,
    isLoading: logsLoading,
    error: logsError,
  } = useQuery({
    queryKey: ['logs'],
    queryFn: fetchLogs,
    retry: 1,
    refetchInterval: 5000, // Auto-refresh every 5 seconds
  });

  // Set up realtime subscription for live updates (WebSocket)
  useEffect(() => {
    const channel = supabase
      .channel('battery_logs_changes')
      .on(
        'postgres_changes',
        {
          event: '*', // Listen to all events (INSERT, UPDATE, DELETE)
          schema: 'public',
          table: 'battery_logs',
        },
        (payload) => {
          console.log('Realtime update:', payload);

          // Invalidate queries to refetch data immediately
          queryClient.invalidateQueries({ queryKey: ['stats'] });
          queryClient.invalidateQueries({ queryKey: ['logs'] });
        }
      )
      .subscribe((status) => {
        console.log('Realtime subscription status:', status);
      });

    // Cleanup subscription on unmount
    return () => {
      supabase.removeChannel(channel);
    };
  }, [queryClient]);

  // Show error toast only if API calls fail
  useEffect(() => {
    if (statsError || logsError) {
      toast.error('Unable to fetch data. Please check your connection.');
    }
  }, [statsError, logsError]);

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader />

      <main className="container mx-auto px-4 py-8">
        {/* Stats Grid */}
        <div className="mb-8 grid gap-4 md:grid-cols-3">
          <StatCard
            title="Total Batteries Collected"
            value={stats?.total?.toLocaleString() || '0'}
            icon={Battery}
            loading={statsLoading}
          />
          <StatCard
            title="Soil Saved (m³)"
            value={stats?.soil?.toLocaleString() || '0'}
            icon={Leaf}
            loading={statsLoading}
          />
          <StatCard
            title="Water Saved (L)"
            value={stats?.water?.toLocaleString() || '0'}
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
