# Modal

**Version:** 1.2.0

## Usage

```react
import React, { Component } from 'react'
import Modal from '~/components/elements/modal'

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      show: false
    }
  }

  handleClose = () => this.setState({ show: false })

  handleShow = () => this.setState({ show: true })

  render() {
    <div>
      <Modal show={this.state.show} onClose={this.handleClose}>
        <div>
          <span>This is a modal!</span>
          <button onClick={this.handleClose}>Close</button>
        </div>
      </Modal>
      <button onClick={this.handleShow}>Open</button>
    </div>
  }
}
```

## Props

#### `show` : bool (Required)

Boolean variable to show or hide modal.

#### `className` : string

Pass className to override styling.

#### `onClose`: func

Set this prop to a function that sets `show` to `false`. It will be called when the backdrop is clicked.

#### `withCloseIcon` : bool

Whether or not to include an 'x' icon to close the modal.

# AttachModal

**Version:** 1.0.1

## Usage

```react
import React, { Component } from 'react'
import { AttachModal } from '.../modal'

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      show: false
    }
  }

  handleClose = () => this.setState({ show: false })

  handleShow = () => this.setState({ show: true })

  render() {
    <div>
      <AttachModal
        visible={this.state.show}
        onClose={this.handleClose}
        onShow={this.handleShow}
        position="topRight"
        overlap={false}
      >
        <span>Click me to open modal</span>
        <div>
          <span>This is a modal!</span>
          <button onClick={this.handleClose}>Close</button>
        </div>
      </AttachModal>
    </div>
}
```

## Props

#### `visible` : bool (Required)

Boolean variable to show or hide modal.

#### `className` : string

Pass className to override styling.

#### `onClose`: func

Set this prop to a function that sets `visible` to `false`. It will be called when anything outside the popup is clicked.

#### `onShow`: func

Set this prop to a function that sets `visible` to `true`. It will be called when the first child of the AttachModal is clicked.

#### `position`: string

One of <'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight'>

Default is `'bottomLeft'`.

#### `overlap`: bool

Prop to set if the modal is going to overlap the interactive element

Default is `true`.

# ToastModal

**Version:** 1.0.0

## Usage

This example code displays the ToastModal after the app has been used for 5 seconds.

```react
import React, { Component } from 'react'
import { ToastModal } from '.../modal'

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      show: false
    }
  }

  componentDidMount = () => {
    this.timer = setTimeout(() => {
      this.setState({ show: true })
    }, 5000)
  }

  componentWillUnmount = () => {
    if (this.timer) {
      clearTimeout(this.timer)
      this.timer = 0
    }
  }

  handleClose = () => this.setState({ show: false })

  render() {
    <div>
      <ToastModal
        show={this.state.show}
      >
        <div>
          <span>This is an announcement!</span>
          <button onClick={this.handleClose}>Close</button>
        </div>
      </ToastModal>
    </div>
}
```

## Props

#### `show` : bool (Required)

Boolean variable to show or hide modal.

#### `className` : object `{ container: string, modal: string }`

Pass className to override styling.

#### `withCloseIcon`: bool

Whether or not to add an 'x' icon to close the modal. Default to `false`. If `true`, the `onClose` prop is also required.

#### `onClose`: func

Set this prop to a function that sets `show` to `false`. It will be called when the close icon is clicked.