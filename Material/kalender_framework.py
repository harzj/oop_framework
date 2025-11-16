from __future__ import annotations
from datetime import date, datetime, timedelta


class Datum:
    """
    Einfacher Datumsklasse.
    Standardwert: 1.1.1970
    """

    def __init__(self, tag: int = 1, monat: int = 1, jahr: int = 1970) -> None:
        self.tag = int(tag)
        self.monat = int(monat)
        self.jahr = int(jahr)
        # Validierung beim Erstellen
        self._validate()

    def _to_date(self) -> date:
        return date(self.jahr, self.monat, self.tag)

    def _validate(self) -> None:
        try:
            self._to_date()
        except Exception as e:
            raise ValueError(f"Ungültiges Datum: {e}")

    def setze_tag(self, t: int) -> None:
        self.tag = int(t)
        self._validate()

    def setze_monat(self, m: int) -> None:
        self.monat = int(m)
        self._validate()

    def setze_jahr(self, j: int) -> None:
        self.jahr = int(j)
        self._validate()

    def gib_tag(self) -> int:
        return self.tag

    def gib_monat(self) -> int:
        return self.monat

    def gib_jahr(self) -> int:
        return self.jahr

    def gib_string(self) -> str:
        return f"{self.tag:02d}.{self.monat:02d}.{self.jahr:04d}"

    def ausgabe(self) -> None:
        print(self.gib_string())

    def zu_heutigem_tag(self) -> None:
        heute = date.today()
        self.tag = heute.day
        self.monat = heute.month
        self.jahr = heute.year

    def tage_bis(self, d: "Datum") -> int:
        """
        Liefert die Differenz in Tagen von self bis d (d - self).
        Ergebnis kann negativ sein, falls d vor self liegt.
        """
        return (d._to_date() - self._to_date()).days


class Termin:
    """
    Termin mit Titel, Beschreibung und Datum.
    """
    def __init__(self, titel: str = "", beschreibung: str = "", datum: Datum | None = None) -> None:
        self.titel = str(titel)
        self.beschreibung = str(beschreibung)
        self.datum = datum if datum is not None else Datum()

    def setze_titel(self, t: str) -> None:
        self.titel = str(t)

    def setze_beschreibung(self, b: str) -> None:
        self.beschreibung = str(b)

    def setze_datum(self, d: Datum) -> None:
        if not isinstance(d, Datum):
            raise TypeError("Erwartet ein Datum-Objekt")
        self.datum = d

    def get_titel(self) -> str:
        return self.titel

    def get_beschreibung(self) -> str:
        return self.beschreibung

    def get_datum(self) -> Datum:
        return self.datum

    def verschiebe_um(self, tage: int) -> None:
        """
        Verschiebt den Termin um die angegebene Anzahl Tage (positiv oder negativ).
        """
        if not isinstance(tage, int):
            tage = int(tage)
        new_date = self.datum._to_date() + timedelta(days=tage)
        # Aktualisiere das Datum-Objekt (nutzt die Setzer zur Validierung)
        self.datum.setze_tag(new_date.day)
        self.datum.setze_monat(new_date.month)
        self.datum.setze_jahr(new_date.year)

    def ist_vergangen(self) -> bool:
        """
        True wenn das Termin-Datum vor dem heutigen Datum liegt.
        """
        return self.datum._to_date() < date.today()

    def ausgabe(self) -> None:
        """
        Gibt den Termin formatiert auf der Konsole aus:

        - Titel am Datum
            Beschreibung
        """
        # Zeile mit Titel und Datum
        print(f"- {self.titel} am {self.datum.gib_string()}")
        # eingerückte Beschreibung (ein Tab oder 4 Leerzeichen)
        if self.beschreibung:
            for line in self.beschreibung.splitlines():
                print(f"    {line}")


# --- Globale Beispiel-Objekte -------------------------------------------------
# Ein Datum-Objekt für den 10.11.2025
aktuell = Datum(10, 11, 2025)
datum2 = Datum(21, 1, 2027)

# Drei Termine (einer leer, zwei mit Inhalten)
termin2 = Termin()  # leerer Termin, Standardwerte

termin1 = Termin(
    titel="Arzttermin",
    beschreibung="Routineuntersuchung um 9:00 Uhr",
    datum=Datum(11, 11, 2025),
)

termin3 = Termin(
    titel="Geburtstagsfeier",
    beschreibung="Gemeinsames Essen und Spieleabend",
    datum=datum2,
)



