---
mode: agent
model: Claude Sonnet 4 (copilot)
---

# User Journey & Use Case Generation for <component>

You are tasked with creating comprehensive user journeys and detailed use cases for the **<component>** system component.

## Source Materials

**Primary Documentation:**

- Review all existing documentation in `docs/10_ComponentDocumentation*<component>*`
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

1. **Executive Summary** of the component's role and key use cases
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

**Component to analyze:** `<component>`

@workspace Please analyze the specified component and create the user journeys and use cases as described above.
