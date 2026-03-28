import { useState } from "react";
import { useLanguage } from "../context/LanguageContext";

const SettingsControls = ({
  profile,
  security,
  timeoutSeconds,
  memoryLimitMb,
  seedArtifactId,
  corpusArtifacts,
  onProfileChange,
  onSecurityChange,
  onTimeoutChange,
  onMemoryChange,
  onSeedChange,
  onUploadCorpus,
  onSavePreferences,
  onChangePassword,
}) => {
  const [corpusFile, setCorpusFile] = useState(null);
  const [profileFileError, setProfileFileError] = useState("");
  const { t } = useLanguage();

  const handleProfilePic = (file) => {
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setProfileFileError("Profile picture must be an image file.");
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      onProfileChange("profilePic", reader.result);
      setProfileFileError("");
    };
    reader.readAsDataURL(file);
  };

  return (
    <section id="ScanSettings" className="p-6">
      <div className="bg-white border border-neutral-200/20 rounded-lg p-6 grid gap-6 lg:grid-cols-2">
        <div className="space-y-3 lg:col-span-2">
          <h3 className="text-lg font-semibold text-neutral-700">Account Profile</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm text-neutral-600">
              Name
              <input
                type="text"
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={profile.name}
                onChange={(e) => onProfileChange("name", e.target.value)}
                placeholder="Full name"
              />
            </label>
            <label className="text-sm text-neutral-600">
              Username
              <input
                type="text"
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={profile.usernameDraft}
                onChange={(e) => onProfileChange("usernameDraft", e.target.value)}
                placeholder={profile.username || "Username"}
              />
            </label>
            <label className="text-sm text-neutral-600">
              Email
              <input
                type="email"
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={profile.emailDraft}
                onChange={(e) => onProfileChange("emailDraft", e.target.value)}
                placeholder={profile.email || "name@example.com"}
              />
            </label>
            {/*
            <label className="text-sm text-neutral-600">
              Timezone
              <select
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={profile.timezone}
                onChange={(e) => onProfileChange("timezone", e.target.value)}
              >
                <option value="UTC">UTC</option>
                <option value="Asia/Kolkata">Asia/Kolkata</option>
                <option value="Europe/London">Europe/London</option>
                <option value="America/New_York">America/New_York</option>
              </select>
            </label>
            */}
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm text-neutral-600">
              Profile Picture
              <input
                type="file"
                accept="image/*"
                className="mt-1 w-full text-sm"
                onChange={(e) => handleProfilePic(e.target.files?.[0])}
              />
            </label>
            <div className="text-sm text-neutral-600">
              Preview
              <div className="mt-1 w-16 h-16 rounded-full overflow-hidden border border-neutral-200 bg-neutral-50 flex items-center justify-center">
                {profile.profilePic ? (
                  <img src={profile.profilePic} alt="Profile" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-xs text-neutral-400">No image</span>
                )}
              </div>
            </div>
          </div>
          {profileFileError && <p className="text-sm text-red-500">{profileFileError}</p>}
        </div>

        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-neutral-700">Corpus Management</h3>
          <div className="flex gap-2 items-center">
            <input type="file" onChange={(e) => setCorpusFile(e.target.files?.[0] || null)} className="text-sm" />
            <button
              className="px-3 py-1 rounded bg-blue-50 text-blue-700 disabled:opacity-50"
              onClick={() => corpusFile && onUploadCorpus(corpusFile)}
              disabled={!corpusFile}
            >
              Upload Corpus
            </button>
          </div>

          <label className="text-sm text-neutral-600 block">
            Seed Corpus
            <select
              className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
              value={seedArtifactId || ""}
              onChange={(e) => onSeedChange(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">No seed corpus</option>
              {corpusArtifacts.map((artifact) => (
                <option key={artifact.id} value={artifact.id}>
                  #{artifact.id} - {artifact.file_name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-neutral-700">Execution Profile</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm text-neutral-600">
              Timeout (s)
              <input
                type="number"
                min={1}
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={timeoutSeconds}
                onChange={(e) => onTimeoutChange(Number(e.target.value))}
              />
            </label>
            <label className="text-sm text-neutral-600">
              Memory (MB)
              <input
                type="number"
                min={64}
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={memoryLimitMb}
                onChange={(e) => onMemoryChange(Number(e.target.value))}
              />
            </label>
          </div>
        </div>

        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-neutral-700">Preferences</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm text-neutral-600">
              Display
              <select
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={profile.displayMode}
                onChange={(e) => onProfileChange("displayMode", e.target.value)}
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </label>

            <label className="text-sm text-neutral-600">
              Language
              <select
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={profile.language}
                onChange={(e) => onProfileChange("language", e.target.value)}
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="hi">Hindi</option>
              </select>
            </label>
          </div>

          <div className="grid gap-2 text-sm text-neutral-700">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={profile.notifyJobComplete}
                onChange={(e) => onProfileChange("notifyJobComplete", e.target.checked)}
              />
              Notify on job completion
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={profile.notifyCriticalOnly}
                onChange={(e) => onProfileChange("notifyCriticalOnly", e.target.checked)}
              />
              Notify for critical findings only
            </label>
          </div>
        </div>

        <div className="space-y-3 lg:col-span-2">
          <h3 className="text-lg font-semibold text-neutral-700">Security</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm text-neutral-600">
              New Password
              <input
                type="password"
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={security.newPassword}
                onChange={(e) => onSecurityChange("newPassword", e.target.value)}
              />
            </label>
            <label className="text-sm text-neutral-600">
              Confirm Password
              <input
                type="password"
                className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
                value={security.confirmPassword}
                onChange={(e) => onSecurityChange("confirmPassword", e.target.value)}
              />
            </label>
          </div>

          <div className="grid gap-2 text-sm text-neutral-700">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={security.twoFactorEnabled}
                onChange={(e) => onSecurityChange("twoFactorEnabled", e.target.checked)}
              />
              Enable two-factor authentication
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={security.sessionAlerts}
                onChange={(e) => onSecurityChange("sessionAlerts", e.target.checked)}
              />
              Alert on new sign-in
            </label>
          </div>

          <button
            onClick={onChangePassword}
            className="px-4 py-2 rounded-lg border border-neutral-300 text-neutral-700 hover:bg-neutral-100"
          >
            Change Password
          </button>
        </div>

        <div className="lg:col-span-2 flex justify-end">
          <button
            onClick={onSavePreferences}
            className="px-4 py-2 rounded-lg bg-slate-900 text-white hover:bg-slate-800"
          >
            {t("saveSettings")}
          </button>
        </div>
      </div>
    </section>
  );
};

export default SettingsControls;
