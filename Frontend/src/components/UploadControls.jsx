import { useState } from "react";

const UploadControls = ({
  timeoutSeconds,
  memoryLimitMb,
  seedArtifactId,
  sourceArtifactId,
  corpusArtifacts,
  sourceArtifacts,
  onTimeoutChange,
  onMemoryChange,
  onSeedChange,
  onSourceChange,
  onUploadBinary,
  onUploadCorpus,
  onUploadSource,
}) => {
  const [binaryFile, setBinaryFile] = useState(null);
  const [corpusFile, setCorpusFile] = useState(null);
  const [repoUrl, setRepoUrl] = useState("");

  return (
    <section id="UploadControls" className="p-6">
      <div className="bg-white border border-neutral-200/20 rounded-lg p-6 grid gap-6 lg:grid-cols-2">
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-neutral-700">Target Intake</h3>
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

          <div className="border border-neutral-200/20 rounded p-3 bg-neutral-50 space-y-2">
            <p className="text-sm font-medium text-neutral-700">Public GitHub Repository</p>
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
        </div>

        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-neutral-700">Scan Profile</h3>
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

          <label className="text-sm text-neutral-600 block">
            Source Repository Target
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

export default UploadControls;
