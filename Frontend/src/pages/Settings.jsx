import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import SettingsControls from "../components/SettingsControls";
import { useScan } from "../context/ScanContext";
import { useAuth } from "../context/AuthContext";
import { useLanguage } from "../context/LanguageContext";
import { changeUserPassword, fetchUserProfile, updateUserProfile } from "../api/api";

const Settings = () => {
  const {
    timeoutSeconds,
    memoryLimitMb,
    cpuLimit,
    seedArtifactId,
    corpusArtifacts,
    setTimeoutSeconds,
    setMemoryLimitMb,
    setCpuLimit,
    setSeedArtifactId,
    handleUploadCorpus,
    error,
  } = useScan();
  const { token } = useAuth();
  const { setPreferredLanguage, t } = useLanguage();

  const [profile, setProfile] = useState({
    name: "",
    username: "",
    usernameDraft: "",
    email: "",
    emailDraft: "",
    profilePic: "",
    displayMode: "light",
    language: "en",
    notifyJobComplete: true,
    notifyCriticalOnly: false,
  });
  const [security, setSecurity] = useState({
    newPassword: "",
    confirmPassword: "",
    twoFactorEnabled: false,
    sessionAlerts: true,
  });
  const [savedMessage, setSavedMessage] = useState("");

  useEffect(() => {
    if (!token) return;

    const loadProfile = async () => {
      try {
        const data = await fetchUserProfile(token);
        const fullName = [data.first_name, data.last_name].filter(Boolean).join(" ");

        setProfile((prev) => ({
          ...prev,
          name: fullName,
          username: data.username || "",
          usernameDraft: "",
          email: data.email || "",
          emailDraft: "",
          profilePic: data.profile_picture || "",
          displayMode: data.display_mode || "light",
          language: data.preferred_language || "en",
          notifyJobComplete: !!data.notify_job_complete,
          notifyCriticalOnly: !!data.notify_critical_only,
        }));

        setSecurity((prev) => ({
          ...prev,
          twoFactorEnabled: !!data.two_factor_enabled,
          sessionAlerts: !!data.session_alerts,
        }));

        setTimeoutSeconds(Number(data.default_timeout_seconds || 300));
        setMemoryLimitMb(Number(data.default_memory_limit_mb || 512));
        setCpuLimit(Number(data.default_cpu_limit || 1.0));
        setPreferredLanguage(data.preferred_language || "en");
      } catch {
        setSavedMessage("Failed to load settings from backend.");
      }
    };

    loadProfile();
  }, [token, setMemoryLimitMb, setPreferredLanguage, setTimeoutSeconds]);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", profile.displayMode === "dark");
  }, [profile.displayMode]);

  const handleProfileChange = (field, value) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
    setSavedMessage("");
  };

  const handleSavePreferences = async () => {
    if (!token) return;

    const trimmedName = (profile.name || "").trim();
    const [firstName, ...rest] = trimmedName.split(" ").filter(Boolean);
    const payload = {
      first_name: firstName || "",
      last_name: rest.join(" "),
      username: (profile.usernameDraft || "").trim() || profile.username,
      email: (profile.emailDraft || "").trim() || profile.email,
      profile_picture: profile.profilePic || "",
      display_mode: profile.displayMode,
      preferred_language: profile.language,
      notify_job_complete: profile.notifyJobComplete,
      notify_critical_only: profile.notifyCriticalOnly,
      two_factor_enabled: security.twoFactorEnabled,
      session_alerts: security.sessionAlerts,
      default_timeout_seconds: timeoutSeconds,
      default_memory_limit_mb: memoryLimitMb,
      default_cpu_limit: cpuLimit,
    };

    try {
      const updated = await updateUserProfile(token, payload);
      setProfile((prev) => ({
        ...prev,
        username: updated.username || prev.username,
        usernameDraft: "",
        email: updated.email || prev.email,
        emailDraft: "",
      }));
      setPreferredLanguage(updated.preferred_language || profile.language);
      setSavedMessage("Settings saved to backend.");
    } catch (err) {
      const detail = err?.response?.data;
      const firstError = typeof detail === "object" && detail !== null ? JSON.stringify(detail) : "";
      setSavedMessage(`Failed to save settings. ${firstError}`.trim());
    }
  };

  const handleSecurityChange = (field, value) => {
    setSecurity((prev) => ({ ...prev, [field]: value }));
    setSavedMessage("");
  };

  const handleChangePassword = async () => {
    if (!security.newPassword || !security.confirmPassword) {
      setSavedMessage("Fill new and confirm password to change password.");
      return;
    }

    if (security.newPassword !== security.confirmPassword) {
      setSavedMessage("New password and confirm password do not match.");
      return;
    }

    if (security.newPassword.length < 8) {
      setSavedMessage("New password must be at least 8 characters.");
      return;
    }

    if (!token) return;

    try {
      await changeUserPassword(token, {
        new_password: security.newPassword,
        confirm_password: security.confirmPassword,
      });
      setSecurity((prev) => ({ ...prev, newPassword: "", confirmPassword: "" }));
      setSavedMessage("Password changed successfully.");
    } catch (err) {
      const detail = err?.response?.data;
      if (typeof detail === "string") {
        setSavedMessage(detail);
        return;
      }

      if (detail && typeof detail === "object") {
        const first = Object.values(detail)[0];
        const message = Array.isArray(first) ? first[0] : first;
        setSavedMessage(String(message || "Password change failed."));
        return;
      }

      setSavedMessage("Password change failed.");
    }
  };

  return (
    <Layout>
      {error && <p className="px-6 text-red-500">{error}</p>}
      {savedMessage && <p className="px-6 text-emerald-600">{savedMessage}</p>}
      <section className="p-6">
        <div className="bg-white border border-neutral-200/20 rounded-lg p-6">
          <div>
            <p className="text-xs uppercase tracking-wider text-neutral-500">Settings</p>
            <h1 className="text-2xl font-bold text-neutral-800 mt-1">{t("settingsTitle")}</h1>
            <p className="text-neutral-600 mt-2">{t("settingsSubtitle")}</p>
          </div>
        </div>
      </section>

      <SettingsControls
        profile={profile}
        security={security}
        timeoutSeconds={timeoutSeconds}
        memoryLimitMb={memoryLimitMb}
        cpuLimit={cpuLimit}
        seedArtifactId={seedArtifactId}
        corpusArtifacts={corpusArtifacts}
        onProfileChange={handleProfileChange}
        onSecurityChange={handleSecurityChange}
        onTimeoutChange={setTimeoutSeconds}
        onMemoryChange={setMemoryLimitMb}
        onCpuChange={setCpuLimit}
        onSeedChange={setSeedArtifactId}
        onUploadCorpus={handleUploadCorpus}
        onSavePreferences={handleSavePreferences}
        onChangePassword={handleChangePassword}
      />
    </Layout>
  );
};

export default Settings;
