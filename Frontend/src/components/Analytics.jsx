import React from "react";
import { Bar, Doughnut } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";
import '../index.css';

Chart.register(...registerables);

const Analytics = ({ report }) => {
  if (!report) return <p>Loading...</p>;

  const summary = report.vulnerability_summary || {};
  const severityData = summary.by_severity || {};
  const categoryData = summary.by_category || {};

  const severityChartData = {
    labels: ["Critical", "High", "Medium", "Low"],
    datasets: [{
      data: Object.values(severityData),
      backgroundColor: ["#b91c1c", "#c2410c", "#fef08a", "#10b981"],
      borderColor: "#fff",
      borderWidth: 2
    }]
  };

  const severityOptions = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: "60%",
    plugins: {
      legend: {
        display: true,
        position: "right",
        labels: {
          usePointStyle: true,
          color: "#6b7280",
          font: { size: 12 }
        }
      },
      tooltip: {
        backgroundColor: "rgba(0, 0, 0, 0.8)",
        titleColor: "#fff"
      }
    },
    animation: {
      duration: 1200,
      easing: "easeInOutBounce"
    }
  };

  const remediationData = {
    labels: ["Fixed", "In Progress", "Pending"],
    datasets: [{
      data: [
        report.remediation_timeline?.immediate || 0,
        report.remediation_timeline?.short_term || 0,
        report.remediation_timeline?.long_term || 0
      ],
      backgroundColor: ["#22c55e", "#f59e0b", "#ef4444"],
      borderRadius: 8
    }]
  };

  return (
    <section id="Analytics" className="p-6">
      <div className="grid gap-6">
        {/* Severity Distribution */}
        <div className="bg-white border border-neutral-200/20 rounded-lg p-6 shadow-lg flex items-center">
          <div className="chartmax">
            <Doughnut data={severityChartData} options={severityOptions} />
          </div>
        </div>

        {/* Category and Remediation are report-derived */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Category Distribution */}
          <div className="bg-white border border-neutral-200/20 rounded-lg p-6 shadow-lg">
            <h3 className="text-lg font-semibold text-neutral-700 mb-4">Category Distribution</h3>
            <div className="h-64">
              <Bar data={{
                labels: Object.keys(categoryData),
                datasets: [{ data: Object.values(categoryData), backgroundColor: ["#2563eb", "#9333ea", "#f97316", "#dc2626", "#16a34a"] }]
              }} options={{ responsive: true, maintainAspectRatio: false }} />
            </div>
          </div>

          {/* Remediation Progress (ADDED BACK) */}
          <div className="bg-white border border-neutral-200/20 rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold text-neutral-700 mb-4">Remediation Progress</h3>
            <div className="h-64">
              <Doughnut
                data={remediationData}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  cutout: "50%",
                  plugins: { legend: { position: "right" } }
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Analytics;
