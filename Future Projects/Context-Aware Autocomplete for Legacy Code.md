You are an experienced senior developer and expert in AI.
I want to make an App using AI, so I need you to give me a comprehensive, detailed project plan for this. Make it AI-friendly. 
The App idea is this: "Context-Aware Autocomplete for Legacy Code
Fine-tuned CodeLlama 7B on 200k lines of internal C++
Runs in VS Code via Ollama — zero latency
Reduced boilerplate by ~40% in refactoring tasks"

------------------------------------

------------------------------------

# Context-Aware Autocomplete for Legacy Code Project Plan

## 1. Project Overview
The Context-Aware Autocomplete for Legacy Code is an AI-powered Visual Studio Code (VS Code) extension that provides intelligent, context-sensitive code completions tailored to legacy C++ codebases. By fine-tuning the CodeLlama 7B model on approximately 200,000 lines of internal C++ code, the app delivers highly relevant suggestions that understand project-specific patterns, idioms, and boilerplate. Running locally via Ollama for zero-latency inference, it integrates seamlessly into VS Code workflows. The tool focuses on reducing boilerplate code during refactoring tasks by about 40%, accelerating development in large, legacy systems while maintaining data privacy through on-device processing.

This project plan is AI-friendly, with a modular structure where each component can be developed, tested, and iterated using AI tools (e.g., LLMs for code generation, prompt-based prototyping). Phases include explicit AI-assisted steps to leverage models like CodeLlama for rapid development and validation.

## 2. Objectives and Goals
### Primary Objectives:
- Fine-tune CodeLlama 7B to provide autocomplete suggestions that are aware of legacy C++ context, including deprecated patterns, custom libraries, and domain-specific logic.
- Achieve zero-latency completions by running inference locally via Ollama.
- Integrate as a VS Code extension for seamless user experience.
- Reduce boilerplate code generation by ~40% in refactoring scenarios, measured through before-after code metrics.

### Secondary Goals:
- Support large codebases (200k+ lines) with efficient tokenization and context handling.
- Ensure compatibility with common C++ standards (e.g., C++11 to C++20) and build systems like CMake.
- Make the extension customizable for different internal codebases via easy fine-tuning pipelines.
- Promote developer productivity with features like inline explanations for suggestions.

### Success Metrics:
- Latency: <50ms for completions on standard hardware.
- Accuracy: 70%+ acceptance rate of suggestions in user tests.
- Efficiency: 40% reduction in lines of code for common refactoring tasks (e.g., via diff analysis).
- Usability: 85%+ satisfaction in internal beta testing.
- Scalability: Handle files up to 10k lines without performance degradation.

## 3. Scope
### In-Scope Features:
- **Model Fine-Tuning**: Train CodeLlama 7B on internal C++ dataset; focus on autocomplete tasks.
- **VS Code Integration**: Extension that hooks into VS Code's completion provider API, using Ollama for local inference.
- **Context Awareness**: Use file history, project structure, and recent edits for personalized suggestions.
- **Boilerplate Reduction**: Suggest refactors for repetitive patterns (e.g., error handling, memory management in legacy C++).
- **User Controls**: Settings for suggestion aggressiveness, model quantization, and debug logging.
- **Metrics Tracking**: Built-in logging to measure boilerplate reduction (e.g., via AST diffing).

### Out-of-Scope (for MVP):
- Support for other languages (focus on C++ only).
- Multi-user collaboration features.
- Cloud-based fine-tuning or inference.
- Advanced IDE integrations beyond VS Code.

### Assumptions:
- Access to 200k lines of internal C++ code for fine-tuning (anonymized if needed).
- Developers have VS Code installed and basic familiarity with extensions.
- Hardware supports Ollama (e.g., CPU/GPU with 8GB+ RAM).
- Open-source components are prioritized for community extensibility.

## 4. Technologies and Tools
### Core AI Stack:
- **LLM**: CodeLlama 7B (fine-tuned for code completion; use Hugging Face for base model).
- **Inference Engine**: Ollama for local, low-latency serving; supports quantization for speed.
- **Fine-Tuning Framework**: PEFT (Parameter-Efficient Fine-Tuning) with LoRA to train on modest hardware.

### Development Tools:
- **Languages**: TypeScript/JavaScript for VS Code extension; Python for fine-tuning scripts.
- **Frameworks**: VS Code Extension API; Transformers library for model handling.
- **Data Processing**: Tree-sitter for C++ parsing; Datasets library for preparing training data.
- **Testing**: Jest for extension tests; Custom Python scripts for model evaluation.
- **Deployment**: VSIX packaging for VS Code Marketplace or internal distribution.
- **Version Control**: Git for codebase; optional GitHub for collaboration.

### AI-Friendly Enhancements:
- Use AI code generators (e.g., CodeLlama itself) for prototyping extension code.
- Prompt templates: E.g., "Generate C++ autocomplete for this context: {code_snippet}. Reduce boilerplate by suggesting refactors."

## 5. High-Level Architecture
The app uses a client-server-like architecture within VS Code:

- **Client Layer**: VS Code extension listens for typing events, sends context (current file, cursor position) to local server.
- **Inference Layer**: Ollama serves the fine-tuned CodeLlama; processes context tokens and generates completions.
- **Processing Layer**: Preprocess input (tokenize C++ code, extract relevant context); post-process outputs (filter suggestions, format for VS Code).
- **Data Layer**: Local storage for model weights and fine-tuning configs.
- **Monitoring**: Extension telemetry for usage metrics (opt-in).

Diagram (text-based for clarity):
```
[VS Code Editor] --> [Extension API] --> [Context Extractor] --> [Ollama Server (CodeLlama 7B)] --> [Suggestion Formatter] --> [Autocomplete UI]
                                           |
                                           v
                                 [Local Storage: Model Weights, Configs]
```

This modular design allows AI-assisted development: E.g., test inference layer independently with mock prompts.

## 6. Development Phases
Phased approach with agile sprints (2-3 weeks each). Total estimated duration: 2-4 months for MVP.

### Phase 1: Planning and Setup (1 week)
- Gather requirements: Define user stories (e.g., "As a C++ dev, I want context-aware completions to reduce typing legacy patterns").
- Set up environment: Install Ollama, download CodeLlama 7B; prepare dataset from 200k C++ lines.
- AI-Friendly Step: Generate dataset prep script via prompt: "Write Python code to preprocess 200k lines of C++ for fine-tuning."

### Phase 2: Model Fine-Tuning (3 weeks)
- Prepare dataset: Curate pairs of incomplete code and completions from internal repo (e.g., using git history).
- Fine-tune CodeLlama: Use LoRA on autocomplete tasks; train on GPU/CPU.
- Evaluate: Measure perplexity and boilerplate reduction on holdout set.
- AI-Friendly Step: Use CodeLlama to augment data: "Generate synthetic C++ legacy code pairs with boilerplate reductions."

### Phase 3: Extension Development (3 weeks)
- Build VS Code extension skeleton: Implement completion provider.
- Integrate Ollama: Set up local API calls for zero-latency inference.
- Add context features: Parse project files for enhanced suggestions.
- AI-Friendly Step: Prototype extension code: Prompt for "Write TypeScript for VS Code autocomplete using Ollama."

### Phase 4: Features and Optimization (2 weeks)
- Implement boilerplate reduction: Detect patterns and suggest refactors.
- Optimize for latency: Quantize model (e.g., 4-bit); cache common contexts.
- Add user settings: UI for toggling features.
- AI-Friendly Step: Generate refactor prompts: "Create examples of C++ boilerplate reductions using AI suggestions."

### Phase 5: Testing and Validation (2 weeks)
- Unit/Integration Tests: Test completions on sample C++ files.
- Performance Testing: Benchmark latency and accuracy.
- User Testing: Internal devs refactor code; measure 40% boilerplate reduction.
- AI-Friendly Step: Automate tests: "Generate test cases for C++ autocomplete scenarios."

### Phase 6: Deployment and Launch (1 week)
- Package extension: Create VSIX file; document installation.
- Release: Internal distribution or VS Code Marketplace.
- AI-Friendly Step: Write docs: "Generate user guide for Context-Aware Autocomplete extension."

## 7. Timeline and Milestones
- **Week 1**: Planning complete; dataset ready.
- **Week 2-4**: Model fine-tuned; initial evaluations.
- **Week 5-7**: Extension integrated; core features working.
- **Week 8-9**: Optimizations and advanced features.
- **Week 10-11**: Testing achieves 40% reduction metric.
- **Week 12**: Deployment; beta launch.

Adjust for solo dev (extend by 1 month) or team.

## 8. Resources
- **Team**: 1 Senior Developer (you), optional 1 Data Engineer for dataset curation.
- **Budget**: Minimal ($200-1000): GPU cloud for fine-tuning if local hardware insufficient.
- **Tools**: Free/open-source; leverage AI for 20-30% code generation.
- **Hardware**: Machine with NVIDIA GPU (e.g., RTX 3060) for fine-tuning/inference.

## 9. Risks and Mitigations
- **Risk**: Fine-tuning doesn't capture legacy nuances.
  - Mitigation: Augment dataset with synthetic examples; iterative training.
- **Risk**: Latency issues on weaker hardware.
  - Mitigation: Model quantization; fallback to smaller variants.
- **Risk**: Data privacy with internal code.
  - Mitigation: All processing local; no external uploads.
- **Risk**: VS Code API changes.
  - Mitigation: Pin to stable versions; monitor updates.

## 10. Testing and Evaluation
- **Unit Tests**: Cover extension logic and model outputs.
- **Integration Tests**: Simulate typing in VS Code with mock Ollama.
- **Efficiency Evaluation**: Use tools like clang-format diffs to quantify boilerplate reduction.
- **User Testing**: A/B tests with/without extension on refactoring tasks.
- **Continuous Improvement**: Collect anonymized usage data for further fine-tuning.

This plan provides a clear, executable roadmap, optimized for AI-assisted development to ensure rapid iteration and high-quality outcomes. Begin with Phase 1 to build momentum.
