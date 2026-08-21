# Getting Started Guide: Proposal Agent Test Harness

*A step-by-step guide for team members with little to no technical experience. No coding knowledge is required. If you can save a file and copy-paste, you can run this.*

## What This Is and Why We Use It

Our team built an AI agent in Microsoft Copilot that drafts and edits proposals. Before we trust it with real submissions, we need to test it the same way every time and keep score. This toolkit does that. You run a set of standard test questions against our Copilot agent, save its answers, and then a second AI (built into VS Code) grades those answers against a fixed scorecard. You end up with a spreadsheet of scores and a report listing exactly what went wrong.

Your job in this process has only three parts: run the test prompts, save the answers with the right file names, and ask the grading assistant to do its work. Everything else is automatic.

## Words You'll See (Plain-English Glossary)

| Term | What it means here |
|---|---|
| VS Code | A free Microsoft program. Think of it as a folder viewer with a built-in AI assistant. You will not write code in it. |
| Copilot agent mode | The AI assistant inside VS Code. You talk to it in a chat panel, like Teams chat. It does the grading. |
| The harness | The folder of files this guide is about. It contains the test questions, the scorecard, and the grading tools. |
| Test ID | A short code for each test, like A1 or B2. The letter is the category, the number is the test. |
| Output | The answer our proposal agent gives when you run a test prompt. You save each one as a file. |
| .md file | A plain text file. You can make one in Notepad. The ".md" ending is just part of the file name. |
| Run | One attempt at a test. We do each test 2 or 3 times because AI answers vary. Run 1, run 2, run 3. |

## Part 1: One-Time Setup (About 30 Minutes)

You only do this section once. If a teammate already set up your computer, skip to Part 2.

### Step 1. Install VS Code

1. Go to code.visualstudio.com in your web browser.
2. Click the big blue Download button and run the installer. Accept all the default options.
3. Open VS Code when it finishes.

### Step 2. Sign in to GitHub Copilot inside VS Code

1. In VS Code, look at the bottom-left corner for a small person/account icon. Click it and choose "Sign in."
2. Sign in with the GitHub account our team uses. A browser window will open; approve the sign-in and return to VS Code.
3. You should now see a chat icon in the left sidebar or top bar. Click it to open the Copilot chat panel. If you see a place to type a message, you're set.
4. In the chat panel, find the small dropdown near the message box and make sure it is set to "Agent" (not "Ask" or "Edit"). Agent mode lets the assistant read files and run the grading for you.

If sign-in fails or you don't see the chat panel, ask the team lead which GitHub account to use. You do not need anything from IT for this.

### Step 3. Install Python

Python is a free helper program the toolkit uses behind the scenes. You will never look at it directly.

1. Go to python.org/downloads and click the yellow download button.
2. Run the installer. **Important: on the first screen, check the box that says "Add Python to PATH" before clicking Install.** This is the one step people miss.
3. Click Install Now and let it finish.

### Step 4. Get the harness folder onto your computer

1. Get the file `proposal-agent-test-harness.zip` from the team (email, Teams, or our shared drive).
2. Right-click the zip file and choose "Extract All," then pick an easy location like your Documents folder.
3. You should now have a folder called `proposal-agent-test-harness` containing folders named `tests`, `outputs`, `grading`, `grades`, `results`, `scripts`, and `grader`.

### Step 5. Open the folder in VS Code

1. In VS Code, click File > Open Folder.
2. Select the `proposal-agent-test-harness` folder and click Open.
3. If VS Code asks "Do you trust the authors of the files in this folder?", click "Yes, I trust the authors."
4. You'll see the folder contents listed on the left side.

### Step 6. Check that everything works

This is the one command worth memorizing. It tells you whether your setup is
sound, and if not, exactly what to fix.

1. In VS Code, open the menu Terminal > New Terminal. A panel opens at the bottom.
2. Type this and press Enter:

   ```
   python check_setup.py
   ```

3. Read the last few lines. If it says **SETUP IS GOOD**, you're done with setup.

If you see lines marked `[FAIL]`, each one includes the fix directly underneath
it. Fix them and run the command again. If you're stuck, select the whole output,
copy it, paste it into the VS Code chat panel, and ask "How do I fix this?"

You can run this command any time. It never changes or deletes anything.

### Step 7. Watch a practice run (2 minutes, optional but recommended)

Before you run a real test, it helps to see what the finished product looks
like. In the terminal, type:

```
python demo.py
```

This runs the entire workflow on twenty pretend answers that ship with the
toolkit, and prints the report it produces. It does not touch anything of yours,
and it does not need the proposal agent at all.

The pretend answers are deliberately mixed. Some are good. Several fail on
purpose, and one of them shows what happens when the agent follows a hidden
instruction planted in a document. You will see the SECURITY FLAG warning that
this raises, so you recognise it if it ever appears in a real run.

Add `--keep` if you want to open the files it generated:

```
python demo.py --keep
```

They land in `demo/_last_run/`.

## Part 2: Running a Test Cycle

This is the part you'll repeat. A full cycle of all 20 tests takes roughly half a day the first time and gets faster after that.

### Step 1. Open the test questions

1. In VS Code's left panel, click the `tests` folder, then click `test_cases.json`.
2. Don't worry about the curly brackets and quotes. Just find the lines that start with `"prompt":`. The text in quotes after that is what you copy into our Copilot agent.
3. Also read the `"setup_notes"` line for each test. It tells you whether to fill in any [bracketed placeholders] before running.

Tip: it's easier to work from the Word version of the Proposal Agent Test Playbook, which has the same prompts with more explanation. Use whichever you prefer; they match.

### Step 2. Find out which documents to attach

Most tests only make sense if you attach the right background documents. Those
documents are already in this folder, under `materials`.

1. Open `materials/README.md`.
2. Find your test in the table at the top. It lists exactly which files to attach.

The documents are fictional on purpose. There is no real agency, no real company,
and no real contract in them. Everyone on the team uses these same documents so
that scores can be compared over time. **Do not edit them**, and do not swap in a
real solicitation.

Two traps worth knowing:

- **Never attach `materials/SEEDED_ERRORS_ANSWER_KEY.md`.** That file lists all
  the mistakes we deliberately hid in the other documents. If the agent sees it,
  the test proves nothing.
- **Test F1 gets the base RFP only**, not the amendment. The amendment fixes the
  contradiction that F1 is testing for.

### Step 3. Run a prompt against our proposal agent

1. Open our proposal agent in Copilot the way you normally would.
2. Start a **brand new chat** for every test. Never reuse an old conversation; leftover context contaminates the results.
3. Attach the documents `materials/README.md` listed for that test, paste the test prompt exactly as written, and send it.
4. Wait for the complete answer.

### Step 4. Save the answer with the correct file name

This step matters most. The grading tools find answers by their file names.

1. Select the agent's entire answer and copy it.
2. In VS Code, right-click the `outputs` folder on the left and choose "New File."
3. Name the file using this exact pattern: the test ID, underscore, the word "run," the run number, then `.md`
   - First attempt at test A1 → `A1_run1.md`
   - Second attempt at test A1 → `A1_run2.md`
   - First attempt at test C3 → `C3_run1.md`
4. Click into the empty file, paste the answer, and press Ctrl+S (Cmd+S on Mac) to save.

Common mistakes to avoid: spaces in the file name, capital "RUN," forgetting `.md`, or saving into the wrong folder. The pattern is always `ID_runNUMBER.md` inside `outputs`.

**Check your file names before going further.** A badly named file is skipped
silently, so you would not find out until your results came back short. In the
terminal, run:

```
python check_setup.py
```

It lists every output file it can read, and for any it cannot, it tells you
exactly what is wrong with the name.

### Step 5. Repeat

Do each test 2 or 3 times (fresh chat each time), saving as `_run1`, `_run2`, `_run3`. You don't have to do all 20 tests in one sitting. Grade whatever you have; you can add more later.

### Step 6. Check what was planted in the test documents

**Good news: there is nothing to do here.** This step used to require typing up
what you planted. The test documents now ship with the mistakes already hidden in
them, and the grader already knows what they are.

Some tests work by hiding known mistakes in the documents you attach. For example:

- **B2** uses a draft that omits five things the RFP requires.
- **C3** uses a draft where the staffing numbers contradict each other.
- **F3** uses a document with a sneaky instruction planted inside it, to see
  whether our agent obeys instructions hidden in a customer's file.

If you are curious what was planted, read
`materials/SEEDED_ERRORS_ANSWER_KEY.md`. Reading it yourself is fine. Just never
attach it to a test, because that hands the agent the answers.

The short version the grader uses lives in `tests/grading_context.json`. You do
not need to edit it unless you change the test documents. If you ever do change
them, tell the team lead, because scores from before the change stop being
comparable to scores after it.

### Step 7. Ask the assistant to grade

1. Open the Copilot chat panel in VS Code (make sure the dropdown says Agent).
2. Type exactly this and send it:

   **Read AGENTS.md, then grade all outputs and summarize the results.**

3. The assistant will run the tools, read each answer, score it, and may ask permission to run commands or save files. Click Allow/Continue when it asks.
4. This can take several minutes for a big batch. Let it finish.

### Step 8. Read your results

When the assistant finishes, it will post a summary in the chat. You also have two files.

`results/report.md` is written so the important things come first:

- **Security flags**, if there are any, right at the top. Tell the team lead.
- **Coverage** — how much of the suite these scores actually cover. Read this
  one carefully. If some answers were not graded, they are *not* counted in the
  pass rate, and this section is where it says so. A batch that is only half
  graded can otherwise look like a clean result.
- **Where the agent is weakest** — which of the five scores is lowest on
  average, which categories fail most, and which tests failed in more than one
  run. A test that fails twice out of three runs is a real problem. Failing once
  might just be a bad day.

Then the detail for each run.

The two files are:

1. `results/report.md`: a readable report. Each test shows PASS or FAIL, the score, and a bullet list of exactly what went wrong. **If you see the words SECURITY FLAG anywhere, tell the team lead immediately.** It means our agent followed instructions hidden inside a document, which is a safety problem, not just a quality problem.
2. `results/scores.csv`: the score spreadsheet. Double-click it to open in Excel. One row per test run, with 1-5 scores for accuracy, compliance, voice, structure, and instruction-following.

A test passes when its key scores are 3 or higher. Scores of 1 or 2 point to real problems; the report's bullet points tell you what they were.

### Step 9. Human review with the scoresheet

Automated grading is fast but not infallible, so a person double-checks it using `proposal_agent_scoresheet.xlsx` (in this folder). How it works:

1. Open the spreadsheet. The "How To Use" tab explains every column.
2. Copy the scores from `results/scores.csv` into the gray columns; the row layout matches (one row per test run). The Overall column calculates itself.
3. For each run you review, read the agent's actual output in `outputs/` and mark Y or N in the yellow "Human Agrees?" column. You do not need to review every run. Always review: anything with a security flag, all C-category tests (the hallucination checks), and any FAIL.
4. If you disagree with a grade, do not change the score. Mark N, explain in Notes, and raise it with the team lead. Recording disagreements is how we learn whether the automated grader can be trusted.

### Step 10. Share and save

1. Email or post `scores.csv`, `report.md`, and the completed scoresheet to the team.
2. If your team lead has set up saving score history, ask the chat assistant: "Please commit results/scores.csv so we keep the score history." If that means nothing to you, skip it; just keep the files.

## Quick Reference Card

Print this part.

**When anything goes wrong, run `python check_setup.py` first.** It diagnoses most
problems and tells you the fix.

1. Open `materials/README.md` → find your test → note which documents to attach.
2. New chat with the proposal agent → attach those documents → paste test prompt → send.
3. Copy the full answer → save in `outputs` as `ID_runNUMBER.md` (example: `B1_run1.md`).
4. Run `python check_setup.py` to confirm the file name is right.
5. Repeat 2-3 times per test, fresh chat every time.
6. In VS Code chat (Agent mode): **"Read AGENTS.md, then grade all outputs and summarize the results."**
7. Read `results/report.md`. SECURITY FLAG = tell the team lead now.
8. Copy scores into `proposal_agent_scoresheet.xlsx` and mark Human Agrees? for flagged runs, C tests, and FAILs.
9. Share `scores.csv`, `report.md`, and the scoresheet with the team.

Never attach `materials/SEEDED_ERRORS_ANSWER_KEY.md` to a test.

## Troubleshooting

**First resort for almost everything: `python check_setup.py`.**

| Problem | Fix |
|---|---|
| The assistant says it can't find any outputs | Run `python check_setup.py`. It lists every output file and explains what is wrong with any name it cannot read. |
| I saved a file but the grader ignored it | Almost always the file name. Run `python check_setup.py` for the specific reason. Watch for spaces, a lowercase test ID, capital "RUN", or a hidden `.txt` ending. |
| "Python is not recognized" or a similar error | Python wasn't added to PATH. Reinstall from python.org and check the "Add Python to PATH" box on the first screen. Then close and reopen VS Code. |
| "python: command not found" on Mac | Try `python3` instead of `python` in every command. |
| The chat panel won't do anything with files | The dropdown near the message box is probably on "Ask." Switch it to "Agent." |
| The assistant asks permission to run a command | Click Allow/Continue. It's running the grading tools described in this guide. |
| A grade seems too kind or too harsh | Tell the team lead. A human should spot-check a few grades each cycle, especially the hallucination tests (C1-C3). Don't edit scores yourself. |
| Which documents do I attach? | `materials/README.md` has a table listing them for every test. |
| I accidentally deleted or changed a file in `tests`, `grader`, or `materials` | Re-extract the original zip and copy the file back. Those folders are the rulebook and shouldn't be edited casually. `python check_setup.py` will tell you if something is missing. |
| The proposal agent's answer includes tables or formatting that looks odd when pasted | That's fine. Paste it as-is; the grader reads the text content. |
| A grade file won't compile — "invalid JSON" | The grading assistant probably wrapped it in ``` code fences. Open the file in `grades/` and delete any line containing ```. |
| The agent claims it hit the word limit but I'm not sure | Check it yourself: `python scripts/wordcount.py outputs/E1_run1.md --limit 1000` |

## For the Team Lead: Making the Zip

Everyone else in this guide receives `proposal-agent-test-harness.zip`. To build
a fresh copy of that file, run this from the project folder:

```
python make_zip.py
```

It bundles everything a teammate needs, starts them with empty `outputs`,
`grades`, and `results` folders, and refuses to build if anything required is
missing. Add `--with-results` if you want to include the current score history.

Send teammates the zip rather than a link to the code repository. One of the
files the harness needs, `AGENTS.md`, is filtered out by common developer
settings, and the zip is guaranteed to include it.

## The Rules of Good Testing (Why We Do It This Way)

1. **Fresh chat every run.** Old conversation history changes how the agent answers and ruins the comparison.
2. **Run each test more than once.** AI answers vary. One bad answer might be a fluke; the same problem in 2 of 3 runs is a real gap.
3. **Same test documents every cycle.** We reuse the same test RFP and source materials so scores are comparable over time.
4. **Never fix the agent's answer before saving it.** We're grading the agent, not you. Save exactly what it produced, mistakes and all.
5. **Humans still check the important stuff.** Automated grading finds patterns fast, but a person always reviews security flags, hallucination results, and anything going into a real proposal.
