"""Schülereingaben über die wirklichen Eingabefelder. Kein Sitzungsstand wird künstlich gesetzt."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gesamt'))
from ergonomie import reach,touch

def antwort(frame,grund='Ich möchte Lauras Wünsche berücksichtigen.',choice=1):
    frame.locator('#spur-wahl').wait_for()
    select=frame.locator('#spur-wahl')
    reach(frame,select)
    select.select_option(index=choice)
    field=frame.locator('#spur-grund')
    reach(frame,field)
    field.fill(grund)
    touch(frame,'#spur-speichern')

def schluss(frame):
    antwort(frame)
    frame.locator('#spur-fertig').wait_for()
    assert frame.locator('#lernspur h1').inner_text()=='Dein Vergleich'
    touch(frame,'#spur-fertig')
