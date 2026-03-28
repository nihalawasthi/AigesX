import { useState } from "react";

const TargetIntakeControls = ({
  binaryArtifactId,
  binaryArtifacts,
  sourceArtifactId,
  sourceArtifacts,
  onBinaryChange,
  onSourceChange,
  onUploadBinary,
  onUploadSource,
  isUploadingBinary,
}) => {
  const [binaryFileName, setBinaryFileName] = useState("");
  const [repoUrl, setRepoUrl] = useState("");

  const handleBinarySelect = async (event) => {
    const file = event.target.files?.[0] || null;
    if (!file) {
      setBinaryFileName("");
      return;
    }

    setBinaryFileName(file.name);
    try {
      await onUploadBinary(file);
    } finally {
      event.target.value = "";
    }
  };

  return (
    <section id="TargetIntake" className="p-6">
      <div className="bg-white border border-neutral-200/20 rounded-lg p-6 grid gap-6 lg:grid-cols-2">
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-neutral-700">Binary Target</h3>
          <div className="space-y-2">
            <input type="file" onChange={handleBinarySelect} className="text-sm" disabled={isUploadingBinary} />
            <p className="text-xs text-neutral-500">
              {isUploadingBinary
                ? `Uploading ${binaryFileName || "binary"}...`
                : binaryFileName
                  ? `Selected and uploaded: ${binaryFileName}`
                  : "Select a binary and it uploads automatically."}
            </p>
          </div>
          <p className="text-xs text-neutral-500">Supported: ELF, PE (.exe), and Mach-O binaries.</p>

          <label className="text-sm text-neutral-600 block">
            Active Binary Target
            <select
              className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
              value={binaryArtifactId || ""}
              onChange={(e) => onBinaryChange(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">Latest uploaded binary</option>
              {binaryArtifacts.map((artifact) => (
                <option key={artifact.id} value={artifact.id}>
                  #{artifact.id} - {artifact.file_name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-neutral-700">Public GitHub Repository</h3>
          <div className="border border-neutral-200/20 rounded p-3 bg-neutral-50 space-y-2">
            <input
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/org/repo"
              className="w-full border border-neutral-200 rounded px-2 py-1 text-sm"
            />
            <button
              className="px-3 py-1 rounded bg-blue-50 text-blue-700 disabled:opacity-50"
              onClick={() => repoUrl && onUploadSource(repoUrl)}
              disabled={!repoUrl}
            >
              Save Source Target
            </button>
          </div>

          <label className="text-sm text-neutral-600 block">
            Active Source Target
            <select
              className="mt-1 w-full border border-neutral-200 rounded px-2 py-1"
              value={sourceArtifactId || ""}
              onChange={(e) => onSourceChange(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">No source target</option>
              {sourceArtifacts.map((artifact) => (
                <option key={artifact.id} value={artifact.id}>
                  #{artifact.id} - {artifact.repo_url}
                </option>
              ))}
            </select>
          </label>
          <p className="text-xs text-neutral-500">If no custom corpus/seed is uploaded, AigesX auto-generates a device-stable default seed for this user.</p>
        </div>
      </div>
    </section>
  );
};

export default TargetIntakeControls;
