# Manual Research Checklist

Use this checklist before merging a manual research file.

## Coverage

- [ ] Broad Nubra brand sweep completed across public web, Reddit, YouTube and indexed social results
- [ ] Relevant Nubra mentions retained even when they introduce a new topic outside the predefined keyword list
- [ ] Targeted Nubra and generic retail feature searches completed
- [ ] Retail trading app/product discussions
- [ ] API/algo/developer discussions
- [ ] YouTube/social comments or indexed social signals
- [ ] Competitor mentions
- [ ] SEO/content opportunity signals
- [ ] At least one source URL per signal

## Quality

- [ ] Public source only
- [ ] No private group or login-only content
- [ ] No CAPTCHA/rate-limit bypass
- [ ] No raw personal contact details
- [ ] Segment set as `retail` or `api_algo`
- [ ] Source method is specific
- [ ] Evidence quality is clear
- [ ] Signal title/body are concise and useful
- [ ] Feature IDs, personas and intent are populated or can be inferred from the saved text

## Merge

- [ ] Save to `staging/manual_research_YYYY-MM-DD.jsonl`
- [ ] Run `insights-publisher add-manual-research`
- [ ] Run `insights-publisher validate`
- [ ] Push complete
