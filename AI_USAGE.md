# AI usage

**Tool:** Claude (Anthropic, Claude Opus 5.5), in a claude.ai Project, with separate chats for planning, code, report and a final independent check. Machine translation helped me read Swedish model outputs.

**How I worked.** I directed the work and made every decision: the question, the hypotheses, the change of target after pilot 1, each deviation, the go/no-go calls and what the report claims. I used Claude to carry out the steps I asked for, then questioned its output repeatedly (why this design, does this number match the result file, what would break this conclusion) until I was satisfied that each step was sound and the pipeline worked.

**What Claude did, at my direction:**
- Drafted the paper analysis from the blog post and released logs (I checked the key numbers).
- Wrote the scripts and configs, tested with mock models. I ran every real experiment on my Apple M1 Pro MacBook Pro.
- Wrote the synthetic prompt sets (I spot-checked them in `data/SPOTCHECK.md`).
- Rated coherence of 160 answers, blind to condition, with a rubric fixed in advance. I rated 20 of them blind myself; we agreed on 17.
- Drafted the report, README and docs, which I reviewed and edited.

**What no AI did.** No LLM read the weights or chose the edit. The edit form comes from the paper authors' logs; a script computes the direction and a rule fixed before any dev run selects the parameters (`configs/step4_6.json`).
