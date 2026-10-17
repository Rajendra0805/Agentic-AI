# ADR-001: Code Analysis Agent

## Status

Proposed

## Context

We need a reusable AI agent capable of analyzing
.NET repositories as part of the AI-DLC lifecycle.

## Decision

We will build a read-only Code Analysis Agent.

The agent will use deterministic repository-analysis
tools for fact extraction and an LLM for interpretation.

RAG will provide organization-specific engineering
and security standards.

## Responsibilities

- Repository analysis
- Architecture identification
- Dependency analysis
- API discovery
- Database discovery
- Security analysis
- Technical debt identification

## Non-Responsibilities

- Code modification
- Git commit
- Git push
- Deployment

## Security

The agent will initially have read-only repository access.

Repository content will be treated as untrusted data.

Secrets will not be intentionally sent to the LLM.

## Output

Structured JSON followed by human-readable Markdown.

## Future

The agent will become part of the AI-DLC multi-agent workflow.

## Architecture Diagram

                           USER
                            │
                            ▼
                    Analysis Request
                            │
                            ▼
              ┌─────────────────────────┐
              │   CODE ANALYSIS AGENT   │
              │                         │
              │  Planning / Reasoning  │
              └────────────┬────────────┘
                           │
       ┌───────────────────┼────────────────────┐
       │                   │                    │
       ▼                   ▼                    ▼
 Repository Tools      Code Tools          RAG
       │                   │                    │
       ├── List Files      ├── Search Code      ├── Standards
       ├── Read File       ├── Find APIs        ├── Security
       ├── Projects        ├── Find DB          └── Architecture
       └── Dependencies    └── Dependencies
       │                   │                    │
       └───────────────────┼────────────────────┘
                           ▼
                          LLM
                           │
                           ▼
                  Structured JSON
                           │
                           ▼
                       Validator
                           │
                           ▼
                    Analysis Report