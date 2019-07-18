# Text field

**Version:** 1.0.0

## Usage

```react
import React, { Component } from 'react'
import TextField from '~components/elements/textfield'

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      value: undefined,
    }
  }

  handleChange = (val) => {
    this.setState({
      value: val,
    })
  }

  render() {
    const { value } = this.state
    return (
      <div>
        <TextField
          type="text"
          name="random"
          onChange={e => this.handleChange(e)}
          value={value}
          length="short"
        />
      </div>
    )
  }
}
```

## Props

#### `name`: string (required)

Name of select element.

#### `className`: string

Add a classname to the select element.

#### `length`: string

One of <`default` | `short` | `long` | `stretch`>

#### `placeholder`: string



#### `isDisabled`: boolean



#### `onChange`: func (required)

A single argument is the new value of the text field.

#### `value`: string



