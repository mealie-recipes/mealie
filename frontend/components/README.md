# Components Folder Guide

## Domain Components
Domain Components are specific to the domain or section of a website. For example if you have an admin page and a user page that have specific, unshared elements. These can be placed in the Domain/Admin folder. 

**Rules**
- Components should be prefixed with their domain name
  - Examples: AdminDashboard, AdminSettings, UserProfile

## Global Components
This folder is for widely reused components that provide little functionality and are primarily used for styling or consistency. Primary examples are Card and Button components.

**Rules**
- Global components cannot container a subfolder to be globally imported
- All elements should start with the 'Base' Prefix
  - Examples: BaseButton, BaseCard, BaseTitleSection

## Layout Components
The layout folder is for reusable components that are specifically **only** used in the layouts for the Nuxt Application. They may take props or may not. They should be larger layout style components that don't have wide the ability to be widely reused in the application.

**Rules:**
- Layout folder should not have a subfolder 
- If they take props they should start with a 'App' Prefix. 
  - Examples: AppSidebar, AppHeader, AppFooter.
- If they do not they should begin with the 'The' prefix
  - Examples: TheSidebar, TheHeader, TheFooter.

## Page Components
The Page folder is dedicated to 'single-use' component to break up large amounts on content in the pages themselves. A good examples of this is breaking your landing page into separate sections to make it more readable and less monolithic. Page components typically consume other components.

**Rules:**
- These are *last resort* components. Only to be used when the page becomes unmanageable. 
- Page components should be prefixed with their page name
  - Examples: HomeAbout, HomeContact, ClientProfile

