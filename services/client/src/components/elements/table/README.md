# Table

**Version:** 1.0.0

## Usage

```react
import React, { Component } from 'react'
import Table from '../../elements/table'

class App extends Component {
  render() {
    const data = [
      {
        firstName: 'Dalton',
        lastName: 'Le'
      },
      {
        firstName: 'Harry',
        lastName: 'Potter'
      },
    ]

    return (
      <div>
        <Table
          data={data}
          columns={[
            {
              Header: "First name",
              accessor: "firstName"
            },
            {
              Header: "Last name",
              accessor: "lastName"
            }
          ]}
          defaultPageSize={data.length}
          showPageSizeOptions={false}
          showPagination={false}
          className="-highlight"
        />
      </div>
    )
  }
}
```
