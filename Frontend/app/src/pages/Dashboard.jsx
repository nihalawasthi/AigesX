import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { fetchLatestReport, fetchScanJobStatus, startScanJob } from "../api/api";
import Layout from "../components/Layout";
import Summary from "../components/Summary";
import VulnerabilityList from "../components/VulnerabilityList";
import Analytics from "../components/Analytics";
import Reports from "../components/Reports";

const Dashboard = () => {
  const { token } = useAuth();  // ✅ Ensure token is available
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      if (!token) {
        setError("❌ No authentication token found.");
        return;
      }

      try {
        const reportData = await fetchLatestReport(token);
        setReport(reportData);
      } catch (err) {
        setError("❌ Failed to load data.");
      }
    };

    loadData();
  }, [token]);

  const handleGenerateReport = async () => {
    if (!token) {
      setError("❌ No authentication token found.");
      return;
    }

    setIsGenerating(true);
    setError("");

    try {
      const startResponse = await startScanJob(token);
      const jobId = startResponse?.job?.id;

      if (!jobId) {
        throw new Error("Missing job id");
      }

      let attempts = 0;
      const maxAttempts = 120;

      while (attempts < maxAttempts) {
        // Poll every 2 seconds for up to ~4 minutes.
        await new Promise((resolve) => setTimeout(resolve, 2000));
        const jobStatus = await fetchScanJobStatus(token, jobId);

        if (jobStatus.status === "COMPLETED") {
          if (jobStatus.report_data) {
            setReport(jobStatus.report_data);
          } else {
            const latest = await fetchLatestReport(token);
            setReport(latest);
          }
          setIsGenerating(false);
          return;
        }

        if (jobStatus.status === "FAILED") {
          const details = jobStatus.error ? ` ${jobStatus.error}` : "";
          throw new Error(`Scan job failed.${details}`);
        }

        attempts += 1;
      }

      throw new Error("Scan job timed out.");
    } catch (err) {
      setError("❌ Failed to generate report.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Layout>
      {error && <p className="text-red-500">{error}</p>}
      {report && <Summary report={report} />}
      {report && <VulnerabilityList id="vulnerabilities" vulnerabilities={report.detailed_findings.vulnerabilities} />}
      {report && <Analytics id="analytics" report={report} />}
      {report && <Reports reports={report} onGenerateReport={handleGenerateReport} isGenerating={isGenerating} />}
    </Layout>
  );
};

export default Dashboard;
