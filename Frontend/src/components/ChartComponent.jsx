import { useEffect, useRef } from "react";
import Chart from "chart.js/auto";

const ChartComponent = ({ data, type, title }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (chartRef.current) {
      new Chart(chartRef.current, {
        type,
        data,
        options: { responsive: true, maintainAspectRatio: false },
      });
    }
  }, [data]);

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <canvas ref={chartRef}></canvas>
    </div>
  );
};

export default ChartComponent;
