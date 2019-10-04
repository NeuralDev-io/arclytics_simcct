/**
 * Copyright 2019, NeuralDev.
 * All rights reserved.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * AccordionSection component for each section in an Accordion
 *
 * @version 1.0.0
 * @author Andrew Che, Dalton Le
 */
import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import ChevronUpIcon from 'react-feather/dist/icons/chevron-up'
import ChevronDownIcon from 'react-feather/dist/icons/chevron-down'
import { buttonize } from '../../../utils/accessibility'

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
      <React.Fragment>
        <div
          className={styles.title}
          role="button"
          aria-expanded={expanded}
          aria-controls={sectionId}
          id={labelId}
          {...buttonize(onToggle)}
        >
          <h6>{title}</h6>
          <div className={styles.icons}>
            <ChevronDownIcon className={`${styles.icon} ${expanded ? styles.hidden : ''}`} />
            <ChevronUpIcon className={`${styles.icon} ${!expanded ? styles.hidden : ''}`} />
          </div>
        </div>
        <div
          className={styles.childrenContainer}
          role="region"
          aria-labelledby={labelId}
          id={sectionId}
          hidden={!expanded}
        >
          {expanded && children}
        </div>
      </React.Fragment>
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
