export const activateNavigationWarning = () => {
    window.onbeforeunload = () => true;
}

export const deactivateNavigationWarning = () => {
    window.onbeforeunload = null;
}
