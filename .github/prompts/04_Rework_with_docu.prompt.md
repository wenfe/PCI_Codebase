---
description: "Identify and document frequently mentioned business topics of the DOCU that were MISSING until now."
model: Claude Sonnet 4.5 (copilot)
tools: ["fetch", "edit/editFiles", "sequential-thinking/*", "search"]
---

@workspace
I need help analyzing a collection of Markdown documentation files to identify frequently recurring topics that don't have dedicated files yet. Please:

1. Scan the #files:../../<YOUR_DOCUMENTATION>.md
2. Identify concepts, terms, components or processes that appear repeatedly in this file (at least 5+ mentions)
3. Check if these recurring topics already have dedicated documentation files in the 'docs' folder
4. For topics without dedicated files, provide:
   - Topic name/title
   - Number of mentions and which files reference it
   - A brief description based on context
   - Recommendation for creating a new dedicated file
5. Suggest a file naming convention and hierarchy for any new topic files
6. Prioritize topics based on frequency of mentions and importance to system understanding

For example, if "BTK validation" is mentioned across inventory, material, and warehouse files but lacks its own documentation, highlight it as a candidate for a dedicated explanation file.

The only interest is in missing documentation for frequently mentioned business topics. Avoid generic terms in software development - i.e. avoid terms from the following list:
System data model
Error handling
Performance optimization
Authorization concept
Monitoring
Logging
System configuration
Batch job management
Testing concept
Development guidelines

Please format your analysis as a Markdown table for easy review, sorted by mention frequency.

Create a new file '00_HelperDocuments/04_Rework_with_docu.md' in the 'docs' folder.
