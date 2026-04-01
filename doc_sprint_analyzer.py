#!/usr/bin/env python3
"""
Jira Documentation Impact Analyzer
Analyzes sprint and backlog tickets for documentation impact.
"""

import json
import sys
from typing import List, Dict, Any


def analyze_doc_impact(issue: Dict[str, Any]) -> Dict[str, str]:
    """
    Analyze a Jira issue for documentation impact.

    Returns:
        Dict with 'impact' level and 'reason' explanation
    """
    summary = issue.get('summary', '').lower()
    description = issue.get('description', '').lower()
    labels = [label.lower() for label in issue.get('labels', [])]
    status = issue.get('status', {}).get('name', '').lower()
    issue_type = issue.get('issuetype', {}).get('name', '').lower()
    combined_text = f"{summary} {description}"

    # STRICT FILTER: Skip Spikes unless they have explicit doc labels
    if issue_type == 'spike':
        if not any(label in labels for label in ['documentation', 'docs-required', 'doc-update']):
            return {'impact': 'SKIP', 'reason': 'Research spike (not user-facing)'}

    # STRICT FILTER: Skip Tasks unless they have explicit doc labels or user-facing signals
    if issue_type == 'task':
        if not any(label in labels for label in ['documentation', 'docs-required', 'doc-update']):
            # Allow tasks through if they have user-facing indicators
            if not any(word in combined_text for word in ['user-facing', 'customer', 'documentation', 'migration', 'deprecat']):
                return {'impact': 'SKIP', 'reason': 'Internal task (not user-facing)'}

    # STRICT FILTER: Skip test tickets (ATF, integration tests, E2E tests)
    test_keywords = [
        'atf-',
        '[atf]',
        'integration test',
        'e2e test',
        'end-to-end test',
        'test plan',
        'add test',
        'implement test',
        'quality engineer',
    ]
    if any(keyword in summary for keyword in test_keywords):
        return {'impact': 'SKIP', 'reason': 'Test/QE ticket (not user-facing)'}

    # STRICT FILTER: Skip dev environment and internal tooling
    dev_keywords = [
        'dev environment',
        'dev env',
        'development environment',
        'sonar cloud',
        'sonarcloud',
        'pre-commit',
        'baseline performance',
        'performance comparison',
        'performance validation',
    ]
    if any(keyword in combined_text for keyword in dev_keywords):
        return {'impact': 'SKIP', 'reason': 'Dev environment/tooling (not user-facing)'}

    # Filter out non-doc-relevant items
    skip_keywords = [
        'tech debt',
        'refactor only',
        'internal refactor',
        'code cleanup',
        'unit test only',
    ]

    # Skip internal process/architecture work
    process_keywords = [
        'produce proposal',
        'open-sourcing',
        'handbook',
        'sdp for',
        'system design plan',
        'async release',
        'go or no-go',
        'pipeline failure',
        'infrastructure-level issue',
        'ci/cd',
        'jenkins',
        'konflux',
    ]

    for keyword in process_keywords:
        if keyword in combined_text:
            return {'impact': 'SKIP', 'reason': f'Internal process/architecture work'}

    # Check if this should be filtered out
    for keyword in skip_keywords:
        if keyword in combined_text and 'user' not in combined_text and 'customer' not in combined_text:
            return {'impact': 'SKIP', 'reason': f'Internal only ({keyword})'}

    # Bug fixes - filter out backend-only bugs
    if issue_type == 'bug':
        backend_only_keywords = ['backend only', 'internal bug', 'does not affect user', 'infrastructure-level']
        if any(kw in combined_text for kw in backend_only_keywords):
            return {'impact': 'SKIP', 'reason': 'Backend-only bug fix'}

    # STRICT: Only explicit doc signals and major user-facing changes
    explicit_doc_signals = [
        'documentation required',
        'documentation needed',
        'docs required',
        'docs needed',
        'doc update',
        'update docs',
        'user guide',
        'customer documentation',
    ]

    # High impact: Major user-facing changes only
    high_impact_signals = [
        'breaking change',
        'migration required',
        'deprecation',
        'deprecating',
        'new user-facing',
        'customer-facing change',
    ]

    # High impact: API/endpoint removals (breaking changes)
    endpoint_removal_patterns = [
        'remove post /',
        'remove get /',
        'remove put /',
        'remove patch /',
        'remove delete /',
        'remove endpoint',
        'remove api',
        'removing endpoint',
        'removing api',
        'delete endpoint',
        'endpoint removal',
        'api removal',
    ]

    # Medium impact: User-facing features and changes
    medium_impact_signals = [
        'new feature',
        'ui change',
        'workflow change',
        'behavior change',
        'configuration change',
        'new parameter',
        'new option',
    ]

    # Check for explicit doc mentions - highest priority
    if any(signal in combined_text for signal in explicit_doc_signals):
        return {
            'impact': 'HIGH',
            'reason': 'Explicit documentation requirement'
        }

    # Check for endpoint/API removals - breaking changes
    for pattern in endpoint_removal_patterns:
        if pattern in combined_text:
            return {
                'impact': 'HIGH',
                'reason': f'API/endpoint removal - detected: "{pattern}"'
            }

    # Check for high impact signals
    for signal in high_impact_signals:
        if signal in combined_text:
            return {
                'impact': 'HIGH',
                'reason': f'Contains: {signal} (user-facing change)'
            }

    # Check for medium impact signals
    for signal in medium_impact_signals:
        if signal in combined_text:
            return {
                'impact': 'MEDIUM',
                'reason': f'Contains: {signal}'
            }

    # User-facing bugs that affect customer experience
    if issue_type == 'bug':
        user_indicators = ['customer', 'user cannot', 'users cannot', 'ui']
        for indicator in user_indicators:
            if indicator in combined_text:
                return {
                    'impact': 'MEDIUM',
                    'reason': f'User-facing bug (contains: {indicator})'
                }

    # CVEs that affect security posture
    if issue_type == 'vulnerability' or 'cve-' in summary:
        # Extract CVE ID if present
        cve_id = 'CVE' if 'cve-' in summary else 'Security issue'
        return {
            'impact': 'MEDIUM',
            'reason': f'Security vulnerability: {cve_id}'
        }

    # Default: low impact but review recommended
    return {
        'impact': 'LOW',
        'reason': 'Gateway component - review recommended'
    }


def format_issue_report(issues: List[Dict[str, Any]]) -> str:
    """
    Format issues into a readable report.
    """
    if not issues:
        return "No issues found matching criteria."

    # Separate by impact level
    high_impact = []
    medium_impact = []
    low_impact = []

    for issue in issues:
        analysis = analyze_doc_impact(issue)

        if analysis['impact'] == 'SKIP':
            continue

        issue_key = issue.get('key', 'UNKNOWN')
        issue_info = {
            'key': issue_key,
            'url': f'https://redhat.atlassian.net/browse/{issue_key}',
            'summary': issue.get('summary', 'No summary'),
            'status': issue.get('status', {}).get('name', 'Unknown'),
            'type': issue.get('issuetype', {}).get('name', 'Unknown'),
            'assignee': issue.get('assignee', {}).get('displayName', 'Unassigned') if issue.get('assignee') else 'Unassigned',
            'sprint': ', '.join([s.get('name', 'Unknown') for s in issue.get('sprints', [])]) if issue.get('sprints') else 'No sprint',
            'analysis': analysis
        }

        if analysis['impact'] == 'HIGH':
            high_impact.append(issue_info)
        elif analysis['impact'] == 'MEDIUM':
            medium_impact.append(issue_info)
        else:
            low_impact.append(issue_info)

    # Build report
    report = []
    report.append("=" * 80)
    report.append("DOCUMENTATION IMPACT ANALYSIS - SPRINT & BACKLOG TICKETS")
    report.append("=" * 80)
    report.append("")

    if high_impact:
        report.append("🔴 HIGH IMPACT - Action Required")
        report.append("-" * 80)
        for issue in high_impact:
            report.append(f"\n{issue['key']}: {issue['summary']}")
            report.append(f"  🔗 {issue['url']}")
            report.append(f"  Type: {issue['type']} | Status: {issue['status']}")
            report.append(f"  Assignee: {issue['assignee']} | Sprint: {issue['sprint']}")
            report.append(f"  💡 Impact: {issue['analysis']['reason']}")
        report.append("")

    if medium_impact:
        report.append("🟡 MEDIUM IMPACT - Review Recommended")
        report.append("-" * 80)
        for issue in medium_impact:
            report.append(f"\n{issue['key']}: {issue['summary']}")
            report.append(f"  🔗 {issue['url']}")
            report.append(f"  Type: {issue['type']} | Status: {issue['status']}")
            report.append(f"  Assignee: {issue['assignee']} | Sprint: {issue['sprint']}")
            report.append(f"  💡 Impact: {issue['analysis']['reason']}")
        report.append("")

    if low_impact:
        report.append("🟢 LOW IMPACT - Monitor")
        report.append("-" * 80)
        for issue in low_impact:
            report.append(f"\n{issue['key']}: {issue['summary']}")
            report.append(f"  🔗 {issue['url']}")
            report.append(f"  Type: {issue['type']} | Status: {issue['status']}")
            report.append(f"  Assignee: {issue['assignee']} | Sprint: {issue['sprint']}")
            report.append(f"  💡 Impact: {issue['analysis']['reason']}")
        report.append("")

    report.append("=" * 80)
    report.append(f"SUMMARY: {len(high_impact)} high | {len(medium_impact)} medium | {len(low_impact)} low impact tickets")
    report.append("=" * 80)

    return "\n".join(report)


if __name__ == "__main__":
    # Read JSON from stdin
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Usage: cat issues.json | python doc_sprint_analyzer.py")
        print("Expects JSON array of Jira issues from stdin")
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
        print(format_issue_report(data))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
