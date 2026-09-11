# Agent Usage Guide

### This guide provides quick reference examples for using the available agents in the flashware origin service project.

---

## unit-test-writer
**Description:** Generate comprehensive Mockito-based unit tests following project patterns
**Usage:** Create unit tests for the FlashwareService.createFlashware method

---

## integration-test-writer
**Description:** Generate comprehensive Spring integration tests following project patterns
**Usage:** Create an integration test for the flashware upload flow with ODX-F verification

---

## agent-creation
**Description:** Expert agent designer for creating effective GitHub Copilot agents with best practices and clear instructions
**Usage:** Create a agent for code review that focuses on security best practices

---

## code-improvement
**Description:** Scans code for readability, performance, and best-practice issues and provides concrete improved versions with explanations (generic)
**Usage:** Scan and improve src/main/java/com/example/service/OrderService.java

---

## bmdb-code-improvement
**Description:** BMDB-specific code scanner for T-SQL (OL/, SL/), Playwright tests, and PowerShell scripts — domain-aware rules for status values, NOLOCK, error handling, and naming conventions
**Usage:** Scan and improve SQL files in OL/

---

## api-developer
**Description:** Implements API endpoints following team conventions — handles routes, DTOs, validation, error handling, and tests using preloaded skills (`api-conventions`, `error-handling-patterns`)
**Usage:** Create a GET endpoint to retrieve a project by ID with proper error handling

---

## data-scientist
**Description:** Data analysis expert for SQL queries, BigQuery operations, and data insights — writes optimized queries, analyzes results, and presents findings with recommendations
**Usage:** Analyze the distribution of SQL object types across OL/ and SL/ folders

---

## safe-researcher
**Description:** Read-only research agent — explores the codebase, traces call chains, maps dependencies, and answers "how does X work?" questions without modifying any files
**Usage:** Research how status calculations work across OL/ and SL/

---

## code-reviewer
**Description:** Reviews code for quality and best practices — learns patterns, conventions, and recurring issues over time via agent memory (`memory: user`); never modifies files
**Usage:** Review the code in OL/usp_merge_Kennzahlen_Neuberechnung_Komplett.sql

---

## architecture-advisor
**Description:** Analyzes architectural decisions with codebase context
**Usage:** What's the best approach to implement caching for our flashware metadata API?

---
