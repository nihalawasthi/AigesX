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
    if (error?.response?.status === 404 && error?.response?.data?.error === "No reports found") {
      return null;
    }
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

export const startScanJob = async (token, payload = {}) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/scan/start/`, payload, {
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

export const fetchScanJobLogs = async (token, jobId) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/scan/jobs/${jobId}/logs/`, {
      headers: authHeaders(token),
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error fetching scan job logs:", error.response ? error.response.data : error.message);
    throw error;
  }
};

export const fetchScanJobs = async (token) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/scan/jobs/`, {
      headers: authHeaders(token),
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error fetching scan jobs:", error.response ? error.response.data : error.message);
    throw error;
  }
};

export const stopScanJob = async (token, jobId) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.post(`${API_BASE_URL}/scan/jobs/${jobId}/stop/`, {}, {
      headers: authHeaders(token),
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error stopping scan job:", error.response ? error.response.data : error.message);
    throw error;
  }
};

export const fetchScanCrashData = async (token, jobId) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/scan/jobs/${jobId}/crashes/`, {
      headers: authHeaders(token),
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error fetching crash data:", error.response ? error.response.data : error.message);
    throw error;
  }
};

export const downloadScanCrashData = async (token, jobId) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/scan/jobs/${jobId}/crashes/download/`, {
      headers: authHeaders(token),
      responseType: "blob",
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error downloading crash data:", error.response ? error.response.data : error.message);
    throw error;
  }
};

export const uploadBinaryFile = async (token, file) => {
  if (!token) throw new Error("No authentication token found.");
  const formData = new FormData();
  formData.append("file", file);
  const response = await axios.post(`${API_BASE_URL}/scan/upload/binary/`, formData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

export const uploadCorpusFile = async (token, file) => {
  if (!token) throw new Error("No authentication token found.");
  const formData = new FormData();
  formData.append("file", file);
  const response = await axios.post(`${API_BASE_URL}/scan/upload/corpus/`, formData, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
};

export const fetchUploadedArtifacts = async (token, kind) => {
  if (!token) throw new Error("No authentication token found.");
  const response = await axios.get(`${API_BASE_URL}/scan/upload/artifacts/`, {
    headers: authHeaders(token),
    params: kind ? { kind } : undefined,
  });
  return response.data;
};

export const uploadSourceRepo = async (token, repoUrl) => {
  if (!token) throw new Error("No authentication token found.");
  const response = await axios.post(
    `${API_BASE_URL}/scan/upload/source/`,
    { repo_url: repoUrl },
    { headers: authHeaders(token) }
  );
  return response.data;
};

export const fetchUserProfile = async (token) => {
  if (!token) throw new Error("No authentication token found.");
  const response = await axios.get(`${API_BASE_URL}/auth/me/`, {
    headers: authHeaders(token),
  });
  return response.data;
};

export const updateUserProfile = async (token, payload) => {
  if (!token) throw new Error("No authentication token found.");
  const response = await axios.patch(`${API_BASE_URL}/auth/me/`, payload, {
    headers: authHeaders(token),
  });
  return response.data;
};

export const changeUserPassword = async (token, payload) => {
  if (!token) throw new Error("No authentication token found.");
  const response = await axios.post(`${API_BASE_URL}/auth/change-password/`, payload, {
    headers: authHeaders(token),
  });
  return response.data;
};
