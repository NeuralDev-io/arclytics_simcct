// Helper functions to improve accessibility

/**
 *
 * This function takes a handler function and returns an object with role, mouse and
 * keyboard listeners. Spread this object in a clickable div to make it more accessible.
 *
 * Read more: ARIA button role
 *
 * The 'button' role should be used for clickable elements that trigger a response when
 * activated by the user. Adding role="button" will make an element appear as a button
 * control to a screen reader. This role can be used in combination with the aria-pressed
 * attribute to create toggle buttons.
 *
 * (https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles)
 * @param {function} handler
 */
export const buttonize = handler => ({ // eslint-disable-line import/prefer-default-export
  role: 'button',
  tabIndex: '0', // to make element tabbable
  onClick: handler,
  onKeyDown: (e) => {
    // only trigger response on key Enter
    if (e.keyCode === 13) handler(e)
  },
})
