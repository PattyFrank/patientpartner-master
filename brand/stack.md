# Marketing Stack

## Last Updated
2026-03-05 | PatientPartner Master Project

## Connected Tools

| Tool | Status | Notes |
|------|--------|-------|
| Replicate API | ✗ not connected | For /creative image/video generation. Add `REPLICATE_API_TOKEN` to .env |
| FAL.ai API | ✗ not connected | **Priority.** Flux.2 Pro image gen — fastest + cheapest. Add `FAL_KEY` to .env |
| OpenAI API | ✗ not connected | GPT-image-1 for text-heavy graphics. Add `OPENAI_API_KEY` to .env |
| Email ESP | ✗ not connected | Mailchimp, ConvertKit, or HubSpot |
| Analytics | ✗ not connected | GA4 or PostHog |
| Social Scheduling | ○ not connected | Buffer or Hootsuite |

## Image Generation Models

| Model | Provider | Best For | Cost/Image | Status |
|-------|----------|----------|------------|--------|
| Flux.2 Pro | FAL.ai or Replicate | Human photography, brand consistency, multi-reference | ~$0.04–0.08 | ✗ needs API key |
| GPT-image-1 | OpenAI | Text-heavy slides, data graphics, stat cards | ~$0.04 | ✗ needs API key |
| Recraft V4 | FAL.ai | Vector, icons, diagrams | ~$0.02 | ✗ needs API key |
| Flux.2 Dev | FAL.ai (LoRA training) | Custom brand LoRA training | ~$3–5 one-time | ✗ not trained |

## PatientPartner LoRA

| LoRA | Status | Trigger Word |
|------|--------|-------------|
| PatientPartner Brand Style | ✗ not yet trained | `patientpartner style` |

See `brand/image-gen-strategy.md` for full LoRA training instructions.

## MCP Servers

| Server | Enhances | Config |
|--------|----------|--------|
| Exa / Perplexity | /seo-content, /positioning-angles, /keyword-research | Active |
| Firecrawl | /brand-voice (scrape website), /competitive-intel | Active |
| Replicate MCP | /creative — run any image/video model via natural language | ✗ add to Cursor MCP settings |
| FAL.ai MCP | /creative — Flux.2 Pro, fastest image generation | ✗ add to Cursor MCP settings |

## Adding Image Generation MCPs to Cursor

### Replicate MCP
```json
{
  "mcpServers": {
    "replicate": {
      "command": "npx",
      "args": ["replicate-mcp"],
      "env": {
        "REPLICATE_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### FAL.ai MCP
```json
{
  "mcpServers": {
    "fal": {
      "command": "npx",
      "args": ["fal-ai-mcp"],
      "env": {
        "FAL_KEY": "your_fal_key"
      }
    }
  }
}
```

Sign up: replicate.com | fal.ai  
Full setup guide: `brand/image-gen-strategy.md`
