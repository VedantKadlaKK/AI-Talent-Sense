import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  BriefcaseBusiness,
  Building2,
  CalendarClock,
  ExternalLink,
  FilePlus2,
  GraduationCap,
  ListFilter,
  LoaderCircle,
  Mail,
  MapPin,
  Plus,
  Sparkles,
  Search,
  ShieldCheck,
  Trophy,
  Trash2,
  Users,
} from "lucide-react";
import { candidatesApi, jobsApi } from "./api";
import type {
  Candidate,
  Job,
  JobCreatePayload,
  JobIntelligence,
  JobStatus,
  RecommendationCandidate,
  SignalResult,
} from "./types";

type View = "dashboard" | "jobs" | "create" | "details" | "candidates" | "candidateDetails";

const statusLabels: Record<JobStatus, string> = {
  draft: "Draft",
  analyzed: "Analyzed",
  searching: "Searching",
  ranked: "Ranked",
  archived: "Archived",
};

const initialForm: JobCreatePayload = {
  title: "",
  company_name: "",
  description: "",
  status: "draft",
};

export function App() {
  const [view, setView] = useState<View>("dashboard");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState<number | null>(null);
  const [form, setForm] = useState<JobCreatePayload>(initialForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingCandidates, setIsLoadingCandidates] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [analyzingJobId, setAnalyzingJobId] = useState<number | null>(null);
  const [searchingJobId, setSearchingJobId] = useState<number | null>(null);
  const [normalizingJobId, setNormalizingJobId] = useState<number | null>(null);
  const [evaluatingJobId, setEvaluatingJobId] = useState<number | null>(null);
  const [rankingJobId, setRankingJobId] = useState<number | null>(null);
  const [candidateResultsByJob, setCandidateResultsByJob] = useState<Record<number, Candidate[]>>({});
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [signalResultsByJob, setSignalResultsByJob] = useState<Record<number, Record<number, SignalResult[]>>>({});
  const [recommendationsByJob, setRecommendationsByJob] = useState<Record<number, RecommendationCandidate[]>>({});
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  const selectedJob = useMemo(
    () => jobs.find((job) => job.id === selectedJobId) ?? null,
    [jobs, selectedJobId],
  );

  const selectedCandidate = useMemo(
    () => candidates.find((candidate) => candidate.id === selectedCandidateId) ?? null,
    [candidates, selectedCandidateId],
  );

  const filteredJobs = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return jobs;
    }
    return jobs.filter((job) =>
      [job.title, job.company_name, job.status]
        .join(" ")
        .toLowerCase()
        .includes(normalizedQuery),
    );
  }, [jobs, query]);

  const loadJobs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setJobs(await jobsApi.list());
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to load jobs");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadJobs();
  }, [loadJobs]);

  const loadCandidates = useCallback(async () => {
    setIsLoadingCandidates(true);
    setError(null);
    try {
      setCandidates(await candidatesApi.list());
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to load candidates");
    } finally {
      setIsLoadingCandidates(false);
    }
  }, []);

  function openJob(jobId: number) {
    setSelectedJobId(jobId);
    setView("details");
  }

  function openCandidates() {
    setView("candidates");
    void loadCandidates();
  }

  async function openCandidate(candidateId: number) {
    setSelectedCandidateId(candidateId);
    setView("candidateDetails");
    setError(null);
    try {
      const candidate = await candidatesApi.get(candidateId);
      setCandidates((currentCandidates) => {
        const exists = currentCandidates.some((current) => current.id === candidate.id);
        return exists
          ? currentCandidates.map((current) => (current.id === candidate.id ? candidate : current))
          : [candidate, ...currentCandidates];
      });
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to load candidate");
    }
  }

  async function createJob(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      const createdJob = await jobsApi.create(form);
      setJobs((currentJobs) => [createdJob, ...currentJobs]);
      setForm(initialForm);
      setSelectedJobId(createdJob.id);
      setView("details");
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to create job");
    } finally {
      setIsSaving(false);
    }
  }

  async function deleteJob(jobId: number) {
    setError(null);
    try {
      await jobsApi.delete(jobId);
      setJobs((currentJobs) => currentJobs.filter((job) => job.id !== jobId));
      if (selectedJobId === jobId) {
        setSelectedJobId(null);
        setView("jobs");
      }
      setCandidateResultsByJob((currentResults) => {
        const nextResults = { ...currentResults };
        delete nextResults[jobId];
        return nextResults;
      });
      setSignalResultsByJob((currentResults) => {
        const nextResults = { ...currentResults };
        delete nextResults[jobId];
        return nextResults;
      });
      setRecommendationsByJob((currentResults) => {
        const nextResults = { ...currentResults };
        delete nextResults[jobId];
        return nextResults;
      });
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to delete job");
    }
  }

  async function analyzeJob(jobId: number) {
    setAnalyzingJobId(jobId);
    setError(null);
    try {
      const intelligence = await jobsApi.analyze(jobId);
      setJobs((currentJobs) =>
        currentJobs.map((job) =>
          job.id === jobId ? { ...job, status: "analyzed", intelligence } : job,
        ),
      );
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to analyze job");
    } finally {
      setAnalyzingJobId(null);
    }
  }

  async function searchCandidates(jobId: number) {
    setSearchingJobId(jobId);
    setError(null);
    try {
      const searchResult = await jobsApi.searchCandidates(jobId);
      setCandidateResultsByJob((currentResults) => ({
        ...currentResults,
        [jobId]: searchResult.candidates,
      }));
      setJobs((currentJobs) =>
        currentJobs.map((job) => (job.id === jobId ? { ...job, status: "searching" } : job)),
      );
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to search candidates");
    } finally {
      setSearchingJobId(null);
    }
  }

  async function normalizeCandidates(jobId: number) {
    setNormalizingJobId(jobId);
    setError(null);
    try {
      const result = await jobsApi.normalizeCandidates(jobId);
      setCandidateResultsByJob((currentResults) => ({
        ...currentResults,
        [jobId]: result.candidates,
      }));
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to normalize candidate profiles");
    } finally {
      setNormalizingJobId(null);
    }
  }

  async function evaluateSignals(jobId: number) {
    setEvaluatingJobId(jobId);
    setError(null);
    try {
      const result = await jobsApi.evaluateSignals(jobId);
      setSignalResultsByJob((currentResults) => ({
        ...currentResults,
        [jobId]: groupSignalResultsByCandidate(result.results),
      }));
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to evaluate candidate signals");
    } finally {
      setEvaluatingJobId(null);
    }
  }

  async function rankCandidates(jobId: number) {
    setRankingJobId(jobId);
    setError(null);
    try {
      const result = await jobsApi.rankCandidates(jobId);
      setRecommendationsByJob((currentResults) => ({
        ...currentResults,
        [jobId]: result.recommendations,
      }));
      setCandidateResultsByJob((currentResults) => ({
        ...currentResults,
        [jobId]: result.recommendations.map((item) => item.candidate),
      }));
      setSignalResultsByJob((currentResults) => ({
        ...currentResults,
        [jobId]: result.recommendations.reduce<Record<number, SignalResult[]>>((grouped, item) => {
          grouped[item.candidate.id] = item.signals;
          return grouped;
        }, {}),
      }));
      setJobs((currentJobs) =>
        currentJobs.map((job) => (job.id === jobId ? { ...job, status: "ranked" } : job)),
      );
    } catch (currentError) {
      setError(currentError instanceof Error ? currentError.message : "Unable to rank candidates");
    } finally {
      setRankingJobId(null);
    }
  }

  return (
    <div className="min-h-screen bg-[#f6f7f9] text-ink">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 border-r border-slate-200 bg-white px-4 py-5 lg:block">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-cobalt text-white">
              <BriefcaseBusiness size={20} />
            </div>
            <div>
              <p className="text-sm font-semibold">AI Talent Sense</p>
              <p className="text-xs text-slate-500">Sourcing workspace</p>
            </div>
          </div>
          <nav className="space-y-1">
            <NavButton active={view === "dashboard"} onClick={() => setView("dashboard")}>
              <ListFilter size={18} />
              Dashboard
            </NavButton>
            <NavButton active={view === "jobs"} onClick={() => setView("jobs")}>
              <BriefcaseBusiness size={18} />
              Jobs
            </NavButton>
            <NavButton active={view === "candidates" || view === "candidateDetails"} onClick={openCandidates}>
              <Users size={18} />
              Candidates
            </NavButton>
            <NavButton active={view === "create"} onClick={() => setView("create")}>
              <FilePlus2 size={18} />
              Create Job
            </NavButton>
          </nav>
        </aside>

        <main className="flex min-w-0 flex-1 flex-col">
          <header className="border-b border-slate-200 bg-white px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-cobalt">
                  Recruiter Dashboard
                </p>
                <h1 className="mt-1 text-2xl font-semibold text-ink">
                  {view === "create"
                    ? "Create Job"
                    : view === "details"
                      ? selectedJob?.title ?? "Job Details"
                      : view === "candidateDetails"
                        ? selectedCandidate?.full_name ?? "Candidate Details"
                        : view === "candidates"
                          ? "Candidates"
                          : view === "jobs"
                            ? "Jobs"
                            : "Dashboard"}
                </h1>
              </div>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded-md bg-cobalt px-4 text-sm font-semibold text-white shadow-panel transition hover:bg-blue-700"
                onClick={() => setView("create")}
                type="button"
              >
                <Plus size={18} />
                New Job
              </button>
            </div>
          </header>

          <section className="flex-1 px-4 py-5 sm:px-6 lg:px-8">
            {error ? (
              <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            ) : null}

            {view === "dashboard" ? (
              <Dashboard
                jobs={jobs}
                isLoading={isLoading}
                onOpenJob={openJob}
                onOpenJobs={() => setView("jobs")}
              />
            ) : null}

            {view === "jobs" ? (
              <JobsView
                jobs={filteredJobs}
                isLoading={isLoading}
                query={query}
                onQueryChange={setQuery}
                onOpenJob={openJob}
                onDeleteJob={deleteJob}
              />
            ) : null}

            {view === "create" ? (
              <CreateJobView
                form={form}
                isSaving={isSaving}
                onBack={() => setView("jobs")}
                onChange={setForm}
                onSubmit={createJob}
              />
            ) : null}

            {view === "candidates" ? (
              <CandidatesView
                candidates={candidates}
                isLoading={isLoadingCandidates}
                onOpenCandidate={(candidateId) => void openCandidate(candidateId)}
              />
            ) : null}

            {view === "candidateDetails" ? (
              <CandidateDetailsView
                candidate={selectedCandidate}
                onBack={openCandidates}
              />
            ) : null}

            {view === "details" ? (
              <JobDetailsView
                job={selectedJob}
                isAnalyzing={selectedJobId !== null && analyzingJobId === selectedJobId}
                isSearching={selectedJobId !== null && searchingJobId === selectedJobId}
                isNormalizing={selectedJobId !== null && normalizingJobId === selectedJobId}
                isEvaluating={selectedJobId !== null && evaluatingJobId === selectedJobId}
                isRanking={selectedJobId !== null && rankingJobId === selectedJobId}
                candidates={selectedJobId !== null ? candidateResultsByJob[selectedJobId] ?? [] : []}
                recommendations={selectedJobId !== null ? recommendationsByJob[selectedJobId] ?? [] : []}
                signalResultsByCandidate={selectedJobId !== null ? signalResultsByJob[selectedJobId] ?? {} : {}}
                onBack={() => setView("jobs")}
                onAnalyzeJob={analyzeJob}
                onSearchCandidates={searchCandidates}
                onNormalizeCandidates={normalizeCandidates}
                onEvaluateSignals={evaluateSignals}
                onRankCandidates={rankCandidates}
                onDeleteJob={deleteJob}
              />
            ) : null}
          </section>
        </main>
      </div>
    </div>
  );
}

function groupSignalResultsByCandidate(results: Array<{ candidate_id: number; results: SignalResult[] }>) {
  return results.reduce<Record<number, SignalResult[]>>((grouped, item) => {
    grouped[item.candidate_id] = item.results;
    return grouped;
  }, {});
}

function NavButton({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      className={`flex h-10 w-full items-center gap-3 rounded-md px-3 text-left text-sm font-medium transition ${
        active ? "bg-blue-50 text-cobalt" : "text-slate-600 hover:bg-slate-50 hover:text-ink"
      }`}
      onClick={onClick}
      type="button"
    >
      {children}
    </button>
  );
}

function Dashboard({
  jobs,
  isLoading,
  onOpenJob,
  onOpenJobs,
}: {
  jobs: Job[];
  isLoading: boolean;
  onOpenJob: (jobId: number) => void;
  onOpenJobs: () => void;
}) {
  const recentJobs = jobs.slice(0, 5);
  const activeCount = jobs.filter((job) => job.status !== "archived").length;

  return (
    <div className="space-y-5">
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Total Jobs" value={jobs.length.toString()} />
        <Metric label="Active Jobs" value={activeCount.toString()} />
        <Metric label="Ranked Jobs" value={jobs.filter((job) => job.status === "ranked").length.toString()} />
      </div>

      <div className="rounded-md border border-slate-200 bg-white shadow-panel">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h2 className="text-sm font-semibold">Recent Jobs</h2>
          <button
            className="inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            onClick={onOpenJobs}
            type="button"
          >
            <BriefcaseBusiness size={16} />
            View Jobs
          </button>
        </div>
        <JobTable
          jobs={recentJobs}
          isLoading={isLoading}
          onOpenJob={onOpenJob}
          onDeleteJob={() => undefined}
          compact
        />
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold">{value}</p>
    </div>
  );
}

function JobsView({
  jobs,
  isLoading,
  query,
  onQueryChange,
  onOpenJob,
  onDeleteJob,
}: {
  jobs: Job[];
  isLoading: boolean;
  query: string;
  onQueryChange: (value: string) => void;
  onOpenJob: (jobId: number) => void;
  onDeleteJob: (jobId: number) => void;
}) {
  return (
    <div className="rounded-md border border-slate-200 bg-white shadow-panel">
      <div className="flex flex-col gap-3 border-b border-slate-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-sm font-semibold">All Jobs</h2>
        <label className="relative block w-full sm:w-80">
          <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={17} />
          <input
            className="h-10 w-full rounded-md border border-slate-200 pl-10 pr-3 text-sm outline-none transition focus:border-cobalt focus:ring-2 focus:ring-blue-100"
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Search jobs"
            type="search"
            value={query}
          />
        </label>
      </div>
      <JobTable jobs={jobs} isLoading={isLoading} onOpenJob={onOpenJob} onDeleteJob={onDeleteJob} />
    </div>
  );
}

function JobTable({
  jobs,
  isLoading,
  onOpenJob,
  onDeleteJob,
  compact = false,
}: {
  jobs: Job[];
  isLoading: boolean;
  onOpenJob: (jobId: number) => void;
  onDeleteJob: (jobId: number) => void;
  compact?: boolean;
}) {
  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center gap-2 text-sm text-slate-500">
        <LoaderCircle className="animate-spin" size={18} />
        Loading jobs
      </div>
    );
  }

  if (jobs.length === 0) {
    return <div className="px-4 py-10 text-center text-sm text-slate-500">No jobs yet.</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-left text-xs font-semibold uppercase text-slate-500">
          <tr>
            <th className="px-4 py-3">Role</th>
            <th className="px-4 py-3">Company</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Created</th>
            {!compact ? <th className="w-24 px-4 py-3 text-right">Actions</th> : null}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {jobs.map((job) => (
            <tr key={job.id} className="hover:bg-slate-50">
              <td className="max-w-xs px-4 py-3">
                <button
                  className="truncate text-left font-semibold text-cobalt hover:text-blue-700"
                  onClick={() => onOpenJob(job.id)}
                  type="button"
                >
                  {job.title}
                </button>
              </td>
              <td className="px-4 py-3 text-slate-600">{job.company_name}</td>
              <td className="px-4 py-3">
                <StatusBadge status={job.status} />
              </td>
              <td className="px-4 py-3 text-slate-600">{formatDate(job.created_at)}</td>
              {!compact ? (
                <td className="px-4 py-3 text-right">
                  <button
                    aria-label={`Delete ${job.title}`}
                    className="inline-flex h-9 w-9 items-center justify-center rounded-md text-slate-500 transition hover:bg-red-50 hover:text-red-600"
                    onClick={() => onDeleteJob(job.id)}
                    title="Delete job"
                    type="button"
                  >
                    <Trash2 size={17} />
                  </button>
                </td>
              ) : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CreateJobView({
  form,
  isSaving,
  onBack,
  onChange,
  onSubmit,
}: {
  form: JobCreatePayload;
  isSaving: boolean;
  onBack: () => void;
  onChange: (form: JobCreatePayload) => void;
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
}) {
  return (
    <form className="max-w-4xl rounded-md border border-slate-200 bg-white shadow-panel" onSubmit={onSubmit}>
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <button
          className="inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
          onClick={onBack}
          type="button"
        >
          <ArrowLeft size={16} />
          Back
        </button>
        <button
          className="inline-flex h-9 items-center gap-2 rounded-md bg-cobalt px-4 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          disabled={isSaving}
          type="submit"
        >
          {isSaving ? <LoaderCircle className="animate-spin" size={16} /> : <FilePlus2 size={16} />}
          Create
        </button>
      </div>

      <div className="grid gap-4 p-4 md:grid-cols-2">
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Job Title</span>
          <input
            className="mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none transition focus:border-cobalt focus:ring-2 focus:ring-blue-100"
            minLength={2}
            onChange={(event) => onChange({ ...form, title: event.target.value })}
            required
            value={form.title}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Company</span>
          <input
            className="mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm outline-none transition focus:border-cobalt focus:ring-2 focus:ring-blue-100"
            minLength={2}
            onChange={(event) => onChange({ ...form, company_name: event.target.value })}
            required
            value={form.company_name}
          />
        </label>
        <label className="block md:col-span-2">
          <span className="text-sm font-medium text-slate-700">Job Description</span>
          <textarea
            className="mt-1 min-h-72 w-full rounded-md border border-slate-200 px-3 py-3 text-sm leading-6 outline-none transition focus:border-cobalt focus:ring-2 focus:ring-blue-100"
            minLength={20}
            onChange={(event) => onChange({ ...form, description: event.target.value })}
            required
            value={form.description}
          />
        </label>
      </div>
    </form>
  );
}

function CandidatesView({
  candidates,
  isLoading,
  onOpenCandidate,
}: {
  candidates: Candidate[];
  isLoading: boolean;
  onOpenCandidate: (candidateId: number) => void;
}) {
  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white text-sm text-slate-500 shadow-panel">
        <LoaderCircle className="animate-spin" size={18} />
        Loading candidates
      </div>
    );
  }

  return (
    <div className="rounded-md border border-slate-200 bg-white shadow-panel">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Users size={18} className="text-pine" />
          Candidate List
        </div>
        <span className="text-xs font-semibold uppercase text-slate-500">{candidates.length} profiles</span>
      </div>
      {candidates.length === 0 ? (
        <div className="px-4 py-10 text-center text-sm text-slate-500">
          Search candidates from a job to populate this list.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50 text-left text-xs font-semibold uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Candidate</th>
                <th className="px-4 py-3">Company</th>
                <th className="px-4 py-3">Location</th>
                <th className="px-4 py-3">Experience</th>
                <th className="px-4 py-3">Profile</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {candidates.map((candidate) => (
                <tr key={candidate.id} className="hover:bg-slate-50">
                  <td className="max-w-xs px-4 py-3">
                    <button
                      className="truncate text-left font-semibold text-cobalt hover:text-blue-700"
                      onClick={() => onOpenCandidate(candidate.id)}
                      type="button"
                    >
                      {candidate.full_name}
                    </button>
                    <div className="mt-1 text-xs text-slate-500">{candidate.email}</div>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{candidate.current_company || "Not specified"}</td>
                  <td className="px-4 py-3 text-slate-600">{candidate.location || "Not specified"}</td>
                  <td className="px-4 py-3 text-slate-600">{candidate.experience || "Not specified"}</td>
                  <td className="px-4 py-3">
                    {candidate.profile?.normalized_at ? (
                      <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-semibold text-cobalt">
                        Normalized
                      </span>
                    ) : (
                      <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
                        Sourced
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function CandidateDetailsView({
  candidate,
  onBack,
}: {
  candidate: Candidate | null;
  onBack: () => void;
}) {
  if (!candidate) {
    return (
      <div className="rounded-md border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 shadow-panel">
        Select a candidate to view details.
      </div>
    );
  }

  return (
    <div className="max-w-5xl space-y-4">
      <div className="rounded-md border border-slate-200 bg-white shadow-panel">
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <button
            className="inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            onClick={onBack}
            type="button"
          >
            <ArrowLeft size={16} />
            Back
          </button>
          <span className="text-xs font-semibold uppercase text-slate-500">
            {candidate.profile?.normalized_at ? "Normalized" : "Sourced"}
          </span>
        </div>
        <div className="grid gap-4 p-4 md:grid-cols-3">
          <DetailItem icon={<Users size={18} />} label="Name" value={candidate.full_name} />
          <DetailItem icon={<BriefcaseBusiness size={18} />} label="Company" value={candidate.current_company || "Not specified"} />
          <DetailItem icon={<MapPin size={18} />} label="Location" value={candidate.location || "Not specified"} />
        </div>
        <div className="border-t border-slate-200 p-4">
          <h2 className="text-sm font-semibold">Summary</h2>
          <p className="mt-3 text-sm leading-6 text-slate-700">{candidate.profile?.normalized_summary || candidate.summary}</p>
        </div>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <RequirementField icon={<ShieldCheck size={17} />} label="Skills">
          <TagList values={candidate.profile?.skills ?? []} />
        </RequirementField>
        <RequirementField icon={<GraduationCap size={17} />} label="Education">
          <TagList values={candidate.profile?.education ?? []} />
        </RequirementField>
        <RequirementField icon={<ShieldCheck size={17} />} label="Certifications">
          <TagList values={candidate.profile?.certifications ?? []} />
        </RequirementField>
        <RequirementField icon={<ListFilter size={17} />} label="Sources">
          <TagList values={candidate.sources.map((source) => source.source)} />
        </RequirementField>
      </div>
    </div>
  );
}

function JobDetailsView({
  job,
  isAnalyzing,
  isSearching,
  isNormalizing,
  isEvaluating,
  isRanking,
  candidates,
  recommendations,
  signalResultsByCandidate,
  onBack,
  onAnalyzeJob,
  onSearchCandidates,
  onNormalizeCandidates,
  onEvaluateSignals,
  onRankCandidates,
  onDeleteJob,
}: {
  job: Job | null;
  isAnalyzing: boolean;
  isSearching: boolean;
  isNormalizing: boolean;
  isEvaluating: boolean;
  isRanking: boolean;
  candidates: Candidate[];
  recommendations: RecommendationCandidate[];
  signalResultsByCandidate: Record<number, SignalResult[]>;
  onBack: () => void;
  onAnalyzeJob: (jobId: number) => void;
  onSearchCandidates: (jobId: number) => void;
  onNormalizeCandidates: (jobId: number) => void;
  onEvaluateSignals: (jobId: number) => void;
  onRankCandidates: (jobId: number) => void;
  onDeleteJob: (jobId: number) => void;
}) {
  if (!job) {
    return (
      <div className="rounded-md border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 shadow-panel">
        Select a job to view details.
      </div>
    );
  }

  return (
    <div className="max-w-5xl space-y-4">
      <div className="rounded-md border border-slate-200 bg-white shadow-panel">
        <div className="flex flex-col gap-3 border-b border-slate-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
          <button
            className="inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
            onClick={onBack}
            type="button"
          >
            <ArrowLeft size={16} />
            Back
          </button>
          <div className="flex flex-wrap gap-2">
            <button
              className="inline-flex h-9 items-center gap-2 rounded-md bg-cobalt px-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={isAnalyzing}
              onClick={() => onAnalyzeJob(job.id)}
              type="button"
            >
              {isAnalyzing ? <LoaderCircle className="animate-spin" size={16} /> : <Sparkles size={16} />}
              Analyze JD
            </button>
            <button
              className="inline-flex h-9 items-center gap-2 rounded-md bg-pine px-3 text-sm font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={isSearching}
              onClick={() => onSearchCandidates(job.id)}
              type="button"
            >
              {isSearching ? <LoaderCircle className="animate-spin" size={16} /> : <Users size={16} />}
              Search Candidates
            </button>
            <button
              className="inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
              disabled={isNormalizing || candidates.length === 0}
              onClick={() => onNormalizeCandidates(job.id)}
              type="button"
            >
              {isNormalizing ? <LoaderCircle className="animate-spin" size={16} /> : <Sparkles size={16} />}
              Normalize Profiles
            </button>
            <button
              className="inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-400"
              disabled={isEvaluating || candidates.length === 0}
              onClick={() => onEvaluateSignals(job.id)}
              type="button"
            >
              {isEvaluating ? <LoaderCircle className="animate-spin" size={16} /> : <ListFilter size={16} />}
              Evaluate Signals
            </button>
            <button
              className="inline-flex h-9 items-center gap-2 rounded-md bg-ember px-3 text-sm font-semibold text-white transition hover:bg-amber-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              disabled={isRanking || candidates.length === 0}
              onClick={() => onRankCandidates(job.id)}
              type="button"
            >
              {isRanking ? <LoaderCircle className="animate-spin" size={16} /> : <Trophy size={16} />}
              Rank
            </button>
            <button
              className="inline-flex h-9 items-center gap-2 rounded-md border border-red-200 px-3 text-sm font-semibold text-red-600 transition hover:bg-red-50"
              onClick={() => onDeleteJob(job.id)}
              type="button"
            >
              <Trash2 size={16} />
              Delete
            </button>
          </div>
        </div>

        <div className="grid gap-4 p-4 md:grid-cols-3">
          <DetailItem icon={<BriefcaseBusiness size={18} />} label="Role" value={job.title} />
          <DetailItem icon={<Building2 size={18} />} label="Company" value={job.company_name} />
          <DetailItem icon={<CalendarClock size={18} />} label="Created" value={formatDate(job.created_at)} />
        </div>

        <div className="border-t border-slate-200 p-4">
          <div className="mb-3 flex items-center gap-2">
            <StatusBadge status={job.status} />
          </div>
          <h2 className="text-sm font-semibold">Description</h2>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{job.description}</p>
        </div>
      </div>
      <JobIntelligencePanel intelligence={job.intelligence} isAnalyzing={isAnalyzing} />
      <RecommendationPanel isRanking={isRanking} recommendations={recommendations} />
      <CandidateSearchPanel
        candidates={candidates}
        isEvaluating={isEvaluating}
        isNormalizing={isNormalizing}
        isSearching={isSearching}
        signalResultsByCandidate={signalResultsByCandidate}
      />
    </div>
  );
}

function JobIntelligencePanel({
  intelligence,
  isAnalyzing,
}: {
  intelligence: JobIntelligence | null;
  isAnalyzing: boolean;
}) {
  if (isAnalyzing) {
    return (
      <div className="rounded-md border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 shadow-panel">
        <LoaderCircle className="mx-auto mb-3 animate-spin text-cobalt" size={24} />
        Analyzing hiring requirements
      </div>
    );
  }

  if (!intelligence) {
    return (
      <div className="rounded-md border border-slate-200 bg-white p-5 shadow-panel">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Sparkles size={18} className="text-cobalt" />
          JD Intelligence
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          Run analysis to extract structured hiring requirements from this job description.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-slate-200 bg-white shadow-panel">
      <div className="border-b border-slate-200 px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Sparkles size={18} className="text-cobalt" />
          JD Intelligence
        </div>
      </div>
      <div className="grid gap-4 p-4 md:grid-cols-2 xl:grid-cols-3">
        <RequirementField icon={<ShieldCheck size={17} />} label="Skills">
          <TagList values={intelligence.skills} />
        </RequirementField>
        <RequirementField icon={<BriefcaseBusiness size={17} />} label="Experience">
          {valueOrFallback(intelligence.experience)}
        </RequirementField>
        <RequirementField icon={<GraduationCap size={17} />} label="Education">
          {valueOrFallback(intelligence.education)}
        </RequirementField>
        <RequirementField icon={<Building2 size={17} />} label="Industry">
          {valueOrFallback(intelligence.industry)}
        </RequirementField>
        <RequirementField icon={<MapPin size={17} />} label="Location">
          {valueOrFallback(intelligence.location)}
        </RequirementField>
        <RequirementField icon={<ListFilter size={17} />} label="Seniority">
          {valueOrFallback(intelligence.seniority)}
        </RequirementField>
        <RequirementField icon={<ShieldCheck size={17} />} label="Certifications">
          <TagList values={intelligence.certifications} />
        </RequirementField>
        <RequirementField icon={<Plus size={17} />} label="Nice-to-have Skills">
          <TagList values={intelligence.nice_to_have_skills} />
        </RequirementField>
      </div>
    </div>
  );
}

function RecommendationPanel({
  isRanking,
  recommendations,
}: {
  isRanking: boolean;
  recommendations: RecommendationCandidate[];
}) {
  if (isRanking) {
    return (
      <div className="rounded-md border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 shadow-panel">
        <LoaderCircle className="mx-auto mb-3 animate-spin text-ember" size={24} />
        Ranking candidates
      </div>
    );
  }

  if (recommendations.length === 0) {
    return null;
  }

  return (
    <div className="rounded-md border border-slate-200 bg-white shadow-panel">
      <div className="flex flex-col gap-2 border-b border-slate-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Trophy size={18} className="text-ember" />
          Ranked Recommendations
        </div>
        <span className="text-xs font-semibold uppercase text-slate-500">
          {recommendations.length} ranked
        </span>
      </div>
      <div className="divide-y divide-slate-100">
        {recommendations.map((item) => (
          <RecommendationItem key={item.recommendation.id} item={item} />
        ))}
      </div>
    </div>
  );
}

function RecommendationItem({ item }: { item: RecommendationCandidate }) {
  const topSignals = [...item.signals].sort((left, right) => right.contribution - left.contribution).slice(0, 3);

  return (
    <article className="grid gap-4 px-4 py-4 lg:grid-cols-[180px_minmax(0,1fr)_minmax(240px,0.7fr)]">
      <div>
        <div className="text-xs font-semibold uppercase text-slate-500">Rank</div>
        <div className="mt-1 flex items-end gap-2">
          <span className="text-3xl font-semibold text-ink">#{item.recommendation.rank}</span>
          <span className="pb-1 text-sm font-semibold text-cobalt">
            {Math.round(item.recommendation.overall_score)}
          </span>
        </div>
        <span className="mt-3 inline-flex rounded-md bg-amber-50 px-2 py-1 text-xs font-semibold text-ember ring-1 ring-amber-200">
          {item.recommendation.recommendation}
        </span>
      </div>

      <div className="min-w-0">
        <h3 className="text-sm font-semibold text-ink">{item.candidate.full_name}</h3>
        <p className="mt-2 text-sm leading-6 text-slate-700">{item.recommendation.summary}</p>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <MiniList label="Strengths" values={item.recommendation.strengths.slice(0, 3)} />
          <MiniList label="Weaknesses" values={item.recommendation.weaknesses.slice(0, 3)} />
        </div>
        {item.recommendation.missing_skills.length > 0 ? (
          <div className="mt-3">
            <div className="mb-2 text-xs font-semibold uppercase text-slate-500">Missing Skills</div>
            <TagList values={item.recommendation.missing_skills} />
          </div>
        ) : null}
      </div>

      <div className="space-y-2">
        <div className="text-xs font-semibold uppercase text-slate-500">Top Signals</div>
        {topSignals.map((signal) => (
          <div key={signal.id} className="rounded-md border border-slate-200 p-3">
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-semibold text-ink">{signal.signal_name}</span>
              <span className="text-xs font-semibold text-cobalt">{Math.round(signal.score)}</span>
            </div>
            <p className="mt-1 text-xs leading-5 text-slate-600">{signal.reason}</p>
          </div>
        ))}
      </div>
    </article>
  );
}

function MiniList({ label, values }: { label: string; values: string[] }) {
  return (
    <div>
      <div className="mb-2 text-xs font-semibold uppercase text-slate-500">{label}</div>
      {values.length === 0 ? (
        <p className="text-sm text-slate-500">Not specified</p>
      ) : (
        <ul className="space-y-1 text-sm leading-6 text-slate-700">
          {values.map((value) => (
            <li key={value}>{value}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function CandidateSearchPanel({
  candidates,
  isEvaluating,
  isNormalizing,
  isSearching,
  signalResultsByCandidate,
}: {
  candidates: Candidate[];
  isEvaluating: boolean;
  isNormalizing: boolean;
  isSearching: boolean;
  signalResultsByCandidate: Record<number, SignalResult[]>;
}) {
  if (isSearching) {
    return (
      <div className="rounded-md border border-slate-200 bg-white p-8 text-center text-sm text-slate-500 shadow-panel">
        <LoaderCircle className="mx-auto mb-3 animate-spin text-pine" size={24} />
        Searching talent sources
      </div>
    );
  }

  return (
    <div className="rounded-md border border-slate-200 bg-white shadow-panel">
      <div className="flex flex-col gap-2 border-b border-slate-200 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Users size={18} className="text-pine" />
          Candidate Search
        </div>
        <div className="flex items-center gap-3 text-xs font-semibold uppercase text-slate-500">
          {isNormalizing ? (
            <span className="inline-flex items-center gap-1 text-cobalt">
              <LoaderCircle className="animate-spin" size={14} />
              Normalizing
            </span>
          ) : null}
          {isEvaluating ? (
            <span className="inline-flex items-center gap-1 text-ember">
              <LoaderCircle className="animate-spin" size={14} />
              Evaluating
            </span>
          ) : null}
          <span>{candidates.length} sourced</span>
        </div>
      </div>
      {candidates.length === 0 ? (
        <div className="px-4 py-8 text-center text-sm text-slate-500">
          No sourced candidates yet.
        </div>
      ) : (
        <div className="divide-y divide-slate-100">
          {candidates.map((candidate) => (
            <CandidateResultItem
              key={candidate.id}
              candidate={candidate}
              signalResults={signalResultsByCandidate[candidate.id] ?? []}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function CandidateResultItem({
  candidate,
  signalResults,
}: {
  candidate: Candidate;
  signalResults: SignalResult[];
}) {
  const sourceNames = candidate.sources.map((source) => source.source);
  const primarySourceUrl = candidate.sources.find((source) => source.profile_url)?.profile_url;
  const skills = candidate.profile?.skills.slice(0, 8) ?? [];
  const normalizedSummary = candidate.profile?.normalized_summary;
  const completeness = getCompleteness(candidate);
  const isNormalized = Boolean(candidate.profile?.normalized_at);

  return (
    <article className="grid gap-4 px-4 py-4 lg:grid-cols-[minmax(0,1.4fr)_minmax(260px,0.8fr)]">
      <div className="min-w-0">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h3 className="break-words text-sm font-semibold text-ink">{candidate.full_name}</h3>
            <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500">
              <span className="inline-flex items-center gap-1">
                <BriefcaseBusiness size={14} />
                {candidate.current_company || "Company unavailable"}
              </span>
              <span className="inline-flex items-center gap-1">
                <MapPin size={14} />
                {candidate.location || "Location unavailable"}
              </span>
              <span className="inline-flex items-center gap-1">
                <Mail size={14} />
                {candidate.email}
              </span>
            </div>
          </div>
          {primarySourceUrl ? (
            <a
              className="inline-flex h-8 items-center gap-2 rounded-md border border-slate-200 px-3 text-xs font-semibold text-slate-700 transition hover:bg-slate-50"
              href={primarySourceUrl}
              rel="noreferrer"
              target="_blank"
            >
              <ExternalLink size={14} />
              Profile
            </a>
          ) : null}
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-700">{candidate.summary}</p>
        {normalizedSummary ? (
          <div className="mt-3 rounded-md border border-blue-100 bg-blue-50 px-3 py-2">
            <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase text-cobalt">
              <Sparkles size={14} />
              Candidate Intelligence
            </div>
            <p className="text-sm leading-6 text-slate-700">{normalizedSummary}</p>
          </div>
        ) : null}
      </div>

      <div className="space-y-3">
        <RequirementField icon={<Sparkles size={17} />} label="Profile Status">
          {isNormalized ? "Normalized" : "Sourced"}
          {completeness !== null ? (
            <span className="ml-2 text-xs font-semibold text-slate-500">
              {Math.round(completeness * 100)}% coverage
            </span>
          ) : null}
        </RequirementField>
        <RequirementField icon={<BriefcaseBusiness size={17} />} label="Experience">
          {valueOrFallback(candidate.experience)}
        </RequirementField>
        <RequirementField icon={<ListFilter size={17} />} label="Sources">
          <TagList values={sourceNames} />
        </RequirementField>
        <RequirementField icon={<ShieldCheck size={17} />} label="Skills">
          <TagList values={skills} />
        </RequirementField>
      </div>
      {signalResults.length > 0 ? <SignalBreakdown results={signalResults} /> : null}
    </article>
  );
}

function SignalBreakdown({ results }: { results: SignalResult[] }) {
  const topResults = [...results].sort((left, right) => right.contribution - left.contribution).slice(0, 5);
  const averageScore = Math.round(results.reduce((total, result) => total + result.score, 0) / results.length);

  return (
    <div className="lg:col-span-2">
      <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
        <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-600">
            <ListFilter size={15} />
            Signal Breakdown
          </div>
          <span className="text-xs font-semibold text-slate-500">
            {results.length} signals, avg {averageScore}
          </span>
        </div>
        <div className="grid gap-2 md:grid-cols-2">
          {topResults.map((result) => (
            <div key={result.id} className="rounded-md border border-slate-200 bg-white p-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-ink">{result.signal_name}</p>
                  <p className="mt-1 text-xs font-medium uppercase text-slate-500">{result.category}</p>
                </div>
                <span className="rounded-md bg-blue-50 px-2 py-1 text-xs font-semibold text-cobalt">
                  {Math.round(result.score)}
                </span>
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-600">{result.reason}</p>
              <p className="mt-2 text-xs font-semibold text-slate-500">
                Weight {result.weight} - Contribution {Math.round(result.contribution)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function getCompleteness(candidate: Candidate) {
  const value = candidate.profile?.source_coverage?.completeness;
  return typeof value === "number" ? value : null;
}

function RequirementField({
  icon,
  label,
  children,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-md border border-slate-200 p-3">
      <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase text-slate-500">
        {icon}
        {label}
      </div>
      <div className="text-sm font-medium text-ink">{children}</div>
    </div>
  );
}

function TagList({ values }: { values: string[] }) {
  if (values.length === 0) {
    return <span className="text-slate-500">Not specified</span>;
  }
  return (
    <div className="flex flex-wrap gap-2">
      {values.map((value) => (
        <span key={value} className="rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700">
          {value}
        </span>
      ))}
    </div>
  );
}

function valueOrFallback(value: string) {
  return value.trim() ? value : <span className="text-slate-500">Not specified</span>;
}

function DetailItem({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md border border-slate-200 p-3">
      <div className="mb-2 flex items-center gap-2 text-slate-500">
        {icon}
        <span className="text-xs font-semibold uppercase">{label}</span>
      </div>
      <p className="break-words text-sm font-semibold text-ink">{value}</p>
    </div>
  );
}

function StatusBadge({ status }: { status: JobStatus }) {
  const className =
    status === "ranked"
      ? "bg-green-50 text-pine ring-green-200"
      : status === "archived"
        ? "bg-slate-100 text-slate-600 ring-slate-200"
        : status === "searching"
          ? "bg-amber-50 text-ember ring-amber-200"
          : "bg-blue-50 text-cobalt ring-blue-200";

  return (
    <span className={`inline-flex rounded-md px-2 py-1 text-xs font-semibold ring-1 ${className}`}>
      {statusLabels[status]}
    </span>
  );
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
