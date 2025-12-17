# Mealie 2.0 Migration Assistant

## 1. Executive Summary

**Mealie 2.0** is a complete architectural rewrite of the frontend for the self-hosted recipe manager _Mealie_. While the original application offers robust backend functionality, the current Vue.js frontend suffers from dated UX patterns and client-side performance bottlenecks.

This project aims to decouple the frontend, migrating it to **Next.js 14 (App Router)** to leverage Server-Side Rendering (SSR), React Server Actions, and a modern Design System, all while maintaining 100% compatibility with the existing Python API.

## 2. Project Structure & Boundaries (CRITICAL)

- **ROOT:** `/` (Monorepo root).
- **SOURCE OF TRUTH (Read-Only):**
  - `frontend/` -> The legacy Vue.js application. Use this to understand business logic and API shapes. **NEVER MODIFY THIS.**
  - `mealie/` -> The Python Backend. Use this to verify API endpoints/schemas. **NEVER MODIFY THIS.**
- **TARGET (Work Area):**
  - `frontend-next/` -> The new Next.js 14 App Router application. **ONLY WRITE CODE HERE.**

## 3. Workflow (The "Golden Loop")

We follow a strict **"Plan (Notion) -> Task (Linear) -> Code (VS Code)"** lifecycle.

1.  **Notion Specs:** Features are first defined in Notion "Functional Specs".
    - _AI Implication:_ If I ask about a complex feature, remind me to check the Notion Spec first.
2.  **Linear Tickets:** All coding work must be tied to a Linear Ticket.
    - _AI Implication:_ Expect a **Ticket Context** (ID + Description) at the start of every prompt.
3.  **Traceability:**
    - Git Commits must reference the Ticket ID (e.g., `feat: login page [MEL-12]`).
    - PRs must link to the Linear Ticket.

## 4. Context Awareness & Migration Strategy

- **The "Strangler" Pattern:** We are rebuilding features one by one (Vertical Slices).
- **Translation:**
  - When asked to build a feature, **FIRST** check `frontend/` to see how it was done in Vue.
  - **Translate** Vue concepts (Options API, Vuex) to Next.js concepts (Server Actions, React Server Components, Zustand/React Query).

## 5. Tech Stack (Target)

| Layer         | Choice                           | Reasoning                                           |
| :------------ | :------------------------------- | :-------------------------------------------------- |
| **Framework** | **Next.js 14**                   | App Router, Server Actions, and API Proxying.       |
| **Styling**   | **Tailwind CSS + Shadcn**        | Rapid UI development with accessible primitives.    |
| **State**     | **React Query / Server Actions** | Moving data fetching off the client.                |
| **Auth**      | **HttpOnly Cookies**             | Secure session management (replacing LocalStorage). |

## 6. Authentication Strategy (Critical)

- **Standard/LDAP:** Uses the standard JSON login endpoint. LDAP users use the same form as local users.
- **OIDC:**
  1.  **Discovery:** On app load, fetch `/api/app/about` to check `oidc_auth_enabled` and `oidc_provider_name`.
  2.  **Trigger:** If enabled, render a "Login with [Provider]" button.
  3.  **Flow:** Button redirects to backend OIDC endpoint.
  4.  **Callback:** IdP redirects back to `/login?code=...`. The Login Page must exchange this code for a token via the backend (Server Action).
