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
}) => {
  const [binaryFile, setBinaryFile] = useState(null);
  const [repoUrl, setRepoUrl] = useState("");

  return (
    <section id="TargetIntake" className="p-6">
      <div className="bg-white border border-neutral-200/20 rounded-lg p-6 grid gap-6 lg:grid-cols-2">
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-neutral-700">Binary Target</h3>
          <div className="flex gap-2 items-center">
            <input type="file" onChange={(e) => setBinaryFile(e.target.files?.[0] || null)} className="text-sm" />
            <button
              className="px-3 py-1 rounded bg-blue-50 text-blue-700 disabled:opacity-50"
              onClick={() => binaryFile && onUploadBinary(binaryFile)}
              disabled={!binaryFile}
            >
              Upload ELF
            </button>
          </div>
          <p className="text-xs text-neutral-500">ELF binaries only for MVP target intake.</p>

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
        </div>
      </div>
    </section>
  );
};

export default TargetIntakeControls;
