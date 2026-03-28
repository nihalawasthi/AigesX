import { useMemo } from "react";
import Layout from "../components/Layout";
import Reports from "../components/Reports";
import Summary from "../components/Summary";
import VulnerabilityList from "../components/VulnerabilityList";
import Analytics from "../components/Analytics";
import { useScan } from "../context/ScanContext";
import { useLanguage } from "../context/LanguageContext";

const ReportPage = () => {
  const { report, runAnalysis, isGenerating, error } = useScan();
  const { t, translateReportData, language } = useLanguage();
  const localizedReport = useMemo(() => translateReportData(report), [report, translateReportData, language]);

  return (
    <Layout>
      {error && <p className="px-6 text-red-500">{error}</p>}
      <section className="p-6">
        <div className="bg-white border border-neutral-200/20 rounded-lg p-6">
          <p className="text-xs uppercase tracking-wider text-neutral-500">{t("reports")}</p>
          <h1 className="text-2xl font-bold text-neutral-800 mt-1">{t("findingsWorkspace")}</h1>
          <p className="text-neutral-600 mt-2">{t("inspectFindings")}</p>
        </div>
      </section>

      {!localizedReport && (
        <section className="p-6">
          <div className="bg-white border border-neutral-200/20 rounded-lg p-6">
            <p className="text-neutral-600">{t("noReportYet")}</p>
            <button
              onClick={runAnalysis}
              disabled={isGenerating}
              className="mt-4 px-4 py-2 rounded-lg bg-slate-900 text-white disabled:opacity-60"
            >
              {isGenerating ? t("running") : t("runAnalysis")}
            </button>
          </div>
        </section>
      )}

      {localizedReport && <Summary report={localizedReport} />}
      {localizedReport && <VulnerabilityList id="vulnerabilities" vulnerabilities={localizedReport.detailed_findings.vulnerabilities} />}
      {localizedReport && <Analytics id="analytics" report={localizedReport} />}
      {localizedReport && <Reports reports={localizedReport} onGenerateReport={runAnalysis} isGenerating={isGenerating} />}
    </Layout>
  );
};

export default ReportPage;
