---
agent: Plan
---

Erstelle einen Plan für die Identifikation von Domänen in der vorliegenden Codesbasis und deren Abhängigkeiten.

# Vorgehen

1. Im Sinne des Domain Driven Designs: welche Domains können für die @codebase im Ordner 'src' vorliegende Codesbasis identifiziert werden? Verwende dazu auch die bereits vorliegende Dokumentation im Ordner 'docs'. Jede identifizierte Komponente in docs/01*SystemSummary.md sollte berücksichtigt werden (evtl. können aber mehrere Komponenten zu einer Domain zusammengefasst werden oder in mehrere Domains aufgebrochen werden). Beachte den Quellcode im Ordner 'src' nur im \_Notfall*, wenn die Dokumentation keine ausreichenden Informationen liefert.

Beachte den SAP-Standard als eigene Domain, ggf. noch auf der Granularität der Unterpakete/-module.

2. Beschreibe nach diesem Abschluss die Abhängigkeiten zwischen den identifizierten Domänen. Stelle die Abhängigkeiten auch graphisch dar.

3. Schlage eine mögliche Transformationsstrategie vor in mehreren Schritten (strangler fig Ansatz).

# Output

Schließlich sollen die Ergebnisse in Files im Ordner docs/21_Domains abgelegt werden: alles in einem File. Beachte die Dokumentationsstandards in .github/instructions/create_documentation.instructions.md.
