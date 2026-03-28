import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

const authHeaders = (token) => ({
  Authorization: `Bearer ${token}`,
  "Content-Type": "application/json",
});

export const fetchLatestReport = async (token) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/latest-report/`, {
      headers: authHeaders(token),
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error fetching latest report:", error.response ? error.response.data : error.message);
    throw error;
  }
};

export const generateScanReport = async (token) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/scan/`, {}, {
      headers: authHeaders(token),
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error generating scan report:", error.response ? error.response.data : error.message);
    throw error;
  }
};

export const startScanJob = async (token) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/scan/start/`, {}, {
      headers: authHeaders(token),
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error starting scan job:", error.response ? error.response.data : error.message);
    throw error;
  }
};

export const fetchScanJobStatus = async (token, jobId) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/scan/jobs/${jobId}/`, {
      headers: authHeaders(token),
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error fetching scan job status:", error.response ? error.response.data : error.message);
    throw error;
  }
};
