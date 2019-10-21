# Checkbox

**Version:** 1.0.0

## Usage

```react
import React from 'react'
import Checkbox from '.../checkbox'

class App extends React.Component {
  constructor() {
    this.state = {
      autoCalc: false,
    }
  }

  render() {
    const { autoCalc } = this.state
    return (
      <div>
        <Checkbox
          name="autoCalc"
          onChange={val => this.setState({ autoCalc: val })}
          isChecked={autoCalc}
          label="Auto-calculate"
        />
      </div>
    )
  }
}
```

## Checkbox Props

#### `name`: string

Input name

#### `onChange`: func

(val) => {...}

#### `className`: string

Add a classname to the checkbox.

#### `isChecked`: bool

#### `label`: string

Input label.

#### `isDisabled`: boolean

