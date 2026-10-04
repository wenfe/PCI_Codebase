# SAXS and Python Copilot Profile

This workspace uses a small scientific-computing profile instead of the general
agent and plugin catalog. Use the default assistant for ordinary edits and
documentation; specialist agents are optional, not mandatory workflow stages.

## Agents

| Agent | Purpose |
|---|---|
| [SAXS Python](agents/subagents/saxs-python.agent.md) | Scientific Python, simulations, parameter sweeps, and notebooks |
| [SAXS Review](agents/subagents/saxs-review.agent.md) | Read-only physics and numerical correctness review |
| [Debugger](agents/subagents/debug.agent.md) | Reproduce and fix implementation defects |
| [Planner](agents/subagents/planner.agent.md) | Plan changes without editing application code |

Agents do not pin a model. Select the desired model through the host's settings.

## Skills

| Skill | Purpose |
|---|---|
| [Context map](skills/context-map/SKILL.md) | Identify relevant code before changing it |
| [Refactor plan](skills/refactor-plan/SKILL.md) | Plan and obtain approval for multi-file refactors |
| [SAXS comparison](skills/saxs-comparison/SKILL.md) | Match configurations and quantify curve differences |
| [SAXS plotting](skills/saxs-plotting/SKILL.md) | Reproducible plots with clear parameters and saved data |
| [Python numerical review](skills/python-numerical-review/SKILL.md) | Check arrays, reductions, sampling, and provenance |

## Archive and recovery

The unused workspace agents, skills, bundled plugins, marketplace, and catalog
indexes were moved to the sibling
[dated archive](../../PCI_Copilot_Archive/2026-10-04-saxs-python-profile/).
Its [manifest](../../PCI_Copilot_Archive/2026-10-04-saxs-python-profile/archive-manifest.json)
records the original relative paths, sizes, and SHA-256 hashes of every file.

Restore only the specific agent or skill needed, using its manifest path.
Compare any existing destination before restoring; never overwrite current
workspace changes blindly. For bundled skills, restore required resources as well
as the skill definition. Do not restore an entire plugin catalog just to recover
one standalone skill.

The archive is outside the Git repository and is not included in repository
commits. Keep it separately backed up if long-term recovery is needed.

## Scope and discovery

Application code, notebooks, instruction files, hooks, and user-wide plugins were
not changed by the curation. User-wide plugins can still expose additional tools.
Reload the VS Code window or start a new assistant session if the old catalog
remains visible; existing sessions may retain their loaded definitions.
