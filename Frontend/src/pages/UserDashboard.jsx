import Layout from "../components/Layout";
import JobsList from "../components/JobsList";
import { useScan } from "../context/ScanContext";

const UserDashboard = () => {
  const { jobs, error, isLoading, stoppingJobId, handleStopJob, handleViewCrashes, handleDownloadCrashes } = useScan();

  return (
    <Layout>
      {error && <p className="px-6 text-red-500">{error}</p>}
      <section className="p-6">
        <div className="bg-white border border-neutral-200/20 rounded-lg p-6">
          <p className="text-xs uppercase tracking-wider text-neutral-500">User Dashboard</p>
          <h1 className="text-2xl font-bold text-neutral-800 mt-1">Execution Overview</h1>
          <p className="text-neutral-600 mt-2">
            Track queued and running jobs, stop execution, and open or download crash outputs from completed analyses.
          </p>
        </div>
      </section>
      {isLoading && <p className="px-6 text-neutral-500">Loading scan data...</p>}
      <JobsList
        jobs={jobs}
        onStopJob={handleStopJob}
        onViewCrashes={handleViewCrashes}
        onDownloadCrashes={handleDownloadCrashes}
        stoppingJobId={stoppingJobId}
      />
    </Layout>
  );
};

export default UserDashboard;
