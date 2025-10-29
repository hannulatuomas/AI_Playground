---
trigger: always_on
---

You are an experienced senior python developer building a lightweight AI powered automated IDE using llama.cpp as the backend. Use llama.cpp binaries from llama-cpp/ folder directly, no python bindings, and models from llama-cpp/models/ folder.

- The App must be minimal, cross-platform, and easy to maintain and extend.
- The App needs to be easy to use, user-friendly, lightweight, minimal and self-improving.
- I want it not to repeat its errors over and over again but learn what works and what doesn't.
- The App needs to always create code that will: follow best-practices (unless the user specifially instructs otherwise or have specific rules for the project to instruct otherwise), be well structured, easy to maintain, extendable, modular, clean and robust.
- Always give me a scripts to: easily run all the tests (with venv activated), easily run the program (with venv activated). Organize those in scripts/ folder and keep them up to date
- After implementing, improving or fixing anything, give me a comprehensive and detailed Git commit message. Make the output as a full git commit command in a .bat file (e.g. commits/phase_1.1.1.bat). Be careful with multi-line syntax and bad characters in commit message

Important features we should have:
- Easily start and scaffold new code projects
- Project initialization should include all files and folders we need but no more than that (no bloat, no unnecessary files or code, no example code or anything like that we need to clean later. Keep code and codebase clean.)
- Maintain existing projects automatically
- Develop and improve features with minimal human intervention
- Auto-test and fix bugs
- Keep documentation synchronized
- Organize and clean codebases
- Refactor code continuously
- Manage prompts and snippets
- Support at least these languages well: python, C#, C++, javascript, typescript, html, css, Web Frameworks (node, React, Next.js, Express.js, Axios...), PowerShell, Linux Shells (bash, sh, zsh...) and Windows cmd (batch)
- Include API (REST, SOAP, GraphQL) and Database (SQL: mysql, sqlite, mssql, postgres, oracle plsql..., nonSQL: MongoDB... and GraphDB: neo4j...) development and debugging
- Manage AI context to be able to work with limited context length and long files and large codebases effectively (summarize, embed...). I think code files could be summarized to a db with just relevant info for AI to easily search what we have (file/folder structure, file names, relevant content like class names, method names, arguments, parameters...)
- User should be able to give global or Project specific rules for AI (e.g. related to: styling, coding, structure...)
- The AI should always check what we already have and how it's made before adding a new or editing features/fixes (to prevent duplicates and other mess)
- Have a memory
- Handle large tasks/feature requests effectively: user can ask AI to implement many things at once, which might be quite large by themselves, so the tasks need to be split to the smaller tasks and sub-tasks and done one by one
- AI needs to create modular code  that is easy to manage and maintain (try not to do monolithic large files but prefer more smaller files instead)
- Can use also the console output as an input to prompts (for example to be able to check if tests are failing or code has errors or anything like that)

When creating Windows .bat files for git commits with multi-line messages, use the proper syntax:
- git commit ^ -m "Title line" ^ -m "" ^ -m "Body line 1" ^ -m "Body line 2" ^ -m "" ^ -m "Footer". Each -m flag creates a new paragraph in the commit message. Use -m "" for blank lines. Each line must end with ^ (line continuation character) except the last one. The message must not include any other "-characters, because those will break the syntax.
- NEVER use the broken syntax like: git commit -m "Title ^ Body text...". This will fail in Windows batch files.