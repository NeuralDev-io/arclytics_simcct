# Select

**Version:** 1.0.0

## Usage

```react
import React, { Component } from 'react'
import Select from '~/components/elements/select'

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      colourOptions: [
        { label: 'red', value: 'go' },
        { label: 'green', value: 'stop' },
      ],
      selected: null,
    }
  }

  handleChange = (val) => {
    this.setState({
      selected: val,
    })
  }

  render() {
    const { colourOptions, selected } = this.state
    return (
      <div>
        <Select
          name="colour"
          placeholder="Choose colour"
          options={colourOptions}
          value={selected}
          length="long"
          onChange={val => this.handleChange(val)}
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

A single argument is the new value object.

#### `options`: array



#### `value`: object

```
Object {
  label: string,
  value: string
}
```

#### `defaultValue`: object

