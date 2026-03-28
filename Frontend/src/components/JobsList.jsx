const statusBadgeClass = (status) => {
  if (status === "FAILED") return "bg-red-100 text-red-700";
  if (status === "RUNNING") return "bg-amber-100 text-amber-700";
  if (status === "COMPLETED") return "bg-emerald-100 text-emerald-700";
  return "bg-blue-100 text-blue-700";
};

const formatTime = (value) => {
  if (!value) return "-";
  return new Date(value).toLocaleString();
};

const JobsList = ({ jobs = [], onStopJob, onViewCrashes, onDownloadCrashes, stoppingJobId }) => {
  return (
    <section id="JobsList" className="p-6">
      <div className="bg-white border border-neutral-200/20 rounded-lg overflow-hidden">
        <div className="p-6 border-b border-neutral-200/20 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-neutral-700">Execution Queue</h2>
          <span className="text-sm text-neutral-500">{jobs.length} total</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-neutral-50 text-neutral-600">
              <tr>
                <th className="px-4 py-3 text-left">Job ID</th>
                <th className="px-4 py-3 text-left">Target</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Crash Count</th>
                <th className="px-4 py-3 text-left">Created</th>
                <th className="px-4 py-3 text-left">Finished</th>
                <th className="px-4 py-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {jobs.length === 0 ? (
                <tr>
                  <td className="px-4 py-4 text-neutral-500" colSpan={7}>No jobs found.</td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="border-t border-neutral-200/20">
                    <td className="px-4 py-3 text-neutral-700 font-mono">{String(job.id).slice(0, 8)}...</td>
                    <td className="px-4 py-3 text-neutral-700">{job.source_artifact_id ? "Source Repo" : "Binary"}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${statusBadgeClass(job.status)}`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-neutral-700">{job.crash_count ?? "-"}</td>
                    <td className="px-4 py-3 text-neutral-700">{formatTime(job.created_at)}</td>
                    <td className="px-4 py-3 text-neutral-700">{formatTime(job.finished_at)}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          className="px-2 py-1 rounded border border-neutral-200 text-neutral-700 disabled:opacity-50"
                          onClick={() => onViewCrashes && onViewCrashes(job.id)}
                          disabled={job.status !== "COMPLETED"}
                        >
                          View Crashes
                        </button>
                        <button
                          className="px-2 py-1 rounded border border-neutral-200 text-neutral-700 disabled:opacity-50"
                          onClick={() => onDownloadCrashes && onDownloadCrashes(job.id)}
                          disabled={job.status !== "COMPLETED"}
                        >
                          Download
                        </button>
                        <button
                          className="px-2 py-1 rounded border border-red-200 text-red-700 disabled:opacity-50"
                          onClick={() => onStopJob && onStopJob(job.id)}
                          disabled={!(["QUEUED", "RUNNING"].includes(job.status)) || stoppingJobId === job.id}
                        >
                          {stoppingJobId === job.id ? "Stopping..." : "Stop"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
};

export default JobsList;
