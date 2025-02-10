import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { fetchLatestReport } from "../api/api";
import Layout from "../components/Layout";
import Summary from "../components/Summary";
import VulnerabilityList from "../components/VulnerabilityList";
import Analytics from "../components/Analytics";
import Reports from "../components/Reports";

const Dashboard = () => {
  const { token } = useAuth();  // ✅ Ensure token is available
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");

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

  return (
    <Layout>
      {error && <p className="text-red-500">{error}</p>}
      {report && <Summary report={report} />}
      {report && <VulnerabilityList id="vulnerabilities" vulnerabilities={report.detailed_findings.vulnerabilities} />}
      {report && <Analytics id="analytics" report={report} />}
      {report && <Reports reports={report} />}
    </Layout>
  );
};

export default Dashboard;
