import { Link } from "react-router-dom";

const About = () => {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="max-w-5xl mx-auto px-6 py-6 flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-900">About AigesX</h1>
        <Link to="/" className="text-sm text-slate-700 hover:text-slate-900">Back To Home</Link>
      </header>

      <main className="max-w-5xl mx-auto px-6 pb-12 grid gap-6">
        <section className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-2xl font-bold text-slate-900">Mission</h2>
          <p className="mt-3 text-slate-700">
            AigesX delivers practical vulnerability discovery as a web service so teams can test software continuously without building custom fuzzing infrastructure.
          </p>
        </section>

        <section className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-2xl font-bold text-slate-900">Core Capabilities</h2>
          <ul className="mt-3 text-slate-700 list-disc list-inside space-y-1">
            <li>AFL++ based fuzzing workflows</li>
            <li>Symbolic execution modules for path-level insights</li>
            <li>CVE correlation and finding metadata enrichment</li>
            <li>Report-driven triage and crash artifact retrieval</li>
          </ul>
        </section>

        <section className="bg-white rounded-xl border border-slate-200 p-6">
          <h2 className="text-2xl font-bold text-slate-900">Target Model</h2>
          <p className="mt-3 text-slate-700">
            Users submit either an ELF binary or a public GitHub repository link, then execute security jobs from the dashboard to inspect findings, severity trends, and crash details.
          </p>
        </section>
      </main>
    </div>
  );
};

export default About;
