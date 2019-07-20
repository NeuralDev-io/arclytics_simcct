# Select

**Version:** 1.0.0

## Usage

```react
import React, { Component } from 'react'
import Select from '~/components/elements/select'

class App extends Component {
  constructor(props) {
    
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

#### `name` : string (required)

Name of select element.