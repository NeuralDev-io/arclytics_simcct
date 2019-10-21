# Accordion

**Version:** 1.0.0

## Usage

```react
import Accordion, { AccordionSection } from '.../accordion'

export const App = () => (
  <div>
    <Accordion defaultExpand={0}>
      <AccordionSection title="Section1" id="sect1">
        {...}
      </AccordionSection>
    </Accordion>
  </div>
)
```

## Accordion Props

#### `defaultExpand`: number

The index of the section that is expanded by default.

## AccordionSection Props

#### `title`: string

Title of the section, will be displayed next to the toggle button

#### `id`: string

ID of this secton

