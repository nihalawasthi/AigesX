import { Link } from "react-router-dom";

const Landing = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-800 text-white">
      <header className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
        <h1 className="text-xl font-bold tracking-wide">AigesX</h1>
        <nav className="flex gap-3 text-sm">
          <Link to="/about" className="px-3 py-1 rounded hover:bg-white/10">About</Link>
          <Link to="/login" className="px-3 py-1 rounded bg-white text-slate-900 font-semibold">Login</Link>
        </nav>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-16 grid gap-8 lg:grid-cols-2 items-center">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Fuzzing As A Service</p>
          <h2 className="text-4xl md:text-5xl font-extrabold leading-tight mt-3">
            Upload Binaries Or Public Repositories,
            <span className="text-cyan-300"> Get Actionable Vulnerability Findings</span>
          </h2>
          <p className="text-slate-200 mt-4 text-lg">
            AigesX combines AFL++, symbolic execution, and CVE correlation into one secure web workflow.
          </p>
          <div className="mt-7 flex gap-3">
            <Link to="/login" className="px-5 py-3 rounded-lg bg-cyan-300 text-slate-900 font-semibold">Start Analysis</Link>
            <Link to="/about" className="px-5 py-3 rounded-lg border border-white/30">Learn More</Link>
          </div>
        </div>

        <div className="bg-white/10 border border-white/15 rounded-2xl p-6 backdrop-blur-sm">
          <h3 className="text-lg font-semibold">Platform Pipeline</h3>
          <ol className="mt-3 space-y-2 text-sm text-slate-200 list-decimal list-inside">
            <li>Target intake from ELF binaries or public GitHub links</li>
            <li>Asynchronous job orchestration and execution queue</li>
            <li>Fuzzing + symbolic analysis + CVE matching</li>
            <li>Crash artifacts and report-driven vulnerability review</li>
          </ol>
        </div>
      </main>
    </div>
  );
};

export default Landing;
