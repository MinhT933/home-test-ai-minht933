# Daily synchronization deployment

The worker is a one-shot process. GitHub Actions starts it daily at `02:00 UTC`,
which is `09:00` in `Asia/Ho_Chi_Minh`.

## Local Docker verification (Git Bash)

```bash
docker build -t optibot-sync:local .
docker run --rm optibot-sync:local --help
mkdir -p .sync-state
# Copy an already verified manifest to .sync-state/sync-state.json first.
docker run --rm \
  --env GEMINI_API_KEY \
  --env GEMINI_FILE_SEARCH_STORE_NAME \
  --volume "$PWD/.sync-state:/state" \
  optibot-sync:local
```

The image defaults to one full `--sync` run and follows every Zendesk API page.
Use `--dry-run --state-file /state/sync-state.json` after the image name when a
read-only delta preview is needed.

The scheduled job allows up to 120 minutes so the first unrestricted run can
index the articles beyond the original 31-document sample. Later delta runs
normally upload only new or changed content.

Never place `.env` or a checkpoint inside the image. A local manifest survives
container restart only when `/state` is mounted from durable host storage. It
does not survive replacement of an unmounted cloud container.

## Legacy bootstrap gate

The existing 31 documents have no verified content hashes. Scheduled mutation
must remain disabled until an operator has reconciled them:

```bash
python main.py --bootstrap-report bootstrap-report.json
python main.py \
  --bootstrap-confirm bootstrap-report.json \
  --state-file .sync-state/sync-state.json \
  --acknowledge-verified-content \
  --verification-evidence "trusted upload run or independent verification reference"
```

Article-ID or filename equality alone is not verification. Acceptable evidence
is an original upload audit associating the exact local file with the Gemini
document resource, or an independent comparison of remote content. Bootstrap
does not upload or delete documents. If evidence is unavailable, do not create
the `sync-state` branch and do not enable the schedule.

After verification, create the dedicated branch in an isolated temporary
worktree, without adding state to `main` or deleting files from its working tree:

```bash
state_worktree="$(mktemp -d)"
git worktree add --detach "$state_worktree" HEAD
cd "$state_worktree"
git switch --orphan sync-state
git rm -rf .
cp /trusted/path/sync-state.json ./sync-state.json
git add sync-state.json
git commit -m "Initialize verified sync checkpoint"
git push origin HEAD:sync-state
cd -
git worktree remove "$state_worktree"
```

Review the manifest before committing. It may contain article IDs, hashes,
Gemini document resource names, timestamps, and verification evidence, but no
credentials.

## GitHub configuration

Add these repository Actions secrets:

- `GEMINI_API_KEY`
- `GEMINI_FILE_SEARCH_STORE_NAME`

The workflow fails closed when the branch or manifest is missing. Concurrency
allows only one run at a time. It persists state only after worker success and
uses a normal non-forced push, so a conflict fails instead of overwriting state.

If synchronization succeeds but publishing the checkpoint fails, the workflow
remains failed and retains its log artifact. Do not start another mutation
manually. Inspect remote metadata and the failed run, restore or merge the
checkpoint on `sync-state`, then rerun. Recovery uses active hash metadata to
avoid re-uploading a successfully indexed document.

The state branch is a lightweight take-home solution, not a general-purpose
production database. Production should use transactional durable storage with
access control, backups, versioning, and concurrency guarantees.

## Runs and logs

Open the repository on GitHub, select **Actions**, then **Daily knowledge-base
sync**. Select a run to obtain its URL. Manual runs use **Run workflow**. The
`daily-sync-log-<run-id>` artifact is uploaded after failures when a log exists.
