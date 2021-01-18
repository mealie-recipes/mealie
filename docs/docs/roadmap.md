# Development Road Map

!!! Current Release
    v0.1.0 BETA - This is technically a pre-release, as such take care to backup data and be aware that breaking changes in future releases are a real possibility.


Feature placement is not set in stone. This is much more of a guideline than anything else.

## v x.x.x - No planned target, but eventually...

### Frontend
- [ ] Login / Logout Navigation
    * [ ] Initial Page
    * [ ] Logic / Function Calls
    * [ ] Password Reset
### Backend
- [ ] Image Minification
- [ ] User Setup
    * [ ] Authentication
    * [ ] Default Admin/Superuser Account
    * [ ] Password Reset
    * [ ] User Accounts
    * [ ] Edit / Delete

## v0.2.0 - Targets


!!! error "MAJOR BREAKING CHANGE"
        MongoDB will no longer be supported as of v0.2.0. Review the database migration page for details on migration to SQL (It's very easy)

## New Features
### Frontend
- [ ] Advanced search
    - [ ] Category Filter
    - [ ] Tag Filter
    - [x] Fuzzy Search
- [ ] Backup card redesign
- [ ] Additional Backup / Import Features
    - [ ] Import Recipes Force/Rebase options
    - [ ] Upload .zip file
- [ ] Improved Color Picker
- [ ] Meal Plan redesign
### Backend
- [ ] PostgreSQL Support
- [ ] Setup SQL Migrations

## Breaking Changes
- MongoDB support dropped
## Code Chores
- [x] Remove MongoDB Interface Code
- [ ] Dockerfile Trim
