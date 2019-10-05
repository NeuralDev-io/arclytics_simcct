/**
 * Get a colour variable from CSS
 * @param {string} color colour variable name
 */
export const getColor = color => getComputedStyle(document.documentElement).getPropertyValue(color)

/**
 * Change the data-theme attribute of html element.
 * @param {string} name name of the theme
 */
export const changeTheme = (name) => {
  document.documentElement.setAttribute('data-theme', name)
}
