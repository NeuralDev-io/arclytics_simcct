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
      size="large"
    >
      Delete entire app
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

#### `size`: string

One of <`default` | `small` | `large`>

Size of the button. Default is `default`.

#### `isDisabled`: boolean



#### `isLoading`: boolean



#### `onClick`: func

