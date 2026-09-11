---
description: "Identify and document frequently mentioned business topics of existing DOCS that were MISSING until now."
model: Claude Sonnet 4.5 (copilot)
---

@workspace

# Rework with existing documentation

I need help analyzing a collection of Markdown documentation files to identify frequently recurring topics that don't have dedicated files yet.
Use the sequentialthinking mcp server.

## Tasks

execute the following steps:

1. Scan the files in folder #files:../../docs/03_ComponentDocumentation
2. List all component names from that folder (-> exclusion list)
3. Identify concepts, terms, components or processes that appear repeatedly in these files (at least 5+ mentions) that are NOT in the exclusion list.
4. Check if these recurring topics already have dedicated documentation files in the 'docs' folder
5. For topics without dedicated files, provide:
   - Topic name/title
   - Number of mentions and which files reference it
   - A brief description based on context
   - Recommendation for creating a new dedicated file
6. Suggest a file naming convention and hierarchy for any new topic files
7. Prioritize topics based on frequency of mentions and importance to system understanding

For example, if "BTK validation" is mentioned across inventory, material, and warehouse files but lacks its own documentation, highlight it as a candidate for a dedicated explanation file.

## Exclusion list

The only interest is in missing documentation for frequently mentioned business topics. Avoid generic terms in software development - i.e. avoid terms from the following list:
System data model
Error handling
Performance optimization
System configuration
Batch job management
Testing concept
Development guidelines

Please format your analysis as a Markdown table for easy review, sorted by mention frequency.

Create a new file '05_Rework_with_docs.md' in the 'docs' folder.
