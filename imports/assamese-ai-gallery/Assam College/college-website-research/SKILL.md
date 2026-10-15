---
name: college-website-research
description: Research college programmes, departments, and faculty from official college websites and admission sources when a directory needs verified, source-linked academic data. Use for college site scraping or audits; not for generic web scraping.
---

# College website research

College sites use different menus and publishing systems. Treat the site as a navigable institution record, rather than reducing its homepage or first few links to a flat text sample.

## Establish identity and scope

- Match the college by official name, location, and controlling domain. Resolve renamed colleges and duplicate directory rows before counting. Keep a college that is a constituent campus unless the institution itself is now a university.
- Prefer the current college site and current admission/prospectus material. Use the Assam Samarth portal or a government notice as corroboration; a missing portal row does not establish that a college or programme is closed.
- Record the academic session and whether evidence is a current offer, standing site description, older source, plan, distance study centre, or unverified mention.

## Explore the actual site

1. Inspect the homepage's navigation tree, including nested dropdowns. Read the underlying link targets and, when menus are rendered only on interaction, expand them in a browser. Follow every relevant Arts, Science, Commerce, vocational, course, department, teaching staff, and faculty branch. Do not stop after an arbitrary number of homepage links.
2. Inventory all department and programme targets before extraction. Follow department pages, central rosters, faculty profile links, prospectuses, and current admission notices as separate evidence channels. The provided `scripts/inventory_cached_site.py` can list candidate links from the existing cache, but its output is navigation evidence, not verified offerings.
3. Distinguish higher secondary streams from undergraduate degrees and postgraduate programmes. A subject page alone does not prove an active degree; check a current prospectus or admission page for the programme level and session. A department may serve more than one degree or stream.
4. For faculty, use current teaching staff/department rosters. Associate each name with the roster's department. Follow the person's profile for published phone/email; do not assign a college helpdesk or department mailbox to an individual. Omit applicants, shortlisted candidates, alumni, retired and nonteaching staff from the current faculty roster.
5. Where pages conflict, retain both source URLs and dates, prefer newer direct evidence for the relevant field, and mark unresolved differences. Do not turn a failed fetch or absent site link into a confirmed zero.

## Record and check

Store one evidence record per assertion: directory row ID, college, field, value, source URL, page title or section, academic session or page date, retrieval date, and verification status. For people, store name, department, role, public professional phone/email if directly tied to that person, and profile/roster URL. Keep blanks blank.

Check the extracted inventory against the site's menus and current prospectus before calling it complete. Review sites with no faculty listing, conflicting programme levels, changed domains, and pages whose text parser dropped navigation or tables. Summarize coverage separately from verified counts.

Read [references/site-patterns.md](references/site-patterns.md) when planning a bulk crawl or interpreting ambiguous college layouts.
