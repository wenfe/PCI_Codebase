---
applyTo: "development planning, user stories, project artifacts"
description: "Instructions for creating development plans and user stories"
---

# Development Planning Instructions

## Core Principles

### Code-Driven Planning

- **Base all estimates on actual codebase analysis**
- **Identify technical debt before feature planning**
- **Consider existing architecture constraints**
- **Prioritize by business value AND technical feasibility**
- **Plan incremental modernization, not big-bang changes**

### Agile Best Practices

- **User-focused story writing** (As a... I want... So that...)
- **INVEST criteria**: Independent, Negotiable, Valuable, Estimable, Small, Testable
- **Clear acceptance criteria** with measurable outcomes
- **Appropriate sizing** (1-8 story points per story)

## Artifact Templates

### Epic Template

```markdown
# Epic: [Epic Name]

## Business Objective

[Clear business goal and expected outcome]

## Success Metrics

- [Measurable metric 1]
- [Measurable metric 2]

## User Types Impacted

- [User type 1]: [How they benefit]
- [User type 2]: [How they benefit]

## Technical Scope

- [Component 1] - [Modification type]
- [Component 2] - [Modification type]

## Dependencies

- [Epic/Story dependency 1]
- [Technical dependency 1]

## Risk Assessment

- **High Risk**: [Risk description] - [Mitigation plan]
- **Medium Risk**: [Risk description] - [Mitigation plan]

## User Stories

1. [Story 1 title]
2. [Story 2 title]
   ...
```

### User Story Template

```markdown
## User Story: [Story Title]

**As a** [user type]
**I want** [functionality goal]  
**So that** [business benefit]

### Acceptance Criteria

- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

### Technical Implementation Notes

- **Components Affected**: [List ABAP components]
- **Database Changes**: [Any table modifications]
- **Integration Points**: [External system impacts]
- **Performance Considerations**: [Any performance impacts]

### Dependencies

- **Story Dependencies**: [Other stories that must be completed first]
- **Technical Dependencies**: [Infrastructure, tools, or platform requirements]

### Definition of Done

- [ ] Code implemented and unit tested
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Code review completed
- [ ] User acceptance testing completed
- [ ] Performance testing (if applicable)

### Effort Estimate

**Story Points**: [1-8]
**Confidence Level**: [High/Medium/Low]

### Business Value

**Priority**: [Critical/High/Medium/Low]
**Business Impact**: [Revenue/Cost Savings/Risk Reduction/User Experience]
```

### Technical Task Template

```markdown
## Technical Task: [Task Title]

### Objective

[Clear technical objective]

### Technical Details

- **Component**: [ABAP component/program]
- **Modification Type**: [New development/Enhancement/Refactoring/Bug fix]
- **Files Affected**: [List of source files]

### Implementation Approach

1. [Step 1]
2. [Step 2]
3. [Step 3]

### Testing Strategy

- **Unit Tests**: [Approach]
- **Integration Tests**: [Approach]
- **Performance Tests**: [If needed]

### Risk Mitigation

- **Technical Risks**: [Risk and mitigation]
- **Business Risks**: [Risk and mitigation]

### Effort Estimate

**Hours**: [Estimated hours]
**Complexity**: [Simple/Medium/Complex]
```

## Planning Process

### Phase 1: Current State Analysis

1. **Codebase Assessment**

   - Identify all components in scope
   - Assess technical debt and code quality
   - Map dependencies and integration points
   - Evaluate performance bottlenecks

2. **Business Process Mapping**
   - Document current workflows
   - Identify pain points and inefficiencies
   - Map user types and their needs
   - Assess business impact of changes

### Phase 2: Future State Design

1. **Target Architecture Definition**

   - Define desired end state
   - Identify required technology changes
   - Plan integration improvements
   - Design new user experiences

2. **Gap Analysis**
   - Compare current vs target state
   - Identify required changes
   - Assess change complexity and risk
   - Prioritize by value and feasibility

### Phase 3: Roadmap Creation

1. **Epic Identification**

   - Group related changes into epics
   - Define business objectives for each epic
   - Estimate epic size and complexity
   - Identify epic dependencies

2. **Release Planning**
   - Define release objectives and scope
   - Sequence epics based on dependencies
   - Balance business value with technical risk
   - Plan incremental delivery approach

## Estimation Guidelines

### Story Point Scale

- **1 Point**: Simple change, well understood, < 4 hours
- **2 Points**: Minor enhancement, clear requirements, < 1 day
- **3 Points**: Standard feature, some complexity, 1-2 days
- **5 Points**: Complex feature, multiple components, 3-5 days
- **8 Points**: Very complex, significant unknowns, 1-2 weeks

### Estimation Factors

- **Code Complexity**: How complex is the existing code?
- **Requirements Clarity**: How well understood are the requirements?
- **Technical Risk**: How much unknown technical complexity?
- **Integration Complexity**: How many systems are affected?
- **Testing Effort**: How much testing is required?

## Risk Management

### Risk Categories

1. **Technical Risks**

   - Legacy code complexity
   - Integration challenges
   - Performance impacts
   - Data migration issues

2. **Business Risks**

   - User adoption challenges
   - Process disruption
   - Training requirements
   - Regulatory compliance

3. **Project Risks**
   - Resource availability
   - Timeline constraints
   - Scope creep
   - Stakeholder alignment

### Mitigation Strategies

- **Proof of Concepts**: For high technical risk items
- **Incremental Delivery**: To reduce business disruption
- **Parallel Running**: For critical system changes
- **Rollback Plans**: For all major changes
- **User Training**: For process changes
- **Documentation**: For knowledge transfer

## Quality Gates

### Story Readiness Criteria

- [ ] Business value clearly defined
- [ ] Acceptance criteria are specific and testable
- [ ] Dependencies identified and planned
- [ ] Technical approach outlined
- [ ] Effort estimated with confidence level
- [ ] Risk assessment completed

### Epic Readiness Criteria

- [ ] Business objective clearly defined
- [ ] Success metrics established
- [ ] All stories identified and estimated
- [ ] Dependencies mapped
- [ ] Risk mitigation plans created
- [ ] Release sequence planned
