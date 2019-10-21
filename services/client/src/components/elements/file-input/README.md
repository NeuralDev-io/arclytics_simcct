# FileInput

**Version:** 1.0.0

> Note: Disabling option for FileInput coming soon...

## Usage

```react
import React from 'react'
import UploadIcon from '.../icons'
import FileInput from '.../file-input'

class App extends React.Component {
  handleInputChange = (e) => {
    const file = e.target.files[0]
    // do something with the file
  }

  render() {
    return (
      <div>
        <FileInput
          name="import_simulation"
          Icon={props => <UploadIcon {...props} />}
          onChange={this.handleFileInputChange}
          filename={filename}
        />
      </div>
    )
  }
}
```

## Checkbox Props

#### `name`: string (Required)

Input name

#### `onChange`: func (Required)

(val) => {...}

#### `className`: string

Add a classname to the checkbox.

#### `placeholder`: string

Default is `'Choose a file'`.

#### `Icon`: node

Add icon to file input.

#### `filename`: string

Set a filename to the file input display when a file is chosen. If this is blank the input will display the placeholder instead

