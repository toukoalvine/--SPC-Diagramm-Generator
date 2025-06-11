# 📊 SPC-Diagramm-Generator für die Produktion

Ein umfassendes Tool für Statistical Process Control (SPC) zur Qualitätskontrolle und Prozessüberwachung in der industriellen Fertigung.

## 🎯 Übersicht

Der SPC-Diagramm-Generator ist eine webbasierte Anwendung, die es Qualitätsingenieuren und Produktionsleitern ermöglicht, statistische Regelkarten zu erstellen und Produktionsprozesse zu überwachen. Das Tool unterstützt alle gängigen SPC-Diagrammtypen und bietet automatisierte Analysen zur Prozessstabilität.

## ✨ Features

### 📈 Unterstützte Diagrammtypen
- **X̄-R Karte** (Mittelwert-Spannweite) - Für Stichprobendaten mit konstanter Größe
- **X̄-s Karte** (Mittelwert-Standardabweichung) - Alternative zu X̄-R für größere Stichproben
- **I-MR Karte** (Einzelwerte-Gleitende Spannweite) - Für Einzelmessungen
- **p-Karte** (Anteil fehlerhaft) - Für Qualitätsraten mit variablen Stichprobengrößen
- **np-Karte** (Anzahl fehlerhaft) - Für konstante Stichprobengrößen
- **c-Karte** (Anzahl Fehler) - Für Fehleranzahl pro Einheit
- **u-Karte** (Fehler pro Einheit) - Für variable Einheitsgrößen

### 🔧 Kernfunktionen
- **Automatische Kontrollgrenzen-Berechnung** (UCL, CL, LCL)
- **Regelverletzungs-Erkennung** mit Warnsystem
- **Prozessfähigkeitsanalyse** (Cp, Cpk Berechnungen)
- **Interaktive Diagramme** mit Zoom und Pan-Funktionen
- **Export-Funktionen** (PNG, CSV)
- **Flexible Dateneingabe** (CSV-Upload, manuelle Eingabe, Beispieldaten)

### 🎨 Benutzerfreundlichkeit
- **Deutsche Benutzeroberfläche**
- **Responsive Design** für Desktop und Mobile
- **Farbkodierte Visualisierungen**
- **Integrierte Hilfe und Interpretationsleitfaden**
- **Echtzeit-Berechnungen**

## 🚀 Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt-für-Schritt Installation

1. **Repository klonen oder Dateien herunterladen**
```bash
git clone https://github.com/yourusername/spc-generator.git
cd spc-generator
```

2. **Virtuelle Umgebung erstellen (empfohlen)**
```bash
python -m venv spc_env
source spc_env/bin/activate  # Linux/Mac
# oder
spc_env\Scripts\activate     # Windows
```

3. **Dependencies installieren**
```bash
pip install -r requirements.txt
```

4. **Anwendung starten**
```bash
streamlit run spc_generator.py
```

5. **Browser öffnen**
Die Anwendung ist unter `http://localhost:8501` verfügbar.

## 📋 Verwendung

### Grundlegende Nutzung

1. **Diagrammtyp auswählen**
   - Wählen Sie in der Seitenleiste den gewünschten SPC-Diagrammtyp

2. **Daten eingeben**
   - **CSV-Upload**: Laden Sie eine CSV-Datei mit Ihren Produktionsdaten
   - **Manuelle Eingabe**: Geben Sie Werte direkt in das Textfeld ein
   - **Beispieldaten**: Nutzen Sie generierte Daten zum Testen

3. **Parameter konfigurieren**
   - Stichprobengröße (für X̄-R/X̄-s Karten)
   - Weitere diagrammspezifische Einstellungen

4. **Analyse durchführen**
   - Automatische Berechnung der Kontrollgrenzen
   - Identifikation regelwidriger Punkte
   - Prozessfähigkeitsanalyse

5. **Ergebnisse exportieren**
   - Diagramme als PNG-Dateien
   - Berechnete Daten als CSV

### Datenformat

#### X̄-R / X̄-s / I-MR Karten
```csv
Messwert
100.5
99.8
101.2
100.1
99.9
```

#### p-Karte
```csv
Stichprobengröße,Fehlerhaft
100,3
120,5
95,2
110,4
```

#### np-Karte
```csv
Fehlerhaft
3
5
2
4
6
```

#### c-Karte
```csv
Fehleranzahl
4
6
3
5
7
```

#### u-Karte
```csv
Einheitsgröße,Fehleranzahl
1.0,4
1.2,5
0.8,3
1.1,6
```

## 📊 Interpretationshilfe

### Kontrollgrenzen
- **UCL (Upper Control Limit)**: Obere Kontrollgrenze
- **CL (Center Line)**: Mittellinie (Prozessmittelwert)
- **LCL (Lower Control Limit)**: Untere Kontrollgrenze

### Regelverletzungen
1. **Punkte außerhalb der Kontrollgrenzen**
2. **7 aufeinanderfolgende Punkte auf einer Seite der Mittellinie**
3. **Trends** (6+ aufeinanderfolgende steigende/fallende Punkte)
4. **Zyklen** oder unnatürliche Muster

### Prozessfähigkeitsindizes
- **Cp**: Verhältnis von Toleranz zu Prozessstreuung (≥1.33 für gute Prozesse)
- **Cpk**: Berücksichtigt Zentrierung des Prozesses (≥1.33 empfohlen)

## 🔧 Erweiterte Konfiguration

### Anpassung der Kontrollgrenzen
Die Anwendung verwendet Standard-3-Sigma-Kontrollgrenzen. Für spezielle Anforderungen können die Konstanten im Code angepasst werden.

### Zusätzliche Regelkriterien
Das Tool kann erweitert werden um zusätzliche Western Electric Rules:
- Rule 2: 2 von 3 Punkten jenseits 2-Sigma
- Rule 3: 4 von 5 Punkten jenseits 1-Sigma
- Rule 4: 8 aufeinanderfolgende Punkte auf einer Seite

## 📁 Projektstruktur

```
spc-generator/
├── spc_generator.py      # Hauptanwendung
├── requirements.txt      # Python Dependencies
├── README.md            # Diese Datei
├── data/               # Beispieldaten (optional)
│   ├── sample_xbar_r.csv
│   ├── sample_p_chart.csv
│   └── ...
└── exports/            # Exportierte Dateien (wird automatisch erstellt)
```

## 🛠️ Technische Details

### Dependencies
- **Streamlit**: Web-Framework für die Benutzeroberfläche
- **Pandas**: Datenmanipulation und -analyse
- **NumPy**: Numerische Berechnungen
- **Plotly**: Interaktive Diagramme
- **SciPy**: Statistische Funktionen

### Berechnungsmethoden
- Kontrollgrenzen nach AIAG SPC Manual
- Prozessfähigkeitsberechnungen nach ISO 21747
- Western Electric Rules für Regelverletzungen

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte beachten Sie:

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committen Sie Ihre Änderungen (`git commit -m 'Add AmazingFeature'`)
4. Pushen Sie zum Branch (`git push origin feature/AmazingFeature`)
5. Öffnen Sie einen Pull Request

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe `LICENSE` Datei für Details.

## 🆘 Support

### Häufige Probleme

**Problem**: Datei kann nicht geladen werden
- **Lösung**: Überprüfen Sie das CSV-Format und Spaltennamen

**Problem**: Kontrollgrenzen erscheinen nicht korrekt
- **Lösung**: Stellen Sie sicher, dass ausreichend Datenpunkte vorhanden sind

**Problem**: Anwendung startet nicht
- **Lösung**: Überprüfen Sie Python-Version und Dependencies

### Kontakt
- **Issues**: Erstellen Sie ein GitHub Issue
- **Email**: [ihre-email@domain.com]
- **Dokumentation**: [Link zur erweiterten Dokumentation]

## 🎓 Weiterführende Ressourcen

- [AIAG SPC Manual](https://www.aiag.org/quality/statistical-process-control)
- [ISO 7870 - Control charts](https://www.iso.org/standard/72578.html)
- [NIST Engineering Statistics Handbook](https://www.itl.nist.gov/div898/handbook/)
- [Six Sigma SPC Guide](https://www.isixsigma.com/tools-templates/control-charts/)

## 📊 Beispiel-Screenshots

### X̄-R Regelkarte
![X̄-R Chart Example](screenshots/xbar_r_chart.png)

### p-Karte mit Regelverletzungen
![p-Chart with Violations](screenshots/p_chart_violations.png)

### Prozessfähigkeitsanalyse
![Process Capability Analysis](screenshots/capability_analysis.png)

---

**Hinweis**: Dieses Tool dient zur Unterstützung der Qualitätskontrolle und ersetzt nicht die fachliche Bewertung durch qualifizierte Qualitätsingenieure. Alle Entscheidungen basierend auf SPC-Analysen sollten von Fachpersonal validiert werden.
