\## 📌 CRITICAL DESIGN PRINCIPLES



These principles are MANDATORY and must be enforced across all phases:



1\. Zero-Bloat Project Initialization

2\. Mandatory Planning Phase Before Implementation

3\. Autonomous Task Execution with Context Management



\### 1. Zero-Bloat Project Initialization



\*\*Principle\*\*: Create ONLY what's needed, nothing more.



\*\*Requirements\*\*:

\- \*\*No example code\*\*: Templates should create minimal, production-ready structure

\- \*\*No placeholder files\*\*: Every file must serve a real purpose

\- \*\*No "TODO" comments\*\*: Code should be ready to use or absent

\- \*\*No demo/sample data\*\*: User adds their own data

\- \*\*Minimal dependencies\*\*: Only essential packages, no "nice-to-have" libraries



\*\*Implementation Details\*\*:

```python

class ProjectScaffolder:

&nbsp;   """

&nbsp;   CRITICAL: Only create essential files.

&nbsp;   

&nbsp;   Template validation rules:

&nbsp;   1. No example/demo code

&nbsp;   2. No placeholder implementations ("pass" functions)

&nbsp;   3. No sample data files

&nbsp;   4. No unnecessary config files

&nbsp;   5. Only required dependencies

&nbsp;   """

&nbsp;   

&nbsp;   def validate\_template\_minimalism(self, template: Dict) -> Tuple\[bool, List\[str]]:

&nbsp;       """

&nbsp;       Validate template follows zero-bloat principle.

&nbsp;       

&nbsp;       Checks:

&nbsp;       - No files with "example" or "demo" in path

&nbsp;       - No dependencies marked as "examples"

&nbsp;       - No TODO/FIXME comments in code

&nbsp;       - All files serve actual purpose

&nbsp;       """

&nbsp;       issues = \[]

&nbsp;       

&nbsp;       # Check file paths

&nbsp;       for file\_path in template\['files'].keys():

&nbsp;           if any(keyword in file\_path.lower() for keyword in \['example', 'demo', 'sample', 'test-data']):

&nbsp;               issues.append(f"Bloat detected: {file\_path} contains example/demo content")

&nbsp;       

&nbsp;       # Check file contents

&nbsp;       for file\_path, content in template\['files'].items():

&nbsp;           if 'TODO:' in content or 'FIXME:' in content:

&nbsp;               issues.append(f"Placeholder detected: {file\_path} contains TODO/FIXME")

&nbsp;           if 'Example usage' in content or 'Sample data' in content:

&nbsp;               issues.append(f"Example code detected: {file\_path} contains examples")

&nbsp;       

&nbsp;       return len(issues) == 0, issues

```



\*\*Template Example\*\* (web-react - CORRECT):

```json

{

&nbsp; "name": "web-react",

&nbsp; "files": {

&nbsp;   "src/App.tsx": "import React from 'react';\\n\\nexport default function App() {\\n  return <div>{{PROJECT\_NAME}}</div>;\\n}",

&nbsp;   "src/main.tsx": "import React from 'react';\\nimport ReactDOM from 'react-dom/client';\\nimport App from './App';\\n\\nReactDOM.createRoot(document.getElementById('root')!).render(<App />);",

&nbsp;   "package.json": "{\\n  \\"name\\": \\"{{PROJECT\_NAME}}\\",\\n  \\"dependencies\\": {\\n    \\"react\\": \\"^18.2.0\\",\\n    \\"react-dom\\": \\"^18.2.0\\"\\n  }\\n}",

&nbsp;   "tsconfig.json": "{ \\"compilerOptions\\": { \\"target\\": \\"ES2020\\", \\"jsx\\": \\"react-jsx\\" } }"

&nbsp; }

}

```



\*\*WRONG - DO NOT CREATE\*\*:

```json

{

&nbsp; "files": {

&nbsp;   "src/examples/TodoExample.tsx": "// Example TODO app",

&nbsp;   "src/components/SampleButton.tsx": "// Sample button component",

&nbsp;   "docs/EXAMPLE.md": "# Example usage",

&nbsp;   "data/sample.json": "{ \\"example\\": \\"data\\" }"

&nbsp; }

}

```



\### 2. Mandatory Planning Phase Before Implementation



\*\*Principle\*\*: ALWAYS plan before coding.



\*\*Requirements\*\*:

\- \*\*Project Context Analysis\*\*: MUST analyze existing codebase before planning (CRITICAL NEW REQUIREMENT)

\- \*\*Automatic Planning\*\*: When user requests a feature, IDE MUST create a plan first

\- \*\*User Approval\*\*: Show plan, get approval before implementation

\- \*\*Plan Structure\*\*: Break down into tasks, estimate complexity, identify dependencies

\- \*\*No Direct Implementation\*\*: Never jump straight to coding

\- \*\*Avoid Duplication\*\*: Check what already exists to prevent duplicating functionality

\- \*\*Prevent Breaking Changes\*\*: Analyze dependencies and integration points



\*\*Implementation Details\*\*:

```python

class ProjectContextAnalyzer:

&nbsp;   """

&nbsp;   CRITICAL: Analyzes existing project before planning.

&nbsp;   

&nbsp;   Must check:

&nbsp;   1. What we already have (existing features, modules, functions)

&nbsp;   2. How it's done (patterns, architecture, coding style)

&nbsp;   3. Dependencies we're using (packages, versions, compatibility)

&nbsp;   4. Integration points (how new feature connects to existing code)

&nbsp;   5. Potential conflicts (duplicate functionality, breaking changes)

&nbsp;   """

&nbsp;   

&nbsp;   def analyze\_project\_context(self, project\_path: Path, feature\_request: str) -> Dict:

&nbsp;       """

&nbsp;       Comprehensive project context analysis.

&nbsp;       

&nbsp;       Returns:

&nbsp;       {

&nbsp;           "existing\_features": List\[Dict],  # Similar existing functionality

&nbsp;           "architecture\_patterns": Dict,     # How things are currently done

&nbsp;           "dependencies": Dict,              # Current dependencies and versions

&nbsp;           "integration\_points": List\[Dict],  # Where new feature connects

&nbsp;           "potential\_conflicts": List\[Dict], # Duplications or breaking changes

&nbsp;           "coding\_standards": Dict,          # Style, patterns used

&nbsp;           "test\_framework": str,             # Testing framework in use

&nbsp;           "recommended\_approach": str        # How to implement consistently

&nbsp;       }

&nbsp;       """

&nbsp;       context = {}

&nbsp;       

&nbsp;       # 1. Scan existing features

&nbsp;       context\['existing\_features'] = self.find\_similar\_features(project\_path, feature\_request)

&nbsp;       

&nbsp;       # 2. Analyze architecture patterns

&nbsp;       context\['architecture\_patterns'] = self.detect\_architecture(project\_path)

&nbsp;       

&nbsp;       # 3. Parse dependencies

&nbsp;       context\['dependencies'] = self.parse\_dependencies(project\_path)

&nbsp;       

&nbsp;       # 4. Find integration points

&nbsp;       context\['integration\_points'] = self.find\_integration\_points(project\_path, feature\_request)

&nbsp;       

&nbsp;       # 5. Detect potential conflicts

&nbsp;       context\['potential\_conflicts'] = self.detect\_conflicts(project\_path, feature\_request, context)

&nbsp;       

&nbsp;       # 6. Extract coding standards

&nbsp;       context\['coding\_standards'] = self.extract\_coding\_standards(project\_path)

&nbsp;       

&nbsp;       # 7. Detect test framework

&nbsp;       context\['test\_framework'] = self.detect\_test\_framework(project\_path)

&nbsp;       

&nbsp;       # 8. Generate recommendations

&nbsp;       context\['recommended\_approach'] = self.generate\_recommendations(context, feature\_request)

&nbsp;       

&nbsp;       return context

&nbsp;   

&nbsp;   def find\_similar\_features(self, project\_path: Path, feature\_request: str) -> List\[Dict]:

&nbsp;       """

&nbsp;       Find existing features similar to the request.

&nbsp;       

&nbsp;       Prevents duplication by identifying:

&nbsp;       - Similar functions/classes

&nbsp;       - Existing implementations

&nbsp;       - Related modules

&nbsp;       """

&nbsp;       similar\_features = \[]

&nbsp;       

&nbsp;       # Use RAG to search semantically

&nbsp;       if self.rag\_retriever:

&nbsp;           search\_results = self.rag\_retriever.retrieve(

&nbsp;               query=feature\_request,

&nbsp;               top\_k=10,

&nbsp;               threshold=0.6

&nbsp;           )

&nbsp;           

&nbsp;           for result in search\_results:

&nbsp;               similar\_features.append({

&nbsp;                   'file': result\['file\_path'],

&nbsp;                   'function': result.get('function\_name'),

&nbsp;                   'description': result.get('docstring'),

&nbsp;                   'similarity': result\['score'],

&nbsp;                   'lines': result.get('line\_numbers')

&nbsp;               })

&nbsp;       

&nbsp;       # Also search by keywords

&nbsp;       keywords = self.extract\_keywords(feature\_request)

&nbsp;       for keyword in keywords:

&nbsp;           results = self.search\_codebase(project\_path, keyword)

&nbsp;           similar\_features.extend(results)

&nbsp;       

&nbsp;       # Deduplicate

&nbsp;       return self.deduplicate\_features(similar\_features)

&nbsp;   

&nbsp;   def detect\_architecture(self, project\_path: Path) -> Dict:

&nbsp;       """

&nbsp;       Detect architectural patterns used in project.

&nbsp;       

&nbsp;       Identifies:

&nbsp;       - MVC, MVVM, Clean Architecture, etc.

&nbsp;       - Folder structure patterns

&nbsp;       - Separation of concerns

&nbsp;       - Common patterns (Repository, Factory, etc.)

&nbsp;       """

&nbsp;       architecture = {

&nbsp;           'pattern': None,

&nbsp;           'structure': {},

&nbsp;           'conventions': \[]

&nbsp;       }

&nbsp;       

&nbsp;       # Detect by folder structure

&nbsp;       folders = self.get\_folder\_structure(project\_path)

&nbsp;       

&nbsp;       if 'models' in folders and 'views' in folders and 'controllers' in folders:

&nbsp;           architecture\['pattern'] = 'MVC'

&nbsp;       elif 'domain' in folders and 'application' in folders and 'infrastructure' in folders:

&nbsp;           architecture\['pattern'] = 'Clean Architecture'

&nbsp;       elif 'src' in folders and 'tests' in folders:

&nbsp;           architecture\['pattern'] = 'Standard Layout'

&nbsp;       

&nbsp;       # Detect design patterns in use

&nbsp;       architecture\['patterns\_used'] = self.detect\_design\_patterns(project\_path)

&nbsp;       

&nbsp;       return architecture

&nbsp;   

&nbsp;   def parse\_dependencies(self, project\_path: Path) -> Dict:

&nbsp;       """

&nbsp;       Parse all project dependencies.

&nbsp;       

&nbsp;       Checks:

&nbsp;       - requirements.txt (Python)

&nbsp;       - package.json (Node.js)

&nbsp;       - Gemfile (Ruby)

&nbsp;       - packages.config (.NET)

&nbsp;       - etc.

&nbsp;       """

&nbsp;       dependencies = {

&nbsp;           'direct': {},

&nbsp;           'dev': {},

&nbsp;           'versions': {},

&nbsp;           'conflicts': \[]

&nbsp;       }

&nbsp;       

&nbsp;       # Python

&nbsp;       req\_file = project\_path / 'requirements.txt'

&nbsp;       if req\_file.exists():

&nbsp;           dependencies\['direct'].update(self.parse\_requirements(req\_file))

&nbsp;       

&nbsp;       # Node.js

&nbsp;       package\_file = project\_path / 'package.json'

&nbsp;       if package\_file.exists():

&nbsp;           pkg\_data = self.parse\_package\_json(package\_file)

&nbsp;           dependencies\['direct'].update(pkg\_data.get('dependencies', {}))

&nbsp;           dependencies\['dev'].update(pkg\_data.get('devDependencies', {}))

&nbsp;       

&nbsp;       # Check for version conflicts

&nbsp;       dependencies\['conflicts'] = self.check\_version\_conflicts(dependencies)

&nbsp;       

&nbsp;       return dependencies

&nbsp;   

&nbsp;   def find\_integration\_points(self, project\_path: Path, feature\_request: str) -> List\[Dict]:

&nbsp;       """

&nbsp;       Find where new feature needs to integrate with existing code.

&nbsp;       

&nbsp;       Identifies:

&nbsp;       - Functions that need to be called

&nbsp;       - Classes that need to be extended

&nbsp;       - APIs that need to be modified

&nbsp;       - Databases tables that need updates

&nbsp;       """

&nbsp;       integration\_points = \[]

&nbsp;       

&nbsp;       # Parse feature request for integration needs

&nbsp;       # Example: "Add JWT authentication" needs to integrate with:

&nbsp;       # - Existing User model

&nbsp;       # - Login/register endpoints

&nbsp;       # - Middleware stack

&nbsp;       

&nbsp;       keywords = self.extract\_integration\_keywords(feature\_request)

&nbsp;       

&nbsp;       for keyword in keywords:

&nbsp;           # Find relevant files/functions

&nbsp;           matches = self.find\_code\_matches(project\_path, keyword)

&nbsp;           integration\_points.extend(matches)

&nbsp;       

&nbsp;       return integration\_points

&nbsp;   

&nbsp;   def detect\_conflicts(self, project\_path: Path, feature\_request: str, context: Dict) -> List\[Dict]:

&nbsp;       """

&nbsp;       Detect potential conflicts and breaking changes.

&nbsp;       

&nbsp;       Checks for:

&nbsp;       - Duplicate functionality

&nbsp;       - Breaking changes to existing APIs

&nbsp;       - Database schema conflicts

&nbsp;       - Dependency conflicts

&nbsp;       """

&nbsp;       conflicts = \[]

&nbsp;       

&nbsp;       # Check for duplicate functionality

&nbsp;       for similar in context.get('existing\_features', \[]):

&nbsp;           if similar\['similarity'] > 0.8:  # Very similar

&nbsp;               conflicts.append({

&nbsp;                   'type': 'potential\_duplication',

&nbsp;                   'severity': 'high',

&nbsp;                   'description': f"Similar functionality exists in {similar\['file']}",

&nbsp;                   'recommendation': f"Consider extending {similar\['function']} instead of creating new"

&nbsp;               })

&nbsp;       

&nbsp;       # Check for API breaking changes

&nbsp;       # (if feature modifies existing functions)

&nbsp;       

&nbsp;       # Check for dependency conflicts

&nbsp;       dep\_conflicts = context.get('dependencies', {}).get('conflicts', \[])

&nbsp;       for conflict in dep\_conflicts:

&nbsp;           conflicts.append({

&nbsp;               'type': 'dependency\_conflict',

&nbsp;               'severity': 'high',

&nbsp;               'description': conflict,

&nbsp;               'recommendation': 'Resolve dependency version before proceeding'

&nbsp;           })

&nbsp;       

&nbsp;       return conflicts

&nbsp;   

&nbsp;   def extract\_coding\_standards(self, project\_path: Path) -> Dict:

&nbsp;       """

&nbsp;       Extract coding standards from existing code.

&nbsp;       

&nbsp;       Identifies:

&nbsp;       - Naming conventions (camelCase, snake\_case, etc.)

&nbsp;       - Docstring style (Google, NumPy, etc.)

&nbsp;       - Import style

&nbsp;       - Error handling patterns

&nbsp;       - Testing patterns

&nbsp;       """

&nbsp;       standards = {

&nbsp;           'naming\_convention': None,

&nbsp;           'docstring\_style': None,

&nbsp;           'import\_style': None,

&nbsp;           'error\_handling': None

&nbsp;       }

&nbsp;       

&nbsp;       # Sample multiple files to detect patterns

&nbsp;       sample\_files = self.get\_sample\_files(project\_path, n=10)

&nbsp;       

&nbsp;       for file in sample\_files:

&nbsp;           # Analyze naming

&nbsp;           naming = self.detect\_naming\_convention(file)

&nbsp;           if naming:

&nbsp;               standards\['naming\_convention'] = naming

&nbsp;               break

&nbsp;       

&nbsp;       # Similar for other standards...

&nbsp;       

&nbsp;       return standards

&nbsp;   

&nbsp;   def detect\_test\_framework(self, project\_path: Path) -> str:

&nbsp;       """

&nbsp;       Detect which test framework is in use.

&nbsp;       

&nbsp;       Returns: 'pytest', 'unittest', 'jest', 'mocha', etc.

&nbsp;       """

&nbsp;       # Check dependencies

&nbsp;       deps = self.parse\_dependencies(project\_path)

&nbsp;       

&nbsp;       if 'pytest' in deps\['direct'] or 'pytest' in deps\['dev']:

&nbsp;           return 'pytest'

&nbsp;       elif 'jest' in deps\['dev']:

&nbsp;           return 'jest'

&nbsp;       elif self.has\_unittest\_imports(project\_path):

&nbsp;           return 'unittest'

&nbsp;       

&nbsp;       return 'unknown'

&nbsp;   

&nbsp;   def generate\_recommendations(self, context: Dict, feature\_request: str) -> str:

&nbsp;       """

&nbsp;       Generate recommendations based on project context.

&nbsp;       

&nbsp;       Returns guidance on:

&nbsp;       - How to implement feature consistently

&nbsp;       - Which patterns to follow

&nbsp;       - Which dependencies to use

&nbsp;       - How to integrate with existing code

&nbsp;       """

&nbsp;       recommendations = \[]

&nbsp;       

&nbsp;       # Architecture recommendation

&nbsp;       if context\['architecture\_patterns']\['pattern']:

&nbsp;           recommendations.append(

&nbsp;               f"Follow {context\['architecture\_patterns']\['pattern']} pattern used in project"

&nbsp;           )

&nbsp;       

&nbsp;       # Dependency recommendation

&nbsp;       if context\['dependencies']\['direct']:

&nbsp;           recommendations.append(

&nbsp;               f"Use existing dependencies where possible: {', '.join(list(context\['dependencies']\['direct'].keys())\[:5])}"

&nbsp;           )

&nbsp;       

&nbsp;       # Integration recommendation

&nbsp;       if context\['integration\_points']:

&nbsp;           recommendations.append(

&nbsp;               f"Integrate with existing: {', '.join(\[p\['description'] for p in context\['integration\_points']\[:3]])}"

&nbsp;           )

&nbsp;       

&nbsp;       # Conflict warnings

&nbsp;       if context\['potential\_conflicts']:

&nbsp;           recommendations.append(

&nbsp;               f"⚠️ Address conflicts: {len(context\['potential\_conflicts'])} potential issues detected"

&nbsp;           )

&nbsp;       

&nbsp;       return "\\n".join(recommendations)





class FeatureDevelopmentOrchestrator:

&nbsp;   """

&nbsp;   CRITICAL: Enforces mandatory planning phase with project context analysis.

&nbsp;   

&nbsp;   Workflow:

&nbsp;   1. User requests feature

&nbsp;   2. IDE analyzes project context (NEW!)

&nbsp;   3. IDE generates comprehensive plan using context

&nbsp;   4. IDE shows plan to user

&nbsp;   5. User approves/modifies plan

&nbsp;   6. IDE implements according to plan

&nbsp;   """

&nbsp;   

&nbsp;   def \_\_init\_\_(self):

&nbsp;       self.context\_analyzer = ProjectContextAnalyzer()

&nbsp;       self.llm = LLMInterface()

&nbsp;       self.project\_manager = ProjectManager()

&nbsp;       

&nbsp;   def develop\_feature(self, user\_request: str, project\_path: Path) -> Dict:

&nbsp;       """

&nbsp;       Main entry point for feature development.

&nbsp;       

&nbsp;       NEVER implements directly - ALWAYS analyzes context and plans first.

&nbsp;       """

&nbsp;       # Step 1: Analyze project context (CRITICAL NEW STEP)

&nbsp;       print("Analyzing project context...")

&nbsp;       context = self.context\_analyzer.analyze\_project\_context(project\_path, user\_request)

&nbsp;       

&nbsp;       # Step 2: Analyze request with context

&nbsp;       analysis = self.analyze\_request(user\_request, context)

&nbsp;       

&nbsp;       # Step 3: Generate plan (MANDATORY) with context awareness

&nbsp;       plan = self.generate\_plan(analysis, context)

&nbsp;       

&nbsp;       # Step 4: Show plan to user (MANDATORY)

&nbsp;       user\_approved = self.present\_plan\_for\_approval(plan, context)

&nbsp;       

&nbsp;       if not user\_approved:

&nbsp;           return {"status": "cancelled", "reason": "User did not approve plan"}

&nbsp;       

&nbsp;       # Step 5: Execute plan (only after approval)

&nbsp;       result = self.execute\_plan(plan, context)

&nbsp;       

&nbsp;       return result

&nbsp;   

&nbsp;   def generate\_plan(self, analysis: Dict, context: Dict) -> Dict:

&nbsp;       """

&nbsp;       Generate comprehensive implementation plan using project context.

&nbsp;       

&nbsp;       Returns:

&nbsp;       {

&nbsp;           "feature\_name": str,

&nbsp;           "description": str,

&nbsp;           "context\_summary": Dict,           # NEW: Context analysis summary

&nbsp;           "reuse\_existing": List\[Dict],      # NEW: Existing code to reuse

&nbsp;           "tasks": \[...],

&nbsp;           "dependencies": \[...],

&nbsp;           "potential\_issues": \[...],

&nbsp;           "estimated\_total\_time": str,

&nbsp;           "testing\_strategy": str

&nbsp;       }

&nbsp;       """

&nbsp;       # Use LLM to generate comprehensive plan WITH context

&nbsp;       prompt = f"""

&nbsp;       Create a detailed implementation plan for this feature request:

&nbsp;       

&nbsp;       Feature Request: {analysis\['description']}

&nbsp;       

&nbsp;       PROJECT CONTEXT (CRITICAL - MUST CONSIDER):

&nbsp;       

&nbsp;       Existing Similar Features:

&nbsp;       {json.dumps(context.get('existing\_features', \[]), indent=2)}

&nbsp;       

&nbsp;       Current Architecture: {context.get('architecture\_patterns', {}).get('pattern', 'Unknown')}

&nbsp;       

&nbsp;       Current Dependencies:

&nbsp;       {json.dumps(list(context.get('dependencies', {}).get('direct', {}).keys()), indent=2)}

&nbsp;       

&nbsp;       Integration Points:

&nbsp;       {json.dumps(context.get('integration\_points', \[]), indent=2)}

&nbsp;       

&nbsp;       Potential Conflicts:

&nbsp;       {json.dumps(context.get('potential\_conflicts', \[]), indent=2)}

&nbsp;       

&nbsp;       Coding Standards: {context.get('coding\_standards', {})}

&nbsp;       Test Framework: {context.get('test\_framework', 'unknown')}

&nbsp;       

&nbsp;       Recommendations:

&nbsp;       {context.get('recommended\_approach', 'None')}

&nbsp;       

&nbsp;       Requirements for the plan:

&nbsp;       1. Break into atomic tasks (each <30 min)

&nbsp;       2. REUSE existing code where possible (don't duplicate!)

&nbsp;       3. Follow existing architecture and patterns

&nbsp;       4. Use existing dependencies (don't add unnecessary new ones)

&nbsp;       5. Integrate with existing code properly

&nbsp;       6. Address all potential conflicts

&nbsp;       7. Specify testing requirements using detected framework

&nbsp;       8. Note potential issues and breaking changes

&nbsp;       9. Estimate total time realistically

&nbsp;       

&nbsp;       Output as JSON with structure:

&nbsp;       {{

&nbsp;           "feature\_name": "...",

&nbsp;           "description": "...",

&nbsp;           "context\_summary": {{

&nbsp;               "similar\_existing": \[...],

&nbsp;               "architecture\_to\_follow": "...",

&nbsp;               "dependencies\_to\_use": \[...]

&nbsp;           }},

&nbsp;           "reuse\_existing": \[

&nbsp;               {{

&nbsp;                   "file": "existing/file.py",

&nbsp;                   "component": "ExistingClass",

&nbsp;                   "how\_to\_use": "Extend this class instead of creating new"

&nbsp;               }}

&nbsp;           ],

&nbsp;           "tasks": \[...],

&nbsp;           "dependencies": \["only new dependencies if absolutely necessary"],

&nbsp;           "potential\_issues": \[...],

&nbsp;           "estimated\_total\_time": "X hours",

&nbsp;           "testing\_strategy": "Use {context.get('test\_framework')} framework..."

&nbsp;       }}

&nbsp;       """

&nbsp;       

&nbsp;       plan\_json = self.llm.generate(prompt)

&nbsp;       plan = json.loads(plan\_json)

&nbsp;       

&nbsp;       # Validate plan quality and context awareness

&nbsp;       self.validate\_plan\_quality(plan, context)

&nbsp;       

&nbsp;       return plan

&nbsp;   

&nbsp;   def present\_plan\_for\_approval(self, plan: Dict, context: Dict) -> bool:

&nbsp;       """

&nbsp;       Present plan to user and get approval.

&nbsp;       

&nbsp;       Shows:

&nbsp;       - Feature description

&nbsp;       - Task list with estimates

&nbsp;       - Files affected

&nbsp;       - Dependencies needed

&nbsp;       - Potential issues

&nbsp;       

&nbsp;       Returns: True if approved, False otherwise

&nbsp;       """

&nbsp;       print("\\n" + "="\*60)

&nbsp;       print("IMPLEMENTATION PLAN")

&nbsp;       print("="\*60)

&nbsp;       print(f"\\nFeature: {plan\['feature\_name']}")

&nbsp;       print(f"Description: {plan\['description']}")

&nbsp;       print(f"\\nEstimated Time: {plan\['estimated\_total\_time']}")

&nbsp;       print(f"\\nTasks ({len(plan\['tasks'])}):\\n")

&nbsp;       

&nbsp;       for i, task in enumerate(plan\['tasks'], 1):

&nbsp;           print(f"  {i}. {task\['description']}")

&nbsp;           print(f"     Time: {task\['estimated\_time']} | Complexity: {task\['complexity']}")

&nbsp;           print(f"     Files: {', '.join(task\['files\_affected'])}")

&nbsp;           if task\['dependencies']:

&nbsp;               print(f"     Depends on: {', '.join(task\['dependencies'])}")

&nbsp;           print()

&nbsp;       

&nbsp;       if plan.get('potential\_issues'):

&nbsp;           print("Potential Issues:")

&nbsp;           for issue in plan\['potential\_issues']:

&nbsp;               print(f"  ⚠️  {issue}")

&nbsp;           print()

&nbsp;       

&nbsp;       print("="\*60)

&nbsp;       response = input("\\nApprove this plan? (yes/no/modify): ").lower()

&nbsp;       

&nbsp;       if response == 'yes':

&nbsp;           return True

&nbsp;       elif response == 'modify':

&nbsp;           # Allow user to modify plan

&nbsp;           modified\_plan = self.allow\_plan\_modification(plan)

&nbsp;           return self.present\_plan\_for\_approval(modified\_plan)

&nbsp;       else:

&nbsp;           return False

```



\*\*CLI Integration\*\* (Enhanced with Context Analysis):

```bash

\# User requests feature

> feature add "JWT authentication"



\# IDE analyzes project context FIRST (NEW!)

Analyzing project context...



Project Context Analysis:

\- Found similar feature: session\_auth in auth/sessions.py (75% similar)

\- Architecture: MVC pattern detected

\- Current auth: Session-based (Flask-Session)

\- Dependencies: Flask 2.3.0, Flask-Session 0.5.0

\- Integration points: User model, login endpoints, middleware

\- Potential conflicts: 1 detected

&nbsp; ⚠️  Existing session-based auth may conflict



Generating implementation plan...



========================================

IMPLEMENTATION PLAN (Context-Aware)

========================================



Feature: JWT Authentication

Estimated Time: 2.5 hours (reduced by reusing existing code)



Context Summary:

\- Reuse: Extend existing User model

\- Follow: MVC pattern (current architecture)

\- Use: Existing Flask setup, add PyJWT only

\- Integrate: With current login/register endpoints



Existing Code to Reuse:

&nbsp; 1. models/user.py - User model (extend with token fields)

&nbsp; 2. routes/auth.py - Auth endpoints (modify for JWT)

&nbsp; 3. middleware/auth\_middleware.py - Auth checking (adapt for JWT)



Tasks (7):  # Reduced from 8 by reusing code

&nbsp; 1. Install PyJWT dependency

&nbsp;    Time: 5 min | Complexity: low

&nbsp;    Note: Only new dependency needed

&nbsp; 

&nbsp; 2. Extend User model with token fields

&nbsp;    Time: 10 min | Complexity: low

&nbsp;    Files: models/user.py (MODIFY existing, don't create new)

&nbsp;    Reuse: Existing User model structure

&nbsp; 

&nbsp; 3. Create JWT utility functions

&nbsp;    Time: 15 min | Complexity: medium

&nbsp;    Files: utils/jwt.py (NEW)

&nbsp;    Follow: Existing utils pattern

&nbsp; 

&nbsp; 4. Adapt authentication middleware for JWT

&nbsp;    Time: 25 min | Complexity: medium

&nbsp;    Files: middleware/auth\_middleware.py (MODIFY existing)

&nbsp;    Reuse: Existing middleware structure

&nbsp; 

&nbsp; 5. Update login endpoint to return JWT

&nbsp;    Time: 20 min | Complexity: medium

&nbsp;    Files: routes/auth.py (MODIFY existing)

&nbsp;    Reuse: Existing endpoint structure

&nbsp; 

&nbsp; 6. Write tests using pytest

&nbsp;    Time: 30 min | Complexity: medium

&nbsp;    Files: tests/test\_jwt\_auth.py

&nbsp;    Follow: Existing pytest patterns

&nbsp; 

&nbsp; 7. Update API documentation

&nbsp;    Time: 15 min | Complexity: low

&nbsp;    Files: docs/API.md



Dependencies:

&nbsp; New: PyJWT==2.8.0

&nbsp; Reuse: Flask, Flask-Session (no removal, backward compatible)



Potential Issues:

&nbsp; ⚠️  Existing session-based auth will coexist with JWT

&nbsp;     Resolution: Support both methods for backward compatibility

&nbsp; 

&nbsp; ⚠️  Need to handle token expiration gracefully

&nbsp;     Plan: Add refresh token mechanism



Testing Strategy:

&nbsp; Use pytest (detected framework)

&nbsp; - Unit tests for JWT functions

&nbsp; - Integration tests for auth endpoints

&nbsp; - Test both session and JWT auth methods



Architecture Compliance:

&nbsp; ✔ Follows MVC pattern

&nbsp; ✔ Reuses existing User model

&nbsp; ✔ Integrates with existing routes

&nbsp; ✔ Maintains backward compatibility



========================================



Approve this plan? (yes/no/modify): 

```



\### 3. Autonomous Task Execution with Context Management



\*\*Principle\*\*: Handle arbitrarily complex tasks autonomously.



\*\*Requirements\*\*:

\- \*\*Recursive Task Decomposition\*\*: Break large tasks into manageable sub-tasks

\- \*\*Context Summarization\*\*: Summarize completed work to save context

\- \*\*Progress Tracking\*\*: Maintain state across long executions

\- \*\*Smart Context Window\*\*: Keep only relevant context active

\- \*\*Autonomous Execution\*\*: No human intervention needed during execution



\*\*Implementation Details\*\*:

```python

class AutonomousTaskExecutor:

&nbsp;   """

&nbsp;   CRITICAL: Executes arbitrarily complex tasks autonomously.

&nbsp;   

&nbsp;   Key features:

&nbsp;   1. Recursive task decomposition (break big tasks into small)

&nbsp;   2. Context management (summarize and checkpoint)

&nbsp;   3. State persistence (resume from failures)

&nbsp;   4. Progress tracking (know what's done, what's next)

&nbsp;   """

&nbsp;   

&nbsp;   def \_\_init\_\_(self, max\_context\_tokens: int = 4000):

&nbsp;       self.max\_context\_tokens = max\_context\_tokens

&nbsp;       self.task\_state = TaskState()  # Persistent state

&nbsp;       self.context\_manager = SmartContextManager()

&nbsp;       

&nbsp;   def execute\_task\_list(self, tasks: List\[Dict], parent\_task\_id: Optional\[str] = None):

&nbsp;       """

&nbsp;       Execute a list of tasks autonomously.

&nbsp;       

&nbsp;       Handles:

&nbsp;       - Long task lists (100+ tasks)

&nbsp;       - Complex tasks requiring decomposition

&nbsp;       - Context overflow (summarize and continue)

&nbsp;       - Failures (checkpoint and retry)

&nbsp;       """

&nbsp;       for task in tasks:

&nbsp;           # Check if task needs decomposition

&nbsp;           if self.is\_task\_too\_complex(task):

&nbsp;               # Decompose recursively

&nbsp;               subtasks = self.decompose\_task(task)

&nbsp;               task\['status'] = 'decomposed'

&nbsp;               task\['subtasks'] = subtasks

&nbsp;               self.task\_state.save()

&nbsp;               

&nbsp;               # Execute subtasks recursively

&nbsp;               self.execute\_task\_list(subtasks, parent\_task\_id=task\['id'])

&nbsp;               

&nbsp;           else:

&nbsp;               # Execute atomic task

&nbsp;               self.execute\_atomic\_task(task)

&nbsp;           

&nbsp;           # Manage context after each task

&nbsp;           self.manage\_context\_window(task)

&nbsp;           

&nbsp;           # Checkpoint progress

&nbsp;           self.task\_state.checkpoint()

&nbsp;   

&nbsp;   def is\_task\_too\_complex(self, task: Dict) -> bool:

&nbsp;       """

&nbsp;       Determine if task needs decomposition.

&nbsp;       

&nbsp;       Criteria:

&nbsp;       - Estimated time > 30 minutes

&nbsp;       - Complexity = 'high' or 'very high'

&nbsp;       - Multiple files affected (>3)

&nbsp;       - Multiple dependencies

&nbsp;       - Description contains 'and' (indicates multiple sub-goals)

&nbsp;       """

&nbsp;       complexity\_scores = {'low': 1, 'medium': 2, 'high': 3, 'very high': 4}

&nbsp;       

&nbsp;       is\_complex = (

&nbsp;           task.get('estimated\_time\_minutes', 0) > 30 or

&nbsp;           complexity\_scores.get(task.get('complexity', 'medium'), 2) >= 3 or

&nbsp;           len(task.get('files\_affected', \[])) > 3 or

&nbsp;           len(task.get('dependencies', \[])) > 2 or

&nbsp;           ' and ' in task\['description'].lower()

&nbsp;       )

&nbsp;       

&nbsp;       return is\_complex

&nbsp;   

&nbsp;   def decompose\_task(self, task: Dict) -> List\[Dict]:

&nbsp;       """

&nbsp;       Decompose complex task into atomic subtasks.

&nbsp;       

&nbsp;       Uses LLM to intelligently break down task.

&nbsp;       

&nbsp;       Example:

&nbsp;       Task: "Implement user authentication system"

&nbsp;       

&nbsp;       Decomposed into:

&nbsp;       1. Create User model

&nbsp;       2. Implement password hashing

&nbsp;       3. Create login endpoint

&nbsp;       4. Create registration endpoint

&nbsp;       5. Add authentication middleware

&nbsp;       6. Write tests for auth system

&nbsp;       7. Update documentation

&nbsp;       """

&nbsp;       prompt = f"""

&nbsp;       Decompose this task into atomic subtasks:

&nbsp;       

&nbsp;       Task: {task\['description']}

&nbsp;       Complexity: {task.get('complexity', 'unknown')}

&nbsp;       Estimated Time: {task.get('estimated\_time', 'unknown')}

&nbsp;       

&nbsp;       Requirements for subtasks:

&nbsp;       1. Each subtask takes <30 minutes

&nbsp;       2. Each subtask is atomic (single file or operation)

&nbsp;       3. Each subtask has clear completion criteria

&nbsp;       4. Subtasks are ordered by dependencies

&nbsp;       5. Include testing subtask

&nbsp;       6. Include documentation subtask

&nbsp;       

&nbsp;       Output as JSON array: \[{{

&nbsp;           "id": "subtask-1",

&nbsp;           "description": "Create User model in models/user.py",

&nbsp;           "estimated\_time\_minutes": 15,

&nbsp;           "complexity": "medium",

&nbsp;           "files\_affected": \["models/user.py"],

&nbsp;           "dependencies": \[],

&nbsp;           "completion\_criteria": "User model created with all required fields"

&nbsp;       }}]

&nbsp;       """

&nbsp;       

&nbsp;       subtasks\_json = self.llm.generate(prompt)

&nbsp;       subtasks = json.loads(subtasks\_json)

&nbsp;       

&nbsp;       # Assign parent ID

&nbsp;       for subtask in subtasks:

&nbsp;           subtask\['parent\_task\_id'] = task\['id']

&nbsp;       

&nbsp;       return subtasks

&nbsp;   

&nbsp;   def manage\_context\_window(self, completed\_task: Dict):

&nbsp;       """

&nbsp;       Manage context to avoid overflow.

&nbsp;       

&nbsp;       Strategy:

&nbsp;       1. Summarize completed tasks

&nbsp;       2. Keep only last N tasks in full detail

&nbsp;       3. Keep only relevant file contents

&nbsp;       4. Evict old context periodically

&nbsp;       """

&nbsp;       # Get current context size

&nbsp;       current\_tokens = self.context\_manager.estimate\_tokens()

&nbsp;       

&nbsp;       if current\_tokens > self.max\_context\_tokens \* 0.8:  # 80% threshold

&nbsp;           # Summarize old context

&nbsp;           summary = self.summarize\_completed\_work()

&nbsp;           

&nbsp;           # Replace detailed context with summary

&nbsp;           self.context\_manager.replace\_old\_context\_with\_summary(summary)

&nbsp;           

&nbsp;           # Log context management action

&nbsp;           self.log\_context\_management("Summarized context", current\_tokens, summary)

&nbsp;   

&nbsp;   def summarize\_completed\_work(self) -> str:

&nbsp;       """

&nbsp;       Create concise summary of completed tasks.

&nbsp;       

&nbsp;       Example summary:

&nbsp;       """

&nbsp;       Completed work summary:

&nbsp;       - Created User model with email, password\_hash, created\_at fields

&nbsp;       - Implemented JWT utility functions (generate\_token, verify\_token)

&nbsp;       - Added authentication middleware that validates JWT tokens

&nbsp;       - Created login endpoint (POST /api/auth/login)

&nbsp;       - Created registration endpoint (POST /api/auth/register)

&nbsp;       - Tests written and passing (15/15)

&nbsp;       - Documentation updated with auth endpoints

&nbsp;       

&nbsp;       Current state:

&nbsp;       - Authentication system fully functional

&nbsp;       - All tests passing

&nbsp;       - Ready for integration with other features

&nbsp;       """

&nbsp;       

&nbsp;       completed\_tasks = self.task\_state.get\_completed\_tasks()

&nbsp;       

&nbsp;       prompt = f"""

&nbsp;       Create a concise summary of completed work:

&nbsp;       

&nbsp;       Completed tasks:

&nbsp;       {json.dumps(completed\_tasks, indent=2)}

&nbsp;       

&nbsp;       Summary should include:

&nbsp;       1. What was accomplished

&nbsp;       2. Key files modified/created

&nbsp;       3. Current state

&nbsp;       4. Any important notes for future tasks

&nbsp;       

&nbsp;       Keep it under 500 words.

&nbsp;       """

&nbsp;       

&nbsp;       summary = self.llm.generate(prompt)

&nbsp;       return summary

&nbsp;   

&nbsp;   def execute\_atomic\_task(self, task: Dict):

&nbsp;       """

&nbsp;       Execute a single atomic task.

&nbsp;       

&nbsp;       Atomic task: Small enough to complete in one go (<30 min).

&nbsp;       """

&nbsp;       try:

&nbsp;           # Log task start

&nbsp;           self.log\_task\_start(task)

&nbsp;           

&nbsp;           # Build context for this specific task

&nbsp;           context = self.context\_manager.build\_task\_context(task)

&nbsp;           

&nbsp;           # Determine task type and execute

&nbsp;           if 'create' in task\['description'].lower():

&nbsp;               result = self.execute\_create\_task(task, context)

&nbsp;           elif 'modify' in task\['description'].lower() or 'update' in task\['description'].lower():

&nbsp;               result = self.execute\_modify\_task(task, context)

&nbsp;           elif 'test' in task\['description'].lower():

&nbsp;               result = self.execute\_test\_task(task, context)

&nbsp;           elif 'document' in task\['description'].lower():

&nbsp;               result = self.execute\_document\_task(task, context)

&nbsp;           else:

&nbsp;               result = self.execute\_generic\_task(task, context)

&nbsp;           

&nbsp;           # Mark task as complete

&nbsp;           task\['status'] = 'completed'

&nbsp;           task\['result'] = result

&nbsp;           self.task\_state.mark\_complete(task\['id'])

&nbsp;           

&nbsp;           # Log task completion

&nbsp;           self.log\_task\_complete(task, result)

&nbsp;           

&nbsp;       except Exception as e:

&nbsp;           # Handle failure

&nbsp;           task\['status'] = 'failed'

&nbsp;           task\['error'] = str(e)

&nbsp;           self.task\_state.mark\_failed(task\['id'], str(e))

&nbsp;           self.log\_task\_failed(task, e)

&nbsp;           

&nbsp;           # Decide whether to retry or skip

&nbsp;           if self.should\_retry(task, e):

&nbsp;               self.retry\_task(task)

&nbsp;           else:

&nbsp;               raise





class SmartContextManager:

&nbsp;   """

&nbsp;   Manages context window intelligently.

&nbsp;   

&nbsp;   Features:

&nbsp;   1. Prioritize recent and relevant information

&nbsp;   2. Summarize old information

&nbsp;   3. Evict least relevant content when full

&nbsp;   4. Track what's in context vs what's summarized

&nbsp;   """

&nbsp;   

&nbsp;   def \_\_init\_\_(self):

&nbsp;       self.active\_context = \[]  # Full detailed context

&nbsp;       self.summarized\_context = \[]  # Summaries of old context

&nbsp;       self.context\_index = {}  # Quick lookup

&nbsp;   

&nbsp;   def build\_task\_context(self, task: Dict) -> str:

&nbsp;       """

&nbsp;       Build optimal context for a specific task.

&nbsp;       

&nbsp;       Includes:

&nbsp;       1. Task description and requirements

&nbsp;       2. Relevant file contents

&nbsp;       3. Related completed tasks

&nbsp;       4. Project structure (if relevant)

&nbsp;       5. User-defined rules

&nbsp;       """

&nbsp;       context\_parts = \[]

&nbsp;       

&nbsp;       # 1. Task information

&nbsp;       context\_parts.append(f"Task: {task\['description']}")

&nbsp;       if task.get('completion\_criteria'):

&nbsp;           context\_parts.append(f"Completion Criteria: {task\['completion\_criteria']}")

&nbsp;       

&nbsp;       # 2. Relevant files

&nbsp;       for file\_path in task.get('files\_affected', \[]):

&nbsp;           if self.file\_exists(file\_path):

&nbsp;               content = self.load\_file\_content(file\_path)

&nbsp;               context\_parts.append(f"\\nFile: {file\_path}\\n```\\n{content}\\n```")

&nbsp;       

&nbsp;       # 3. Related tasks

&nbsp;       related\_tasks = self.find\_related\_tasks(task)

&nbsp;       if related\_tasks:

&nbsp;           context\_parts.append("\\nRelated completed tasks:")

&nbsp;           for related in related\_tasks:

&nbsp;               context\_parts.append(f"- {related\['description']} (completed)")

&nbsp;       

&nbsp;       # 4. Summarized context (old work)

&nbsp;       if self.summarized\_context:

&nbsp;           context\_parts.append("\\nPreviously completed work:")

&nbsp;           context\_parts.append(self.summarized\_context\[-1])  # Most recent summary

&nbsp;       

&nbsp;       # 5. User rules (always include)

&nbsp;       user\_rules = self.get\_user\_rules()

&nbsp;       if user\_rules:

&nbsp;           context\_parts.append("\\nUser-defined rules:")

&nbsp;           context\_parts.append(user\_rules)

&nbsp;       

&nbsp;       return "\\n\\n".join(context\_parts)





class TaskState:

&nbsp;   """

&nbsp;   Maintains persistent state of task execution.

&nbsp;   

&nbsp;   Allows:

&nbsp;   1. Resume from failures

&nbsp;   2. Track progress

&nbsp;   3. Generate reports

&nbsp;   4. Rollback if needed

&nbsp;   """

&nbsp;   

&nbsp;   def \_\_init\_\_(self, state\_file: Path = Path('data/task\_state.json')):

&nbsp;       self.state\_file = state\_file

&nbsp;       self.load\_state()

&nbsp;   

&nbsp;   def save(self):

&nbsp;       """Save current state to disk."""

&nbsp;       with open(self.state\_file, 'w') as f:

&nbsp;           json.dump(self.state, f, indent=2)

&nbsp;   

&nbsp;   def checkpoint(self):

&nbsp;       """Create a checkpoint for rollback."""

&nbsp;       checkpoint\_file = self.state\_file.parent / f'checkpoint\_{int(time.time())}.json'

&nbsp;       with open(checkpoint\_file, 'w') as f:

&nbsp;           json.dump(self.state, f, indent=2)

&nbsp;   

&nbsp;   def get\_progress(self) -> Dict:

&nbsp;       """Get current progress statistics."""

&nbsp;       completed = len(\[t for t in self.state\['tasks'] if t\['status'] == 'completed'])

&nbsp;       failed = len(\[t for t in self.state\['tasks'] if t\['status'] == 'failed'])

&nbsp;       pending = len(\[t for t in self.state\['tasks'] if t\['status'] == 'pending'])

&nbsp;       total = len(self.state\['tasks'])

&nbsp;       

&nbsp;       return {

&nbsp;           'completed': completed,

&nbsp;           'failed': failed,

&nbsp;           'pending': pending,

&nbsp;           'total': total,

&nbsp;           'progress\_percent': (completed / total \* 100) if total > 0 else 0

&nbsp;       }

```



\*\*CLI Usage Example\*\*:

```bash

\# User requests complex feature

> feature add "Complete e-commerce checkout system with payment processing, order management, email notifications, and admin dashboard"



Analyzing request...

This is a complex feature. Creating detailed plan...



Generated plan with 47 tasks.

Estimated time: 12-15 hours



========================================

IMPLEMENTATION PLAN

========================================



Phase 1: Database Schema (8 tasks, ~2 hours)

Phase 2: Payment Integration (12 tasks, ~4 hours)

Phase 3: Order Management (15 tasks, ~4 hours)

Phase 4: Email System (6 tasks, ~1.5 hours)

Phase 5: Admin Dashboard (6 tasks, ~2 hours)



Approve? (yes/no): yes



Starting execution...



Phase 1: Database Schema

\[1/8] Creating Order model... ✅ (3m 15s)

\[2/8] Creating Payment model... ✅ (2m 45s)

\[3/8] Creating OrderItem model... ✅ (2m 30s)

\[4/8] Creating relationships... ✅ (4m 10s)

\[5/8] Writing migrations... ✅ (3m 5s)

\[6/8] Running migrations... ✅ (45s)

\[7/8] Writing model tests... ✅ (8m 20s)

\[8/8] Testing models... ✅ (1m 30s)



Phase 1 complete! (26m 15s)

Progress: 8/47 tasks (17%)



Context summarized. Continuing...



Phase 2: Payment Integration

\[9/47] Installing payment SDK... ✅ (1m 10s)

\[10/47] Creating PaymentService... ✅ (6m 45s)

...



\[continuing autonomously through all 47 tasks]



========================================

FEATURE COMPLETE

========================================



Completed: 47/47 tasks (100%)

Total time: 13h 42m

Tests passing: 89/89

Documentation: Updated



Feature "Complete e-commerce checkout system" is ready!

```



\### Integration with Existing System



These principles integrate with existing components:



\*\*Existing TaskManager\*\* (Phase 1-9):

```python

\# Enhance existing TaskManager

class TaskManager:

&nbsp;   def \_\_init\_\_(self):

&nbsp;       # Add new components

&nbsp;       self.autonomous\_executor = AutonomousTaskExecutor()

&nbsp;       self.feature\_orchestrator = FeatureDevelopmentOrchestrator()

&nbsp;   

&nbsp;   def execute\_task(self, task\_description: str):

&nbsp;       # OLD WAY: Direct execution

&nbsp;       # return self.\_execute\_directly(task\_description)

&nbsp;       

&nbsp;       # NEW WAY: Plan -> Approve -> Execute

&nbsp;       return self.feature\_orchestrator.develop\_feature(task\_description)

```



\*\*Project Initialization\*\* (Phase 10):

```python

class ProjectInitializer:

&nbsp;   def \_\_init\_\_(self):

&nbsp;       self.bloat\_validator = BloatValidator()

&nbsp;   

&nbsp;   def create\_from\_template(self, template: Dict, dest: Path):

&nbsp;       # Validate zero-bloat principle

&nbsp;       is\_minimal, issues = self.bloat\_validator.validate(template)

&nbsp;       if not is\_minimal:

&nbsp;           raise ValueError(f"Template violates zero-bloat principle: {issues}")

&nbsp;       

&nbsp;       # Proceed with creation

&nbsp;       ...

```



