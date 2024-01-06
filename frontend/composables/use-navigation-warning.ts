export function useNavigationWarning() {
    return { activateNavigationWarning, deactivateNavigationWarning };
}

/**
 * Displays a warning before the user navigates to another page
 * e.g., by clicking a link (which isn't internal and rendered without page load),
 * reloading the page,
 * or closing the tab.
 */
const activateNavigationWarning = () => {
    console.log("ACTIVATE");
    window.onbeforeunload = () => true;
}

/**
 * Disables the warning when navigating to a page
 */
const deactivateNavigationWarning = () => {
    console.log("deACTIVATE");
    window.onbeforeunload = null;
}
