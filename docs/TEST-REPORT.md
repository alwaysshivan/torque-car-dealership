# Validation report

Date: 25 October 2026. Environment: Linux, Python 3.12, Node.js 24.

## Automated results

| Check | Result | Evidence |
|---|---|---|
| Backend pytest suite | 26 passed | backend-tests.txt, backend-junit.xml |
| Backend statement coverage | 99% (rounded) | coverage.xml; backend-tests.txt |
| Frontend Vitest suite | 5 passed in 2 files | frontend-tests.txt |
| React production build | Passed | build-output.txt |

Coverage excludes test files and includes all backend production modules and the CLI. The three uncovered statements are a defensive secret-file creation race handler and the CLI module entry-point call. Coverage measures executed statements, not correctness or all possible branches. The installed Starlette version emits a deprecation warning for its httpx-based TestClient; the test suite still passes.

## What was verified

- Registration stores salted password hashes and never returns passwords.
- Case-insensitive duplicate email handling; strict validation; role-injection rejection.
- Login, profile access, missing/malformed/expired/forged tokens, deleted accounts.
- Account data survives closing/recreating the app against the same on-disk file.
- Persistent JWT signing secret, external-secret validation, invalid password hashes.
- Protected routes and server-side administrator restrictions.
- Vehicle create/read/update/delete, search, price ranges, and literal SQL wildcard handling.
- Stock purchase/restock operations, zero/negative/fractional/boolean quantity rejection.
- Concurrent purchases do not oversell; receipts are private to the purchaser.
- Missing IDs, inventory summaries, stock ceiling, sort validation.
- Trusted admin CLI, hidden password prompts, confirmation, duplicate accounts, idempotent seeding.
- Frontend zero-stock disabled button, correct vehicle purchase callback, role-based controls.
- Frontend sign-in/registration navigation and network error feedback.

## Browser review and limits

The actual React sign-in and registration screens were opened in the managed browser and visually checked. Screenshots are in `screenshots/`. The initial Vite host restriction was fixed by allowing the observed managed-preview host.

The separate browser-preview container could not execute the project's Python virtual environment. Consequently the integrated authenticated dashboard, admin forms, and purchase flow were **not browser-tested**. They are covered at API/component level, with a local walkthrough checklist below. No synthetic results are reported as browser checks.

Windows batch startup, macOS startup, Docker build, GitHub push, and live deployment were not executed in this environment. Startup scripts and Docker configuration are provided. All automated results above were obtained using the local Linux runtime.

## Local walkthrough checklist

1. Launch the app, create an admin with the CLI, and seed sample inventory.
2. Sign in as admin; add/edit/delete a disposable listing and restock another listing.
3. Search by make/model, select a category, set a price range, and test both view modes.
4. Register a regular account and verify admin controls are absent.
5. Purchase one unit, verify its new stock count and your receipt in My purchases.
6. Verify the zero-stock vehicle's button is disabled; use API docs to confirm an oversell returns 409.
7. Sign out/in and restart the app; verify account, vehicle, and receipt persistence.
8. Use a narrow/mobile viewport and keyboard navigation; check dialog focus and Escape behavior.
9. Save dashboard/purchase screenshots for the submission README.

## Test-first evidence

`tdd-auth-red.txt`, `tdd-auth-green.txt`, `tdd-inventory-red.txt`, `tdd-inventory-green.txt`, and `tdd-frontend-red.txt` are actual earlier run outputs. The Git history has test-first, implementation, and refactor commits with AI co-author trailers. Early logs reflect dependencies/test-secret strings at the time of those runs; current tests use appropriately sized test secrets.
