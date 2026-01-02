import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

interface DashboardStats {
  total_jobs: number;
  running_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  storage_used_mb: number;
  compute_hours_used: number;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentJobs, setRecentJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsResponse, jobsResponse] = await Promise.all([
        axios.get('/api/users/stats'),
        axios.get('/api/jobs?limit=5'),
      ]);
      
      setStats(statsResponse.data);
      setRecentJobs(jobsResponse.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome section */}
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.username}!
        </h1>
        <p className="mt-2 text-gray-600">
          Subscription: <span className="font-semibold capitalize">{user?.subscription_tier}</span>
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Jobs"
          value={stats?.total_jobs || 0}
          icon="📊"
          color="blue"
        />
        <StatCard
          title="Running Jobs"
          value={stats?.running_jobs || 0}
          icon="⚡"
          color="yellow"
        />
        <StatCard
          title="Completed Jobs"
          value={stats?.completed_jobs || 0}
          icon="✅"
          color="green"
        />
        <StatCard
          title="Storage Used"
          value={`${((stats?.storage_used_mb || 0) / 1024).toFixed(2)} GB`}
          icon="💾"
          color="purple"
        />
      </div>

      {/* Quick actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/upload"
            className="flex items-center justify-center p-4 bg-blue-50 hover:bg-blue-100 rounded-lg border-2 border-blue-200 transition"
          >
            <span className="text-2xl mr-3">📤</span>
            <span className="font-semibold text-blue-900">Upload Data</span>
          </Link>
          
          <Link
            to="/jobs"
            className="flex items-center justify-center p-4 bg-green-50 hover:bg-green-100 rounded-lg border-2 border-green-200 transition"
          >
            <span className="text-2xl mr-3">🔬</span>
            <span className="font-semibold text-green-900">View All Jobs</span>
          </Link>
          
          <Link
            to="/billing"
            className="flex items-center justify-center p-4 bg-purple-50 hover:bg-purple-100 rounded-lg border-2 border-purple-200 transition"
          >
            <span className="text-2xl mr-3">💳</span>
            <span className="font-semibold text-purple-900">Manage Billing</span>
          </Link>
        </div>
      </div>

      {/* Recent jobs */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Jobs</h2>
        {recentJobs.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            No jobs yet. Upload data to get started!
          </p>
        ) : (
          <div className="space-y-3">
            {recentJobs.map((job) => (
              <Link
                key={job.id}
                to={`/jobs/${job.id}`}
                className="block p-4 border rounded-lg hover:bg-gray-50 transition"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">{job.job_name}</h3>
                    <p className="text-sm text-gray-600 capitalize">
                      {job.job_type.replace('_', ' ')}
                    </p>
                  </div>
                  <div className="text-right">
                    <StatusBadge status={job.status} />
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(job.submitted_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// Helper components
const StatCard: React.FC<{
  title: string;
  value: number | string;
  icon: string;
  color: string;
}> = ({ title, value, icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    green: 'bg-green-50 border-green-200',
    purple: 'bg-purple-50 border-purple-200',
  };

  return (
    <div className={`${colorClasses[color]} border-2 rounded-lg p-6`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <span className="text-4xl">{icon}</span>
      </div>
    </div>
  );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  const statusColors = {
    pending: 'bg-gray-100 text-gray-800',
    running: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[status]}`}>
      {status.toUpperCase()}
    </span>
  );
};

export default Dashboard;