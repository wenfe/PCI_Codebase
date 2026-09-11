@workspace Lege einen Ordner "2_CreateComponentDocumentation" im Ordner "prompts" an (wenn noch nicht vorhanden). Erzeuge darin je in der Dokumentation "docs/01_SystemSummary.md" aufgeführtem Komponente eine Prompt-Datei "<Komponentenummer>\_Create<Komponentename>Documentation.prompt.md". Entscheide dafür, welcher Komponenteart das Komponente zuzuordnen ist und das zugehörige Template aus dem template-Ordner verwendest:

1. Stammdaten, Data Management Components => "02_CreateMasterdataDocumentation.template.prompt.md"
1. Schnittstelle, Communication Components => "02_CreateInterfaceDocumentation.template.prompt.md"
1. Presentation Layer Components => "02_CreatePresentationLayerDocumentation.template.prompt.md"
1. Business Layer Components => "02_CreateBusinessLayerDocumentation.template.prompt.md"
1. Framework, Infrastructure Components, Utility Components => "02_CreateFrameworkDocumentation.template.prompt.md"
1. sonst, Analytics & Reporting Components: "02_CreateComponentDocumentation.template.prompt.md"
   Ersetze dabei alle Platzhalter wie <Komponentename>. Verwende die Kapitelnummer plus eine aufsteigende Nummer aus der Dokumentation als Komponentenummer. Achte auf eindeutige Komponentenummern.

Ordne die Dokumente in der Reihenfolge:

1. Stammdaten, Data Management Components
1. Schnittstelle, Integration , Communication Components
1. Business Layer Components
1. Presentation Layer Components
1. restliche Komponenten.

## Weitere Elemente

Mache kenntlich wenn bei den Komponenten Dialoge (GUI, SAPGUI) vorhanden sind und liste diese auf.
Mache kenntlich, wenn bei den Komponenten Formen (Smartform, Adobe Form, SAP Script) vorhanden sind und liste diese auf.
