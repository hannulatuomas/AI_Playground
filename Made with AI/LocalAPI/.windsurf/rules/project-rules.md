---
trigger: always_on
---

- You are an experienced senior developer and expert with APIs.
- We are building fully local, offline-capable API development tool named "LocalAPI," inspired by Postman (and little bit by Insomnia and SoapUI).
- It focuses on the specified must-have features: core API development, protocol support with automatic extraction, mock servers, secure storage, performance optimization, variables.

- The App must be minimal, cross-platform, and easy to maintain and extend.
- The App UI/UX needs to be easy to use, user-friendly, lightweight and minimal.
- Always give me a scripts to: easily run all the tests (with venv activated), easily run the program (with venv activated). Organize those in scripts/ folder and keep them up to date
- After implementing, improving or fixing anything, give me a comprehensive and detailed Git commit message. Make the output as a full git commit command in a .bat file (e.g. commits/phase_1.1.1.bat). Be careful with multi-line syntax and bad characters in commit message

Important features we should have:
1. All the Core API Development and Workflow Management
- testing, collections, environments, and scripting
- API Design and Prototyping
- Request Building and Sending
- Response Handling and Testing
- API Documentation
- Collections Management
(- Workflow Automation)
(- Monitoring and Reliability)
2. API clients for various protocols (GraphQL, SOAP, gRPC in addition to REST)
- With Tools to design API schemas automatically/easily (e.g., OpenAPI/Swagger support, WSDL support etc.)
3. Mock servers, documentation generation, and basic integrations
4. Secure storage of secrets
5. Performance Optimization
6. Variables (global and collection scoped)
- Easy way to automatically extract or update variables (or values) from API responses (for example: get Auth token from /auth endpoint and update it to token variable to be used in other API calls later)

We don't need any:
1. Collaboration and Team Features
2. AI and Intelligent Features

When creating Windows .bat files for git commits with multi-line messages, use the proper syntax:
- git commit ^ -m "Title line" ^ -m "" ^ -m "Body line 1" ^ -m "Body line 2" ^ -m "" ^ -m "Footer". Each -m flag creates a new paragraph in the commit message. Use -m "" for blank lines. Each line must end with ^ (line continuation character) except the last one. The message must not include any other "-characters, because those will break the syntax.
- NEVER use the broken syntax like: git commit -m "Title ^ Body text...". This will fail in Windows batch files.