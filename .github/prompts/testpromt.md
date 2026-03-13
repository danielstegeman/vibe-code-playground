# Comprehensive Code Review Criteria

Review the following pull request code using the following criteria.
Retrieve the pull request here using mcp:
https://github.com/danielstegeman/vibe-code-playground/pull/1

Output the findings int output/reports/single_agent_review_report.md

## 1. Security Review Criteria

### Scope Areas
- SQL injection vulnerabilities
- XSS (Cross-Site Scripting) vulnerabilities
- CSRF protection
- Authentication/Authorization flaws
- Secrets/credentials in code
- Insecure dependencies
- Data exposure risks
- Input validation and sanitization
- Cryptography usage

### Assessment Requirements
- Specific line numbers or code excerpts
- Vulnerability severity (critical/high/medium/low)
- Remediation recommendations
- Mark each item as ✓ Passed, ⚠ Warning, or ✗ Failed

---

## 2. Code Quality Review Criteria

### Scope Areas
- SOLID principles adherence
- Design pattern appropriateness
- Code complexity (cyclomatic complexity)
- Code duplication (DRY violations)
- Naming conventions and readability
- Error handling robustness
- Performance implications
- Code organization and structure

### Assessment Requirements
- Specific code locations
- Quality assessment (good/acceptable/needs improvement/poor)
- Concrete improvement suggestions
- Mark each item as ✓ Passed, ⚠ Warning, or ✗ Failed

---

## 3. Test Coverage Review Criteria

### Scope Areas
- Unit test coverage for new/modified code
- Edge case handling
- Integration test appropriateness
- Mock/stub usage correctness
- Test clarity and maintainability
- Assertion quality and specificity
- Test performance (slow tests)
- Regression test coverage

### Assessment Requirements
- Identify specific test files and cases
- Assess coverage percentage (if determinable)
- Note missing test scenarios
- Evaluate test quality
- Mark each item as ✓ Passed, ⚠ Warning, or ✗ Failed

---

## 4. Documentation Review Criteria

### Scope Areas
- Inline code comments quality
- Function/class docstrings
- README updates for new features
- API documentation completeness
- Breaking change documentation
- Changelog entries
- Migration guides (if needed)
- Code example clarity

### Assessment Requirements
- Identify specific files and locations
- Assess documentation clarity and completeness
- Note missing or unclear documentation
- Suggest improvements
- Mark each item as ✓ Passed, ⚠ Warning, or ✗ Failed

---

## 5. QA Validation Criteria

### Validation Areas
1. **Scope Drift**: Did review cover areas not mentioned in plan?
2. **Missed Items**: Were checklist items from plan skipped?
3. **Methodology Deviation**: Were different analysis methods used than planned?
4. **Hallucinations**: Were claims made without evidence or outside expertise?

### Discrepancy Reporting
For each discrepancy:
- Agent name
- Type (scope_drift|missed_item|methodology_deviation|hallucination)
- Severity (critical|major|minor)
- Clear explanation of mismatch
- Plan excerpt
- Output excerpt showing mismatch

---

## 6. Director Synthesis Criteria

### Synthesis Requirements
- Consolidate all reviewer findings
- Note QA validation concerns
- Identify cross-cutting issues mentioned by multiple reviewers
- Prioritize issues by severity and impact

### Final Recommendation Options
- ✅ **APPROVE**: Code is production-ready with no blocking issues
- ⚠️ **APPROVE WITH COMMENTS**: Code acceptable but has non-blocking improvements
- 🔄 **REQUEST CHANGES**: Code has issues that must be addressed before merge
- ❌ **REJECT**: Code has critical flaws requiring substantial rework

### Required Report Sections
1. Overall Recommendation (with brief justification)
2. Critical Issues (Must Fix)
3. Major Issues (Should Fix)
4. Minor Issues (Consider Fixing)
5. QA Validation Concerns
6. Positive Highlights
7. Next Steps (clear actionable items)
8. Human Review Required (flagged plan-output mismatches)

---

## Universal Requirements

### Two-Phase Process (All Reviewers Except Director & QA)
**PHASE 1 - PLANNING**: Create detailed review plan with scope, checklist, and methodology
**PHASE 2 - EXECUTION**: Execute review following plan exactly, do not deviate from planned scope

### Evidence-Based Assessment
- All findings must reference specific code locations
- Provide concrete examples and excerpts
- Use clear severity/quality classifications
- Give actionable recommendations

### Consistency
- Stay within planned scope
- Complete all checklist items
- Follow stated methodology
- No hallucinations or unsubstantiated claims