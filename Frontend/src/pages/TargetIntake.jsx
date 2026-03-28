import Layout from "../components/Layout";
import TargetIntakeControls from "../components/TargetIntakeControls";
import { useScan } from "../context/ScanContext";

const TargetIntake = () => {
  const {
    binaryArtifactId,
    binaryArtifacts,
    sourceArtifactId,
    sourceArtifacts,
    setBinaryArtifactId,
    setSourceArtifactId,
    handleUploadBinary,
    handleUploadSource,
    runAnalysis,
    isGenerating,
    error,
  } = useScan();

  return (
    <Layout>
      {error && <p className="px-6 text-red-500">{error}</p>}
      <section className="p-6">
        <div className="bg-white border border-neutral-200/20 rounded-lg p-6 flex items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-wider text-neutral-500">Target Intake</p>
            <h1 className="text-2xl font-bold text-neutral-800 mt-1">Binary Upload And Source Repository Intake</h1>
            <p className="text-neutral-600 mt-2">Submit your executable targets and select the active source repository target for analysis jobs.</p>
          </div>
          <button
            onClick={runAnalysis}
            disabled={isGenerating}
            className="px-4 py-2 rounded-lg bg-slate-900 text-white disabled:opacity-60"
          >
            {isGenerating ? "Running..." : "Start Analysis"}
          </button>
        </div>
      </section>

      <TargetIntakeControls
        binaryArtifactId={binaryArtifactId}
        binaryArtifacts={binaryArtifacts}
        sourceArtifactId={sourceArtifactId}
        sourceArtifacts={sourceArtifacts}
        onBinaryChange={setBinaryArtifactId}
        onSourceChange={setSourceArtifactId}
        onUploadBinary={handleUploadBinary}
        onUploadSource={handleUploadSource}
      />
    </Layout>
  );
};

export default TargetIntake;
