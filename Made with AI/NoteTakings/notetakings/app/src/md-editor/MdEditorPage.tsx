// TODO: Add messages page
import { AuthUser } from "wasp/auth"
import {MDXEditor} from '../mdxeditor';
import {
  diffSourcePlugin,
  markdownShortcutPlugin,
  AdmonitionDirectiveDescriptor,
  DirectiveDescriptor,
  directivesPlugin,
  frontmatterPlugin,
  headingsPlugin,
  imagePlugin,
  linkDialogPlugin,
  linkPlugin,
  listsPlugin,
  quotePlugin,
  tablePlugin,
  thematicBreakPlugin,
  toolbarPlugin,
  SandpackConfig,
  codeBlockPlugin,
  codeMirrorPlugin,
  sandpackPlugin,
  KitchenSinkToolbar
} from '../mdxeditor'
import '../mdxeditor/style.css';

function MdEditor({user} : {user: AuthUser}) {

  return (
    <MDXEditor markdown={'# Hello World'} contentEditableClassName="prose" plugins={[
      toolbarPlugin({ toolbarContents: () => <KitchenSinkToolbar /> }),
      listsPlugin(),
      quotePlugin(),
      headingsPlugin({ allowedHeadingLevels: [1, 2, 3] }),
      linkPlugin(),
      linkDialogPlugin(),
      imagePlugin({
        imageAutocompleteSuggestions: ['https://via.placeholder.com/150', 'https://via.placeholder.com/150'],
        imageUploadHandler: async () => Promise.resolve('https://picsum.photos/200/300')
      }),
      tablePlugin(),
      thematicBreakPlugin(),
      frontmatterPlugin(),
      codeBlockPlugin({ defaultCodeBlockLanguage: '' }),
      //sandpackPlugin({ sandpackConfig: virtuosoSampleSandpackConfig }),
      //codeMirrorPlugin({ codeBlockLanguages: { js: 'JavaScript', css: 'CSS', txt: 'Plain Text', tsx: 'TypeScript', '': 'Unspecified' } }),
      codeMirrorPlugin({ codeBlockLanguages: { '': 'Unspecified', js: 'JavaScript', jsx: 'JavaScript (React)', ts: 'TypeScript', tsx: 'TypeScript (React)', html: 'HTML', css: 'CSS', c: 'C', cpp: 'C++', csharp: 'C#', sql: 'SQL', pgsql: 'PQSQL', mysql: 'MySQL', 
         python: 'Python', shell: 'Shell', powershell: 'Powershell', java: 'Java', php: 'PHP', go: 'GO', rust: 'Rust', dockerfile: 'Dockerfile', http: 'HTTP', json: 'JSON', yaml: 'YAML', toml: 'TOLM', xml: 'XML', markdown: 'Markdown', 
         nix: 'NiX', vb: 'VB', vbscript: 'VBScript', lua: 'Lua', shader: 'Shader', kotlin: 'Kotlin', q: 'Q', r: 'R', cmake: 'CMake', txt: 'Plain Text' }, autoLoadLanguageSupport: true }),
      //directivesPlugin({ directiveDescriptors: [YoutubeDirectiveDescriptor, AdmonitionDirectiveDescriptor] }),
      directivesPlugin({ directiveDescriptors: [AdmonitionDirectiveDescriptor] }),
      diffSourcePlugin({ viewMode: 'rich-text' }),
      markdownShortcutPlugin()
    ]} />
  )
}

export default MdEditor
