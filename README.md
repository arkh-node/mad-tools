# mad-tools

```
[M·A·D]  model · agent · destruction
```

CLI toolkit for AI/LLM security research and bug bounty.
20 tools covering recon, prompt injection, RAG attacks, MCP exploitation, OPSEC and more.

Runs locally on mrph.

---

## Tools

### Recon & OPSEC
| Tool | Description |
|------|-------------|
| `banshee` | Recon pipeline: subfinder → httpx → nuclei + Shodan + AI summary |
| `periscope` | Bug bounty scope snapshots and change tracking |
| `cloak` | Identity-layer and OPSEC checker |
| `ferret` | Finding organizer with Textual TUI board |

### Prompt Injection & Jailbreaks
| Tool | Description |
|------|-------------|
| `spike` | Prompt injection payload battery |
| `needler` | MCP tool fuzzer |
| `smuggler` | Token smuggling battery |
| `ghostwrite` | Cross-session memory poison tester |
| `babel` | Multi-agent confusion scenarios |

### LLM Internals & RAG
| Tool | Description |
|------|-------------|
| `arsenic` | Adversarial RAG document generator |
| `collider` | Embedding collision finder |
| `exhaust` | Context flood and performance fuzzer |
| `overreach` | Excessive-agency analyzer |

### MCP & Agents
| Tool | Description |
|------|-------------|
| `mcpx` | MCP server black-box probe |
| `shadow` | Agent trace diff recorder |
| `snare` | Browser trap / callback catcher |

### Reporting
| Tool | Description |
|------|-------------|
| `inkwell` | Disclosure template generator (also at [n0madgang/inkwell](https://github.com/n0madgang/inkwell)) |
| `arsenic` | Adversarial document kit for PoC reports |
| `grimoire` | Local MAD wiki and research notes |

---

## Install

```bash
git clone https://github.com/n0madgang/mad-tools
cd mad-tools
source ~/envs/mad/bin/activate

# install all tools
for d in banshee periscope cloak ferret spike needler smuggler ghostwrite \
          babel arsenic collider exhaust overreach mcpx shadow snare grimoire \
          disclosure-template finding-organizer; do
  pip install -e $d
done
```

Requires: subfinder, httpx, nuclei in PATH for banshee recon pipeline.

---

MIT License
