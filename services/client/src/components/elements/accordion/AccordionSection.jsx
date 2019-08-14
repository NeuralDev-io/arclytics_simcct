import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import ChevronUpIcon from 'react-feather/dist/icons/chevron-up'
import ChevronDownIcon from 'react-feather/dist/icons/chevron-down'

import styles from './AccordionSection.module.scss'

class AccordionSection extends PureComponent {
  render() {
    const {
      children,
      title,
      expanded,
      id,
      onToggle,
    } = this.props
    const sectionId = `section-${id}`
    const labelId = `label-${id}`

    return (
      <>
        <div
          className={styles.title}
          role="button"
          aria-expanded={expanded}
          aria-controls={sectionId}
          id={labelId}
          tabIndex={0}
          onClick={onToggle}
          onKeyDown={(e) => {
            switch (e.key) {
              case ' ':
              case 'Enter':
                onToggle()
                break
              default:
            }
          }}
        >
          <h4>{title}</h4>
          {expanded ? (
            <ChevronUpIcon />
          ) : (
            <ChevronDownIcon />
          ) }
        </div>
        <div
          role="region"
          aria-labelledby={labelId}
          id={sectionId}
          hidden={!expanded}
        >
          {expanded && children}
        </div>
      </>
    )
  }
}

AccordionSection.propTypes = {
  children: PropTypes.instanceOf(Object).isRequired,
  id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  title: PropTypes.string.isRequired,
  expanded: PropTypes.bool,
  onToggle: PropTypes.func,
}

AccordionSection.defaultProps = {
  expanded: false,
  onToggle: () => {},
}

export default AccordionSection
