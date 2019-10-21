# Button

**Version:** 1.0.0

## Usage

```react
import Button from './button'

export const App = () => (
  <div>
    <Button onClick={() => console.log("clicked")}>
      Click me
    </Button>
    <Button
      appearance="dangerous"
      onClick={() => console.log("danger!")}
      length="long"
    >
      Delete entire app
    </Button>
  </div>
)
```

## Button Props

#### `appearance`: string

One of <`default` | `outline` | `text`>

The base styling for the button. Default is `default`.

#### `color`: string

One of <`dangerous` | `warning`>

Color of the button, default is `default` (ARC500), `dangerous` is R400 and `warning` is O400.

#### `className`: string

Add a classname to the button.

#### `type`: string

One of <`button` | `submit` | `reset`>

Button type. Default is `button`.

#### `length`: string

One of <`default` | `small` | `large`>

Length of the button. Default is `default`.

#### `isDisabled`: boolean

#### `isLoading`: boolean

If `isLoading` is true, Button will render a spinner instead of button name.

#### `onClick`: func

#### `IconComponent`: node

To add icon to button.

Example

```react
import React from 'react'
import DisapproveIcon from './icons'
import Button from '.../button'
...

export MyComponent = () => (
  <Button
    appearance="dangerous"
    onClick={() => console.log("danger!")}
    IconComponent={props => <DisapproveIcon {...props} />}
  />
)
```

Note that `props` has to be passed in for the icon to be styled properly.

# IconButton

**Version:** 1.0.0

Styling support for buttons with icons coming soon...

## Usage

```react
import { IconButton } from '.../button'
import XIcon from './icons'

export const App = () => (
  <div>
    <IconButton
      onClick={() => {}}
      Icon={props => <XIcon {...props}>}
      withTooltip
      tooltipText="Close"
    />
  </div>
)
```

## Button Props

#### `className`: object `{ button: string, icon: string }`

Add a classname to the button to override styling.

#### `isDisabled`: boolean

#### `onClick`: func (required)

#### `withTooltip`: boolean

Add a tooltip for the button to increase usability. If this is set to true, the next 2 props are required to set a tooltip.

Default is `false`.

#### `tooltipText`: string

Button name. Default is `'Click me'`.

#### `tooltipPosition`: string

Position of the tooltip. One of <'bottom' | 'right' | 'top' | 'left'>

Default is `'right'`.

#### `Icon`: node

Icon to be used for button.

Note that `props` has to be passed in for the icon to be styled properly.


