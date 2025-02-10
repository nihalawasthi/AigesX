import React, { useEffect, useState } from "react";
import { Bar, Line, Doughnut, PolarArea } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";
import '../index.css';
import { useAuth } from "../context/AuthContext";
import axios from "axios";

Chart.register(...registerables);

const Analytics = ({ report }) => {
  const [trendData, setTrendData] = useState({
    labels: [],
    datasets: [{ label: "Loading...", data: [], backgroundColor: [] }]
  });

  const [riskScoreData, setRiskScoreData] = useState({
    labels: [],
    datasets: [{ label: "Loading...", data: [], borderColor: "#ef4444", tension: 0.3 }]
  });

  const { token } = useAuth();
  const API_BASE_URL = "http://127.0.0.1:8000/api";

  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  useEffect(() => {
    axios.get(`${API_BASE_URL}/vulnerability-trends/`, {
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
    })
      .then((res) => {
        if (!res.data || !res.data.labels || !res.data.values) throw new Error("Invalid API response format");

        const filteredData = res.data.labels
          .map((label, index) => ({ label, value: res.data.values[index] }))
          .filter(item => !item.label.includes("CWE-NVD") && !item.label.includes("CWE-Other"))
          .sort((a, b) => b.value - a.value); // Sorting highest first for better visuals

        setTrendData({
          labels: filteredData.map(item => item.label),
          datasets: [{
            label: "Vulnerabilities",
            data: filteredData.map(item => item.value),
            backgroundColor: ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#10b981", "#8b5cf6"],
            borderWidth: 2,
            borderColor: "#fff",
            hoverBorderColor: "#000",
            hoverOffset: 12
          }]
        });
      })
      .catch((err) => console.error("Error fetching vulnerability trends:", err));

    axios.get(`${API_BASE_URL}/cyber-risk-index/`, {
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
    })
      .then((res) => {
        if (!res.data || !res.data.labels) throw new Error("Invalid API response format");
        setRiskScoreData({
          labels: res.data.labels,
          datasets: [{
            label: "Risk Score",
            data: res.data.values,
            borderColor: "#ef4444",
            backgroundColor: "rgba(239, 68, 68, 0.2)",
            borderWidth: 2,
            tension: 0.3
          }]
        });
      })
      .catch((err) => console.error("Error fetching cyber risk index:", err));
  }, []);

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

  const vulnTrendsOptions = {
    responsive: true,
    maintainAspectRatio: false,
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
    scales: {
      r: {
        grid: { display: false },
        ticks: { display: false }
      }
    },
    animation: {
      duration: 1200,
      easing: "easeInOutBounce"
    }
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
        {/* Severity & Vulnerability Trends - Side by Side */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Severity Distribution */}
          <div className="bg-white border border-neutral-200/20 rounded-lg p-6 shadow-lg flex items-center">
            <div className="chartmax">
              <Doughnut data={severityChartData} options={severityOptions} />
            </div>
          </div>

          {/* Vulnerability Trends */}
          <div className="bg-white border border-neutral-200/20 rounded-lg p-6 shadow-lg flex items-center">
            <div className="chartmax">
              <PolarArea data={trendData} options={vulnTrendsOptions} />
            </div>
          </div>
        </div>

        {/* Category, Remediation, Risk Score */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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

          {/* Cyber Risk Index */}
          <div className="bg-white border border-neutral-200/20 rounded-lg p-6 shadow-md">
            <h3 className="text-lg font-semibold text-neutral-700 mb-4">Cyber Risk Index</h3>
            <div className="h-64">
              <Line data={riskScoreData} options={{ responsive: true, maintainAspectRatio: false }} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Analytics;
