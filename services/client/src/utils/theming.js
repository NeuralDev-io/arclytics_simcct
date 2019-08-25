export const getColor = color => getComputedStyle(document.documentElement).getPropertyValue(color)

export const changeTheme = (name) => {
  document.documentElement.setAttribute('data-theme', name)
}
