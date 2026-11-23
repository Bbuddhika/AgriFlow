# Dambulla AgriFlow — current documentation

- [Latest PDF](output/Dambulla_AgriFlow_Project_Documentation_v1.5.pdf)
- [Latest HTML](output/Dambulla_AgriFlow_Project_Documentation_v1.5.html)
- [Consolidated editable source](project-documentation-v1.5.md)
- [Editable diagrams](diagrams/README.md)
- [Step-by-step member implementation guide](development/member-guide.md)
- [Development progress, repository review and file inventory](development/README.md)
- [Requirement-to-stage/test traceability](testing/requirements-traceability.csv)
- [Current separate-service architecture](architecture/003-separate-backend-services.md)
- [Historical application architecture](architecture/001-application-foundation.md)
- [RabbitMQ architecture amendment](architecture/002-rabbitmq.md)
- [Local setup and Docker operations](operations/local-development.md)

Edit project-documentation-v1.5.md for content and tools/build_documentation.py for diagram layouts. Run `python docs/tools/build_documentation.py` to regenerate HTML and SVGs. Print the HTML to PDF in Chrome using A4 with browser headers/footers disabled. tools/export_pdf.ps1 automates export where local script policy allows it.

The consolidated v1.5 source remains the functional baseline. ADR 003 supersedes
its single-backend deployment assumptions; use current setup instructions. The newer user
decision in architecture/002-rabbitmq.md supersedes its older broker-deferral
clause. The development guide reflects current source presence and pending
verification; the v1.5 PDF/HTML remain historical generated design outputs.

The generator no longer depends on earlier review/amendment files. Keep current
development/, architecture/, operations/ and testing/ documents alongside the
consolidated source, diagrams and documentation tools. Older amendments/reviews
are retained as history. Browser-profile folders are temporary runtime state,
not documentation or application source; do not commit them as project evidence.
