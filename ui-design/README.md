# Dambulla AgriFlow — UI direction 01

Open `index.html` in a browser to review 25 linked design screens. Each file in `screens/` is self-contained HTML with inline CSS and editable SVG illustrations, prepared as source for a subsequent Figma import. These are local design artifacts, not a deployed application or a Figma file.

## Delivery status

- Farmer: 9 mobile screens, from harvest registration through settlement approval.
- Buyer: 11 mobile screens, including offers, reservations, shortage consent, expiry and receipts.
- Administrator: 4 desktop screens and 1 mobile gate/queue screen.
- Forest green, warm ivory, fresh lime accents; Segoe UI typography; text-labelled status colours; 48 px primary controls.
- Linked screens simulate a journey using illustrative data. Inputs are read-only; operational save buttons are disabled. No real business action is executed.
- Source baseline: `docs/project-documentation-v1.5.md`.

Figma was confirmed installed and enabled, but no Figma MCP editing or file-creation tools were exposed in the authoring session. No remote Figma file, native components, variables or prototype interactions have been created. Resume the Figma work when those tools become available, using the new-file and design skills. Use the HTML source to create editable layers, never flattened screen screenshots.

## Validation

26 HTML documents have no broken local links. Chrome checked all 21 mobile screens at 390 px and 360 px and all 4 desktop screens at 1440 px: 46 layouts with no horizontal overflow. Results are in `layout-check.json`. Representative farmer and administrator screenshots were visually reviewed. This is not a complete accessibility or usability audit.

## Remaining design scope

This is the initial core-workflow design pass. Add authentication, detailed visit booking, notifications, role-specific help, profile/account management, catalog/reference-price administration, reports, audit/correction screens, and fuller empty/error/loading states before claiming full SRS coverage. Review mobile information density with real farmers and buyers. The catalogue links focus on the potato example; other produce is illustrative.

## Rebuild

Run `python ui-design/build.py` from the repository root. `check-layout.mjs` optionally validates via a local Chrome DevTools endpoint at port 9236. Do not publish the temporary `.chrome-preview` directory.

## Figma continuation

The user supplied the existing destination: https://www.figma.com/design/iR5T4SR5iNWa7V2CWxGyjz/Dambulla-AgriFlow (file key `iR5T4SR5iNWa7V2CWxGyjz`). Use this file; do not create a duplicate. Inspect its existing content before importing. Suggested pages: Foundations, Farmer Mobile, Buyer Mobile, Administrator Desktop, Administrator Mobile. Import the self-contained sources as editable layers, establish native variables/components, connect the core journey, and visually inspect the imported results. `screen-manifest.json` lists sources and canvas widths.
