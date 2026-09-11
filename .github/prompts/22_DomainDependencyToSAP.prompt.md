# Domain Dependency to SAP

## Create new file

Use the file #files:../docs/21_Domains/DomainAnalysis_Summary.md to create a new file #newfile:../docs/22_DomainDependencyToSAP.md.

## Create a chapter per domain

## Per domain to the following steps.

Analyze the dependencies to the SAP standard in the following sense:

- list all accesses to the standard per domain and document their kind (read, write, delete, function module call, BAPI call, IDoc processing, etc.). Be clear that the accesses are real database accesses like SELECT, INSERT, UPDATE, DELETE statements or calls to SAP standard function modules, BAPIs, IDocs, etc. Avoid vague terms like "uses", "relies on", "depends on", etc.
- make that accessible in a structured comprehensive table for overview (quantity) and detailed lists for each domain (quality).

This documentation should finally serve as a basis for the assessment of the linkage of the domain to the SAP standard.
