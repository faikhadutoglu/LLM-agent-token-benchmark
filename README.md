# TESTFAIKMETHODIK - Token Comparison of 4 AI Agent Methods

## Purpose

This project is part of a **Bachelor's thesis** investigating how different
ways of providing context and instructions to an AI agent (Claude API)
affect **token consumption**, **execution time**, and **correctness** when
the agent has to perform the same file-editing task in a project.

The core question: if an agent must find and update several pieces of
information scattered across many files, does it matter *how* it is told
where to look — and if so, how much does that choice cost in tokens and time?
To answer this, four different "briefing strategies" (methods) are tested
against the identical task, on the identical example project, with the same
tools and the same automated correctness check. Only the guidance the agent
receives (the "skill") differs between methods.

This experiment compares **4 methods** by which an AI agent (Claude API)
performs derivable name/variant changes ("Group A") throughout a project.
**Token usage**, **duration**, and **correctness** are measured.

The example project is deliberately neutral: a **desk lamp** with 10 stages.
It contains no real company data and does not need to actually "work" -
it exists only to make the changes and the measurement comparison possible.

---



## 1. The Task (identical for all 4 methods)

In the template project (`projekt_vorlage/`), the placeholder variant
**Variantx** appears in 5 different spellings. The agent must derive a new
variant from it (e.g. `Entry`):


| Placeholder   | becomes (example: Entry) |
| ------------- | ------------------------ |
| `VARIANTX`    | `ENTRY`                  |
| `Variantx`    | `Entry`                  |
| `variantx`    | `entry`                  |
| `variantxevo` | `entryevo`               |
| `VariantxEVO` | `EntryEVO`               |


**Capitalization must match exactly.**

There are **10 changes in total**: each of the 10 stages has a `stage.json`
with exactly one variant field (the field name differs per stage, e.g.
`variantenkennung`, `variant_id`, `modellname` ...). The exact list is in
`projekt_vorlage/tools/variant_manifest.json`.

The stages alternate between **5 files** (stage.json, README.md, config.yaml,
bom.csv, pruefplan.txt) and **3 files** (stage.json, config.yaml, notizen.txt).
The filler files contain NO variant identifier - they only simulate
"searching through a large project".

## 2. The 4 Methods


| #   | Method              | Agent              | Skill                            | Idea                                                                                                                                                         |
| --- | ------------------- | ------------------ | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Search it yourself  | agent1_sucher      | skills/method1_selbst_suchen     | The agent gets nothing. It searches all folders/files itself and figures out where changes are needed.                                                       |
| 2   | Exact paths         | agent2_pfadfolger  | skills/method2_exakte_pfade      | The agent gets the exact file/field list and replaces directly, without reading first.                                                                       |
| 3   | Semantic map        | agent3_kartenleser | skills/method3_semantische_karte | The agent first reads `SEMANTIC_MAP.md` (describes what each file is for) and then decides itself what to read. A middle ground between 1 and 2.             |
| 4   | variant.json + tool | agent4_toolnutzer  | skills/method4_variant_json_tool | All changes live centrally in `variant.json`. The agent only edits this one file and runs `tools/apply_variant.py`, which writes all 10 files automatically. |


Each agent uses **exactly one skill**. Agent text + skill text together form
the system prompt (it is also written into every `agent_log.txt`, for full
transparency).

Only Agent 4 gets the additional tool `run_apply_tool`.
Otherwise all agents have the same tools: `list_dir`, `read_file`,
`str_replace`, `write_file`.

## 3. What Happens on One Button Press (Test Run)

Pressing a method button automatically runs the following, **5 times in a
row** (once per variant name: **Entry, Middle, Einfach, Mittlere, Easy**):

1. A new variant folder is created:
  `results/<method>/<timestamp>/<variant>/`
2. The unmodified template is copied there into `project/`
  (so every run starts from zero).
3. The AI agent is started with the matching system prompt (agent + skill)
  and the task, and works autonomously with its tools until it reports
   "FERTIG" (done). The prompt, every tool call, and the tokens per API
   call are logged to `agent_log.txt`.
4. **Time is measured** (pure agent runtime).
5. The result is **automatically checked against the reference**:
  - all 10 target fields must have exactly the correct value in the
   correct spelling (the expected value is computed deterministically
   from template + manifest + variant name),
  - all remaining 30 stage files must be unchanged.
   Result per run: `pruefung.txt` in the variant folder.
6. After the 5 runs, `report.txt` is created in the timestamp folder:
  per variant PASSED/FAILED, time, API calls, input/output tokens,
   plus totals.

Tokens are shown directly in the report (summed from the API responses) -
you can also cross-check consumption as usual in the Anthropic Console.

## 4. Installation on a Private PC

Requirement: Python 3.10+ (tested with 3.11).

```
1. Copy the TESTFAIKMETHODIK folder to your PC
2. cd TESTFAIKMETHODIK
3. pip install -r requirements.txt
4. Set up an API key - one of two options:
   a) Environment variable:   setx ANTHROPIC_API_KEY "sk-ant-..."   (reopen terminal)
   b) Create a file api_key.txt in this folder, content = just the key
      (the file is listed in .gitignore and is never committed)
```



## 5. Running It

**GUI (recommended):**

```
python gui.py
```

4 buttons appear - one per method - plus "Self-test (no API)".
Press a button -> the 5 variant runs start sequentially, progress is
shown in the window.

**Without GUI (command line):**

```
python run_test.py --selftest     # check the harness, NO API usage
python run_test.py --method 2     # only method 2
python run_test.py --all          # all 4 methods in sequence
```

**Recommendation:** run `--selftest` first. It applies the tool
deterministically and checks that the reference check works correctly
(and that an unmodified copy correctly fails) - with zero API cost.

## 6. Reading the Results

```
results/
  methode2_exakte_pfade/
    2025-01-15_143000/
      Entry/
        project/        <- copy edited by the agent
        agent_log.txt   <- prompts, every tool call, tokens per API call
        pruefung.txt    <- comparison against the reference (file by file)
      Middle/ ...
      Einfach/ ...
      Mittlere/ ...
      Easy/ ...
      report.txt        <- summary of the 5 runs + token totals
```



## 7. Settings

`config.json`:

```json
{
  "model": "claude-sonnet-4-5",   <- change to a different model here if needed
  "max_tokens": 4096,             <- max tokens per response
  "max_turns": 60,                <- safety limit on agent turns
  "varianten": ["Entry", "Middle", "Einfach", "Mittlere", "Easy"]
}
```



## 8. Notes on Fairness of the Comparison

- Every run starts from a fresh copy of the template.
- Task, tools, and validation are identical across all methods;
only the skill (the "route description") differs.
- For method 4, the user prompt is deliberately shorter (no replacement
table is needed, the tool derives the spellings itself) - that is
exactly the core idea of this method. All prompts are logged verbatim
in `agent_log.txt`.
- Method 1 naturally consumes the most tokens (it may read all
~43 files), method 4 the least (1 file + 1 tool call) - the test
makes this difference measurable.
- Cost: one complete method run = 5 agent runs. Method 1 in particular
can consume tens of thousands of input tokens depending on the model.

**The  results for each method are in the "results" folder and Token Consumption screenshots as .csv files under results/Token Data. The language of the reports as the skills is in German**