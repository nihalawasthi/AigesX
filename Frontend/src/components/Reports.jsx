import React from "react";
import { useLanguage } from "../context/LanguageContext";

const Reports = ({ reports, onGenerateReport, isGenerating = false }) => {
  const { t } = useLanguage();
  if (!reports) return <p>Loading...</p>;

  const generatedAt = reports?.scan_summary?.generated_at;
  const riskScore = reports?.scan_summary?.risk_score;
  const totalVulnerabilities = reports?.scan_summary?.total_vulnerabilities || 0;
  const categories = reports?.vulnerability_summary?.by_category || {};

  return (
    <section id="Reports" className="p-6">
      <div className="bg-white border border-neutral-200/20 rounded-lg overflow-hidden">
        <div className="p-6 border-b border-neutral-200/20 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-neutral-700">{t("findingsSnapshot")}</h2>
          <button
            className="flex items-center px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 disabled:opacity-60 disabled:cursor-not-allowed"
            onClick={onGenerateReport}
            disabled={isGenerating}
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M12 4v16m8-8H4"></path>
            </svg>
            {isGenerating ? t("runningAnalysis") : t("runNewAnalysis")}
          </button>
        </div>

        <div className="p-6 grid gap-4 md:grid-cols-3">
          <div className="border border-neutral-200/20 rounded-lg p-4">
            <p className="text-sm text-neutral-500">{t("lastGenerated")}</p>
            <p className="mt-1 font-medium text-neutral-700">
              {generatedAt ? new Date(generatedAt).toLocaleString() : "N/A"}
            </p>
          </div>

          <div className="border border-neutral-200/20 rounded-lg p-4">
            <p className="text-sm text-neutral-500">{t("riskScore")}</p>
            <p className="mt-1 font-medium text-neutral-700">{riskScore ?? "N/A"}</p>
          </div>

          <div className="border border-neutral-200/20 rounded-lg p-4">
            <p className="text-sm text-neutral-500">{t("totalFindings")}</p>
            <p className="mt-1 font-medium text-neutral-700">{totalVulnerabilities}</p>
          </div>
        </div>

        <div className="px-6 pb-6">
          <h3 className="text-lg font-medium text-neutral-700 mb-3">{t("categoryBreakdown")}</h3>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Object.keys(categories).length > 0 ? (
              Object.entries(categories).map(([name, count]) => (
                <div key={name} className="border border-neutral-200/20 rounded-lg p-3 flex items-center justify-between">
                  <span className="text-neutral-600">{name}</span>
                  <span className="font-semibold text-neutral-700">{count}</span>
                </div>
              ))
            ) : (
              <p className="text-neutral-500">{t("noCategoryData")}</p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Reports;
