import React from 'react'
import i18next from 'i18next'
import markdown from './assets/live-demo-contents.md?raw'
import { MDXEditor } from '..'
import { ALL_PLUGINS } from './_boilerplate'

const sl = {
  toolbar: {
    undo: 'Razveljavi {{shortcut}}',
    redo: 'Uveljavi {{shortcut}}',
    blockTypeSelect: {
      selectBlockTypeTooltip: 'Izberi vrsto bloka',
      placeholder: 'Vrsta bloka'
    },

    blockTypes: {
      paragraph: 'Odstavek',
      heading: 'Naslov',
      quote: 'Citat'
    }
  }
}

const es = {
  toolbar: {
    undo: "Deshacer {{shortcut}}",
    redo: "Rehacer {{shortcut}}",
    blockTypeSelect: {
      selectBlockTypeTooltip: 'Selecciona el tipo de bloque',
      placeholder: 'Tipo de bloque'
    },

    blockTypes: {
      paragraph: 'Párrafo',
      heading: 'Encabezado {{level}}',
      quote: 'Cita'
    }
  }
}

void i18next.init({
  lng: 'en', // if you're using a language detector, do not define the lng option
  debug: true,
  resources: {
    sl: {
      translation: sl
    },
    es: {
      translation: es
      }
    }
})

export const Example = () => {
  return (
    <MDXEditor
      translation={(key, defaultValue, interpolations) => {
        return i18next.t(key, defaultValue, interpolations) as string
      }}
      markdown={markdown}
      onChange={(md) => {
        console.log('change', { md })
      }}
      plugins={ALL_PLUGINS}
    />
  )
}
