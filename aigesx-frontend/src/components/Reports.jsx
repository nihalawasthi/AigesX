import React from "react";

const Reports = ({ reports }) => {
  if (!reports) return <p>Loading...</p>;

  return (
    <section id="Reports" className="p-6">
      <div className="bg-white border border-neutral-200/20 rounded-lg overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-neutral-200/20 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-neutral-700">Reports</h2>
          <button className="flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M12 4v16m8-8H4"></path>
            </svg>
            Generate New Report
          </button>
        </div>

        {/* Recent Reports */}
        <div className="p-6">
          <div className="mb-6">
            <div className="flex items-center mb-4">
              <h3 className="text-lg font-medium text-neutral-700">Recent Reports</h3>
              <span className="ml-2 px-2 py-1 text-xs font-medium bg-blue-50 text-blue-600 rounded-full">
                Last 7 days
              </span>
            </div>
            <div className="space-y-4">
              {reports.recent?.length > 0 ? (
                reports.recent.map((report, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-neutral-200/20 rounded-lg hover:bg-neutral-50">
                    <div className="flex items-center">
                      <div className={`p-2 rounded-lg ${report.severity === "Critical" ? "bg-red-50" : "bg-blue-50"}`}>
                        <svg className={`w-6 h-6 ${report.severity === "Critical" ? "text-red-600" : "text-blue-600"}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                      </div>
                      <div className="ml-4">
                        <h4 className="text-sm font-medium text-neutral-700">{report.name}</h4>
                        <p className="text-sm text-neutral-500">
                          Generated on {new Date(report.date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <button className="flex items-center px-3 py-1 text-sm text-neutral-600 hover:text-neutral-900">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                          <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                        </svg>
                        View
                      </button>
                      <button className="flex items-center px-3 py-1 text-sm text-neutral-600 hover:text-neutral-900">
                        <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                        Download
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-neutral-500 text-center">No recent reports available.</p>
              )}
            </div>
          </div>

          {/* Scheduled Reports */}
          <div className="border-t border-neutral-200/20 pt-6">
            <h3 className="text-lg font-medium text-neutral-700 mb-4">Scheduled Reports</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="text-left border-b border-neutral-200/20">
                    <th className="pb-3 font-semibold text-neutral-600">Report Name</th>
                    <th className="pb-3 font-semibold text-neutral-600">Frequency</th>
                    <th className="pb-3 font-semibold text-neutral-600">Last Generated</th>
                    <th className="pb-3 font-semibold text-neutral-600">Next Run</th>
                    <th className="pb-3 font-semibold text-neutral-600">Status</th>
                    <th className="pb-3 font-semibold text-neutral-600">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {reports.scheduled?.length > 0 ? (
                    reports.scheduled.map((report, index) => (
                      <tr key={index} className="border-b border-neutral-200/20">
                        <td className="py-3">{report.name}</td>
                        <td className="py-3">{report.frequency}</td>
                        <td className="py-3">{new Date(report.lastGenerated).toLocaleDateString()}</td>
                        <td className="py-3">{new Date(report.nextRun).toLocaleDateString()}</td>
                        <td className="py-3">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${report.status === "Active" ? "bg-green-50 text-green-600" : "bg-red-50 text-red-600"}`}>
                            {report.status}
                          </span>
                        </td>
                        <td className="py-3">
                          <button className="text-neutral-600 hover:text-neutral-900">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"></path>
                            </svg>
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="py-3 text-center text-neutral-500">
                        No scheduled reports available.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Reports;
