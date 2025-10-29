import React from 'react'
import * as RadixPopover from '@radix-ui/react-popover'
import { editorRootElementRef$ } from '..'
import styles from '../../../styles/ui.module.css'
import { useCellValue } from '@mdxeditor/gurx'

export const PopoverPortal = (props: RadixPopover.PopoverPortalProps) => {
  const editorRootElementRef = useCellValue(editorRootElementRef$)
  return <RadixPopover.Portal {...props} container={editorRootElementRef?.current} />
}

export const PopoverContent = React.forwardRef<any, React.ComponentProps<typeof RadixPopover.Content>>(
  (props: React.ComponentProps<typeof RadixPopover.Content>, ref) => {
    return (
      <RadixPopover.Content {...props} className={styles.popoverContent} sideOffset={5} side="top" ref={ref}>
        <span className={styles.popoverArrow}>
          <RadixPopover.Arrow />
        </span>
        {props.children}
      </RadixPopover.Content>
    )
  }
)
