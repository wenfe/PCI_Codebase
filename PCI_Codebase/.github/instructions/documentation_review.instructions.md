---
applyTo: "**/docs/**/*.md"
description: "Documentation review and quality assessment instructions"
---

# Documentation Review Instructions

## Review Criteria

### 1. Technical Accuracy (Critical)

- **Code Verification**: All technical details match actual source code
- **Function Descriptions**: Accurate representation of what code actually does
- **Data Structures**: Correct field names, types, and relationships
- **Process Flows**: Accurate sequence diagrams and workflow descriptions
- **Examples**: Working code examples that can be executed

**Assessment Scale**:

- ✅ Fully Accurate (5/5)
- ⚠️ Mostly Accurate with Minor Issues (3-4/5)
- ❌ Significant Inaccuracies (1-2/5)

### 2. Completeness Assessment

- **Component Coverage**: All major functions and features documented
- **Required Sections**: All standard sections present per template
- **Business Context**: Business purpose and value clearly explained
- **Integration Points**: External dependencies and interfaces covered
- **Configuration**: Customization and configuration options documented

**Missing Elements Checklist**:

- [ ] Architecture overview
- [ ] Data model/structures
- [ ] Business processes
- [ ] Error handling
- [ ] Performance considerations
- [ ] Integration interfaces

### 3. Structure and Clarity

- **Consistent Formatting**: Follows established markdown standards
- **Logical Flow**: Information presented in logical sequence
- **Clear Headings**: Descriptive section headers and hierarchy
- **Readable Diagrams**: Mermaid diagrams render correctly and clearly
- **Navigation**: Good use of table of contents and cross-references

### 4. Language and Style (German)

- **Grammar**: Correct German grammar and spelling
- **Technical Terms**: Appropriate use of German technical vocabulary
- **Consistency**: Consistent terminology throughout document
- **Clarity**: Clear, concise explanations without ambiguity

## Review Process

### Step 1: Initial Assessment

```markdown
## Documentation Review Summary

**Document**: [Document Name/Path]
**Review Date**: [Date]
**Reviewer**: [Name/Role]

### Overall Scores

- Technical Accuracy: [X/5]
- Completeness: [X/5]
- Structure & Clarity: [X/5]
- Language Quality: [X/5]

**Overall Rating**: [X/5] ([Excellent/Good/Needs Improvement/Poor])
```

### Step 2: Detailed Analysis

For each major section, provide:

- Accuracy assessment
- Completeness check
- Clarity evaluation
- Specific improvement suggestions

### Step 3: Priority Recommendations

Categorize findings by priority:

#### High Priority (Fix Immediately)

- Technical inaccuracies
- Missing critical sections
- Broken diagrams or examples

#### Medium Priority (Next Review Cycle)

- Structural improvements
- Additional detail needed
- Better examples or explanations

#### Low Priority (Future Enhancement)

- Style improvements
- Additional diagrams
- Extended examples

## Review Templates

### Technical Accuracy Review

```markdown
### Technical Accuracy Check

**Code References Verified**: ✅/❌

- [ ] Function names and signatures correct
- [ ] Database table structures accurate
- [ ] Process flows match actual implementation
- [ ] Examples are executable

**Inaccuracies Found**:

1. [Description] - Line/Section reference
2. [Description] - Line/Section reference

**Recommendations**:

- Specific fixes needed
- Code sections to re-examine
```

### Completeness Review

```markdown
### Completeness Assessment

**Required Sections**:

- [ ] Overview/Purpose
- [ ] Architecture
- [ ] Data Model
- [ ] Business Processes
- [ ] Configuration
- [ ] Integration
- [ ] Examples

**Missing Content**:

1. [Section]: [What's missing]
2. [Section]: [What's missing]

**Enhancement Opportunities**:

- Additional diagrams needed
- More detailed examples
- Better process explanations
```

## Improvement Guidelines

### Making Corrections

1. **Always verify against source code** before making changes
2. **Use specific line references** when suggesting changes
3. **Provide corrected examples** not just identification of errors
4. **Test Mermaid diagrams** for syntax and rendering
5. **Cross-check consistency** with related documentation

### Enhancement Suggestions

- Suggest additional diagrams for complex processes
- Recommend more detailed examples for key functions
- Identify opportunities for cross-referencing
- Suggest user-focused explanations for business processes

### Quality Gates

Before marking review complete:

- [ ] All technical details verified against code
- [ ] All Mermaid diagrams render correctly
- [ ] All cross-references work properly
- [ ] Document follows template structure
- [ ] German language quality is professional
- [ ] Examples are practical and executable
