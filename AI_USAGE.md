# AI Usage Documentation

## Summary

This project was made with the use of two AI systems, Claude and Gemini. I created the backend (`app.py` and `database.py`) in my own style and format with the help of both AI systems. I used Claude to create a draft of the backend and then I rewrote it. I also used Claude to make the database schema and the sample data (`schema.sql`). I used Claude the most for the frontend design. I used it to create the CSS design system and also the HTML templates.

## Tools Used

- **Claude (Anthropic, Claude Opus 5.5):** created the frontend, reviewed my rewritten backend, helped with debugging my environment setup, and tested the finished application
- **Gemini (Google):** [explain how you used Gemini. For example, you could have used it to explain errors, review code, or help write a route.]

## Prompts

1. "I forgot my MySQL password." Claude guided me through resetting my MySQL password on my Mac with `--skip-grant-tables`.
2. "Here is what I have right now. I have rewritten both app.py and database.py." I asked Claude to review my rewritten backend.
3. "Go through the checklist for me." With my application running, Claude went through every page and CRUD operation using 41 checks.

## What Worked Well

- **Sample data that allows for testing.** The jobs at DataCo and TechCorp in the sample data match the Job Match example in the spec (100%, then 67% missing Tableau). This let me test my algorithm immediately.
- **Code review.** When I sent Claude my rewritten `app.py`, it tested it against the templates and found two issues (described below) rather than simply telling me the code appeared to work.
- **Debugging environment issues.** `mysql: command not found`, `code: command not found`, a forgotten MySQL password, and a `sudo` command that got stuck in the background.

## What I Changed

- **Rewrote `app.py` and `database.py`.** I created the helpers in my own style (`parse_db_json`, `get_skills_list`, `clean_input`), put the input validation inline in each route, used my own variable names (`min_sal`, `comp_id`, `app_id`), and added my own comments throughout.
- **Fixed an issue found during code review.** My `edit_job` route only validated the job title. When a job was edited with min salary > max salary, the MySQL CHECK constraint caused a 500 error. I added the same min/max salary and skills validation that was in `add_job`.
- **Naming inconsistency.** My route used `app_id`, but Claude's templates used `application_id`. I chose to keep my naming, and the templates were adjusted to match my code.

## What AI Got Wrong or Failed to Catch

- Claude told me to expect 27 routes from a quick check, but the actual count was 21. Claude re-ran the check, confirmed 21 was correct, and corrected its mistake.
- The initial dark mode inverted the depth of the active nav pill and the stat-card faces: they were darker than the surfaces they sat on. Claude noticed this in its own screenshots and fixed it before handing me the files.

## Lessons Learned

- **Test AI-generated code rather than just believing the AI.** The route count and the dark mode issue were only found when the code was actually run and looked at.
- **Add and edit routes need the same input validation.** The edit route failed on data the add route handled, and browser validation doesn't catch all invalid data.
- **AI is strong at debugging environment issues.** Resetting the MySQL password and fixing the PATH issues would have been much harder alone.
- **Specific design ideas work better than "make it look nice."** Naming specific design techniques produced a more unique UI instead of a default Bootstrap page.
