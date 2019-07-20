# Button

**Version:** 1.0.0

Styling support for buttons with icons coming soon...

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

One of <`default` | `outline` | `text` | `dangerous` | `warning`>

The base styling for the button. Default is `default`.

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
