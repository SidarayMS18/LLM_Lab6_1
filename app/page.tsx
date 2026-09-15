const tools = [
  { name: "save_note", args: "content, tags?", desc: "Create a note in notes.json" },
  { name: "search_notes", args: "query", desc: "Keyword search over content and tags" },
  { name: "list_notes", args: "limit?", desc: "Read the most recent notes" },
  { name: "update_note", args: "note_id, content?, tags?", desc: "Edit an existing note" },
  { name: "delete_note", args: "note_id", desc: "Remove a note permanently" },
];

const steps = [
  "cd lab6 && pip install -r requirements.txt",
  "cp .env.example .env   # paste your GROQ_API_KEY inside",
  "python client.py",
];

export default function Home() {
  const hasGroqKey = Boolean(process.env.GROQ_API_KEY);
  return (
    <div className="flex min-h-screen justify-center font-sans">
      <main className="flex w-full max-w-3xl flex-col gap-10 px-6 py-16">
        <header className="flex flex-col gap-3">
          <p className="text-sm font-medium text-muted-foreground">Lab6_LLM / Expt 1</p>
          <h1 className="text-4xl font-bold tracking-tight">Personal Assistant Memory Server</h1>
          <p className="max-w-xl text-lg text-muted-foreground">
            An MCP server that gives an LLM persistent memory through CRUD tools over a local{" "}
            <code className="rounded bg-muted px-1.5 py-0.5 text-base">notes.json</code> file, plus
            a Python client where the model decides which tool to call.
          </p>
        </header>

        <section className="flex flex-col gap-4">
          <h2 className="text-xl font-semibold">Exposed tools</h2>
          <ul className="divide-y rounded-lg border">
            {tools.map((t) => (
              <li key={t.name} className="flex flex-col gap-1 px-4 py-3 sm:flex-row sm:items-baseline sm:gap-4">
                <code className="shrink-0 font-mono text-sm font-semibold">
                  {t.name}({t.args})
                </code>
                <span className="text-sm text-muted-foreground">{t.desc}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-xl font-semibold">Run it</h2>
            <span
              className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${
                hasGroqKey ? "text-emerald-600 dark:text-emerald-400" : "text-amber-600 dark:text-amber-400"
              }`}
            >
              <span
                aria-hidden="true"
                className={`size-2 rounded-full ${hasGroqKey ? "bg-emerald-500" : "bg-amber-500"}`}
              />
              GROQ_API_KEY {hasGroqKey ? "configured in this project" : "missing in this project"}
            </span>
          </div>
          <pre className="overflow-x-auto rounded-lg border bg-muted p-4 font-mono text-sm leading-7">
            {steps.join("\n")}
          </pre>
          <p className="text-sm text-muted-foreground">
            The client launches <code>lab6/server.py</code> over stdio, converts its MCP tool schemas
            into function-calling definitions, and loops until the model returns a final answer. Try:{" "}
            <em>&quot;Remember the project deadline is 20 Sept&quot;</em>, then{" "}
            <em>&quot;What did I say about the project deadline?&quot;</em>
          </p>
          <p className="text-sm text-muted-foreground">
            Note: project secrets are not included in a downloaded ZIP, so after downloading you
            still need to paste the key into <code>lab6/.env</code>. The client reads{" "}
            <code>lab6/.env</code>, then the root <code>.env.local</code> / <code>.env</code>, then
            your shell environment.
          </p>
        </section>
      </main>
    </div>
  );
}
