import { BaseBoxShapeUtil, HTMLContainer, RecordProps, T, TLBaseShape } from 'tldraw'

////////////////////////////////

type IToDoItem = TLBaseShape<
	'todo-item',
	{
		id: number
        w: number,
		h: number,
		checked: boolean
		text: string
	}
>

export class ToDoItem extends BaseBoxShapeUtil<IToDoItem> {
	static override type = 'todo-item' as const
	static override props: RecordProps<IToDoItem> = {
		id: T.number,
        w: T.number,
		h: T.number,
		checked: T.boolean,
		text: T.string,
	}

	getDefaultProps(): IToDoItem['props'] {
		return {
            id: 1,
			w: 230,
			h: 50,
			checked: false,
			text: '',
		}
	}

	component(shape: IToDoItem) {
		return (
			<div
				style={{
					padding: 16,
					height: shape.props.h,
					width: shape.props.w,

					pointerEvents: 'all',
					//backgroundColor: '#efefef',
					overflow: 'hidden',
				}}
			>
				<input
					type="checkbox"
					checked={shape.props.checked}
					onChange={() =>
						this.editor.updateShape<IToDoItem>({
							id: shape.id,
							type: 'todo-item',
							props: { checked: !shape.props.checked },
						})
					}

					onPointerDown={(e) => e.stopPropagation()}
					onTouchStart={(e) => e.stopPropagation()}
					onTouchEnd={(e) => e.stopPropagation()}
				/>
				<input
					type="text"
					placeholder="Enter a todo..."
					readOnly={shape.props.checked}
					value={shape.props.text}
					onChange={(e) =>
						this.editor.updateShape<IToDoItem>({
							id: shape.id,
							type: 'todo-item',
							props: { text: e.currentTarget.value },
						})
					}

					onPointerDown={(e) => {
						if (!shape.props.checked) {
							e.stopPropagation()
						}
					}}
					onTouchStart={(e) => {
						if (!shape.props.checked) {
							e.stopPropagation()
						}
					}}
					onTouchEnd={(e) => {
						if (!shape.props.checked) {
							e.stopPropagation()
						}
					}}
				/>
			</div>
		)
	}

	indicator(shape: IToDoItem) {
		return <rect width={shape.props.w} height={shape.props.h} />
	}
}


////////////////////////////////

type IToDoShape = TLBaseShape<
	'todo-shape',
	{
		w: number
		h: number
		checked: boolean
		text: string
	}
>

export class ToDoShape extends BaseBoxShapeUtil<IToDoShape> {
	static override type = 'todo-shape' as const
	static override props: RecordProps<IToDoShape> = {
		w: T.number,
		h: T.number,
		checked: T.boolean,
		text: T.string,
	}

	getDefaultProps(): IToDoShape['props'] {
		return {
			w: 230,
			h: 230,
			checked: false,
			text: '',
		}
	}

	component(shape: IToDoShape) {
		return (
			<HTMLContainer
				style={{
					padding: 16,
					height: shape.props.h,
					width: shape.props.w,

					pointerEvents: 'all',
					backgroundColor: '#efefef',
					overflow: 'hidden',
				}}
			>
				<input
					type="checkbox"
					checked={shape.props.checked}
					onChange={() =>
						this.editor.updateShape<IToDoShape>({
							id: shape.id,
							type: 'todo-shape',
							props: { checked: !shape.props.checked },
						})
					}

					onPointerDown={(e) => e.stopPropagation()}
					onTouchStart={(e) => e.stopPropagation()}
					onTouchEnd={(e) => e.stopPropagation()}
				/>
				<input
					type="text"
					placeholder="Enter a todo..."
					readOnly={shape.props.checked}
					value={shape.props.text}
					onChange={(e) =>
						this.editor.updateShape<IToDoShape>({
							id: shape.id,
							type: 'todo-shape',
							props: { text: e.currentTarget.value },
						})
					}

					onPointerDown={(e) => {
						if (!shape.props.checked) {
							e.stopPropagation()
						}
					}}
					onTouchStart={(e) => {
						if (!shape.props.checked) {
							e.stopPropagation()
						}
					}}
					onTouchEnd={(e) => {
						if (!shape.props.checked) {
							e.stopPropagation()
						}
					}}
				/>
			</HTMLContainer>
		)
	}

	indicator(shape: IToDoShape) {
		return <rect width={shape.props.w} height={shape.props.h} />
	}
}
