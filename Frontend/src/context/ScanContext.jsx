import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";
import {
  downloadScanCrashData,
  fetchUserProfile,
  fetchLatestReport,
  fetchScanCrashData,
  fetchScanJobs,
  fetchScanJobStatus,
  fetchUploadedArtifacts,
  startScanJob,
  stopScanJob,
  uploadBinaryFile,
  uploadCorpusFile,
  uploadSourceRepo,
} from "../api/api";

const ScanContext = createContext(null);

export const ScanProvider = ({ children }) => {
  const { token } = useAuth();
  const [report, setReport] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [binaryArtifacts, setBinaryArtifacts] = useState([]);
  const [corpusArtifacts, setCorpusArtifacts] = useState([]);
  const [sourceArtifacts, setSourceArtifacts] = useState([]);
  const [stoppingJobId, setStoppingJobId] = useState(null);
  const [timeoutSeconds, setTimeoutSeconds] = useState(300);
  const [memoryLimitMb, setMemoryLimitMb] = useState(512);
  const [cpuLimit, setCpuLimit] = useState(1.0);
  const [binaryArtifactId, setBinaryArtifactId] = useState(null);
  const [seedArtifactId, setSeedArtifactId] = useState(null);
  const [sourceArtifactId, setSourceArtifactId] = useState(null);
  const [error, setError] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploadingBinary, setIsUploadingBinary] = useState(false);

  const refreshData = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const reportData = await fetchLatestReport(token);
      const jobsData = await fetchScanJobs(token);
      const binaries = await fetchUploadedArtifacts(token, "BINARY");
      const corpus = await fetchUploadedArtifacts(token, "CORPUS");
      const sources = await fetchUploadedArtifacts(token, "SOURCE");

      setReport(reportData || null);
      setJobs(jobsData);
      setBinaryArtifacts(binaries);
      setCorpusArtifacts(corpus);
      setSourceArtifacts(sources);

      if (!binaryArtifactId && Array.isArray(binaries) && binaries.length > 0) {
        setBinaryArtifactId(binaries[0].id);
      }

      if (!seedArtifactId && Array.isArray(corpus) && corpus.length > 0) {
        setSeedArtifactId(corpus[0].id);
      }
      if (!sourceArtifactId && Array.isArray(sources) && sources.length > 0) {
        setSourceArtifactId(sources[0].id);
      }
      setError("");
    } catch (err) {
      setError("Failed to load scan data.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!token) {
      setReport(null);
      setJobs([]);
      setBinaryArtifacts([]);
      setCorpusArtifacts([]);
      setSourceArtifacts([]);
      setError("");
      return;
    }
    refreshData();

    fetchUserProfile(token)
      .then((user) => {
        if (user?.default_timeout_seconds) {
          setTimeoutSeconds(Number(user.default_timeout_seconds));
        }
        if (user?.default_memory_limit_mb) {
          setMemoryLimitMb(Number(user.default_memory_limit_mb));
        }
        if (user?.default_cpu_limit) {
          setCpuLimit(Number(user.default_cpu_limit));
        }
      })
      .catch(() => {
        // Keep existing defaults if profile fetch fails.
      });
  }, [token]);

  const runAnalysis = async () => {
    if (!token) return;
    if (isUploadingBinary) {
      setError("Binary upload in progress. Please wait a moment and try again.");
      return;
    }
    setIsGenerating(true);
    setError("");

    try {
      const startResponse = await startScanJob(token, {
        timeout_seconds: timeoutSeconds,
        memory_limit_mb: memoryLimitMb,
        cpu_limit: cpuLimit,
        binary_artifact_id: binaryArtifactId,
        seed_artifact_id: seedArtifactId,
        source_artifact_id: sourceArtifactId,
      });

      const jobId = startResponse?.job?.id;
      if (!jobId) throw new Error("Missing job id");

      await refreshData();

      let attempts = 0;
      const maxAttempts = 120;

      while (attempts < maxAttempts) {
        await new Promise((resolve) => setTimeout(resolve, 2000));
        const jobStatus = await fetchScanJobStatus(token, jobId);

        if (jobStatus.status === "COMPLETED") {
          if (jobStatus.report_data) {
            setReport(jobStatus.report_data);
          } else {
            const latest = await fetchLatestReport(token);
            setReport(latest || null);
          }
          await refreshData();
          return;
        }

        if (jobStatus.status === "FAILED") {
          throw new Error(jobStatus.error || "Scan job failed");
        }

        attempts += 1;
      }

      throw new Error("Scan job timed out");
    } catch (err) {
      const apiError = err?.response?.data?.error || err?.response?.data?.details || err?.message;
      setError(apiError ? `Failed to run analysis: ${apiError}` : "Failed to run analysis.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleStopJob = async (jobId) => {
    if (!token) return;
    setStoppingJobId(jobId);
    setError("");
    try {
      await stopScanJob(token, jobId);
      await refreshData();
    } catch (err) {
      setError("Failed to stop job.");
    } finally {
      setStoppingJobId(null);
    }
  };

  const handleViewCrashes = async (jobId) => {
    if (!token) return;
    setError("");
    try {
      const data = await fetchScanCrashData(token, jobId);
      const crashes = data?.crashes || [];
      setReport((prev) => ({
        ...(prev || {}),
        detailed_findings: {
          ...(prev?.detailed_findings || {}),
          vulnerabilities: crashes,
        },
      }));
    } catch (err) {
      setError("Failed to fetch crash data.");
    }
  };

  const handleDownloadCrashes = async (jobId) => {
    if (!token) return;
    setError("");
    try {
      const blob = await downloadScanCrashData(token, jobId);
      const url = window.URL.createObjectURL(new Blob([blob], { type: "application/json" }));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `job_${jobId}_crashes.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError("Failed to download crash data.");
    }
  };

  const handleUploadBinary = async (file) => {
    if (!token) return;
    setIsUploadingBinary(true);
    setError("");
    try {
      const uploaded = await uploadBinaryFile(token, file);
      if (uploaded?.id) {
        setBinaryArtifactId(uploaded.id);
      }
      await refreshData();
    } catch (err) {
      const apiError = err?.response?.data?.error || err?.response?.data?.details || err?.message;
      setError(apiError ? `Failed to upload binary: ${apiError}` : "Failed to upload binary.");
    } finally {
      setIsUploadingBinary(false);
    }
  };

  const handleUploadCorpus = async (file) => {
    if (!token) return;
    setError("");
    try {
      await uploadCorpusFile(token, file);
      await refreshData();
    } catch (err) {
      setError("Failed to upload corpus.");
    }
  };

  const handleUploadSource = async (repoUrl) => {
    if (!token) return;
    setError("");
    try {
      await uploadSourceRepo(token, repoUrl);
      await refreshData();
    } catch (err) {
      setError("Failed to save source repository link.");
    }
  };

  const value = useMemo(
    () => ({
      report,
      jobs,
      binaryArtifacts,
      corpusArtifacts,
      sourceArtifacts,
      stoppingJobId,
      timeoutSeconds,
      memoryLimitMb,
      cpuLimit,
      binaryArtifactId,
      seedArtifactId,
      sourceArtifactId,
      error,
      isGenerating,
      isLoading,
      isUploadingBinary,
      setTimeoutSeconds,
      setMemoryLimitMb,
      setCpuLimit,
      setBinaryArtifactId,
      setSeedArtifactId,
      setSourceArtifactId,
      runAnalysis,
      refreshData,
      handleStopJob,
      handleViewCrashes,
      handleDownloadCrashes,
      handleUploadBinary,
      handleUploadCorpus,
      handleUploadSource,
    }),
    [
      report,
      jobs,
      binaryArtifacts,
      corpusArtifacts,
      sourceArtifacts,
      stoppingJobId,
      timeoutSeconds,
      memoryLimitMb,
      cpuLimit,
      binaryArtifactId,
      seedArtifactId,
      sourceArtifactId,
      error,
      isGenerating,
      isLoading,
      isUploadingBinary,
    ]
  );

  return <ScanContext.Provider value={value}>{children}</ScanContext.Provider>;
};

export const useScan = () => {
  const ctx = useContext(ScanContext);
  if (!ctx) throw new Error("useScan must be used within ScanProvider");
  return ctx;
};
