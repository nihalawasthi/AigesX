import { useEffect, useState } from "react";
import { Line, PolarArea } from "react-chartjs-2";
import { Chart, registerables } from "chart.js";
import axios from "axios";

Chart.register(...registerables);

const API_BASE_URL = "http://127.0.0.1:8000/api";

const ThreatLandscape = () => {
  const [trendData, setTrendData] = useState({ labels: [], datasets: [] });
  const [riskScoreData, setRiskScoreData] = useState({ labels: [], datasets: [] });

  useEffect(() => {
    axios
      .get(`${API_BASE_URL}/vulnerability-trends/`)
      .then((res) => {
        const labels = Array.isArray(res?.data?.labels) ? res.data.labels : [];
        const values = Array.isArray(res?.data?.values) ? res.data.values : [];

        const filteredData = labels
          .map((label, index) => ({ label, value: values[index] || 0 }))
          .filter((item) => !item.label.includes("CWE-NVD") && !item.label.includes("CWE-Other"))
          .sort((a, b) => b.value - a.value);

        setTrendData({
          labels: filteredData.map((item) => item.label),
          datasets: [
            {
              label: "Global CWE Trend",
              data: filteredData.map((item) => item.value),
              backgroundColor: ["#ef4444", "#f97316", "#eab308", "#3b82f6", "#10b981", "#8b5cf6"],
              borderWidth: 2,
              borderColor: "#fff",
            },
          ],
        });
      })
      .catch(() => {
        setTrendData({ labels: [], datasets: [] });
      });

    axios
      .get(`${API_BASE_URL}/cyber-risk-index/`)
      .then((res) => {
        const labels = Array.isArray(res?.data?.labels) ? res.data.labels : [];
        const values = Array.isArray(res?.data?.values) ? res.data.values : [];

        setRiskScoreData({
          labels,
          datasets: [
            {
              label: "Cyber Risk Index",
              data: values,
              borderColor: "#ef4444",
              backgroundColor: "rgba(239, 68, 68, 0.18)",
              borderWidth: 2,
              tension: 0.3,
            },
          ],
        });
      })
      .catch(() => {
        setRiskScoreData({ labels: [], datasets: [] });
      });
  }, []);

  return (
    <section className="max-w-6xl mx-auto px-6 pb-16">
      <div className="rounded-2xl border border-white/15 bg-white/10 backdrop-blur-sm p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Threat Landscape</p>
        <h3 className="text-2xl font-bold mt-2">Global Cyber Signals</h3>
        <p className="text-slate-200 mt-2">High-level trends from public feeds, separate from your private report findings.</p>

        <div className="mt-6 grid gap-6 md:grid-cols-2">
          <div className="rounded-xl border border-white/15 bg-slate-900/40 p-4">
            <h4 className="font-semibold mb-3">Vulnerability Trends (Global)</h4>
            <div className="h-72">
              {trendData.datasets.length ? (
                <PolarArea
                  data={trendData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: "right", labels: { color: "#e2e8f0" } } },
                  }}
                />
              ) : (
                <p className="text-slate-300 text-sm">Trend data unavailable right now.</p>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-white/15 bg-slate-900/40 p-4">
            <h4 className="font-semibold mb-3">Cyber Risk Index (Global)</h4>
            <div className="h-72">
              {riskScoreData.datasets.length ? (
                <Line
                  data={riskScoreData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: "#e2e8f0" } } },
                    scales: {
                      x: { ticks: { color: "#cbd5e1" }, grid: { color: "rgba(148,163,184,0.2)" } },
                      y: { ticks: { color: "#cbd5e1" }, grid: { color: "rgba(148,163,184,0.2)" } },
                    },
                  }}
                />
              ) : (
                <p className="text-slate-300 text-sm">Risk index unavailable right now.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ThreatLandscape;