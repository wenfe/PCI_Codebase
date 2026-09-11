---
applyTo: "**/4_CreateUserJourneys/*.prompt.md**"
description: "Create user journeys"
---

# User Journey Creation Instructions

## Core Principles

### No Guessing Policy

- **NEVER make assumptions** about code functionality, business logic, or system behavior
- **ALWAYS verify** information by reading source code, configuration files, or existing documentation
- **STATE accuracy** when information is unclear or missing
- **Never REFERENCE actual code**
- **VALIDATE** all technical details against the codebase and existing documentation

### Documentation Standards

- **All documentation MUST be in Markdown format** (.md files)
- **Always use GERMAN language**: `DE`
- **Store all documentation in the `docs/4_UserJourneys` folder**
- **Use clear, descriptive filenames** following the pattern: `<03_Component_Topic>UserJourney.md`
- **Follow consistent heading structure** (H1 for main title, H2 for sections, H3 for subsections)
- **Include table of contents** for documents longer than 3 sections

# User Journey & Use Case Generation for FrameworkSystemwerkzeuge

You are tasked with creating comprehensive user journeys and detailed use cases for the **FrameworkSystemwerkzeuge** system component.

## Source Materials

**Primary Documentation:**

- Review all existing documentation in `docs/10_ComponentDocumentation*Component_Topic*`
- Extract key functionalities, processes, and system behaviors

**Source Code Analysis:**

- Analyze the referenced source folders in `src/` for the component
- Identify:
  - Database tables and their relationships
  - Function modules and their interfaces
  - Dialog screens and transactions
  - Business logic and validation rules
  - Error handling scenarios

## Deliverables Required

### 1. User Journey Maps

Create visual user journey maps showing:

- **User personas** (different types of users/roles)
- **Touchpoints** with the system
- **Pain points** and friction areas
- **Emotions** at each step
- **Opportunities** for improvement

### 2. Detailed Use Cases

For each identified use case, provide:

**Use Case Structure:**

- **Use Case ID & Name**: Unique identifier and descriptive name
- **Description**: Brief summary of what the use case accomplishes
- **Actors**: Primary and secondary actors (users, systems, external entities)
- **Stakeholders**: Who has vested interests in this use case
- **Preconditions**: What must be true before the use case can execute
- **Triggers**: What initiates the use case
- **Success Criteria**: How we know the goal has been achieved
- **Standard Flow**: Step-by-step normal scenario
- **Alternate Flows**: Variations and exception scenarios
- **Post-conditions**: System state after successful completion
- **Business Rules**: Constraints and validation rules
- **Non-functional Requirements**: Performance, security, usability requirements

**UML Notation:**

- Create UML use case diagrams showing:
  - Actor relationships
  - Use case relationships (include, extend, generalization)
  - System boundaries
  - Use case dependencies

### 3. Scenario Analysis

For each use case, provide:

- **Happy Path**: Ideal execution scenario
- **Edge Cases**: Boundary conditions and unusual inputs
- **Error Scenarios**: What happens when things go wrong
- **Recovery Paths**: How the system and user recover from errors

### 4. Cross-Component Integration

Identify and document:

- **Dependencies** on other system components
- **Integration points** and data flows
- **Shared resources** and potential conflicts
- **Cascade effects** of failures or changes

## Output Format

Structure your response as follows:

0. Table of Contents (up to level 2 (##) headings)
1. **Executive Summary** of the component's role and key use cases + list of user journeys (as later pointed out in detailes use cases)
2. **User Persona Definitions**
3. **User Journey Maps** (textual description with key touchpoints)
4. **Detailed Use Cases** (following the structure above)
5. **UML Use Case Diagrams** (textual description of diagram elements)
6. **Integration Analysis** with other components
7. **Recommendations** for improvements or optimizations

## Guidelines

- Base all use cases on actual functionality found in the source code
- Ensure traceability between documentation, code, and use cases
- Consider both functional and technical users where applicable
- Include realistic data examples and scenarios
- Address both online and batch processing scenarios where relevant
- Consider authorization and security aspects
- Think about audit trails and logging requirements

Create comprehensive, actionable use cases that can guide development, testing, and user training activities.

## Error Prevention

### Common Mistakes to Avoid

- ❌ Making assumptions about code behavior
- ❌ Using incorrect Mermaid syntax
- ❌ Storing documentation outside `docs/` folder
- ❌ Using inconsistent formatting
- ❌ Missing required sections
- ❌ Broken internal links
- ❌ Unvalidated technical claims

### Best Practices

- ✅ Always read the source code first
- ✅ Validate all Mermaid diagrams before committing
- ✅ Use consistent naming and structure
- ✅ Include practical examples
- ✅ Reference actual file paths and line numbers
- ✅ Test all links and references
- ✅ Follow the established folder structure

**Remember: When in doubt, read the code. Never guess.**
