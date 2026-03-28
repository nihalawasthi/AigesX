import React from "react";

const Summary = ({ report }) => {
  if (!report) return <p>Loading...</p>;

  return (
    <section id="Summary" className="p-6">
      {/* Severity Overview Cards */}
      <div className="grid gap-6 mb-8 md:grid-cols-2 xl:grid-cols-4">
        {/* Critical */}
        <div className="flex items-center p-4 bg-white border border-neutral-200/20 rounded-lg">
          <div className="p-3 rounded-full bg-red-100">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
            </svg>
          </div>
          <div className="ml-4">
            <p className="mb-2 text-sm font-medium text-neutral-600">Critical</p>
            <p className="text-lg font-semibold text-neutral-700">{report.vulnerability_summary.by_severity.CRITICAL || 0}</p>
          </div>
        </div>

        {/* High */}
        <div className="flex items-center p-4 bg-white border border-neutral-200/20 rounded-lg">
          <div className="p-3 rounded-full bg-orange-100">
            <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
          <div className="ml-4">
            <p className="mb-2 text-sm font-medium text-neutral-600">High</p>
            <p className="text-lg font-semibold text-neutral-700">{report.vulnerability_summary.by_severity.HIGH || 0}</p>
          </div>
        </div>

        {/* Medium */}
        <div className="flex items-center p-4 bg-white border border-neutral-200/20 rounded-lg">
          <div className="p-3 rounded-full bg-yellow-100">
            <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div className="ml-4">
            <p className="mb-2 text-sm font-medium text-neutral-600">Medium</p>
            <p className="text-lg font-semibold text-neutral-700">{report.vulnerability_summary.by_severity.MEDIUM || 0}</p>
          </div>
        </div>

        {/* Low */}
        <div className="flex items-center p-4 bg-white border border-neutral-200/20 rounded-lg">
          <div className="p-3 rounded-full bg-blue-100">
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div className="ml-4">
            <p className="mb-2 text-sm font-medium text-neutral-600">Low</p>
            <p className="text-lg font-semibold text-neutral-700">{report.vulnerability_summary.by_severity.LOW || 0}</p>
          </div>
        </div>
      </div>

      {/* System Info & Risk Score */}
      <div className="grid gap-6 mb-8 md:grid-cols-2">
        {/* System Information */}
        <div className="bg-white p-6 border border-neutral-200/20 rounded-lg">
          <h3 className="text-lg font-semibold text-neutral-700 mb-4">System Information</h3>
          <div className="grid gap-4">
            <div className="flex justify-between border-b border-neutral-200/20 pb-2">
              <span className="text-neutral-600">Platform</span>
              <span className="font-medium">{report.scan_summary.system_info.platform || "N/A"}</span>
            </div>
            <div className="flex justify-between border-b border-neutral-200/20 pb-2">
              <span className="text-neutral-600">Version</span>
              <span className="font-medium">{report.scan_summary.system_info.version || "N/A"}</span>
            </div>
            <div className="flex justify-between border-b border-neutral-200/20 pb-2">
              <span className="text-neutral-600">Processor</span>
              <span className="font-medium">{report.scan_summary.system_info.machine || "N/A"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-neutral-600">Architecture</span>
              <span className="font-medium">{report.scan_summary.system_info.architecture || "N/A"}</span>
            </div>
          </div>
        </div>

        {/* Risk Score */}
        <div className="bg-white p-6 border border-neutral-200/20 rounded-lg flex flex-col items-center">
          <h3 className="text-lg font-semibold text-neutral-700 mb-4">Risk Score</h3>
          <div className="relative">
            <div className="flex items-center justify-center w-32 h-32 rounded-full border-8 border-red-500">
              <span className="text-3xl font-bold text-neutral-700">{report.scan_summary.risk_score || "N/A"}</span>
            </div>
            <span className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-sm text-neutral-600">Risk</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Summary;
