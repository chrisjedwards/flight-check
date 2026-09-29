# Phase 3: Completion

## Finalizing the Project

### Removing unused code

Before the final phase, I cleaned up the frontend. The first version had a continent dropdown and an "Only upcoming" checkbox. They were replaced by the search box and the quick filters, but some code for them was still left. Unused code makes the project harder to read and can hide real mistakes, so I searched the whole frontend for code, CSS classes, and element IDs that were no longer used.

| File                    | Removed                                                             | Why it was unused                                                                                  |
| ----------------------- | ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `frontend/js/app.js`    | `CONTINENT_ORDER`                                                   | Sort order for the old continent dropdown; never read                                              |
| `frontend/js/app.js`    | Lookups of `#continent-select` and `#upcoming-only`                 | The elements no longer exist, so both lookups returned `null` and were never used                  |
| `frontend/index.html`   | IDs `arrivals-tab`, `departures-tab`, and `quick-filters`           | Not referenced by JavaScript, CSS, or ARIA attributes; the code finds these elements by `data-` attributes and classes |
| `frontend/css/style.css`| The `.btn-primary` rule                                             | No element in the page uses the class, and no commit ever did                                      |
| `frontend/css/style.css`| Variables `--primary-text` and `--primary-hover-bg` in both themes  | Only used by the removed `.btn-primary` rule                                                       |

I also fixed uneven indentation in the `elements` object in `app.js`. All remaining functions, element lookups, CSS classes, CSS variables, and IDs are in use.

### Fixing the browser theme color

The `theme-color` meta tag tells mobile browsers which color to use for their toolbar. It was still `#e9f0eb`, a light green from the first design, which matched neither theme. Now it follows the active theme: `#0B2545` for Nordic sky and `#111418` for Departure board.

- The small script at the top of the page head sets the color together with the theme, so it is correct from the first moment.
- `applyTheme()` in `app.js` updates it when the user switches theme.
- The default value in the HTML is `#0B2545`, so the Nordic sky color is used if the script cannot run.

### Checking the cleanup

- A browser test checked both themes at desktop (1280 px) and mobile (390 px) width: arrivals and departures, all four quick filters, search, the time filter and Now button, Clear filters, and the details panel (click, Enter, Escape, and focus return). The "Showing X of Y" numbers matched counts calculated directly from the API data. All 117 checks passed.
- The theme color was correct on page load and changed when the theme was switched.
- There were no console errors, no duplicate HTML IDs, no horizontal scrolling on mobile, and still no `innerHTML`.
- All 25 backend tests passed (`cd backend && python -m pytest -q`).

## Testing

<!-- Document tests performed and their results. -->

## Improvements & Optimization

<!-- Record improvements and optimization opportunities. -->

## Deployment / Presentation

<!-- Describe how the project is deployed or presented. -->

## Problems & Solutions

<!-- Record completion-phase problems and how they were addressed. -->
