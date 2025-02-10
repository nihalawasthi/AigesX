import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

export const fetchLatestReport = async (token) => {
  if (!token) {
    console.error("❌ No authentication token found.");
    throw new Error("No authentication token found.");
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/latest-report/`, {
      headers: {
        Authorization: `Bearer ${token}`,  // ✅ Ensure the token is passed
        "Content-Type": "application/json",
      },
    });
    return response.data;
  } catch (error) {
    console.error("❌ Error fetching latest report:", error.response ? error.response.data : error.message);
    throw error;
  }
};
