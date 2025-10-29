import React from 'react'
import { DiffSourceToggleWrapper, MDXEditor, MDXEditorMethods, UndoRedo, diffSourcePlugin, headingsPlugin, toolbarPlugin } from '../'
import { useRef } from 'react'

export function GetMarkdownInSourceMode() {
  const ref = useRef<MDXEditorMethods>(null)
  return (
    <div className="App">
      <MDXEditor
        ref={ref}
        onChange={(md) => {
          console.log('change', md)
        }}
        markdown="Hello world"
        plugins={[diffSourcePlugin({ viewMode: 'source' })]}
      />
      <button
        onClick={() => {
          console.log(ref.current?.getMarkdown())
        }}
      >
        Get Markdown
      </button>
    </div>
  )
}

export function ChangeDiffMarkdown() {
  const ref = useRef<MDXEditorMethods>(null)
  const [diffMarkdown, setDiffMarkdown] = React.useState('foo')
  const [markdown] = React.useState('Hello world')
  console.log(`rendering`, markdown)
  return (
    <div className="App">
      <button
        onClick={() => {
          setDiffMarkdown('bar')
        }}
      >
        Change Diff Markdown
      </button>
      <MDXEditor
        ref={ref}
        onChange={(md) => {
          console.log('change', md)
        }}
        markdown={markdown}
        plugins={[
          diffSourcePlugin({ diffMarkdown }),
          toolbarPlugin({
            toolbarContents: () => (
              <DiffSourceToggleWrapper>
                <UndoRedo />
              </DiffSourceToggleWrapper>
            )
          })
        ]}
      />
      <button
        onClick={() => {
          console.log(ref.current?.getMarkdown())
        }}
      >
        Get Markdown
      </button>
      <button
        onClick={() => {
          setDiffMarkdown('q')
          ref.current?.setMarkdown('moo')
        }}
      >
        Set Markdown to moo
      </button>
    </div>
  )
}

const markdown = `# Hello, Diff Mode!
This line is unchanged`

const oldMarkdown = `# Hello, World!
This line is unchanged`

export function ReadOnlyDiffMode() {
  const ref = useRef<MDXEditorMethods>(null)
  return (
    <div className="App">
      <MDXEditor
        ref={ref}
        markdown={markdown}
        plugins={[
          headingsPlugin(),
          diffSourcePlugin({
            viewMode: 'diff',
            readOnlyDiff: true,
            diffMarkdown: oldMarkdown
          })
        ]}
      />
      <button
        onClick={() => {
          console.log(ref.current?.getMarkdown())
        }}
      >
        Get Markdown
      </button>
    </div>
  )
}
