import { Battery } from 'lucide-react';

export const DashboardHeader = () => {
  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-primary p-2">
            <Battery className="h-6 w-6 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-bold text-foreground">
            Battery Recycling Dashboard
          </h1>
        </div>
      </div>
    </header>
  );
};
