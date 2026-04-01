# Sprint Analyzer for Documentation Teams

Automate Jira sprint review and documentation impact analysis using Claude Code.

**Time Savings:** 45-60 minutes → 15 seconds (98% reduction)

## Demo

[Link to demo video - shows this tool in action]

## What It Does

- Queries Jira for sprint and backlog tickets via natural language
- Automatically filters out internal work (tests, spikes, CI/CD)
- Categorizes tickets by documentation impact (HIGH/MEDIUM/LOW)
- Generates actionable reports with direct Jira links
- All through simple questions in Claude Code

## Requirements

- **Claude Code** - CLI, desktop app, or web ([claude.ai/code](https://claude.ai/code))
- **Atlassian MCP Server** - For Jira integration ([setup guide](https://medium.com/@milad.jafary/how-to-connect-atlassian-mcp-server-to-claude-code-5c22d47d5cd5))
- **Python 3.x** - To run the analyzer script
- **Jira Instance** - With sprint-based workflow

## Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/EMcWhinn/sprint-analyzer
cd sprint-analyzer

# Copy template and customize for your project
cp CLAUDE.md.template CLAUDE.md
```

### 2. Edit CLAUDE.md

Open `CLAUDE.md` and replace the placeholders:

- `[YOUR PRODUCT NAME]` - Your product/project name
- `[YOUR DOCUMENTATION URL]` - Where your docs live
- `[YOUR_PROJECT]` - Your Jira project key (e.g., SHOP, DOCS, MYPROJ)
- `[YOUR_TEAM_FILTER]` - Your Jira team/workstream field (e.g., `Team = "Backend"`)
- `[YOUR_COMPONENT]` - Your product components

**Example JQL customization:**
```
# From template:
project = [YOUR_PROJECT] AND [YOUR_TEAM_FILTER] AND sprint in openSprints()

# For your project:
project = SHOP AND Team = "Backend" AND sprint in openSprints()
```

See inline comments in `CLAUDE.md.template` for guidance.

### 3. Set Up Atlassian MCP

Configure the Atlassian MCP server with your Jira credentials. This enables Claude Code to query your Jira instance.

### 4. Use It

Open Claude Code in this directory and ask:

```
Analyze [your project] sprints for documentation impact
```

Claude will automatically query Jira, run the analyzer, and show categorized results.

## How It Works

```
User asks in natural language
    ↓
Claude Code interprets intent
    ↓
Atlassian MCP queries Jira
    ↓
Data converted for analyzer
    ↓
doc_sprint_analyzer.py categorizes tickets
    ↓
Report displayed (HIGH/MEDIUM/LOW impact)
```

### Impact Categories

**HIGH Impact** (action required):
- Breaking changes, deprecations, migrations
- API/endpoint removals
- Explicit documentation requirements

**MEDIUM Impact** (review recommended):
- New user-facing features
- Security vulnerabilities (CVEs)
- Customer-facing bugs
- Workflow/behavior changes

**LOW Impact** (monitor):
- Minor enhancements
- Component updates

**Automatically Filtered** (not shown):
- Test tickets, spikes, CI/CD work
- Internal refactoring, dev environment setup

## Customizing Keywords

Want different categorization? Edit `doc_sprint_analyzer.py`:

**Add your product-specific terms** (around line 109-148):
```python
# High priority signals
high_impact_signals = [
    'breaking change',
    'incompatible with',     # Add yours
]

# Medium priority signals
medium_impact_signals = [
    'new feature',
    'merchant-facing',       # Add yours
]
```

**Change default message** (around line 210):
```python
return {
    'impact': 'LOW',
    'reason': 'Review recommended'  # Customize
}
```

## Example Queries

Once configured, ask Claude Code questions in natural language:

**Sprint Analysis:**
- `Analyze Platform Services sprints for documentation impact`
- `Analyze [your team name] sprints for documentation impact`
- `What breaking changes are in the next sprint?`
- `Compare this sprint to last sprint`

**Component/Label-Specific:**
- `Analyze aap-gateway label for documentation impact`
- `Analyze the API component backlog`
- `Show me [your component] tickets`

**Filtered Views:**
- `Show me just the CVEs from the current sprint`
- `What customer-facing bugs are in the backlog?`
- `List all breaking changes`

The tool automatically:
- Constructs the correct JQL query based on your CLAUDE.md configuration
- Queries your Jira instance
- Filters and categorizes results
- Presents actionable reports

## Current Example Configuration

This repo includes an example configuration for **Red Hat Ansible Automation Platform** as a reference:

- Jira Project: AAP
- Workstream: Platform Services
- Components: aap-gateway, platform-services-utilities
- Docs: docs.redhat.com/ansible-automation-platform

You can use this to understand the structure when configuring for your own project.

## Different Jira Structures?

Your CLAUDE.md template needs the right JQL queries for your Jira setup. Here are examples:

**Sprint analysis (workstream/team-based):**
```
# Platform Services example (current config)
project = AAP AND Workstream = "Platform Services" AND sprint in openSprints()

# Simple team filter
project = DOCS AND Team = "Backend" AND sprint in openSprints()

# Multiple teams
project = SHOP AND Team in ("Checkout", "Payments") AND sprint in openSprints()

# No custom fields (just use sprint)
project = MYPROJ AND sprint in openSprints()
```

**Component/label analysis:**
```
# By component (like aap-gateway)
project = AAP AND component = "aap-gateway" AND status in (Backlog, Refinement, New, "In Progress")

# By label
project = MYPROJ AND labels = "api-changes" AND status in (Open, "In Progress")

# Multiple components
project = SHOP AND component in ("Checkout", "Payments") AND status in (Backlog, "In Progress")
```

Use your Jira query builder to find the right field names for your instance.

## Troubleshooting

**No results?**
- Check your JQL query in CLAUDE.md matches your Jira structure
- Verify Atlassian MCP is configured correctly
- Make sure you're in the project directory when running Claude Code

**Wrong categorization?**
- Add product-specific keywords to `doc_sprint_analyzer.py`
- Adjust impact signals for your workflow

**Too many results?**
- Add more filters to your JQL (team, component, status)
- Customize what gets filtered in `doc_sprint_analyzer.py` (line 39-95)

## Files

- **README.md** - This file
- **doc_sprint_analyzer.py** - Core analyzer (works out of the box)
- **CLAUDE.md.template** - Template project instructions (customize this)
- **.gitignore** - Prevents committing your personal CLAUDE.md

## Contributing

Improvements welcome! Common additions:
- More pattern matching keywords
- GitHub/GitLab issue tracker support
- Additional filtering logic

## Questions?

Open an issue or see the demo video for a walkthrough.

---

**Note:** This tool uses pattern matching to pre-filter tickets. It saves significant time but doesn't replace human review—always verify the results make sense for your context.
