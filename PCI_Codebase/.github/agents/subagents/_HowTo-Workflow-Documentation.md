# Workflow Documentation - HowTo Guide

**Last Updated:** December 18, 2025  
**Purpose:** Guide for creating, reviewing, and maintaining workflow documentation for Spring Boot microservices

## Overview

5 specialized agents work together using **Zero-Hallucination Protocol** (verified against actual code) and **Iterative Quality Loop**:

**Agents**: workflow-scanner, doc-create-workflow, doc-review-workflow, doc-fix-workflow, doc-update-workflow

**Quality Loop**: `CREATE → REVIEW → FIX → REVIEW → ... → PASSED`
- **PASSED**: Zero findings
- **FAILED**: Any findings (Critical/Major/Minor)
- **Goal**: Iterate until PASSED (2-4 cycles)

## Process

### 1. Discovery (Optional)
```bash
@workflow-scanner Scan this repository for workflow entry points.
```
Output: `doc/Workflows/WorkflowList.md` with categorized entry points.

### 2. Create
```bash
@doc-create-workflow Document this workflow PUT /v1/subscriptions/{tid}
```
Traces code (Controller→Service→Repository), generates sections, creates validated Mermaid diagrams (Sequence + Flowchart) using Mermaid CLI (auto-installs if needed), saves to `doc/Workflows/[WorkflowName].md`.

### 3. Review
```bash
@doc-review-workflow Review doc/Workflows/UpdateMdEmailSubscription.md
```
Verifies every workflow step, method name, HTTP code, exception type against actual code. Validates diagrams step-by-step. Appends "Review Findings" section (PASSED/FAILED).

### 4. Fix
```bash
@doc-fix-workflow Fix findings in doc/Workflows/UpdateMdEmailSubscription.md
```
Parses findings, validates against source, applies corrections, validates diagrams, removes findings section.

### 5. Iterate
```bash
@doc-review-workflow Review doc/Workflows/UpdateMdEmailSubscription.md
@doc-fix-workflow Fix findings in doc/Workflows/UpdateMdEmailSubscription.md
```
Repeat until PASSED. Typical: Cycle 1 (10-20 findings) → Cycle 2 (3-5) → Cycle 3 (0-1) → PASSED.

### 6. Update
```bash
@doc-update-workflow Update documentation for PUT /v1/subscriptions/{tid}
```
Analyzes git changes since last commit, surgically updates affected sections and diagrams. Always review after updating.

## Best Practices

- Run workflow-scanner first for discovery
- Provide exact endpoint paths (`PUT /v1/subscriptions/{tid}`)
- Fix ALL findings (even Minor) - zero findings required
- Use doc-update-workflow after code changes (don't recreate)
- **Mermaid**: Validated via CLI (auto-installed). Sequence (use `activate`/`deactivate`, `alt/else`), Flowchart (decision nodes, error paths with HTTP codes)
- **Code Tracing**: Focus on business logic, include validations/errors, exclude logging/boilerplate
- Iterate until PASSED (typically 2-4 cycles)

## Troubleshooting

**Same issue repeating**: Manually inspect code, verify finding validity, consider recreating doc

**Mermaid validation fails**: Agents use Mermaid CLI (`@mermaid-js/mermaid-cli`) with document-specific temp files. CLI provides exit code (0=valid, 1=error) and error messages with line numbers. Common issues: missing `end`, unclosed `{}`, invalid node IDs. Fix one issue at a time using CLI error output. Consult `.github/mermaid-syntax/mermaid-flowchart-sequence-rules.md`

**Many findings (10-20)**: Normal for first cycle. Pattern: 10-20 → 3-5 → 0-1. Keep iterating.

**Entry point not found**: Run workflow-scanner, check controller mappings, provide full class name

**Very outdated (>100 commits)**: If >50% changed, recreate; else update and iterate

## Quick Reference

```bash
# Discovery
@workflow-scanner Scan this repository for workflow entry points.

# Create, Review, Fix Loop
@doc-create-workflow Document this workflow POST /v1/ecu/search
@doc-review-workflow Review doc/Workflows/SearchEcus.md
@doc-fix-workflow Fix findings in doc/Workflows/SearchEcus.md
@doc-review-workflow Review doc/Workflows/SearchEcus.md
# Repeat until PASSED

# Update (after code changes)
@doc-update-workflow Update documentation for POST /v1/ecu/search
@doc-review-workflow Review doc/Workflows/SearchEcus.md
```

## Example Flow

```
1. Create: @doc-create-workflow Document this workflow PUT /v1/subscriptions/{tid}
2. Review: FAILED (2 Critical, 3 Major, 1 Minor)
3. Fix: 6 findings corrected
4. Review: FAILED (1 Major)
5. Fix: 1 finding corrected
6. Review: PASSED ✅

Update (later): @doc-update-workflow → Review → PASSED ✅
```

## Output Structure

```markdown
# [Use Case Title]
**Endpoint:** `[METHOD] [path]`
**Method:** `ControllerClass.methodName()`
**Last Updated/Commit:** [Date/Hash]

## Overview | Workflow Steps | Decision Points | External Integrations
## Sequence Diagram | Workflow Flowchart | Notes
```

**Execution Time**: 10-15 minutes per workflow (including iterations)
