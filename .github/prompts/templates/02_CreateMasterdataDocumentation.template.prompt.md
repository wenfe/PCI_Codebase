@workspace Erzeuge eine Dokumentation zum Stammdatenmodul <Modulname> und lege diese als Markdown-Datei mit dem Namen "<Modulnummer>\_<Modulname>Documentation.md" im "docs" Ordner ab. Erzeuge einen Verweis darauf in der "01_SystemSummary.md" im entsprechenden Kapitel.

Lege dabei Wert auf das Datenmodell, indem du

- ein ER-Diagramm im Mermaid-Format erstellst
- alle Tabellen und ihre Felder mit Typ müssen dokumentiert werden
- die Datenflüsse zwischen den Entitäten beschreibst
  Je Entität soll außerdem dokumentiert werden, wobei du darauf achtest,
- den möglichen Wertebereich für die Daten nennst, insbesondere Enumerationen inkl. zugehöriger Werte
- fachliche Schlüsselfelder oder Schlüsselfeldgruppen nennst. Fremdschlüsselbeziehungen zwischen Tabellen sind ebenfalls zu dokumentieren.
  Je Entität soll außerdem beschrieben werden, mit welchem Pflegedialog die Daten verwaltet werden, welche Anwenderrolle dafür zuständig ist und ob hierfür spezielle Berechtigungen erforderlich sind.
