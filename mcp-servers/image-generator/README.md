# PatientPartner Image Generator MCP

MCP (Model Context Protocol) server that generates photorealistic images of people for PatientPartner.com using **NanoBanana2** (Google Gemini 3.1 Flash Image) via the Replicate API.

## Setup

### 1. Install dependencies

```bash
cd mcp-servers/image-generator
pip install -r requirements.txt
```

### 2. Set your Replicate API token

Add to your `.env` file in the project root:

```
REPLICATE_API_TOKEN=r8_your_token_here
```

Get a token at [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens).

### 3. Verify the MCP is configured

The `.mcp.json` in the project root registers this server with Claude Code:

```json
{
  "mcpServers": {
    "image-generator": {
      "command": "python",
      "args": ["mcp-servers/image-generator/server.py"],
      "env": {
        "REPLICATE_API_TOKEN": "${REPLICATE_API_TOKEN}"
      }
    }
  }
}
```

## Available Tools

| Tool | Purpose | Default Size |
|------|---------|-------------|
| `generate_image` | Full-featured image generation with all options | Custom |
| `generate_patient_photo` | Quick patient portrait | Blog (3:2) |
| `generate_mentor_photo` | Quick mentor/peer supporter portrait | Blog (3:2) |
| `generate_hero_image` | Website hero image | Hero (16:9) |
| `generate_social_image` | Platform-specific social media image | Per platform |
| `list_presets` | List all available presets, emotions, subjects | — |

## Resolution Presets

| Preset | Aspect Ratio | Use Case |
|--------|-------------|----------|
| `social_square` | 1:1 | Instagram feed, LinkedIn, Facebook |
| `social_portrait` | 4:5 | Instagram feed optimal, Facebook ads |
| `social_story` | 9:16 | Stories, Reels, TikTok |
| `hero` | 16:9 | Website hero images, landing pages |
| `blog` | 3:2 | Blog posts, articles |
| `blog_wide` | 16:9 | Blog headers, newsletter banners |

## Subject Types

- `patient` — Real patient in healthcare setting
- `mentor` — Peer supporter / mentor figure
- `caregiver` — Family member / caregiver
- `healthcare_professional` — Doctor, nurse, clinician
- `patient_and_mentor` — Two people in mentorship interaction
- `group` — Support group setting

## Emotions

`hopeful` · `supportive` · `reflective` · `confident` · `grateful` · `determined` · `relieved` · `connected`

## Scene Settings

`consultation` · `waiting_room` · `home` · `outdoors` · `hospital` · `support_group` · `virtual` · `pharmacy` · `recovery`

## Usage Examples

### In Claude Code

```
Generate a hero image of a diverse group of patients and mentors
in a bright modern healthcare facility, looking hopeful and connected.
```

Claude will automatically call `generate_hero_image` with the right parameters.

### Prompt-Only Mode

If `REPLICATE_API_TOKEN` is not set, the server runs in **prompt-only mode** — it returns the fully enhanced prompt and API payload without making API calls. You can copy the prompt into any image generation tool.

## Cost

- ~$0.02–0.04 per image via Replicate
- Pay-per-use, no monthly commitment

## Architecture

```
mcp-servers/image-generator/
├── server.py          # MCP server with all tools and prompt enhancement
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

The server uses the standard MCP stdio transport, compatible with Claude Code and any MCP client.
