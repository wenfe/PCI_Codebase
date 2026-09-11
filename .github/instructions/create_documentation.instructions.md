---
applyTo: "**/01*.md, **/02*.md, **/03*.md"
description: "Create documentation"
---

# Documentation Creation Instructions

## Tools

Use the MCP-server for sequential-thinking.

## Core Principles

### No Guessing Policy

- **NEVER make assumptions** about code functionality, business logic, or system behavior
- **ALWAYS verify** information by reading source code, configuration files, or existing documentation
- **STATE accuracy** when information is unclear or missing
- **REFERENCE actual code** when explaining functionality
- **VALIDATE** all technical details against the codebase

### Documentation Standards

- **All documentation MUST be in Markdown format** (.md files)
- **Always use GERMAN language**: `DE`
- **Store all documentation in the `docs/` folder**
- **Use clear, descriptive filenames** following the pattern: `03_Component_Topic.md`
- **Follow consistent heading structure** (H1 for main title, H2 for sections, H3 for subsections)
- **Include table of contents** for documents longer than 3 sections

## File Organization

### Folder Structure

```
docs/
├── 01_ComponentName/
│   ├── ComponentName_01_SystemSummary.md
│   ├── ComponentName_Subtopic_1.md
│   ├── ComponentName_Subtopic_2.md
│   └── ...
├── 02_AnotherComponent/
│   └── ...
└── README.md
```

### Naming Conventions

- **Folders**: Use numbered prefixes for logical ordering (1_Component, 2_Component)
- **Files**: Use descriptive names with Component prefix (ComponentName_Topic.md)

## Diagram Requirements

### Mermaid Syntax Only

- **ALL diagrams MUST use Mermaid syntax**
- **Validate syntax** before including in documentation
- **Test rendering** to ensure diagrams display correctly

### Diagram Best Practices

- **Use meaningful node IDs** and labels
- **Keep diagrams focused** - one concept per diagram
- **Include diagram title** and brief description
- **Use consistent styling** across all diagrams
- **Validate syntax** using Mermaid live editor before committing

## Content Structure

### Required Sections for Technical Documentation

1. **Overview** - Purpose and scope
2. **Architecture** - System design and components
3. **Dependencies** - Required modules and external systems
4. **Configuration** - Setup and configuration details
5. **API/Interfaces** - Public interfaces and contracts
6. **Examples** - Usage examples and code snippets
7. **Troubleshooting** - Common issues and solutions

### Code Documentation Standards

- **Include actual code snippets** from the codebase
- **Reference specific files and line numbers** when applicable
- **Explain business logic** with context from the code
- **Document function signatures** and parameter descriptions
- **Include error handling** and edge cases

## Quality Assurance

### Validation Checklist

- [ ] All facts verified against source code
- [ ] No assumptions or guesses made
- [ ] Markdown syntax is correct
- [ ] Mermaid diagrams render properly
- [ ] All links work correctly
- [ ] File is saved in correct `docs/` subfolder
- [ ] Filename follows naming convention
- [ ] Content is technically accurate

### Review Process

1. **Self-review** - Check against this instruction file
2. **Syntax validation** - Verify Markdown and Mermaid syntax
3. **Accuracy verification** - Cross-reference with actual code
4. **Completeness check** - Ensure all required sections are present

## Markdown Formatting Guidelines

### Headers

```markdown
# Main Title (H1) - Once per document

## Major Section (H2) - Primary divisions

### Subsection (H3) - Secondary divisions

#### Details (H4) - Specific topics
```

### Code Blocks

````markdown
# For inline code

Use `backticks` for inline code references

# For code blocks

\```language
code here
\```

# For ABAP code specifically

\```abap
DATA: lv_variable TYPE string.
\```
````

### Tables

```markdown
| Column 1 | Column 2 | Column 3 |
| -------- | -------- | -------- |
| Data 1   | Data 2   | Data 3   |
```

### Links and References

```markdown
# For relative links to documentation files (examples)

[Project Documentation](../../s-warehouse-Doku.md)

# For external links

[External Link](https://example.com)

# For images

![Image Alt Text](../docs/diagrams/system_overview.png)
```

## Error Prevention

### Common Mistakes to Avoid

- ❌ Making assumptions about code behavior
- ❌ Using incorrect Mermaid syntax
- ❌ Storing documentation outside `docs/` folder
- ❌ Using inconsistent formatting
- ❌ Missing required sections
- ❌ Broken internal links
- ❌ Unvalidated technical claims
- ❌ History of edits
- ❌ Information about future plans or possible developments

### Best Practices

- ✅ Always read the source code first
- ✅ Validate all Mermaid diagrams before committing
- ✅ Use consistent naming and structure
- ✅ Include practical examples
- ✅ Reference actual file paths and line numbers
- ✅ Test all links and references
- ✅ Follow the established folder structure

**Remember: When in doubt, read the code. Never guess.**
