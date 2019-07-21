# Select

**Version:** 1.0.0

## Usage

```react
import React, { Component } from 'react'
import Select from '~/components/elements/select'

class App extends Component {
  constructor(props) {
    super(props)
    this.state{
      show: world;
    }
  }

  handleChange = () => {
    this.state.show ? this.setState({show: false}) : this.setState({show: true}) 
  }

  render() {
    <Modal show={this.state.show} clicked={this.handleChange} >
      <button onClick={this.handleChange}>Close</button>
    </Modal>
      <button onClick={this.handleChange}> Open </button>
  }
}
```

## Props

#### `show` : bool (isRequired)

Boolean variable to show or hide modal.

#### `className` : string

Name of className

#### `clicked` : func

For when the user clicks on the backdrop to exit the modal. 