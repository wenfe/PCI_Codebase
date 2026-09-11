# GitHub main to GitLab

The [Sync main to GitLab workflow](../.github/workflows/sync-gitlab.yml) pushes
GitHub `main` to GitLab `main` whenever a commit is pushed or a pull request is
merged into GitHub `main`. It can also be run manually on `main`.

The source repository is `wenfe/PCI_Codebase`. Its configured destination is
`https://codebase.helmholtz.cloud/feng48/p3129_automate.git`, selected by the
GitHub repository variable `GITLAB_REPO_URL`. The local Git remote named `gitlab`
is independent of this setting.

## One-time setup

1. Create the destination GitLab project, or use an existing project whose
   `main` history is already included in GitHub `main`. Leave a new project empty
   rather than initializing it with a README.
2. In GitLab, create a personal or project access token with `write_repository`
   scope. Its user or bot must have permission to push to the destination's
   `main` branch, including any protected-branch rules. Set an expiration date
   and replace the stored secret before it expires.
3. In [GitHub Actions secrets and variables](https://github.com/wenfe/PCI_Codebase/settings/secrets/actions),
   configure these repository settings:

   | Kind | Name | Value |
   | --- | --- | --- |
   | Variable | `GITLAB_REPO_URL` | `https://codebase.helmholtz.cloud/feng48/p3129_automate.git` |
   | Secret | `GITLAB_TOKEN` | The GitLab access token |

   Use an HTTPS clone URL ending in `.git`, with no username or token in the URL.
   Enter the token directly in GitHub's secret form; never commit it to this repo.
4. Commit the workflow at `.github/workflows/sync-gitlab.yml` relative to the
   **Git repository root**, then push it to GitHub `main`. A file under
   `PCI_Codebase/.github/workflows/` inside the repository is not discovered by
   GitHub Actions.
5. Open [Actions](https://github.com/wenfe/PCI_Codebase/actions/workflows/sync-gitlab.yml),
   select **Sync main to GitLab**, and check the run. For a manual sync, select
   **Run workflow** with branch `main`. Confirm that GitLab `main` shows the same
   latest commit as GitHub `main` after the run succeeds.

## Sync behavior

- Sync is one way, from GitHub to GitLab, and updates only `main`.
- The job fetches the latest GitHub `main` with full history into a temporary
  bare repository. All committed files are included, without checking out a
  working tree or initializing submodules. This supports legacy submodule
  entries without `.gitmodules` URLs. Runs are serialized so a running push is
  not interrupted by a newer run.
- GitHub access uses its automatic read-only `GITHUB_TOKEN`; GitLab access uses
  `GITLAB_TOKEN`. Credentials are supplied through a temporary Git prompt helper
  for each operation, never stored in a remote URL or Git config. The helper is
  deleted when the step exits.
- Pushes are fast-forward only. The workflow does not force-push, delete
  branches, or copy tags, issues, settings, secrets, or submodule repositories.
- No GitLab CI configuration is required for the repository sync. A separate
  GitLab build/test pipeline requires a `.gitlab-ci.yml` in the synced project.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Workflow missing from Actions | The YAML must be committed under the root `.github/workflows/`, and GitHub Actions must be enabled. |
| Missing `GITLAB_TOKEN` or `GITLAB_REPO_URL` | Add the exact repository secret and variable names above. |
| URL validation fails | Use the HTTPS clone URL ending in `.git`, without credentials, a query, or a fragment. |
| Authentication failed / HTTP 401 or 403 | Check token expiration, `write_repository` scope, project access, and permission to push to protected `main`. |
| Non-fast-forward / fetch first | GitLab has commits absent from GitHub. Fetch and review them, merge the required history into GitHub `main`, then rerun. |
| Connection timeout | Check that the GitLab host is reachable from GitHub-hosted runners. |
| Manual run skipped | Select branch `main`. Other branches are intentionally excluded. |

References: [GitHub workflow location and syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax),
[GitLab token scopes](https://docs.gitlab.com/security/tokens/access_token_scopes/),
and [GitLab branch protection](https://docs.gitlab.com/user/project/repository/branches/protected/).
