const FALLAKTE = {
  "meta": {
    "levels": {
      "Foerder": "Förder",
      "ESA": "ESA",
      "MSA": "MSA",
      "AHR": "AHR"
    }
  },
  "cases": {
    "Laura": [
      {
        "id": "L0",
        "type": "class_poll_intro",
        "message": {
          "Foerder": [
            "Hi, ich bin Laura. Ich bin 16.",
            "Beim Sex können Krankheiten übertragen werden. Davor möchte ich mich schützen.",
            "Welche Verhütungsmethode könnt ihr mir dafür empfehlen?"
          ],
          "ESA": [
            "Hi, ich bin Laura, 16.",
            "Beim Sex möchte ich mich vor sexuell übertragbaren Infektionen schützen.",
            "Welche Verhütungsmethode könnt ihr mir dafür empfehlen?"
          ],
          "MSA": [
            "Hi, ich bin Laura, 16.",
            "Ich möchte beim Sex das Risiko sexuell übertragbarer Infektionen verringern.",
            "Welche der bekannten Verhütungsmethoden würdet ihr mir empfehlen?"
          ],
          "AHR": [
            "Hi, ich bin Laura, 16.",
            "Ich möchte beim Sex das Risiko sexuell übertragbarer Infektionen verringern.",
            "Welche der vier bekannten Methoden würdet ihr für dieses Ziel zunächst vorschlagen?"
          ]
        },
        "task": {
          "Foerder": "Auf dem Laufzettel: Notiere deinen ersten Vorschlag und einen Grund.",
          "ESA": "Auf dem Laufzettel: Notiere deinen ersten Vorschlag und einen Grund.",
          "MSA": "Auf dem Laufzettel: Notiere deine erste Empfehlung mit einem Grund aus dem Fall.",
          "AHR": "Auf dem Laufzettel: Notiere eine erste Empfehlung. Begründe sie mit Lauras bisherigem Ziel."
        },
        "options": {
          "K": "Wir schlagen dir ein Kondom vor.",
          "P": "Wir schlagen dir die Kombinationspille vor.",
          "Cu": "Wir schlagen dir die Kupferspirale vor.",
          "H": "Wir schlagen dir die Hormonspirale vor.",
          "K+P": "Wir schlagen dir ein Kondom und die Kombinationspille vor.",
          "K+Cu": "Wir schlagen dir ein Kondom und die Kupferspirale vor.",
          "K+H": "Wir schlagen dir ein Kondom und die Hormonspirale vor."
        },
        "replies": {
          "K": "Wie viel Schutz kann ich davon erwarten?",
          "P": "Wie hilft mir das gegen Infektionen beim Sex? Genau danach habe ich gefragt.",
          "Cu": "Wie hilft mir das gegen Infektionen beim Sex? Genau danach habe ich gefragt.",
          "H": "Wie hilft mir das gegen Infektionen beim Sex? Genau danach habe ich gefragt.",
          "K+P": "Ihr nennt zwei Mittel. Welches davon hilft bei meinem ersten Wunsch?",
          "K+Cu": "Ihr nennt zwei Mittel. Welches davon hilft bei meinem ersten Wunsch?",
          "K+H": "Ihr nennt zwei Mittel. Welches davon hilft bei meinem ersten Wunsch?"
        },
        "hints": {
          "K": [
            "Lies auf der Karte „Kondom“ den Abschnitt „Infektionsschutz“.",
            "Kondome senken das Risiko vieler Infektionen. Ganz ausschließen können sie es nicht."
          ],
          "P": [
            "Lies auf der Karte „Kombinationspille“ den Abschnitt „Infektionsschutz“.",
            "Die Kombinationspille allein schützt nicht vor sexuell übertragbaren Infektionen."
          ],
          "Cu": [
            "Lies auf der Karte „Kupferspirale“ den Abschnitt „Infektionsschutz“.",
            "Die Kupferspirale allein schützt nicht vor sexuell übertragbaren Infektionen."
          ],
          "H": [
            "Lies auf der Karte „Hormonspirale“ den Abschnitt „Infektionsschutz“.",
            "Die Hormonspirale allein schützt nicht vor sexuell übertragbaren Infektionen."
          ],
          "K+P": [
            "Lies auf der Karte „Kombinationspille“ den Abschnitt „Infektionsschutz“.",
            "Die Kombinationspille allein schützt nicht vor sexuell übertragbaren Infektionen. Das Kondom in eurem Vorschlag senkt das Risiko vieler Infektionen."
          ],
          "K+Cu": [
            "Lies auf der Karte „Kupferspirale“ den Abschnitt „Infektionsschutz“.",
            "Die Kupferspirale allein schützt nicht vor sexuell übertragbaren Infektionen. Das Kondom in eurem Vorschlag senkt das Risiko vieler Infektionen."
          ],
          "K+H": [
            "Lies auf der Karte „Hormonspirale“ den Abschnitt „Infektionsschutz“.",
            "Die Hormonspirale allein schützt nicht vor sexuell übertragbaren Infektionen. Das Kondom in eurem Vorschlag senkt das Risiko vieler Infektionen."
          ]
        },
        "title": "Infektionsschutz",
        "questions": [
          [
            "Was meinst du mit Infektionen?",
            "Ich meine Krankheiten, die beim Sex übertragen werden können."
          ],
          [
            "Was ist dir gerade am wichtigsten?",
            "Zuerst möchte ich über den Schutz vor solchen Infektionen sprechen."
          ]
        ],
        "helpBefore": [
          "Lies Lauras erste Frage. Wovor will sie sich schützen?",
          "Sie fragt nach Infektionen, die beim Sex übertragen werden."
        ]
      },
      {
        "id": "L1",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Ich möchte auch nicht ungewollt schwanger werden. Mir ist ein sicherer Schutz wichtig.",
            "Ich vergesse manchmal Dinge, die ich jeden Tag machen muss.",
            "Prüft euren Vorschlag noch einmal."
          ],
          "ESA": [
            "Außerdem möchte ich eine Schwangerschaft möglichst zuverlässig vermeiden.",
            "Mein Alltag ist oft anders. An regelmäßige Dinge denke ich nicht immer.",
            "Was bedeutet das für euren Vorschlag?"
          ],
          "MSA": [
            "Eine Schwangerschaft möchte ich ebenfalls möglichst zuverlässig vermeiden.",
            "Mein Alltag ist unregelmäßig. Tägliche Routinen vergesse ich gelegentlich.",
            "Welche Bedeutung hat das für eure Empfehlung?"
          ],
          "AHR": [
            "Neben Infektionsschutz hat für mich die zuverlässige Vermeidung einer Schwangerschaft einen hohen Stellenwert.",
            "Mein Tagesablauf ist wechselhaft; täglich wiederkehrende Handlungen vergesse ich gelegentlich.",
            "Wie verändert diese Information eure vorläufige Abwägung?"
          ]
        },
        "task": {
          "Foerder": "Lies Lauras neue Nachricht. Prüfe: Passt dein Vorschlag noch?",
          "ESA": "Lies Lauras neue Wünsche. Prüfe deinen Vorschlag mit deinen Infokarten.",
          "MSA": "Prüfe beide Schutzziele und den Aufwand im Alltag. Vergleiche zwei Möglichkeiten.",
          "AHR": "Gewichte Schwangerschaftsschutz, Infektionsschutz und Anwendung. Vergleiche zwei Strategien."
        },
        "options": {
          "K": "Wir möchten dir ein Kondom vorschlagen.",
          "P": "Wir möchten dir die Kombinationspille vorschlagen.",
          "Cu": "Wir möchten dir die Kupferspirale vorschlagen.",
          "H": "Wir möchten dir die Hormonspirale vorschlagen.",
          "K+P": "Wir möchten dir ein Kondom und die Kombinationspille vorschlagen.",
          "K+Cu": "Wir möchten dir ein Kondom und die Kupferspirale vorschlagen.",
          "K+H": "Wir möchten dir ein Kondom und die Hormonspirale vorschlagen."
        },
        "replies": {
          "K": "An das Kondom müssten wir dann beim Sex denken. Ich erzähle euch gleich noch etwas.",
          "P": "Die Tablette müsste ich regelmäßig nehmen. Wie könnte ich das im Alltag schaffen?",
          "Cu": "Dann müsste ich nicht jeden Tag daran denken. Was wäre im Alltag trotzdem wichtig?",
          "H": "Das wäre also keine tägliche Aufgabe. Was müsste ich dafür tun?",
          "K+P": "Das wären zwei Methoden. Die tägliche Einnahme wäre dabei weiterhin ein Thema.",
          "K+Cu": "Ihr nennt zwei Methoden. Welche Aufgabe soll jede davon haben?",
          "K+H": "Bei eurem Vorschlag müsste ich nicht täglich eine Pille nehmen. Über die Spirale hätte ich noch Fragen."
        },
        "hints": {
          "K": [
            "Lies auf der Kondom-Karte „Anwendung“. Wann braucht man es?",
            "Ein Kondom braucht man bei jedem Sex neu. Es muss von Anfang an richtig sitzen."
          ],
          "P": [
            "Lies auf der Pillen-Karte „Anwendung“. Wie oft wird sie genommen?",
            "Die Pille braucht regelmäßige Einnahme. Einnahmefehler können den Schutz verringern."
          ],
          "Cu": [
            "Lies auf der Kupferspiralen-Karte „Anwendung“. Wer setzt sie ein?",
            "Eine Ärztin oder ein Arzt setzt sie ein. Es gibt keine tägliche Einnahme. Kontrollen bleiben wichtig."
          ],
          "H": [
            "Lies auf der Hormonspiralen-Karte „Anwendung“. Was entfällt im Alltag?",
            "Es gibt keine tägliche Einnahme. Die Spirale wird ärztlich eingesetzt und kontrolliert."
          ],
          "K+P": [
            "Lies auf der Pillen-Karte „Anwendung“. Wie oft wird sie genommen?",
            "Die Pille braucht regelmäßige Einnahme. Einnahmefehler können den Schutz verringern."
          ],
          "K+Cu": [
            "Lies auf der Kupferspiralen-Karte „Anwendung“. Wer setzt sie ein?",
            "Eine Ärztin oder ein Arzt setzt sie ein. Es gibt keine tägliche Einnahme. Kontrollen bleiben wichtig."
          ],
          "K+H": [
            "Lies auf der Hormonspiralen-Karte „Anwendung“. Was entfällt im Alltag?",
            "Es gibt keine tägliche Einnahme. Die Spirale wird ärztlich eingesetzt und kontrolliert."
          ]
        },
        "title": "Schutz im Alltag",
        "questions": [
          [
            "Was fällt dir im Alltag schwer?",
            "Mein Tag läuft oft anders als geplant. Dann vergesse ich feste Termine leicht."
          ],
          [
            "Geht es dir jetzt um beide Ziele?",
            "Ja. Ich möchte eine Schwangerschaft vermeiden. Der Schutz vor Infektionen ist mir auch wichtig."
          ]
        ],
        "helpBefore": [
          "Lies Lauras Nachricht über ihren Tag. Was vergisst sie leicht?",
          "Eine feste Zeit ist für Laura schwierig. Vergleiche, wann man die Methoden anwendet."
        ]
      },
      {
        "id": "L2",
        "type": "reason_on_paper",
        "message": {
          "Foerder": [
            "Meine Freundin nimmt die Pille. Ihr wurde davon übel.",
            "Bekomme ich das dann auch? Ich bin unsicher."
          ],
          "ESA": [
            "Eine Freundin erzählt, dass ihr von der Pille übel wurde.",
            "Jetzt habe ich Sorge. Kann man daraus schon wissen, wie es mir damit gehen würde?"
          ],
          "MSA": [
            "Meine Freundin hatte mit ihrer Pille Übelkeit. Sie meint, bei mir wäre das bestimmt genauso.",
            "Was lässt sich aus ihrer Erfahrung wirklich sagen?"
          ],
          "AHR": [
            "Eine Freundin berichtet von Übelkeit durch ihre Pille. Sie schließt daraus, dass ich sie ebenfalls nicht vertragen werde.",
            "Was ist an ihrer Aussage eine Erfahrung, was eine Vermutung?"
          ]
        },
        "task": {
          "Foerder": "Lies die Pillen-Karte. Muss Laura auch übel werden? Sprecht zu zweit.",
          "ESA": "Lies „Mögliche Nachteile“. Was weiß Laura über sich selbst? Sprecht zu zweit.",
          "MSA": "Trenne die Erfahrung der Freundin von einer Vorhersage für Laura.",
          "AHR": "Wie weit trägt ein einzelner Erfahrungsbericht? Erklärt, welche Aussage belegt ist."
        },
        "options": {
          "DONE": "Wir haben über die Erfahrung deiner Freundin gesprochen."
        },
        "replies": {
          "DONE": "Danke, dass ihr meine Sorge besprecht. Ich habe außerdem eine Entscheidung für mich getroffen."
        },
        "hints": {
          "DONE": [
            "Lies auf der Pillen-Karte „Mögliche Nachteile“. Steht dort „immer“ oder „kann“?",
            "Übelkeit ist möglich. Aus der Erfahrung einer Freundin folgt nicht, dass Laura dieselbe Nebenwirkung bekommt."
          ]
        },
        "title": "Die Erfahrung einer Freundin",
        "questions": [
          [
            "Wer hat die Pille genommen?",
            "Meine Freundin. Sie hat mir von ihrer Übelkeit erzählt."
          ],
          [
            "Weißt du, wie du die Pille verträgst?",
            "Das weiß ich nicht. Ich mache mir wegen ihrer Erfahrung Sorgen."
          ]
        ],
        "helpBefore": [
          "Lies auf der Pillen-Karte den Abschnitt „Mögliche Nachteile“.",
          "Übelkeit ist möglich. Bei Laura kann es anders sein als bei ihrer Freundin."
        ]
      },
      {
        "id": "L3",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Die Pille möchte ich nicht nehmen.",
            "Bei anderen Mitteln mit Hormonen bin ich noch offen.",
            "Über eine Spirale möchte ich erst mehr wissen. Das Einsetzen macht mir etwas Angst."
          ],
          "ESA": [
            "Ich möchte die Pille nicht nehmen. Das habe ich für mich entschieden.",
            "Andere Mittel mit Hormonen schließe ich nicht aus. Bei einer Spirale bin ich wegen des Einsetzens noch unsicher."
          ],
          "MSA": [
            "Die Pille möchte ich für mich ausschließen. Das ist nicht dasselbe wie ein Nein zu allen Hormonen.",
            "Über eine Spirale würde ich mich beraten lassen. Vor dem Einsetzen habe ich aber Respekt."
          ],
          "AHR": [
            "Die Pille lehne ich ab. Andere hormonelle Methoden habe ich noch nicht ausgeschlossen.",
            "Meine Sorge vor dem Einsetzen einer Spirale ist bisher keine feste Ablehnung. Ich möchte erst informiert entscheiden."
          ]
        },
        "task": {
          "Foerder": "Laura sagt zur Pille Nein. Wo hat sie noch Fragen? Prüft euren Vorschlag.",
          "ESA": "Beachte Lauras Nein zur Pille. Prüfe die übrigen Möglichkeiten mit deinen Karten.",
          "MSA": "Unterscheide Lauras Entscheidung von ihrer noch offenen Sorge. Prüfe deinen Vorschlag.",
          "AHR": "Trenne eine verbindliche Grenze von einer abwägbaren Präferenz. Vergleiche die verbleibenden Strategien."
        },
        "options": {
          "K": "Wir würden dir ein Kondom vorschlagen.",
          "P": "Wir würden dir die Kombinationspille vorschlagen.",
          "Cu": "Wir würden dir die Kupferspirale vorschlagen.",
          "H": "Wir würden dir die Hormonspirale vorschlagen.",
          "K+P": "Wir würden dir ein Kondom und die Kombinationspille vorschlagen.",
          "K+Cu": "Wir würden dir ein Kondom und die Kupferspirale vorschlagen.",
          "K+H": "Wir würden dir ein Kondom und die Hormonspirale vorschlagen."
        },
        "replies": {
          "K": "Das wäre ohne Pille. Mich interessiert, was bei der Anwendung wichtig ist.",
          "P": "Aber die Pille möchte ich nicht nehmen. Schaut bitte noch einmal auf meinen Wunsch.",
          "Cu": "Über die Kupferspirale möchte ich mehr wissen. Zugestimmt habe ich dem Einsetzen noch nicht.",
          "H": "Bei anderen Hormonen bin ich noch offen. Eine Hormonspirale möchte ich erst nach Beratung abwägen.",
          "K+P": "In eurem Vorschlag steckt noch die Pille. Die möchte ich nicht nehmen.",
          "K+Cu": "Bei der Kupferspirale habe ich noch Fragen. Wie läuft das Einsetzen ab?",
          "K+H": "Bei der Hormonspirale bin ich noch nicht entschieden. Wie läuft das Einsetzen ab?"
        },
        "hints": {
          "K": [
            "Lies Lauras Nachricht „Die Pille möchte ich nicht nehmen“. Enthält dein Vorschlag eine Pille?",
            "Ein Nein zur Pille ist kein Nein zum Kondom. Vergleiche danach die weiteren Wünsche."
          ],
          "P": [
            "Lies Lauras Nachricht zur Pille noch einmal.",
            "Laura lehnt die Pille ab. Eine andere Person darf diese Entscheidung nicht für sie aufheben."
          ],
          "Cu": [
            "Lies Lauras Nachricht zum Einsetzen. Hat sie schon Nein gesagt?",
            "Laura ist bei einer Spirale noch unsicher. Das ist weder eine Zustimmung noch eine feste Ablehnung."
          ],
          "H": [
            "Lies Lauras Nachricht zu anderen Hormonen. Was ist noch offen?",
            "Laura lehnt die Pille ab, aber nicht automatisch alle Hormone. Über die Spirale entscheidet sie nach Beratung."
          ],
          "K+P": [
            "Lies Lauras Nachricht zur Pille noch einmal.",
            "Laura lehnt die Pille ab. Eine andere Person darf diese Entscheidung nicht für sie aufheben."
          ],
          "K+Cu": [
            "Lies Lauras Nachricht zum Einsetzen. Hat sie schon Nein gesagt?",
            "Laura ist bei einer Spirale noch unsicher. Das ist weder eine Zustimmung noch eine feste Ablehnung."
          ],
          "K+H": [
            "Lies Lauras Nachricht zu anderen Hormonen. Was ist noch offen?",
            "Laura lehnt die Pille ab, aber nicht automatisch alle Hormone. Über die Spirale entscheidet sie nach Beratung."
          ]
        },
        "title": "Lauras Entscheidung",
        "questions": [
          [
            "Gilt dein Nein für alle Hormone?",
            "Nein. Für mich steht nur fest, dass ich die Pille nicht nehmen möchte."
          ],
          [
            "Was macht dir an der Spirale Sorgen?",
            "Das Einsetzen. Ich würde erst gern in einer Praxis fragen, wie das abläuft."
          ]
        ],
        "helpBefore": [
          "Lies Lauras Satz über die Pille. Wozu sagt sie Nein?",
          "Laura sagt Nein zur Pille. Bei der Spirale hat sie noch Fragen."
        ]
      },
      {
        "id": "L4",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Bei meiner Periode habe ich oft starke Schmerzen.",
            "Ich war deshalb noch nicht bei einer Ärztin oder einem Arzt.",
            "Noch mehr Schmerzen möchte ich nicht. Was bedeutet das für euren Vorschlag?"
          ],
          "ESA": [
            "Bei meiner Periode habe ich oft starke Schmerzen. Bisher wurde das nicht untersucht.",
            "Ich möchte nicht, dass sie noch stärker werden. Prüft ihr das bei eurem Vorschlag?"
          ],
          "MSA": [
            "Ich habe häufig starke Regelschmerzen, die noch nicht ärztlich abgeklärt wurden.",
            "Eine mögliche Verstärkung wäre für mich ein wichtiger Nachteil."
          ],
          "AHR": [
            "Häufige starke Regelschmerzen wurden bisher nicht ärztlich abgeklärt.",
            "Was würdet ihr mir jetzt raten, solange ich den Grund für die Schmerzen noch nicht kenne?"
          ]
        },
        "task": {
          "Foerder": "Schau auf deiner Karte bei „Blutung und Schmerzen“. Passt dein Vorschlag noch?",
          "ESA": "Lies auf deiner gewählten Karte „Blutung und Schmerzen“. Prüfe deinen Vorschlag.",
          "MSA": "Vergleiche die Angaben zu Blutung und Schmerzen bei zwei Strategien. Nenne eine offene medizinische Frage.",
          "AHR": "Vergleiche Nutzen, mögliche Belastung und ungeklärte Eignung. Formuliere eine bedingte Empfehlung statt einer Diagnose."
        },
        "options": {
          "K": "Wir schlagen dir ein Kondom vor.",
          "P": "Wir schlagen dir die Kombinationspille vor.",
          "Cu": "Wir schlagen dir die Kupferspirale vor.",
          "H": "Wir schlagen dir die Hormonspirale vor.",
          "K+P": "Wir schlagen dir ein Kondom und die Kombinationspille vor.",
          "K+Cu": "Wir schlagen dir ein Kondom und die Kupferspirale vor.",
          "K+H": "Wir schlagen dir ein Kondom und die Hormonspirale vor."
        },
        "replies": {
          "K": "Meine Schmerzen bleiben dann eine eigene Frage. Ich möchte sie ärztlich klären lassen.",
          "P": "Die Pille möchte ich weiterhin nicht. Meine Schmerzen ändern daran nichts.",
          "Cu": {
            "Foerder": "Ich habe schon oft starke Schmerzen. Könnte die Kupferspirale meine Schmerzen verändern?",
            "ESA": "Meine Periode tut schon oft weh. Könnte die Kupferspirale das verändern?",
            "MSA": "Welche Bedeutung hat die mögliche Veränderung meiner Beschwerden für euren Kupferspiralen-Vorschlag?",
            "AHR": "Wie gewichtet ihr bei der Kupferspirale die möglichen Blutungs- und Schmerzveränderungen gegenüber den Vorteilen?"
          },
          "H": "Wäre das für mich medizinisch geeignet? Das ist bisher noch nicht geklärt.",
          "K+P": "Die Pille ist immer noch dabei. Ich habe sie aber abgelehnt.",
          "K+Cu": "Bitte prüft den Teil zur Kupferspirale noch einmal. Mehr Schmerzen wären für mich ein wichtiger Nachteil.",
          "K+H": "Bei der Hormonspirale brauche ich ärztliche Beratung. Und die Ursache meiner Schmerzen ist noch offen."
        },
        "hints": {
          "K": [
            "Lies auf der Kondom-Karte „Blutung und Schmerzen“.",
            "Das Kondom behandelt keine Regelschmerzen. Starke Schmerzen sollen ärztlich geklärt werden."
          ],
          "P": [
            "Lies die Pillen-Karte: „Blutung und Schmerzen“. Lies dann Lauras Nein zur Pille.",
            "Die Pille kann Beschwerden verringern. Das erlaubt aber nicht, Lauras Nein zu übergehen."
          ],
          "Cu": [
            "Lies auf der Kupferspiralen-Karte „Blutung und Schmerzen“. Können sie stärker werden?",
            "Mit einer Kupferspirale können Blutungen und Schmerzen zunehmen. Prüfe, wie wichtig das für Laura ist."
          ],
          "H": [
            "Lies auf der Hormonspiralen-Karte „Blutung und Schmerzen“. Ist eine Wirkung garantiert?",
            "Blutungen und Schmerzen können geringer werden. Das ist keine Garantie. Die medizinische Eignung muss geklärt werden."
          ],
          "K+P": [
            "Lies die Pillen-Karte: „Blutung und Schmerzen“. Lies dann Lauras Nein zur Pille.",
            "Die Pille kann Beschwerden verringern. Das erlaubt aber nicht, Lauras Nein zu übergehen."
          ],
          "K+Cu": [
            "Lies auf der Kupferspiralen-Karte „Blutung und Schmerzen“. Können sie stärker werden?",
            "Mit einer Kupferspirale können Blutungen und Schmerzen zunehmen. Prüfe, wie wichtig das für Laura ist."
          ],
          "K+H": [
            "Lies auf der Hormonspiralen-Karte „Blutung und Schmerzen“. Ist eine Wirkung garantiert?",
            "Blutungen und Schmerzen können geringer werden. Das ist keine Garantie. Die medizinische Eignung muss geklärt werden."
          ]
        },
        "title": "Regelschmerzen",
        "questions": [
          [
            "Kennst du den Grund für die Schmerzen?",
            "Nein, das habe ich noch nicht untersuchen lassen."
          ],
          [
            "Wie wichtig sind dir die Schmerzen bei der Wahl?",
            "Sehr wichtig. Mehr Schmerzen wären für mich schwer auszuhalten."
          ]
        ],
        "helpBefore": [
          "Lies die Stelle über Schmerzen auf den Spiralen-Karten.",
          "Blutungen und Schmerzen können sich je nach Spirale anders verändern."
        ]
      },
      {
        "id": "L5",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Der Schutz vor Infektionen ist mir immer noch wichtig.",
            "Kondome wären für uns okay.",
            "Passt euer Vorschlag auch zu diesem Wunsch?"
          ],
          "ESA": [
            "Der Infektionsschutz ist mir weiterhin wichtig.",
            "Kondome würden für uns infrage kommen.",
            "Prüft eure bisherige Empfehlung noch einmal."
          ],
          "MSA": [
            "Die Verringerung des Infektionsrisikos bleibt für mich ein wichtiges Ziel.",
            "Kondome sind für uns vorstellbar.",
            "Prüft, ob euer Vorschlag beide Schutzziele berücksichtigt."
          ],
          "AHR": [
            "Die Verringerung des Infektionsrisikos bleibt eine eigenständige Priorität.",
            "Kondome sind für uns akzeptabel.",
            "Beurteilt, ob eure bisherige Strategie beide Schutzziele ausreichend berücksichtigt."
          ]
        },
        "task": {
          "Foerder": "Lies die neue Nachricht. Prüfe mit deiner Infokarte den Infektionsschutz.",
          "ESA": "Prüfe mit deinen Infokarten: Welche Ziele deckt dein Vorschlag ab?",
          "MSA": "Prüfe die beiden Schutzziele und mögliche Kombinationen.",
          "AHR": "Beurteile die Strategie im Hinblick auf zwei unterschiedliche Schutzziele."
        },
        "options": {
          "K": "Wir möchten dir ein Kondom vorschlagen.",
          "P": "Wir möchten dir die Kombinationspille vorschlagen.",
          "Cu": "Wir möchten dir die Kupferspirale vorschlagen.",
          "H": "Wir möchten dir die Hormonspirale vorschlagen.",
          "K+P": "Wir möchten dir ein Kondom und die Kombinationspille vorschlagen.",
          "K+Cu": "Wir möchten dir ein Kondom und die Kupferspirale vorschlagen.",
          "K+H": "Wir möchten dir ein Kondom und die Hormonspirale vorschlagen."
        },
        "replies": {
          "K": "Erklärt mir bitte, was das Kondom leisten kann und was nicht.",
          "P": "Die Pille möchte ich nicht. Und meine Frage zum Infektionsschutz bleibt auch noch offen.",
          "Cu": "Und wie berücksichtigt euer Vorschlag das Infektionsrisiko? Schaut noch einmal auf die Karten.",
          "H": "Welche Rolle spielt bei eurem Vorschlag mein Wunsch nach weniger Infektionsrisiko?",
          "K+P": "Das Kondom ist für uns vorstellbar. Die Pille möchte ich aber nicht nehmen.",
          "K+Cu": "Erklärt bitte beide Teile. Vergesst dabei meine Schmerzen und die offene Frage zum Einsetzen nicht.",
          "K+H": "Erklärt bitte, wozu beide Teile dienen. Bei der Spirale bleibt meine Entscheidung noch offen."
        },
        "hints": {
          "K": [
            "Lies auf der Kondom-Karte „Infektionsschutz“.",
            "Kondome verringern das Risiko vieler Infektionen beim Sex. Vollständigen Schutz vor allen Infektionen bieten sie nicht."
          ],
          "P": [
            "Lies auf der Pillen-Karte „Infektionsschutz“.",
            "Die Pille schützt nicht vor Infektionen beim Sex."
          ],
          "Cu": [
            "Lies auf der Kupferspiralen-Karte „Infektionsschutz“.",
            "Die Kupferspirale schützt nicht vor Infektionen beim Sex."
          ],
          "H": [
            "Lies auf der Hormonspiralen-Karte „Infektionsschutz“.",
            "Die Hormonspirale schützt nicht vor Infektionen beim Sex."
          ],
          "K+P": [
            "Lies auf beiden gewählten Karten „Infektionsschutz“. Welche Methode übernimmt diese Aufgabe?",
            "Das Kondom im Vorschlag senkt das Risiko vieler Infektionen beim Sex. Die andere Methode schützt davor nicht."
          ],
          "K+Cu": [
            "Lies auf beiden gewählten Karten „Infektionsschutz“. Welche Methode übernimmt diese Aufgabe?",
            "Das Kondom im Vorschlag senkt das Risiko vieler Infektionen beim Sex. Die andere Methode schützt davor nicht."
          ],
          "K+H": [
            "Lies auf beiden gewählten Karten „Infektionsschutz“. Welche Methode übernimmt diese Aufgabe?",
            "Das Kondom im Vorschlag senkt das Risiko vieler Infektionen beim Sex. Die andere Methode schützt davor nicht."
          ]
        },
        "title": "Zwei Schutzziele",
        "questions": [
          [
            "Welche Rolle spielt der Schutz vor Infektionen?",
            "Den möchte ich bei meiner Entscheidung behalten."
          ],
          [
            "Wäre ein Kondom für euch möglich?",
            "Ja, wir können uns vorstellen, es jedes Mal zu benutzen."
          ]
        ],
        "helpBefore": [
          "Lies auf zwei Karten den Abschnitt „Infektionsschutz“.",
          "Schutz vor Schwangerschaft und Schutz vor Infektionen sind zwei verschiedene Ziele."
        ]
      },
      {
        "id": "L6",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Jetzt kennt ihr meine Wünsche.",
            "Welche Verhütung würdet ihr mir vorschlagen? Nennt bitte auch einen Nachteil.",
            "Ich möchte nach einer Beratung selbst entscheiden."
          ],
          "ESA": [
            "Jetzt kennt ihr meine Wünsche und Sorgen.",
            "Welche Verhütungsstrategie schlagt ihr mir vor? Begründet sie und nennt einen Nachteil.",
            "Die Entscheidung treffe ich nach einer Beratung selbst."
          ],
          "MSA": [
            "Ihr kennt jetzt meine verschiedenen Ziele und Grenzen.",
            "Vergleicht die ernsthaft infrage kommenden Verhütungsstrategien. Welche würdet ihr begründet vorschlagen?",
            "Ich möchte erst nach medizinischer Beratung selbst entscheiden."
          ],
          "AHR": [
            "Jetzt kennt ihr meine wichtigsten Wünsche, Sorgen und eine klare Grenze.",
            "Welche akzeptable Strategie würdet ihr begründet vorschlagen und unter welcher Bedingung könnte eine Alternative besser passen?",
            "Was medizinisch zu mir passt, will ich in einer Praxis klären. Entscheiden möchte ich selbst."
          ]
        },
        "task": {
          "Foerder": "Vergleiche zwei Vorschläge. Was passt für Laura? Was spricht dagegen?",
          "ESA": "Vergleiche zwei Vorschläge. Welcher Grund zählt für Laura am meisten?",
          "MSA": "Gewichte Schutz und Anwendung. Prüfe deinen Vorschlag an einem Einwand.",
          "AHR": "Vergleicht zwei akzeptable Strategien. Wann würde sich eure Gewichtung ändern?"
        },
        "options": {
          "K": "Wir würden dir ein Kondom empfehlen.",
          "P": "Wir würden dir die Kombinationspille empfehlen.",
          "Cu": "Wir würden dir die Kupferspirale empfehlen.",
          "H": "Wir würden dir die Hormonspirale empfehlen.",
          "K+P": "Wir würden dir ein Kondom und die Kombinationspille empfehlen.",
          "K+Cu": "Wir würden dir ein Kondom und die Kupferspirale empfehlen.",
          "K+H": "Wir würden dir ein Kondom und die Hormonspirale empfehlen."
        },
        "replies": {
          "K": "Das kann ich mir vorstellen. Was müsste bei uns jedes Mal klappen?",
          "P": "Die Pille möchte ich weiterhin nicht. Wie passt euer Vorschlag zu meinem Nein?",
          "Cu": "Bei diesem Vorschlag sind meine Schmerzen und der Infektionsschutz noch zu prüfen.",
          "H": "Die Entscheidung über die Spirale ist noch offen. Und wie wird der Infektionsschutz berücksichtigt?",
          "K+P": "Die Pille gehört weiter zu eurem Vorschlag. Die möchte ich aber nicht. Prüft das noch einmal.",
          "K+Cu": "Die Kupferspirale braucht wegen meiner Beschwerden eine besonders sorgfältige Abklärung. Begründet euren Vorschlag und seine Grenze.",
          "K+H": "Die Hormonspirale kommt nur nach Beratung und mit meiner Zustimmung infrage. Begründet bitte auch, weshalb ihr sie zusätzlich vorschlagt."
        },
        "hints": {
          "K": [
            "Lies auf der Kondom-Karte „Anwendung“. Was muss jedes Mal klappen?",
            "Ein Kondom senkt auch das Infektionsrisiko. Falsch benutzt schützt es schlechter."
          ],
          "P": [
            "Lies im Chat, was Laura über die Pille entschieden hat.",
            "Laura sagt Nein zur Pille. Auch ein guter Schutz hebt ihr Nein nicht auf."
          ],
          "Cu": [
            "Lies auf der Kupferspiralen-Karte „Blutung und Schmerzen“. Was ist Laura wichtig?",
            "Die Periode kann mehr wehtun. Die Kupferspirale schützt nicht vor Infektionen."
          ],
          "H": [
            "Lies auf der Hormonspiralen-Karte „Anwendung“ und „Infektionsschutz“.",
            "Die Hormonspirale wirkt lange. Sie schützt nicht vor Infektionen. Laura hat der Einlage noch nicht zugestimmt."
          ],
          "K+P": [
            "Lies Lauras Nachricht zur Pille. Was steckt in deinem Vorschlag?",
            "Das Kondom senkt das Infektionsrisiko. Die Pille hat Laura abgelehnt."
          ],
          "K+Cu": [
            "Lies auf der Kupferspiralen-Karte die Stelle zur Periode. Vergleiche mit Lauras Wunsch.",
            "Das Kondom senkt das Infektionsrisiko. Die Kupferspirale kann Schmerzen verstärken."
          ],
          "K+H": [
            "Lies auf der Hormonspiralen-Karte „Anwendung“. Was muss Laura noch klären?",
            "Das Kondom senkt das Infektionsrisiko. Die Hormonspirale wirkt lange. Vor der Einlage braucht Laura Beratung."
          ]
        },
        "title": "Dein Rat an Laura",
        "questions": [
          [
            "Was hast du schon entschieden?",
            "Die Pille möchte ich nicht. Ein Kondom ist für uns möglich."
          ],
          [
            "Was möchtest du noch klären?",
            "Die Schmerzen und meine Fragen zu einer Spirale möchte ich in einer Praxis besprechen."
          ]
        ],
        "helpBefore": [
          "Suche im Chat Lauras Nein und einen Wunsch.",
          "Ein Kondom wäre für sie möglich. Über eine Spirale möchte sie erst mehr wissen."
        ]
      }
    ],
    "Celina": [
      {
        "id": "C0",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Hi, ich bin Celina. Ich bin 17.",
            "Ich möchte nicht schwanger werden. Zusätzliche Hormone möchte ich nicht.",
            "Was könnt ihr mir vorschlagen?"
          ],
          "ESA": [
            "Hi, ich bin Celina, 17. Ich suche eine zuverlässige Verhütung ohne zusätzliche Hormone.",
            "Welche Möglichkeiten würdet ihr mit mir vergleichen?"
          ],
          "MSA": [
            "Ich bin Celina, 17, und möchte in den nächsten Jahren nicht schwanger werden.",
            "Ich habe entschieden: keine zusätzlichen Hormone zur Verhütung. Welche Möglichkeiten bleiben?"
          ],
          "AHR": [
            "Ich bin Celina, 17. Eine Schwangerschaft möchte ich derzeit vermeiden.",
            "Zusätzliche Hormone lehne ich für meine Verhütung ab. Vergleicht die verbleibenden Möglichkeiten, statt meine Grenze neu zu verhandeln."
          ]
        },
        "task": {
          "Foerder": "Lies auf den vier Karten „Wirkung“. Wähle einen Vorschlag.",
          "ESA": "Prüfe die Karten: Welche Methoden enthalten Hormone? Wähle einen Vorschlag.",
          "MSA": "Vergleiche zwei hormonfreie Strategien.",
          "AHR": "Trenne akzeptable Optionen und Gewichtung. Formuliere einen vorläufigen Vorschlag."
        },
        "options": {
          "K": "Wir schlagen dir ein Kondom vor.",
          "P": "Wir schlagen dir die Kombinationspille vor.",
          "Cu": "Wir schlagen dir die Kupferspirale vor.",
          "H": "Wir schlagen dir die Hormonspirale vor.",
          "K+P": "Wir schlagen dir ein Kondom und die Kombinationspille vor.",
          "K+Cu": "Wir schlagen dir ein Kondom und die Kupferspirale vor.",
          "K+H": "Wir schlagen dir ein Kondom und die Hormonspirale vor."
        },
        "replies": {
          "K": "Das ist ohne zusätzliche Hormone. Was müsste ich bei der Anwendung beachten?",
          "P": "Die Pille enthält Hormone. Die möchte ich nicht zusätzlich nehmen.",
          "Cu": "Über eine Kupferspirale würde ich gern mehr wissen.",
          "H": "Auch die Hormonspirale enthält Hormone. Die möchte ich nicht.",
          "K+P": "Die Kombination enthält die Pille. Ich möchte ohne zusätzliche Hormone verhüten.",
          "K+Cu": "Ihr nennt eine hormonfreie Kombination. Was spricht für beide Teile?",
          "K+H": "In eurem Vorschlag ist eine Hormonspirale. Mein Wunsch ist aber hormonfrei."
        },
        "hints": {
          "K": [
            "Lies auf der Kondom-Karte „Mögliche Nachteile“.",
            "Das Kondom enthält keine Hormone. Die richtige Anwendung ist für den Schutz wichtig."
          ],
          "P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Lies auf der Kupferspiralen-Karte „Mögliche Nachteile“.",
            "Ohne Hormone bedeutet nicht ohne mögliche Nachteile. Blutungen und Schmerzen können stärker werden."
          ],
          "H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Lies auf der Kupferspiralen-Karte „Mögliche Nachteile“.",
            "Ohne Hormone bedeutet nicht ohne mögliche Nachteile. Blutungen und Schmerzen können stärker werden."
          ],
          "K+H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ]
        },
        "title": "Ohne zusätzliche Hormone",
        "questions": [
          [
            "Was bedeutet „ohne Hormone“ für dich?",
            "Ich möchte zur Verhütung keine zusätzlichen Hormone nehmen."
          ],
          [
            "Was soll die Methode für dich leisten?",
            "Sie soll mich zuverlässig vor einer Schwangerschaft schützen."
          ]
        ],
        "helpBefore": [
          "Lies Celinas ersten Wunsch. Schau auf der Karte unter „Wirkung“ nach.",
          "Celina möchte ohne zusätzliche Hormone verhüten."
        ]
      },
      {
        "id": "C1",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Ich möchte länger verhüten. Später möchte ich vielleicht ein Kind.",
            "Eine tägliche Aufgabe möchte ich nicht. Kondome wären für uns möglich."
          ],
          "ESA": [
            "Ich suche etwas für längere Zeit, aber nichts Dauerhaftes. Später möchte ich vielleicht ein Kind.",
            "An eine tägliche Aufgabe möchte ich nicht denken müssen. Kondome sind für uns vorstellbar."
          ],
          "MSA": [
            "Die Methode soll für die nächsten Jahre passen, aber später beendet werden können.",
            "Wenig täglicher Aufwand ist mir wichtig. Kondome akzeptieren wir."
          ],
          "AHR": [
            "Langfristige Verhütung ist mir wichtig; meine spätere Entscheidung für ein Kind soll offenbleiben.",
            "Ich möchte wenig Alltagsaufwand. Eine zusätzliche Belastung nehme ich aber nicht automatisch für höhere Sicherheit in Kauf.",
            "Kondome akzeptieren wir."
          ]
        },
        "task": {
          "Foerder": "Lies „Anwendung“ auf der Kondom-Karte und der Kupferspiralen-Karte. Prüfe deinen Vorschlag.",
          "ESA": "Vergleiche Anwendung und Dauer bei Kondom und Kupferspirale.",
          "MSA": "Vergleiche reversiblen Langzeitschutz mit situationsbezogener Anwendung.",
          "AHR": "Prüfe den Unterschied zwischen lang wirkend und dauerhaft. Begründe eine Gewichtung."
        },
        "options": {
          "K": "Wir möchten dir ein Kondom vorschlagen.",
          "P": "Wir möchten dir die Kombinationspille vorschlagen.",
          "Cu": "Wir möchten dir die Kupferspirale vorschlagen.",
          "H": "Wir möchten dir die Hormonspirale vorschlagen.",
          "K+P": "Wir möchten dir ein Kondom und die Kombinationspille vorschlagen.",
          "K+Cu": "Wir möchten dir ein Kondom und die Kupferspirale vorschlagen.",
          "K+H": "Wir möchten dir ein Kondom und die Hormonspirale vorschlagen."
        },
        "replies": {
          "K": "Beim Sex müssten wir dann immer daran denken. Das können wir uns vorstellen.",
          "P": "Die tägliche Tablette passt nicht zu meinem Wunsch. Zusätzliche Hormone möchte ich nicht.",
          "Cu": "Das klingt nach einer länger wirkenden Möglichkeit. Vor dem Einsetzen hätte ich Fragen.",
          "H": "Wenig täglicher Aufwand wäre gut. Trotzdem habe ich Hormone abgelehnt.",
          "K+P": "Das Kondom wäre möglich. Die Pille bleibt für mich ausgeschlossen.",
          "K+Cu": "Wie unterscheiden sich die Aufgaben der beiden Methoden im Alltag?",
          "K+H": "Die Hormonspirale möchte ich nicht. Mein Wunsch nach wenig Aufwand ändert das nicht."
        },
        "hints": {
          "K": [
            "Lies auf der Kondom-Karte „Anwendung“. Wann braucht man es?",
            "Das Kondom wird bei jedem Sex neu und richtig verwendet. Es ist keine tägliche Tablette."
          ],
          "P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Lies auf der Kupferspiralen-Karte „Anwendung“. Wer setzt sie ein?",
            "Eine Ärztin oder ein Arzt setzt sie ein. Es gibt keine tägliche Einnahme. Kontrollen bleiben wichtig."
          ],
          "H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Lies auf der Kupferspiralen-Karte „Anwendung“. Wer setzt sie ein?",
            "Eine Ärztin oder ein Arzt setzt sie ein. Es gibt keine tägliche Einnahme. Kontrollen bleiben wichtig."
          ],
          "K+H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ]
        },
        "title": "Schutz über längere Zeit",
        "questions": [
          [
            "Was meinst du mit „für längere Zeit“?",
            "Ich möchte mehrere Jahre verhüten. Später möchte ich vielleicht ein Kind."
          ],
          [
            "Wie viel Aufwand passt für dich?",
            "Nicht jeden Tag daran denken zu müssen, wäre gut. Kondome wären für uns möglich."
          ]
        ],
        "helpBefore": [
          "Lies auf der Karte „Anwendung“. Wann muss Celina daran denken?",
          "Eine Spirale bleibt längere Zeit im Körper. Ein Kondom braucht man bei jedem Sex neu."
        ]
      },
      {
        "id": "C2",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Vor dem Einsetzen einer Spirale habe ich Angst. Ich sage aber noch nicht Nein.",
            "Meine Periode ist meistens ohne starke Schmerzen.",
            "Ob eine Spirale für mich geeignet ist, weiß ich noch nicht."
          ],
          "ESA": [
            "Das Einsetzen einer Spirale macht mir Sorgen. Ganz ausgeschlossen habe ich sie nicht.",
            "Meine Periode ist meist ohne starke Schmerzen. Die medizinische Eignung ist noch nicht geklärt."
          ],
          "MSA": [
            "Vor der Einlage habe ich Respekt, aber ich lehne sie noch nicht ab.",
            "Meine Blutung ist meist wenig schmerzhaft. Daraus folgt wohl noch nicht, dass die Spirale medizinisch sicher passt."
          ],
          "AHR": [
            "Ich bin wegen der Einlage unsicher, nicht grundsätzlich dagegen.",
            "Meine Periode ist meist wenig schmerzhaft; eine ärztliche Eignungsprüfung fehlt. Wie geht ihr mit dieser Unsicherheit um?"
          ]
        },
        "task": {
          "Foerder": "Lies auf der Kupferspiralen-Karte „Mögliche Nachteile“. Vergleiche mit dem Kondom.",
          "ESA": "Vergleiche mögliche Nachteile und Anwendung. Beachte: Celina hat zur Spirale noch nicht Nein gesagt.",
          "MSA": "Erkläre, welche Sorge abwägbar bleibt und welche Entscheidung noch offen ist.",
          "AHR": "Entwickle zwei bedingte Wege abhängig von Celinas späterer Zustimmung, ohne medizinische Eignung zu unterstellen."
        },
        "options": {
          "K": "Unser Vorschlag ist: Ein Kondom.",
          "P": "Unser Vorschlag ist: Die Kombinationspille.",
          "Cu": "Unser Vorschlag ist: Die Kupferspirale.",
          "H": "Unser Vorschlag ist: Die Hormonspirale.",
          "K+P": "Unser Vorschlag ist: Ein Kondom und die Kombinationspille.",
          "K+Cu": "Unser Vorschlag ist: Ein Kondom und die Kupferspirale.",
          "K+H": "Unser Vorschlag ist: Ein Kondom und die Hormonspirale."
        },
        "replies": {
          "K": "Das wäre ohne Einsetzen einer Spirale. Wie wägt ihr den Schutz im Alltag ab?",
          "P": "Meine Sorge vor der Einlage ist kein Ja zur Pille. Hormone möchte ich nicht.",
          "Cu": "Eine Einlage habe ich noch nicht ausgeschlossen. Aber ich möchte vorher Beratung.",
          "H": "Die Unsicherheit bei der Einlage ändert nichts an meinem Nein zu Hormonen.",
          "K+P": "Die Pille bleibt für mich ausgeschlossen. Bitte prüft die andere Möglichkeit.",
          "K+Cu": "Diese Möglichkeit würde ich nach Beratung abwägen. Sagt mir bitte auch, was dagegen spricht.",
          "K+H": "Mein Nein zu zusätzlichen Hormonen gilt weiterhin."
        },
        "hints": {
          "K": [
            "Lies auf der Kupferspiralen-Karte „Mögliche Nachteile“. Vergleiche mit dem Kondom.",
            "Eine Kupferspirale muss eingesetzt werden. Blutungen und Schmerzen können zunehmen. Ein Kondom braucht keine Einlage. Vergleiche auch die Sicherheit."
          ],
          "P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Lies auf der Kupferspiralen-Karte „Mögliche Nachteile“. Vergleiche mit dem Kondom.",
            "Eine Kupferspirale muss eingesetzt werden. Blutungen und Schmerzen können zunehmen. Ein Kondom braucht keine Einlage. Vergleiche auch die Sicherheit."
          ],
          "H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Lies auf der Kupferspiralen-Karte „Mögliche Nachteile“. Vergleiche mit dem Kondom.",
            "Eine Kupferspirale muss eingesetzt werden. Blutungen und Schmerzen können zunehmen. Ein Kondom braucht keine Einlage. Vergleiche auch die Sicherheit."
          ],
          "K+H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ]
        },
        "title": "Sorge vor dem Einsetzen",
        "questions": [
          [
            "Hast du dich gegen eine Spirale entschieden?",
            "Nein. Das Einsetzen macht mir Sorgen. Ich möchte erst mehr erfahren."
          ],
          [
            "Weißt du schon, ob eine Spirale für dich passt?",
            "Das weiß ich noch nicht. Das möchte ich in der Praxis klären."
          ]
        ],
        "helpBefore": [
          "Lies Celinas Satz über das Einsetzen.",
          "Celina hat Angst vor der Einlage. Sie hat noch nicht Nein gesagt."
        ]
      },
      {
        "id": "C3",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Wir sind fest zusammen. Wir vertrauen uns.",
            "Trotzdem möchte ich das Risiko sexuell übertragbarer Infektionen kleiner machen.",
            "Was muss unser Vorschlag dafür leisten?"
          ],
          "ESA": [
            "Wir sind fest zusammen und vertrauen uns. Trotzdem möchte ich auch das STI-Risiko verringern.",
            "Wie passt das zu eurem Vorschlag?"
          ],
          "MSA": [
            "Eine feste Beziehung ersetzt für mich keinen Infektionsschutz. Auch dieses Risiko möchte ich verringern.",
            "Prüft euren Vorschlag darauf."
          ],
          "AHR": [
            "Vertrauen ist mir wichtig, aber es ist kein medizinischer Nachweis eines Infektionsstatus.",
            "Ich möchte das STI-Risiko verringern. Prüft die Schutzfunktionen eurer Strategie getrennt."
          ]
        },
        "task": {
          "Foerder": "Lies auf deinen gewählten Karten „Infektionsschutz“. Wähle erneut.",
          "ESA": "Prüfe den Infektionsschutz. Du darfst Methoden kombinieren.",
          "MSA": "Begründe eine Strategie, die beide Schutzziele berücksichtigt.",
          "AHR": "Begründe, welche Aussagen zum Schutz durch die Angaben gedeckt sind und welche nicht."
        },
        "options": {
          "K": "Wir würden dir ein Kondom vorschlagen.",
          "P": "Wir würden dir die Kombinationspille vorschlagen.",
          "Cu": "Wir würden dir die Kupferspirale vorschlagen.",
          "H": "Wir würden dir die Hormonspirale vorschlagen.",
          "K+P": "Wir würden dir ein Kondom und die Kombinationspille vorschlagen.",
          "K+Cu": "Wir würden dir ein Kondom und die Kupferspirale vorschlagen.",
          "K+H": "Wir würden dir ein Kondom und die Hormonspirale vorschlagen."
        },
        "replies": {
          "K": "Erklärt bitte auch, welche Grenzen das Kondom hat.",
          "P": "Die Pille möchte ich nicht. Und meine Frage zum Infektionsschutz ist damit noch offen.",
          "Cu": "Was ist bei eurem Vorschlag mit meinem Wunsch nach Infektionsschutz?",
          "H": "Die Hormonspirale enthält Hormone. Auch den Infektionsschutz müsst ihr getrennt prüfen.",
          "K+P": "Das Kondom ist möglich. Die Pille ist für mich weiter keine Option.",
          "K+Cu": "Erklärt, welche Aufgabe jeder Teil übernimmt. Meine Zustimmung zur Spirale ist noch offen.",
          "K+H": "Das Kondom ist möglich. Die Hormonspirale möchte ich aber nicht."
        },
        "hints": {
          "K": [
            "Lies auf der Kondom-Karte „Infektionsschutz“.",
            "Kondome verringern das Risiko vieler Infektionen beim Sex. Vollständigen Schutz vor allen Infektionen bieten sie nicht."
          ],
          "P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Lies auf der Kupferspiralen-Karte „Infektionsschutz“.",
            "Die Kupferspirale schützt nicht vor Infektionen beim Sex."
          ],
          "H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Lies auf beiden gewählten Karten „Infektionsschutz“. Welche Methode übernimmt diese Aufgabe?",
            "Das Kondom im Vorschlag senkt das Risiko vieler Infektionen beim Sex. Die andere Methode schützt davor nicht."
          ],
          "K+H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ]
        },
        "title": "Schutz in der Beziehung",
        "questions": [
          [
            "Welcher Schutz ist dir jetzt noch wichtig?",
            "Auch den Schutz vor Infektionen möchte ich mitbedenken."
          ],
          [
            "Gilt dein Wunsch zu Hormonen noch?",
            "Ja, ich möchte weiterhin ohne zusätzliche Hormone verhüten."
          ]
        ],
        "helpBefore": [
          "Lies auf deiner Karte „Infektionsschutz“.",
          "Vertrauen sagt nichts Sicheres über eine Infektion aus."
        ]
      },
      {
        "id": "C4",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Ich möchte keine zusätzlichen Hormone.",
            "Über eine Spirale will ich erst beraten werden.",
            "Welchen Vorschlag macht ihr mir? Nennt auch einen Nachteil."
          ],
          "ESA": [
            "Bitte nennt mir euren Vorschlag und einen Grund, der besonders für mich zählt.",
            "Welche andere Möglichkeit wäre ebenfalls vertretbar? Ich entscheide nach Beratung selbst."
          ],
          "MSA": [
            "Begründet eure Empfehlung gegenüber einer Alternative.",
            "Was bleibt offen, obwohl ihr die Fachinformationen geprüft habt?"
          ],
          "AHR": [
            "Formuliert einen begründeten Vorschlag mit einer Bedingung.",
            "Welche neue Entscheidung von mir würde ihn verändern, und welche fachlichen Aussagen blieben gleich?"
          ]
        },
        "task": {
          "Foerder": "Was passt für Celina? Nenne einen Grund und einen Nachteil.",
          "ESA": "Vergleiche zwei Vorschläge. Erkläre, welcher besser zu Celinas Wünschen passt.",
          "MSA": "Wäge Aufwand und Sicherheit ab. Was bleibt für Celina offen?",
          "AHR": "Prüfe, wie eine andere Gewichtung oder Celinas Entscheidung eure Empfehlung verändert."
        },
        "options": {
          "K": "Wir schlagen dir ein Kondom vor.",
          "P": "Wir schlagen dir die Kombinationspille vor.",
          "Cu": "Wir schlagen dir die Kupferspirale vor.",
          "H": "Wir schlagen dir die Hormonspirale vor.",
          "K+P": "Wir schlagen dir ein Kondom und die Kombinationspille vor.",
          "K+Cu": "Wir schlagen dir ein Kondom und die Kupferspirale vor.",
          "K+H": "Wir schlagen dir ein Kondom und die Hormonspirale vor."
        },
        "replies": {
          "K": "Begründet euren Vorschlag bitte mit meinen Wünschen und einer Fachinformation.",
          "P": "Die Pille widerspricht meinem Nein zu zusätzlichen Hormonen. Prüft euren Vorschlag noch einmal.",
          "Cu": "Vor der Einlage brauche ich Beratung. Den Infektionsschutz müsst ihr noch ergänzen oder klären.",
          "H": "Ich möchte ohne zusätzliche Hormone verhüten. Das gilt auch für die Hormonspirale.",
          "K+P": "Die Pille möchte ich nicht. Prüft euren Vorschlag vor dem Aufschreiben.",
          "K+Cu": "Die Kupferspirale kommt nur infrage, wenn ich nach Beratung zustimme. Begründet auch, warum ihr sie zusätzlich vorschlagt.",
          "K+H": "Meine Grenze zu Hormonen bleibt bestehen. Prüft den Vorschlag noch einmal."
        },
        "hints": {
          "K": [
            "Lies auf der Kondom-Karte „Anwendung“. Was muss jedes Mal klappen?",
            "Ein Kondom enthält keine Hormone. Beide müssen jedes Mal daran denken."
          ],
          "P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Lies Celinas Nachricht über das Einsetzen. Was ist noch offen?",
            "Die Kupferspirale wirkt lange ohne Hormone. Celina möchte sich erst beraten lassen."
          ],
          "H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Lies auf der Karte „Kombinationspille“ die Stelle zur Wirkung.",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Lies Celinas Nachricht über das Einsetzen. Was ist noch offen?",
            "Die Kupferspirale wirkt lange ohne Hormone. Celina möchte sich erst beraten lassen."
          ],
          "K+H": [
            "Lies auf der Karte „Hormonspirale“ die Stelle zur Wirkung.",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ]
        },
        "title": "Dein Rat an Celina",
        "questions": [
          [
            "Was ist bei der Spirale noch offen?",
            "Ob sie für meinen Körper passt. Und ob ich sie nach der Beratung möchte."
          ],
          [
            "Welche Aufgabe wäre im Alltag für euch möglich?",
            "Ein Kondom bei jedem Sex wäre für uns möglich."
          ]
        ],
        "helpBefore": [
          "Lies noch einmal, was Celina zu Hormonen und zum Einsetzen sagt.",
          "Sie möchte keine Hormone. Über die Spirale entscheidet sie erst nach einer Beratung."
        ]
      }
    ],
    "Tom": [
      {
        "id": "T0",
        "type": "recommend",
        "message": {
          "Foerder": [
            "Hi, ich bin Tom. Ich bin 17.",
            "Ich möchte auch Verantwortung für Verhütung übernehmen.",
            "Welche Methode kann ich selbst benutzen?"
          ],
          "ESA": [
            "Hi, ich bin Tom, 17. Verhütung soll nicht nur Aufgabe meiner Freundin sein.",
            "Ich suche eine Methode, die ich selbst anwenden kann. Welche schlagt ihr vor?"
          ],
          "MSA": [
            "Ich bin Tom, 17, und möchte selbst zur Verhütung beitragen.",
            "Welche der bekannten Methoden kann ich selbst anwenden? Nicht: Welche soll meine Freundin für mich nehmen?"
          ],
          "AHR": [
            "Hi, ich bin Tom, 17.",
            "Ich möchte meinen eigenen Beitrag zur Verhütung leisten, ohne meiner Freundin eine Methode vorzuschreiben.",
            "Welche der behandelten Methoden kann ich selbst anwenden?"
          ]
        },
        "task": {
          "Foerder": "Lies auf den Karten „Anwendung“. Wähle deinen Vorschlag.",
          "ESA": "Prüfe, wer die Methode selbst anwenden kann.",
          "MSA": "Unterscheide eigene Anwendung und eine gemeinsam besprochene Strategie.",
          "AHR": "Prüfe körperliche Anwendungsvoraussetzungen und Entscheidungsrechte getrennt."
        },
        "options": {
          "K": "Wir schlagen dir ein Kondom vor.",
          "P": "Wir schlagen dir die Kombinationspille vor.",
          "Cu": "Wir schlagen dir die Kupferspirale vor.",
          "H": "Wir schlagen dir die Hormonspirale vor.",
          "K+P": "Wir schlagen dir ein Kondom und die Kombinationspille vor.",
          "K+Cu": "Wir schlagen dir ein Kondom und die Kupferspirale vor.",
          "K+H": "Wir schlagen dir ein Kondom und die Hormonspirale vor."
        },
        "replies": {
          "K": "Ein Kondom kann ich selbst benutzen. Ich hätte gern noch weitere Möglichkeiten. Dazu habe ich einen Artikel gefunden.",
          "P": "Diese Pille wirkt auf einen Zyklus mit Eisprung. So einen Zyklus habe ich nicht. Ich suche etwas, das ich selbst anwenden kann.",
          "Cu": "Eine Kupferspirale wird in eine Gebärmutter eingesetzt. Die habe ich nicht. Ich suche eine Methode für mich.",
          "H": "Auch eine Hormonspirale wird in eine Gebärmutter eingesetzt. Die habe ich nicht. Welche Methode kann ich selbst anwenden?",
          "K+P": "Das Kondom kann ich benutzen. Die Pille wäre aber nicht meine eigene Methode. Darüber entscheidet meine Freundin selbst.",
          "K+Cu": "Das Kondom ist mein eigener Beitrag. Eine Kupferspirale würde meine Freundin betreffen; das wäre ihre Entscheidung.",
          "K+H": "Das Kondom kann ich selbst verwenden. Eine Hormonspirale kann ich nicht für meine Freundin auswählen."
        },
        "hints": {
          "K": [
            "Lies auf der Karte „Kondom“ den Abschnitt „Anwendung“.",
            "Ein Kondom benutzt Tom an seinem Penis."
          ],
          "P": [
            "Lies auf der Karte „Kombinationspille“ den Abschnitt „Anwendung“.",
            "Die Kombinationspille hemmt den Eisprung. Tom hat keinen Eisprung."
          ],
          "Cu": [
            "Lies auf der Karte „Kupferspirale“ den Abschnitt „Anwendung“.",
            "Eine Kupferspirale wird in eine Gebärmutter eingesetzt. Tom hat keine."
          ],
          "H": [
            "Lies auf der Karte „Hormonspirale“ den Abschnitt „Anwendung“.",
            "Eine Hormonspirale wird in eine Gebärmutter eingesetzt. Tom hat keine."
          ],
          "K+P": [
            "Lies auf der Karte „Kombinationspille“ den Abschnitt „Anwendung“.",
            "Die Kombinationspille hemmt den Eisprung. Tom hat keinen Eisprung."
          ],
          "K+Cu": [
            "Lies auf der Karte „Kupferspirale“ den Abschnitt „Anwendung“.",
            "Eine Kupferspirale wird in eine Gebärmutter eingesetzt. Tom hat keine."
          ],
          "K+H": [
            "Lies auf der Karte „Hormonspirale“ den Abschnitt „Anwendung“.",
            "Eine Hormonspirale wird in eine Gebärmutter eingesetzt. Tom hat keine."
          ]
        },
        "title": "Selbst verhüten",
        "questions": [
          [
            "Was möchtest du selbst übernehmen?",
            "Ich möchte selbst ein Mittel zur Verhütung benutzen können."
          ],
          [
            "Wer entscheidet bei einer gemeinsamen Strategie?",
            "Meine Freundin entscheidet über ihren Körper. Ich entscheide über meinen. Wir reden darüber."
          ]
        ],
        "helpBefore": [
          "Lies auf den Karten „Anwendung“. Wer benutzt die Methode?",
          "Tom fragt nach einer Methode für seinen eigenen Körper."
        ]
      },
      {
        "id": "T1",
        "type": "article",
        "message": {
          "Foerder": [
            "Ein Kondom kann ich selbst benutzen. Ich hätte aber gern mehr Auswahl.",
            "Ich habe dazu einen kurzen Artikel gefunden. Lest ihr mit?"
          ],
          "ESA": [
            "Kondome sind eine Möglichkeit. Trotzdem wünsche ich mir mehr Auswahl.",
            "Hier ist ein Artikel über neue Mittel. Was kann man daraus schließen?"
          ],
          "MSA": [
            "Eine weitere selbst anwendbare Möglichkeit wäre interessant.",
            "Ich habe einen Artikel über Forschung gefunden. Warum dauert die Entwicklung wohl so lange?"
          ],
          "AHR": [
            "Mehr reversible, selbst anwendbare Optionen wären interessant.",
            "Hier sind ein Artikel und zwei veröffentlichte Studien. Was rechtfertigen die Ergebnisse wirklich?"
          ]
        },
        "task": {
          "Foerder": "Lies den Artikel. Warum braucht die Forschung Zeit? Sag deinen Grund.",
          "ESA": "Lies den Artikel. Verbinde zwei Hinweise zu einer Vermutung.",
          "MSA": "Vergleiche zwei Ansätze. Erkläre mit dem Artikel eine mögliche Hürde.",
          "AHR": "Vergleiche die beiden Studien. Welche misst Schwangerschaften? Welche prüft Verträglichkeit?"
        },
        "options": {
          "DONE": "Wir haben den Artikel gelesen und unsere Vermutung besprochen."
        },
        "replies": {
          "DONE": "Welche eurer Ideen lässt sich mit dem Text belegen?"
        },
        "hints": {
          "DONE": {
            "Foerder": [
              "Lies im Artikel die Stelle über die Tests. Was muss ein neues Mittel können?",
              "Eine Testfrage kann lauten: Verhindert es Schwangerschaften? Welche Nebenwirkungen gibt es? Kehrt die Fruchtbarkeit zurück?"
            ],
            "ESA": [
              "Lies im Artikel den Absatz über die Prüfung eines neuen Mittels.",
              "Es kann einige Zeit dauern, bis klar ist, ob ein Mittel gut schützt und vertragen wird."
            ],
            "MSA": [
              "Lies im Artikel den Absatz über die Spermienzahl. Was verrät dieser Messwert?",
              "Ein Ergebnis belegt nur das, was mit der beschriebenen Methode untersucht wurde."
            ],
            "AHR": [
              "Vergleiche Zielgruppe, Vergleichsgruppe, Messgröße und Dauer beider Studien.",
              "In Studie B waren die Teilnehmer bereits vasektomiert. Spermienparameter wurden nicht gemessen. Prüfe, was das für die Behauptung über Schwangerschaftsschutz bedeutet."
            ]
          }
        },
        "title": "Ein Artikel von Tom",
        "questions": [],
        "helpBefore": [
          "Lies den Absatz über die Prüfung eines neuen Mittels.",
          "Forschende prüfen Wirkung und Risiken getrennt. Das braucht Zeit."
        ]
      },
      {
        "id": "T2",
        "type": "reason_on_paper",
        "message": {
          "Foerder": [
            "Ist eure Vermutung schon bewiesen?",
            "Was müsste man noch untersuchen?"
          ],
          "ESA": [
            "Eure Idee soll auf dem Artikel beruhen. Ist sie damit schon bewiesen?",
            "Welche Frage müsste eine Untersuchung beantworten?"
          ],
          "MSA": [
            "Erklärt ihr mit dem Text wirklich alle Gründe für die geringe Auswahl?",
            "Welche zusätzliche Information wäre nötig?"
          ],
          "AHR": [
            "Ein Forschungsergebnis ist nicht automatisch eine Zulassungsempfehlung.",
            "Welche Grenzen entstehen durch Stichprobe, Beobachtungsdauer und untersuchten Endpunkt?"
          ]
        },
        "task": {
          "Foerder": "Notiere eine Vermutung und eine offene Frage.",
          "ESA": "Notiere deine Vermutung mit einem Grund aus dem Artikel. Was ist noch offen?",
          "MSA": "Notiere einen Befund, deine Vermutung und eine offene Frage.",
          "AHR": "Prüfe die Behauptung „Studie B belegt sicheren Schutz“. Nutze zwei Befunde und zwei Grenzen. Skizziere eine Folgeuntersuchung mit Zielgruppe, Vergleich und Endpunkt."
        },
        "options": {
          "DONE": "Wir haben unsere Überlegungen aufgeschrieben."
        },
        "replies": {
          "DONE": "Danke fürs Mitdenken. Eure Vermutung und eure offene Frage könnt ihr später gemeinsam prüfen."
        },
        "hints": {
          "DONE": {
            "Foerder": [
              "Lies im Artikel die Stelle über die Tests. Was muss ein neues Mittel können?",
              "Eine Testfrage kann lauten: Verhindert es Schwangerschaften? Welche Nebenwirkungen gibt es? Kehrt die Fruchtbarkeit zurück?"
            ],
            "ESA": [
              "Lies im Artikel den Absatz über die Prüfung eines neuen Mittels.",
              "Es kann einige Zeit dauern, bis klar ist, ob ein Mittel gut schützt und vertragen wird."
            ],
            "MSA": [
              "Lies im Artikel den Absatz über die Spermienzahl. Was verrät dieser Messwert?",
              "Ein Ergebnis belegt nur das, was mit der beschriebenen Methode untersucht wurde."
            ],
            "AHR": [
              "Vergleiche Zielgruppe, Vergleichsgruppe, Messgröße und Dauer beider Studien.",
              "In Studie B waren die Teilnehmer bereits vasektomiert. Spermienparameter wurden nicht gemessen. Prüfe, was das für die Behauptung über Schwangerschaftsschutz bedeutet."
            ]
          }
        },
        "title": "Was bleibt offen?",
        "questions": [],
        "helpBefore": [
          "Suche im Artikel, was untersucht wurde.",
          "Ein Ergebnis zur Verträglichkeit allein zeigt noch keinen Schutz vor Schwangerschaft."
        ]
      }
    ]
  },
  "tom_articles": {
    "Foerder": {
      "title": "Mehr Möglichkeiten für Männer?",
      "paragraphs": [
        "Ein Kondom kann eine Schwangerschaft verhindern und das Risiko vieler Infektionen verringern. Es muss richtig benutzt werden.",
        "Es gibt auch eine Vasektomie. Dabei werden die Samenleiter unterbrochen. Sie ist als dauerhafte Verhütung gedacht. Sie schützt nicht vor Infektionen.",
        "Forschende arbeiten an weiteren Mitteln. Sie wollen zum Beispiel die Bildung von Spermien bremsen. Andere Mittel sollen Spermien beim Befruchten stören.",
        "Ein neues Mittel muss zuverlässig wirken. Es darf die Gesundheit nicht unvertretbar gefährden. Nach dem Absetzen soll die Fruchtbarkeit zurückkehren. Dafür sind Untersuchungen nötig."
      ],
      "glossary": {
        "Spermien": "männliche Keimzellen",
        "Fruchtbarkeit": "die Fähigkeit, ein Kind zu zeugen",
        "Untersuchung": "ein geplanter Test, der eine Frage klärt"
      }
    },
    "ESA": {
      "title": "Warum dauert die Entwicklung neuer Mittel?",
      "paragraphs": [
        "Männer können unter anderem mit Kondomen verhüten. Eine Vasektomie ist ein Eingriff an den Samenleitern und als dauerhafte Verhütung gedacht. Beide Möglichkeiten erfüllen also nicht dieselben Wünsche.",
        "Spermien entstehen fortlaufend in den Hoden. Für die Verhütung werden mehrere Ansätze untersucht: die Bildung stark verringern, die Funktion der Spermien stören oder ihren Transport blockieren.",
        "Eine Veränderung im Labor reicht nicht allein. Es muss untersucht werden, ob eine Methode Schwangerschaften zuverlässig verhindert. Ebenso wichtig sind gesundheitliche Risiken. Bei einer vorübergehenden Methode soll die Fruchtbarkeit später wiederkehren.",
        "Dass es Forschung gibt, bedeutet noch nicht, dass jedes untersuchte Mittel schon ausreichend geprüft und verfügbar ist. Der Text nennt wichtige Prüfaufgaben, aber nicht alle Gründe für die bisher geringe Auswahl."
      ],
      "glossary": {
        "Vasektomie": "als dauerhaft gedachte Unterbrechung der Samenleiter",
        "reversibel": "rückgängig zu machen; die Wirkung endet wieder"
      }
    },
    "MSA": {
      "title": "Neue Verhütung: eine Idee ist noch kein geprüftes Mittel",
      "paragraphs": [
        "Kondome und die als dauerhaft gedachte Vasektomie sind etablierte Möglichkeiten, die Männer selbst anwenden beziehungsweise vornehmen lassen können. Die Vasektomie schützt nicht vor STIs. Kondome können deren Risiko verringern, ohne vollständigen Schutz zu garantieren.",
        "Neue Methoden werden an unterschiedlichen Stellen untersucht: Sie sollen die fortlaufende Spermienbildung stark verringern, die Funktion von Spermien beeinträchtigen oder ihren Transport durch die Samenleiter blockieren. Nicht jeder Ansatz verändert die Sexualhormone.",
        "Eine geringe Spermienzahl ist ein Messwert. Ob eine Methode zuverlässig Schwangerschaften verhindert, ist eine andere Untersuchungsfrage. Zusätzlich sind gesundheitliche Risiken und die Rückkehr der Fruchtbarkeit nach Ende einer vorübergehenden Anwendung wichtig.",
        "Diese biologischen und medizinischen Anforderungen erlauben begründete Vermutungen über Entwicklungsprobleme. Warum historisch weniger Methoden für Männer verfügbar wurden, ist damit nicht vollständig erklärt. Dafür wären zum Beispiel auch Belege über Forschung, Finanzierung und Nutzung nötig. Diese Belege liefert der Artikel nicht."
      ],
      "glossary": {
        "Spermienparameter": "gemessene Eigenschaften, etwa Zahl oder Beweglichkeit",
        "reversibel": "die Wirkung lässt sich wieder aufheben"
      }
    },
    "AHR": {
      "title": "Wirksam im Labor – auch zuverlässig im Alltag?",
      "paragraphs": [
        "Neue männliche Verhütungsmethoden können an Spermienbildung, Spermienfunktion oder Spermientransport ansetzen. Ein hormoneller Ansatz verringert über veränderte Rückmeldesignale die für die Spermienbildung nötige hormonelle Stimulation. Nicht hormonelle Ansätze können andere Signalwege oder Funktionen beeinflussen. Ein Transportansatz setzt nicht notwendig an der Bildung an.",
        "Für eine vorübergehende Methode müssen Verhütungswirkung, gesundheitliche Sicherheit und Rückkehr der Fruchtbarkeit getrennt untersucht werden. Ein Laborwert, eine Schwangerschaftsrate und eine beobachtete Nebenwirkung beantworten verschiedene Fragen.",
        "Die folgenden Beispiele sind veröffentlichte Untersuchungen aus 2016 und 2025, kein vollständiger Überblick über den Forschungsstand 2026. Die Ergebnisse dürfen nicht ohne Berücksichtigung von Versuchsaufbau, Zielgruppe und Beobachtungsdauer miteinander gleichgesetzt werden."
      ],
      "glossary": {
        "Placebo": "Vergleichsmittel ohne den untersuchten Wirkstoff",
        "vasektomiert": "die Samenleiter wurden für dauerhafte Verhütung unterbrochen",
        "Endpunkt": "das Ergebnis, das in einer Untersuchung gemessen wird",
        "reversibel": "die Wirkung lässt sich wieder aufheben"
      }
    }
  },
  "research": [
    {
      "label": "Studie A · Hormonspritzen (2016)",
      "body": "Von 320 Teilnehmern erreichten 266 mit ihren Partnerinnen die Wirksamkeitsphase. In bis zu 56 Wochen traten vier Schwangerschaften auf. Unter anderem wurden Stimmungsschwankungen beobachtet. Nach einer externen Sicherheitsprüfung endeten Rekrutierung und Injektionen vorzeitig.",
      "source": "Behre et al. · DOI 10.1210/jc.2016-2141",
      "meaning": "Schwangerschaften wurden tatsächlich erfasst. Die Zahlen sind keine einfache Jahresrate für alle 320 Teilnehmer. Die Studie beantwortet nicht allein alle Fragen zu Sicherheit und Alltagseinsatz."
    },
    {
      "label": "Studie B · YCT-529 · Veröffentlichung 2025",
      "body": "16 bereits vasektomierte Männer nahmen an einer placebokontrollierten Untersuchung aufsteigender Einzeldosen teil. Geprüft wurden unter anderem Verträglichkeit und Wirkstoffverarbeitung. Die untersuchten Einzeldosen waren gut verträglich. Spermienparameter wurden nicht untersucht; ein Schutz vor Schwangerschaft wurde hier nicht nachgewiesen.",
      "source": "Mannowetz et al. · DOI 10.1038/s43856-025-01004-4",
      "meaning": "Erste Verträglichkeitsdaten sind kein Nachweis langfristiger Sicherheit oder kontrazeptiver Wirksamkeit. Die Studie ist nicht wertlos; sie beantwortet eine frühe Entwicklungsfrage."
    }
  ],
  "methods": {
    "K": [
      "Kondom",
      "Hält Sperma auf. So gelangen Spermien bei intaktem Kondom nicht in die Scheide.",
      "Für jeden Sex ein neues Kondom von Anfang an richtig benutzen.",
      "Kann reißen oder abrutschen. Fehler bei der Anwendung mindern den Schutz.",
      "Verändert die Periode nicht.",
      "Senkt das Risiko vieler sexuell übertragbarer Infektionen. Vollständigen Schutz bietet es nicht."
    ],
    "P": [
      "Kombinationspille",
      "Enthält zwei Hormone. Sie verhindern vor allem den Eisprung.",
      "Bei richtiger Einnahme sehr zuverlässig. Wer die Pille vergisst, kann schlechter geschützt sein. Regelmäßig nach Einnahmeplan nehmen.",
      "Übelkeit ist möglich. Selten können gefährliche Blutgerinnsel entstehen. Die Eignung ärztlich klären.",
      "Blutungen können schwächer und weniger schmerzhaft werden.",
      "Schützt nicht vor sexuell übertragbaren Infektionen."
    ],
    "Cu": [
      "Kupferspirale",
      "Kupfer hemmt die Beweglichkeit und die Befruchtungsfähigkeit von Spermien. Enthält keine Hormone.",
      "Wird in einer Praxis in die Gebärmutter eingesetzt. Wirkt lange und sehr zuverlässig. Keine tägliche Einnahme.",
      "Das Einsetzen kann wehtun. Die Spirale kann verrutschen oder ausgestoßen werden.",
      "Die Periode kann stärker und schmerzhafter werden.",
      "Schützt nicht vor sexuell übertragbaren Infektionen."
    ],
    "H": [
      "Hormonspirale",
      "Gibt ein Hormon ab. Der Schleim am Gebärmutterhals wird für Spermien schwer durchlässig.",
      "Wird in einer Praxis in die Gebärmutter eingesetzt. Wirkt lange und sehr zuverlässig. Keine tägliche Einnahme.",
      "Das Einsetzen kann wehtun. Unregelmäßige Blutungen sind vor allem am Anfang möglich.",
      "Blutungen und Schmerzen können nachlassen. Wie es einer Person damit geht, ist offen.",
      "Schützt nicht vor sexuell übertragbaren Infektionen."
    ]
  }
};
