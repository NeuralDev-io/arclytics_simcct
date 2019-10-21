# Tooltip

**Version:** 1.0.0

## Usage

```react
import React, { Component } from 'react'
import InfoIcon from '...'
import Tooltip from '~components/elements/Tooltip'

const App = () => (
  <Tooltip>
    <InfoIcon>
    <p>This will be display in the tooltip</p>
  </Tooltip>
)
```

## Props

#### `position`: string. 'top' | 'right' | 'bottom' | 'left'

Position of the tooltip. Default is `'bottom'`.

#### `className`: object. `{ container: string, tooltip: string }`

Class name to override styling.
