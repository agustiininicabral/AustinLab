# Rule catalogue

The initial rule set is deterministic and offline. A finding is a review signal, not proof that a page violates every applicable standard.

| Rule ID | Severity | Condition | Suggested remediation |
|---|---|---|---|
| SEO001 | Error | The document has no non-empty title text | Add a concise, page-specific title |
| SEO002 | Warning | No non-empty meta description is present | Add a useful page summary in the document head |
| STR001 | Error | No H1 heading is found | Add a descriptive primary heading |
| STR002 | Warning | More than one H1 heading is found | Review the page heading hierarchy |
| A11Y001 | Warning | An image has no alt attribute | Add meaningful alternative text, or alt="" for decorative images |
| A11Y002 | Warning | A link has no discernible text | Provide visible link text or an accessible name |
| A11Y003 | Warning | A form control has no matching explicit label | Add a label whose for attribute matches the control ID |
| LINK001 | Warning | A link has no destination, uses #, or uses javascript:void(0) | Use a real destination or a button for an action |

## Severity and exit status

- Error: indicates a structural issue that makes the audit exit with status 1.
- Warning: indicates a review item; warning-only reports exit with status 0.
- Input errors: missing files, unsupported extensions and unreadable UTF-8 input are CLI errors and exit non-zero.

## Known limitations

The parser does not execute JavaScript, fetch CSS, compute accessible names from the full accessibility tree, validate links over the network, or evaluate rendered layout. It currently checks explicit label associations only. For complete accessibility evaluation, combine this static report with browser-based checks and manual review.
