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
            "Hi, ich bin Laura. Ich bin 19.",
            "Beim Sex können Krankheiten übertragen werden. Davor möchte ich mich schützen.",
            "Welche Verhütungsmethode könnt ihr mir dafür empfehlen?"
          ],
          "ESA": [
            "Hi, ich bin Laura, 19.",
            "Beim Sex möchte ich mich vor sexuell übertragbaren Infektionen schützen.",
            "Welche Verhütungsmethode könnt ihr mir dafür empfehlen?"
          ],
          "MSA": [
            "Hi, ich bin Laura, 19.",
            "Ich möchte beim Sex das Risiko sexuell übertragbarer Infektionen verringern.",
            "Welche der bekannten Verhütungsmethoden würdet ihr mir empfehlen?"
          ],
          "AHR": [
            "Hi, ich bin Laura, 19.",
            "Ich möchte beim Sex das Risiko sexuell übertragbarer Infektionen verringern.",
            "Welche der vier bekannten Methoden würdet ihr für dieses Ziel zunächst vorschlagen?"
          ]
        },
        "task": {
          "Foerder": "Wähle die Methode, die du bei „Mein erster Rat“ notiert hast.",
          "ESA": "Wähle die Methode, die du bei „Mein erster Rat“ notiert hast.",
          "MSA": "Greift euren notierten Rat auf. Welche Kartenangabe belegt den Infektionsschutz?",
          "AHR": "Prüft euren notierten Rat am ersten Schutzziel. Welche Grenze hat eure Aussage?"
        },
        "options": {
          "K": "Wir schlagen dir ein Kondom vor.",
          "P": "Wir schlagen dir die Kombinationspille vor.",
          "Cu": "Wir schlagen dir die Kupferspirale vor.",
          "H": "Wir schlagen dir die Hormonspirale vor."
        },
        "replies": {
          "K": "Wie viel Schutz kann ich davon erwarten?",
          "P": "Wie hilft mir das gegen Infektionen beim Sex? Genau danach habe ich gefragt.",
          "Cu": "Wie hilft mir das gegen Infektionen beim Sex? Genau danach habe ich gefragt.",
          "H": "Wie hilft mir das gegen Infektionen beim Sex? Genau danach habe ich gefragt."
        },
        "hints": {
          "K": {
            "section": "Infektionsschutz",
            "find": "Welches Risiko wird kleiner?",
            "fact": "Kondome senken das Risiko vieler Infektionen. Ganz ausschließen können sie es nicht."
          },
          "P": {
            "section": "Infektionsschutz",
            "find": "Hilft die Pille gegen Infektionen?",
            "fact": "Die Kombinationspille allein schützt nicht vor sexuell übertragbaren Infektionen."
          },
          "Cu": {
            "section": "Infektionsschutz",
            "find": "Hilft die Kupferspirale gegen Infektionen?",
            "fact": "Die Kupferspirale allein schützt nicht vor sexuell übertragbaren Infektionen."
          },
          "H": {
            "section": "Infektionsschutz",
            "find": "Hilft die Hormonspirale gegen Infektionen?",
            "fact": "Die Hormonspirale allein schützt nicht vor sexuell übertragbaren Infektionen."
          }
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
        "helpBefore": {
          "Foerder": [
            "Lies im Chat „Infektionsschutz“. Wovor möchte sie sich schützen?",
            "Sie fragt nach Infektionen, die beim Sex übertragen werden."
          ],
          "ESA": [
            "Welche Karte passt zu Lauras erstem Schutzziel?",
            "Sie fragt nach Infektionen, die beim Sex übertragen werden."
          ],
          "MSA": [
            "Vergleiche zwei Karten. Welche Wirkung hilft bei Lauras erster Frage?",
            "Sie fragt nach Infektionen, die beim Sex übertragen werden."
          ],
          "AHR": [
            "Vergleiche zwei Möglichkeiten. Welches Risiko bleibt jeweils offen?",
            "Sie fragt nach Infektionen, die beim Sex übertragen werden."
          ]
        },
        "hintQuestions": {
          "ESA": "Welche Karte passt zu Lauras erstem Schutzziel?",
          "MSA": "Vergleiche zwei Karten. Welche Wirkung hilft bei Lauras erster Frage?",
          "AHR": "Vergleiche zwei Möglichkeiten. Welches Risiko bleibt jeweils offen?"
        },
        "recap": "Laura ist 19. Sie möchte sich vor Krankheiten schützen, die beim Sex übertragen werden."
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
          "Foerder": "Prüfe, wann Laura deine Methode anwenden muss.",
          "ESA": "Prüfe, ob die Anwendung zu Lauras Alltag passt.",
          "MSA": "Prüfe beide Schutzziele und den Aufwand im Alltag. Vergleiche zwei Möglichkeiten.",
          "AHR": "Wägt zwei Strategien für beide Ziele ab. Wann verändert Lauras Alltag eure Gewichtung?"
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
          "K": "An das Kondom müssten wir dann bei jedem Sex denken.",
          "P": "Die Tablette müsste ich regelmäßig nehmen. Wie könnte ich das im Alltag schaffen?",
          "Cu": "Dann müsste ich nicht jeden Tag daran denken. Was wäre im Alltag trotzdem wichtig?",
          "H": "Das wäre also keine tägliche Aufgabe. Was müsste ich dafür tun?",
          "K+P": "Das wären zwei Methoden. Die tägliche Einnahme wäre dabei weiterhin ein Thema.",
          "K+Cu": "Ihr nennt zwei Methoden. Welche Aufgabe soll jede davon haben?",
          "K+H": "Bei eurem Vorschlag müsste ich nicht täglich eine Pille nehmen. Über die Spirale hätte ich noch Fragen."
        },
        "hints": {
          "K": {
            "section": "Anwendung",
            "find": "Wann braucht man ein neues Kondom?",
            "fact": "Ein Kondom braucht man bei jedem Sex neu. Es muss von Anfang an richtig sitzen."
          },
          "P": {
            "section": "Anwendung",
            "find": "Wie oft muss man an die Pille denken?",
            "fact": "Die Pille braucht regelmäßige Einnahme. Einnahmefehler können den Schutz verringern."
          },
          "Cu": {
            "section": "Anwendung",
            "find": "Wer setzt die Spirale ein?",
            "fact": "Eine Ärztin oder ein Arzt setzt sie ein. Es gibt keine tägliche Einnahme. Kontrollen bleiben wichtig."
          },
          "H": {
            "section": "Anwendung",
            "find": "Muss man jeden Tag daran denken?",
            "fact": "Es gibt keine tägliche Einnahme. Die Spirale wird ärztlich eingesetzt und kontrolliert."
          },
          "K+P": {
            "section": "Anwendung",
            "find": "Wie oft muss man an die Pille denken?",
            "fact": "Die Pille braucht regelmäßige Einnahme. Einnahmefehler können den Schutz verringern."
          },
          "K+Cu": {
            "section": "Anwendung",
            "find": "Wer setzt die Spirale ein?",
            "fact": "Eine Ärztin oder ein Arzt setzt sie ein. Es gibt keine tägliche Einnahme. Kontrollen bleiben wichtig."
          },
          "K+H": {
            "section": "Anwendung",
            "find": "Muss man jeden Tag daran denken?",
            "fact": "Es gibt keine tägliche Einnahme. Die Spirale wird ärztlich eingesetzt und kontrolliert."
          }
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
        "helpBefore": {
          "Foerder": [
            "Lies im Chat „Schutz im Alltag“. Was vergisst sie leicht?",
            "Eine feste Zeit ist für Laura schwierig. Vergleiche, wann man die Methoden anwendet."
          ],
          "ESA": [
            "Wann müsste Laura bei diesem Vorschlag an die Anwendung denken?",
            "Eine feste Zeit ist für Laura schwierig. Vergleiche, wann man die Methoden anwendet."
          ],
          "MSA": [
            "Vergleiche zwei Vorschläge. Wie gut passen Schutz und Aufwand zu Lauras Alltag?",
            "Eine feste Zeit ist für Laura schwierig. Vergleiche, wann man die Methoden anwendet."
          ],
          "AHR": [
            "Vergleiche zwei Strategien. Wann könnte eine im Alltag weniger zuverlässig sein als auf der Karte?",
            "Eine feste Zeit ist für Laura schwierig. Vergleiche, wann man die Methoden anwendet."
          ]
        },
        "hintQuestions": {
          "ESA": "Wann müsste Laura bei diesem Vorschlag an die Anwendung denken?",
          "MSA": "Vergleiche zwei Vorschläge. Wie gut passen Schutz und Aufwand zu Lauras Alltag?",
          "AHR": "Vergleiche zwei Strategien. Wann könnte eine im Alltag weniger zuverlässig sein als auf der Karte?"
        },
        "reviewPrevious": true,
        "recap": "Sie möchte auch eine Schwangerschaft vermeiden. Tägliche Dinge vergisst sie manchmal."
      },
      {
        "id": "L3",
        "type": "recommend",
        "message": [
          "Meiner Freundin wurde von der Pille übel. Wie ich sie vertragen würde, weiß ich nicht.",
          "Ich möchte die Pille nicht nehmen. Für andere Hormone bin ich offen.",
          "Das Einsetzen einer Spirale macht mir Sorgen. Ich möchte mich erst beraten lassen."
        ],
        "task": {
          "Foerder": "Prüfe deinen Rat. Laura will keine Pille. Zur Spirale hat sie Fragen.",
          "ESA": "Prüfe deinen Rat. Beachte Lauras Nein zur Pille und ihre Frage zum Einsetzen.",
          "MSA": "Was zeigt der Einzelfall? Unterscheidet Lauras feste Entscheidung von ihrer offenen Sorge.",
          "AHR": "Prüft die Vorhersage aus dem Einzelfall. Welche Option schließt Lauras Nein aus, welche bleibt unter einer Bedingung offen?"
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
          "K": {
            "section": "Anwendung",
            "find": "Wie wird ein Kondom benutzt?",
            "fact": "Das Kondom wird über den Penis gerollt. Dafür braucht Laura weder eine Pille noch eine Spirale."
          },
          "P": {
            "section": "Mögliche Nachteile",
            "find": "Ist Übelkeit möglich oder sicher? Was folgt daraus für Laura?",
            "fact": "Übelkeit ist möglich. Die Erfahrung der Freundin sagt Lauras Verträglichkeit nicht sicher voraus. Laura lehnt die Pille ab."
          },
          "Cu": {
            "section": "Anwendung",
            "find": "Was möchte Laura vor dem Einsetzen wissen?",
            "fact": "Laura ist bei einer Spirale noch unsicher. Das ist weder eine Zustimmung noch eine feste Ablehnung."
          },
          "H": {
            "section": "Anwendung",
            "find": "Was möchte Laura vor dem Einsetzen wissen?",
            "fact": "Laura lehnt die Pille ab, aber nicht automatisch alle Hormone. Über die Spirale entscheidet sie nach Beratung."
          },
          "K+P": {
            "section": "Mögliche Nachteile",
            "find": "Ist Übelkeit möglich oder sicher? Was folgt daraus für Laura?",
            "fact": "Übelkeit ist möglich. Die Erfahrung der Freundin sagt Lauras Verträglichkeit nicht sicher voraus. Laura lehnt die Pille ab."
          },
          "K+Cu": {
            "section": "Anwendung",
            "find": "Was möchte Laura vor dem Einsetzen wissen?",
            "fact": "Laura ist bei einer Spirale noch unsicher. Das ist weder eine Zustimmung noch eine feste Ablehnung."
          },
          "K+H": {
            "section": "Anwendung",
            "find": "Was möchte Laura vor dem Einsetzen wissen?",
            "fact": "Laura lehnt die Pille ab, aber nicht automatisch alle Hormone. Über die Spirale entscheidet sie nach Beratung."
          }
        },
        "title": "Lauras Entscheidung",
        "questions": [
          [
            "Weißt du, wie du die Pille verträgst?",
            "Das weiß ich nicht. Ich mache mir wegen ihrer Erfahrung Sorgen."
          ],
          [
            "Gilt dein Nein für alle Hormone?",
            "Nein. Für mich steht nur fest, dass ich die Pille nicht nehmen möchte."
          ],
          [
            "Was macht dir an der Spirale Sorgen?",
            "Das Einsetzen. Ich würde erst gern in einer Praxis fragen, wie das abläuft."
          ]
        ],
        "helpBefore": {
          "Foerder": [
            "Lies im Chat „Lauras Entscheidung“. Wozu sagt sie Nein?",
            "Laura sagt Nein zur Pille. Bei der Spirale hat sie noch Fragen."
          ],
          "ESA": [
            "Vergleiche mit Lauras Nachricht. Wozu sagt sie Nein, wo hat sie Fragen?",
            "Laura sagt Nein zur Pille. Bei der Spirale hat sie noch Fragen."
          ],
          "MSA": [
            "Vergleiche zwei Möglichkeiten. Wo darf ein Vorteil der Methode Lauras Entscheidung nicht ersetzen?",
            "Laura sagt Nein zur Pille. Bei der Spirale hat sie noch Fragen."
          ],
          "AHR": [
            "Welche Alternative respektiert Lauras Grenze? Unter welcher Bedingung wäre ihre offene Frage geklärt?",
            "Laura sagt Nein zur Pille. Bei der Spirale hat sie noch Fragen."
          ]
        },
        "declined": {
          "P": "Die Pille möchte ich nicht nehmen. Mein Nein gilt auch bei einer Kombination."
        },
        "hintQuestions": {
          "ESA": "Vergleiche mit Lauras Nachricht. Wozu sagt sie Nein, wo hat sie Fragen?",
          "MSA": "Vergleiche zwei Möglichkeiten. Wo darf ein Vorteil der Methode Lauras Entscheidung nicht ersetzen?",
          "AHR": "Welche Alternative respektiert Lauras Grenze? Unter welcher Bedingung wäre ihre offene Frage geklärt?"
        },
        "reviewPrevious": true,
        "recap": "Ihrer Freundin wurde von der Pille übel. Laura weiß nicht, wie sie die Pille verträgt. Sie will keine Pille. Andere Hormone sind für sie möglich. Das Einsetzen einer Spirale macht ihr Sorgen. Sie möchte Beratung."
      },
      {
        "id": "L4",
        "type": "recommend",
        "message": [
          "Bei meiner Regel habe ich oft starke Schmerzen. Die Ursache wurde noch nicht untersucht.",
          "Mehr Schmerzen möchte ich nicht. Der Schutz vor Infektionen ist mir weiterhin wichtig.",
          "Ein Kondom wäre für uns in Ordnung."
        ],
        "task": {
          "Foerder": "Prüfe deinen Rat bei Regelschmerzen und beim Schutz vor Infektionen.",
          "ESA": "Prüfe deinen Rat. Beachte die Schmerzen und den Schutz vor Infektionen.",
          "MSA": "Vergleicht zwei Strategien bei Schmerzen und Infektionsschutz. Was muss eine Praxis klären?",
          "AHR": "Wägt Infektionsschutz und mögliche Belastung bei zwei Strategien ab. Unter welcher medizinischen Bedingung würdet ihr anders raten?"
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
          "K": "Ein Kondom kommt für uns infrage. Meine Schmerzen möchte ich ärztlich klären lassen.",
          "P": "Die Pille möchte ich weiterhin nicht. Meine Schmerzen ändern daran nichts.",
          "Cu": {
            "Foerder": "Könnten meine Schmerzen stärker werden? Wie schützen wir uns vor Infektionen?",
            "ESA": "Könnte die Kupferspirale meine Schmerzen verstärken? Was ist mit dem Infektionsschutz?",
            "MSA": "Wie berücksichtigt ihr mögliche stärkere Schmerzen und den fehlenden Infektionsschutz der Kupferspirale?",
            "AHR": "Wie gewichtet ihr den Schutz vor Schwangerschaft gegenüber möglichen stärkeren Schmerzen und fehlendem Infektionsschutz?"
          },
          "H": "Ob sie für mich passt, muss ich ärztlich klären. Was schützt mich bei diesem Rat vor Infektionen?",
          "K+P": "Die Pille ist immer noch dabei. Ich habe sie aber abgelehnt.",
          "K+Cu": "Das Kondom passt für uns. Könnte die Kupferspirale meine Schmerzen verstärken?",
          "K+H": "Bei der Hormonspirale brauche ich ärztliche Beratung. Und die Ursache meiner Schmerzen ist noch offen."
        },
        "hints": {
          "K": {
            "section": "Blutung und Schmerzen",
            "find": "Verändert ein Kondom die Regel?",
            "fact": "Ein Kondom verändert die Regel nicht. Richtig benutzt senkt es das Risiko vieler Infektionen. Die starken Schmerzen sollte Laura ärztlich klären lassen."
          },
          "P": {
            "section": "Blutung und Schmerzen",
            "find": "Was kann sich bei der Blutung ändern?",
            "fact": "Die Pille kann Schmerzen lindern. Laura will die Pille trotzdem nicht."
          },
          "Cu": {
            "section": "Blutung und Schmerzen",
            "find": "Können die Schmerzen stärker werden?",
            "fact": "Die Kupferspirale kann Regelschmerzen verstärken. Die Spirale schützt nicht vor Infektionen."
          },
          "H": {
            "section": "Blutung und Schmerzen",
            "find": "Wie kann sich die Periode ändern?",
            "fact": "Bei einer Hormonspirale können Schmerzen nachlassen. Sie schützt nicht vor Infektionen. Die Eignung ist ärztlich zu klären."
          },
          "K+P": {
            "section": "Blutung und Schmerzen",
            "find": "Was kann sich bei der Blutung ändern?",
            "fact": "Die Pille kann Schmerzen lindern. Laura will die Pille trotzdem nicht."
          },
          "K+Cu": {
            "section": "Blutung und Schmerzen",
            "find": "Können die Schmerzen stärker werden?",
            "fact": "Die Kupferspirale kann Regelschmerzen verstärken. Das Kondom senkt das Risiko vieler Infektionen."
          },
          "K+H": {
            "section": "Blutung und Schmerzen",
            "find": "Wie kann sich die Periode ändern?",
            "fact": "Das Kondom senkt das Infektionsrisiko. Ob die Hormonspirale bei Lauras Beschwerden passt, muss sie ärztlich klären. Laura entscheidet selbst."
          }
        },
        "title": "Regelschmerzen und Infektionsschutz",
        "questions": [
          [
            "Kennst du den Grund für die Schmerzen?",
            "Nein, das habe ich noch nicht untersuchen lassen."
          ],
          [
            "Wie wichtig sind dir die Schmerzen bei der Wahl?",
            "Sehr wichtig. Mehr Schmerzen wären für mich schwer auszuhalten."
          ],
          [
            "Wäre ein Kondom für euch möglich?",
            "Ja, wir können uns vorstellen, es jedes Mal zu benutzen."
          ]
        ],
        "helpBefore": {
          "Foerder": [
            "Lies im Chat „Regelschmerzen“. Was tut ihr weh?",
            "Blutungen und Schmerzen können sich je nach Spirale anders verändern."
          ],
          "ESA": [
            "Was steht über Schmerzen auf der Karte? Passt das zu Lauras Wunsch?",
            "Blutungen und Schmerzen können sich je nach Spirale anders verändern."
          ],
          "MSA": [
            "Wie wiegst du möglichen Schutz und mögliche Beschwerden bei zwei Vorschlägen ab?",
            "Blutungen und Schmerzen können sich je nach Spirale anders verändern."
          ],
          "AHR": [
            "Vergleiche zwei Strategien. Welche medizinische Unsicherheit begrenzt dein Urteil über Schmerzen?",
            "Blutungen und Schmerzen können sich je nach Spirale anders verändern."
          ]
        },
        "declined": {
          "P": "Die Pille möchte ich nicht nehmen. Mein Nein gilt auch bei einer Kombination."
        },
        "hintQuestions": {
          "ESA": "Was steht über Schmerzen auf der Karte? Passt das zu Lauras Wunsch?",
          "MSA": "Wie wiegst du möglichen Schutz und mögliche Beschwerden bei zwei Vorschlägen ab?",
          "AHR": "Vergleiche zwei Strategien. Welche medizinische Unsicherheit begrenzt dein Urteil über Schmerzen?"
        },
        "reviewPrevious": true,
        "recap": "Laura hat oft starke Regelschmerzen. Die Ursache ist noch offen. Mehr Schmerzen möchte sie nicht. Infektionsschutz bleibt ihr wichtig. Ein Kondom ist für sie in Ordnung.",
        "resumeTitle": "Schmerzen und Infektionsschutz"
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
          "Foerder": "Wähle deinen Rat für Laura. Begründe ihn kurz. Nenne auch einen Nachteil.",
          "ESA": "Nenne deinen Rat. Begründe ihn mit Lauras Wunsch und nenne einen Nachteil.",
          "MSA": "Vergleiche zwei vertretbare Vorschläge. Gewichte ein Kriterium und berücksichtige einen Nachteil.",
          "AHR": "Gewichtet zwei vertretbare Strategien. Unter welcher konkreten Bedingung wäre die Alternative besser?"
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
          "K+Cu": "Ob eine Kupferspirale für mich passt, ist wegen meiner Schmerzen offen. Was kann ich bis zur Beratung tun?",
          "K+H": "Die Hormonspirale kommt nur nach Beratung und mit meiner Zustimmung infrage. Begründet bitte auch, weshalb ihr sie zusätzlich vorschlagt."
        },
        "hints": {
          "K": {
            "section": "Anwendung",
            "find": "Wann braucht man ein neues Kondom?",
            "fact": "Ein Kondom senkt auch das Infektionsrisiko. Falsch benutzt schützt es schlechter."
          },
          "P": {
            "section": "Anwendung",
            "find": "Wie oft muss man an die Pille denken?",
            "fact": "Die Pille muss regelmäßig genommen werden. Laura hat zur Pille Nein gesagt."
          },
          "Cu": {
            "section": "Blutung und Schmerzen",
            "find": "Können die Schmerzen stärker werden?",
            "fact": "Die Periode kann mehr wehtun. Die Kupferspirale schützt nicht vor Infektionen."
          },
          "H": {
            "section": "Anwendung",
            "find": "Muss man jeden Tag daran denken?",
            "fact": "Die Hormonspirale wirkt lange. Sie schützt nicht vor Infektionen. Laura hat der Einlage noch nicht zugestimmt."
          },
          "K+P": {
            "section": "Anwendung",
            "find": "Wie oft muss man an die Pille denken?",
            "fact": "Die Pille muss regelmäßig genommen werden. Laura hat zur Pille Nein gesagt."
          },
          "K+Cu": {
            "section": "Blutung und Schmerzen",
            "find": "Können die Schmerzen stärker werden?",
            "fact": "Das Kondom senkt das Infektionsrisiko. Die Kupferspirale kann Schmerzen verstärken."
          },
          "K+H": {
            "section": "Anwendung",
            "find": "Muss man jeden Tag daran denken?",
            "fact": "Das Kondom senkt das Infektionsrisiko. Die Hormonspirale wirkt lange. Vor der Einlage braucht Laura Beratung."
          }
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
        "helpBefore": {
          "Foerder": [
            "Lies im Chat „Dein Rat an Laura“. Wer soll am Ende entscheiden?",
            "Ein Kondom wäre für sie möglich. Über eine Spirale möchte sie erst mehr wissen."
          ],
          "ESA": [
            "Welcher Wunsch von Laura spricht für deinen Rat?",
            "Ein Kondom wäre für sie möglich. Über eine Spirale möchte sie erst mehr wissen."
          ],
          "MSA": [
            "Welchen Vorteil von A gewichtest du höher als den Vorteil von B? Nenne auch eine Grenze.",
            "Ein Kondom wäre für sie möglich. Über eine Spirale möchte sie erst mehr wissen."
          ],
          "AHR": [
            "Vergleiche deine Wahl mit einer Alternative. Welche offene Bedingung könnte den Ausschlag ändern?",
            "Ein Kondom wäre für sie möglich. Über eine Spirale möchte sie erst mehr wissen."
          ]
        },
        "declined": {
          "P": "Die Pille möchte ich nicht nehmen. Mein Nein gilt auch bei einer Kombination."
        },
        "hintQuestions": {
          "ESA": "Was spricht bei Laura für deinen Vorschlag?",
          "MSA": "Wann würde ein anderes Kriterium für Laura schwerer wiegen? Vergleiche den Nachteil beider Vorschläge.",
          "AHR": "Welche noch offene Annahme könnte deine Gewichtung ändern? Begründe den Wechsel zur Alternative."
        },
        "tentative": "Unser Rat ist vorläufig. Offene medizinische Fragen kannst du in der Praxis klären. Du entscheidest selbst.",
        "resumeTitle": "Mein letzter Rat"
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
            "Karte „Kondom“, Abschnitt „Wirkung“. Enthält das Kondom Hormone?",
            "Das Kondom enthält keine Hormone. Die richtige Anwendung ist für den Schutz wichtig."
          ],
          "P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Karte „Kupferspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
            "Die Kupferspirale enthält keine Hormone. Sie wird in einer Praxis eingesetzt."
          ],
          "H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Karte „Kupferspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
            "Die Kupferspirale enthält keine Hormone. Sie wird in einer Praxis eingesetzt."
          ],
          "K+H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
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
          "Lies im Chat „Ohne zusätzliche Hormone“. Was möchte sie vermeiden?",
          "Celina möchte ohne zusätzliche Hormone verhüten."
        ],
        "declined": {
          "P": "Die Pille enthält Hormone. Deshalb kommt sie für mich nicht infrage.",
          "H": "Ich möchte keine zusätzlichen Hormone. Deshalb möchte ich auch die Hormonspirale nicht."
        },
        "recap": "Celina ist 17. Sie möchte eine Schwangerschaft vermeiden. Zusätzliche Hormone möchte sie nicht."
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
            "Karte „Kondom“, Abschnitt „Anwendung“. Wann braucht man ein neues Kondom?",
            "Das Kondom wird bei jedem Sex neu und richtig verwendet. Es ist keine tägliche Tablette."
          ],
          "P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Karte „Kupferspirale“, Abschnitt „Anwendung“. Wer setzt die Spirale ein?",
            "Eine Ärztin oder ein Arzt setzt sie ein. Es gibt keine tägliche Einnahme. Kontrollen bleiben wichtig."
          ],
          "H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Karte „Kupferspirale“, Abschnitt „Anwendung“. Wer setzt die Spirale ein?",
            "Eine Ärztin oder ein Arzt setzt sie ein. Es gibt keine tägliche Einnahme. Kontrollen bleiben wichtig."
          ],
          "K+H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
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
          "Lies im Chat „Schutz über längere Zeit“. Wann wäre eine Methode für sie praktisch?",
          "Eine Spirale bleibt längere Zeit im Körper. Ein Kondom braucht man bei jedem Sex neu."
        ],
        "declined": {
          "P": "Die Pille enthält Hormone. Deshalb kommt sie für mich nicht infrage.",
          "H": "Ich möchte keine zusätzlichen Hormone. Deshalb möchte ich auch die Hormonspirale nicht."
        },
        "recap": "Sie möchte lange verhüten und später vielleicht ein Kind bekommen. Sie möchte keine tägliche Aufgabe. Ein Kondom ist für sie möglich."
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
            "Karte „Kondom“, Abschnitt „Anwendung“. Wie wird das Kondom benutzt?",
            "Für ein Kondom ist keine Einlage nötig. Bei jedem Sex braucht man von Anfang an ein neues Kondom."
          ],
          "P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Karte „Kupferspirale“, Abschnitt „Mögliche Nachteile“. Was kann beim Einsetzen wehtun?",
            "Eine Kupferspirale muss eingesetzt werden. Blutungen und Schmerzen können zunehmen. Ein Kondom braucht keine Einlage. Vergleiche auch die Sicherheit."
          ],
          "H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Karte „Kupferspirale“, Abschnitt „Mögliche Nachteile“. Was kann beim Einsetzen wehtun?",
            "Eine Kupferspirale muss eingesetzt werden. Blutungen und Schmerzen können zunehmen. Ein Kondom braucht keine Einlage. Vergleiche auch die Sicherheit."
          ],
          "K+H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
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
          "Lies im Chat „Sorge vor dem Einsetzen“. Was macht ihr Sorgen?",
          "Celina hat Angst vor der Einlage. Sie hat noch nicht Nein gesagt."
        ],
        "declined": {
          "P": "Die Pille enthält Hormone. Deshalb kommt sie für mich nicht infrage.",
          "H": "Ich möchte keine zusätzlichen Hormone. Deshalb möchte ich auch die Hormonspirale nicht."
        },
        "recap": "Das Einsetzen einer Spirale macht ihr Angst. Entschieden hat sie noch nicht. Bei der Regel hat sie meist keine starken Schmerzen."
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
          "H": "Die Hormonspirale möchte ich wegen der Hormone nicht. Und wie wäre das mit dem Schutz vor Infektionen?",
          "K+P": "Das Kondom ist möglich. Die Pille ist für mich weiter keine Option.",
          "K+Cu": "Erklärt, welche Aufgabe jeder Teil übernimmt. Meine Zustimmung zur Spirale ist noch offen.",
          "K+H": "Das Kondom ist möglich. Die Hormonspirale möchte ich aber nicht."
        },
        "hints": {
          "K": [
            "Karte „Kondom“, Abschnitt „Infektionsschutz“. Welches Risiko wird kleiner?",
            "Kondome verringern das Risiko vieler Infektionen beim Sex. Vollständigen Schutz vor allen Infektionen bieten sie nicht."
          ],
          "P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Karte „Kupferspirale“, Abschnitt „Infektionsschutz“. Hilft die Kupferspirale gegen Infektionen?",
            "Die Kupferspirale schützt nicht vor Infektionen beim Sex."
          ],
          "H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Karte „Kupferspirale“, Abschnitt „Infektionsschutz“. Hilft die Kupferspirale gegen Infektionen?",
            "Das Kondom im Vorschlag senkt das Risiko vieler Infektionen beim Sex. Die andere Methode schützt davor nicht."
          ],
          "K+H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
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
          "Lies im Chat „Schutz in der Beziehung“. Wovor möchte sie sich jetzt auch schützen?",
          "Vertrauen sagt nichts Sicheres über eine Infektion aus."
        ],
        "declined": {
          "P": "Die Pille enthält Hormone. Deshalb kommt sie für mich nicht infrage.",
          "H": "Ich möchte keine zusätzlichen Hormone. Deshalb möchte ich auch die Hormonspirale nicht."
        },
        "recap": "Celina möchte sich auch in ihrer festen Beziehung vor Infektionen schützen."
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
          "Cu": "Ich möchte erst klären, ob sie medizinisch passt und ob ich das Einsetzen will. Wie berücksichtige ich bis dahin den Infektionsschutz?",
          "H": "Ich möchte ohne zusätzliche Hormone verhüten. Das gilt auch für die Hormonspirale.",
          "K+P": "Die Pille möchte ich nicht. Prüft euren Vorschlag vor dem Aufschreiben.",
          "K+Cu": "Die Kupferspirale kommt nur infrage, wenn ich nach Beratung zustimme. Begründet auch, warum ihr sie zusätzlich vorschlagt.",
          "K+H": "Meine Grenze zu Hormonen bleibt bestehen. Prüft den Vorschlag noch einmal."
        },
        "hints": {
          "K": [
            "Karte „Kondom“, Abschnitt „Anwendung“. Wann braucht man ein neues Kondom?",
            "Ein Kondom enthält keine Hormone. Beide müssen jedes Mal daran denken."
          ],
          "P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "Cu": [
            "Karte „Kupferspirale“, Abschnitt „Anwendung“. Wer setzt die Spirale ein?",
            "Die Kupferspirale wirkt lange ohne Hormone. Celina möchte sich erst beraten lassen."
          ],
          "H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
            "Die Hormonspirale enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Enthält die Pille Hormone?",
            "Die Kombinationspille enthält Hormone. Celina möchte keine zusätzlichen Hormone."
          ],
          "K+Cu": [
            "Karte „Kupferspirale“, Abschnitt „Anwendung“. Wer setzt die Spirale ein?",
            "Die Kupferspirale wirkt lange ohne Hormone. Celina möchte sich erst beraten lassen."
          ],
          "K+H": [
            "Karte „Hormonspirale“, Abschnitt „Wirkung“. Enthält die Spirale Hormone?",
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
          "Lies im Chat „Dein Rat an Celina“. Welcher Wunsch gilt noch?",
          "Sie möchte keine Hormone. Über die Spirale entscheidet sie erst nach einer Beratung."
        ],
        "declined": {
          "P": "Die Pille enthält Hormone. Deshalb kommt sie für mich nicht infrage.",
          "H": "Ich möchte keine zusätzlichen Hormone. Deshalb möchte ich auch die Hormonspirale nicht."
        },
        "tentative": "Unser Rat ist vorläufig. Offene medizinische Fragen kannst du in der Praxis klären. Du entscheidest selbst."
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
          "K": "Ein Kondom kann ich an meinem eigenen Körper benutzen. Das ist mir wichtig.",
          "P": "Diese Pille wirkt auf einen Zyklus mit Eisprung. So einen Zyklus habe ich nicht. Ich suche etwas, das ich selbst anwenden kann.",
          "Cu": "Eine Kupferspirale wird in eine Gebärmutter eingesetzt. Die habe ich nicht. Ich suche eine Methode für mich.",
          "H": "Auch eine Hormonspirale wird in eine Gebärmutter eingesetzt. Die habe ich nicht. Welche Methode kann ich selbst anwenden?",
          "K+P": "Das Kondom kann ich benutzen. Die Pille wäre aber nicht meine eigene Methode. Darüber entscheidet meine Freundin selbst.",
          "K+Cu": "Das Kondom ist mein eigener Beitrag. Eine Kupferspirale würde meine Freundin betreffen; das wäre ihre Entscheidung.",
          "K+H": "Das Kondom kann ich selbst verwenden. Eine Hormonspirale kann ich nicht für meine Freundin auswählen."
        },
        "hints": {
          "K": [
            "Karte „Kondom“, Abschnitt „Anwendung“. Wer kann das Kondom am eigenen Körper benutzen?",
            "Ein Kondom benutzt Tom an seinem Penis."
          ],
          "P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Was macht die Pille mit dem Eisprung?",
            "Die Kombinationspille hemmt den Eisprung. Tom hat keinen Eisprung."
          ],
          "Cu": [
            "Karte „Kupferspirale“, Abschnitt „Anwendung“. Wo sitzt die Spirale?",
            "Eine Kupferspirale wird in eine Gebärmutter eingesetzt. Tom hat keine."
          ],
          "H": [
            "Karte „Hormonspirale“, Abschnitt „Anwendung“. Wo sitzt die Spirale?",
            "Eine Hormonspirale wird in eine Gebärmutter eingesetzt. Tom hat keine."
          ],
          "K+P": [
            "Karte „Kombinationspille“, Abschnitt „Wirkung“. Was macht die Pille mit dem Eisprung?",
            "Die Kombinationspille hemmt den Eisprung. Tom hat keinen Eisprung. Das Kondom kann er selbst benutzen."
          ],
          "K+Cu": [
            "Karte „Kupferspirale“, Abschnitt „Anwendung“. Wo sitzt die Spirale?",
            "Eine Kupferspirale wird in eine Gebärmutter eingesetzt. Tom hat keine. Das Kondom kann er selbst benutzen."
          ],
          "K+H": [
            "Karte „Hormonspirale“, Abschnitt „Anwendung“. Wo sitzt die Spirale?",
            "Eine Hormonspirale wird in eine Gebärmutter eingesetzt. Tom hat keine. Das Kondom kann er selbst benutzen."
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
          "Lies im Chat „Selbst verhüten“. Wer möchte das Mittel benutzen?",
          "Tom fragt nach einer Methode für seinen eigenen Körper."
        ],
        "selfAdvice": "Für dich selbst schlagen wir ein Kondom vor.",
        "selfAnswer": "Ein Kondom kann ich selbst benutzen. Was würdet ihr mir für meinen Körper vorschlagen?",
        "recap": "Tom ist 17. Er möchte bei der Verhütung selbst etwas tun."
      },
      {
        "id": "T1",
        "type": "article",
        "message": {
          "Foerder": [
            "Ich möchte mehr Auswahl. Gibt es bald noch etwas für mich?",
            "Ich habe dazu einen Artikel gefunden. Lest mit mir!"
          ],
          "ESA": [
            "Ich hätte gern noch mehr Möglichkeiten, mit denen ich selbst verhüten kann.",
            "Ich habe einen Artikel über die Forschung gefunden. Lest ihr mit?"
          ],
          "MSA": [
            "Ich hätte gern noch mehr Möglichkeiten, mit denen ich selbst verhüten kann.",
            "Ich habe einen Artikel über die Forschung gefunden. Lest ihr mit?"
          ],
          "AHR": [
            "Ich hätte gern noch mehr Möglichkeiten, mit denen ich selbst verhüten kann.",
            "Ich habe einen Artikel über die Forschung gefunden. Lest ihr mit?"
          ]
        },
        "task": {
          "Foerder": "Lies den Artikel. Warum braucht die Forschung Zeit? Sag deinen Grund.",
          "ESA": "Lies den Artikel. Verbinde zwei Hinweise zu einer Vermutung.",
          "MSA": "Vergleiche zwei Ansätze. Erkläre mit dem Artikel eine mögliche Hürde.",
          "AHR": "Vergleiche die beiden Studien. Welche misst Schwangerschaften? Welche prüft Verträglichkeit?"
        },
        "options": {
          "DONE": "Wir haben den Artikel gelesen und eine Vermutung formuliert."
        },
        "replies": {
          "DONE": "Welche eurer Ideen lässt sich mit dem Text belegen?"
        },
        "hints": {
          "DONE": {
            "Foerder": [
              "Lies im Artikel den letzten Absatz. Was muss ein neues Mittel können?",
              "Es soll Schwangerschaften verhindern. Forschende müssen auch prüfen, ob es der Gesundheit schadet."
            ],
            "ESA": [
              "Lies den dritten Absatz im Artikel. Welche Fragen müssen Tests klären?",
              "Es kann einige Zeit dauern, bis klar ist, ob ein Mittel gut schützt und vertragen wird."
            ],
            "MSA": [
              "Lies im Artikel den Absatz zur Spermienzahl. Was sagt der Messwert über Schwangerschaften aus?",
              "Ein Ergebnis belegt nur das, was mit der beschriebenen Methode untersucht wurde."
            ],
            "AHR": [
              "Lies die Kästen zu Studie A und B. Welche Messgröße wurde jeweils erhoben?",
              "In Studie B waren die Teilnehmer bereits vasektomiert. Spermienparameter wurden nicht gemessen. Prüfe, was das für die Behauptung über Schwangerschaftsschutz bedeutet."
            ]
          }
        },
        "title": "Ein Artikel von Tom",
        "questions": [],
        "helpBefore": [
          "Lies den Absatz über die Prüfung eines neuen Mittels.",
          "Forschende prüfen Wirkung und Risiken getrennt. Das braucht Zeit."
        ],
        "recap": "Tom hat einen Artikel über die Forschung zur Verhütung für Männer mitgebracht."
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
            "Ein Freund meint: „Studie B zeigt schon, dass das Mittel sicher vor einer Schwangerschaft schützt.“",
            "Was sagen die Ergebnisse wirklich? Welche weitere Untersuchung würdet ihr vorschlagen?"
          ]
        },
        "task": {
          "Foerder": "Auf dem Laufzettel bei Tom: Schreibe deine Idee und eine offene Frage auf.",
          "ESA": "Auf dem Laufzettel bei Tom: Begründe deine Vermutung mit dem Artikel. Welche Frage bleibt offen?",
          "MSA": "Auf dem Laufzettel bei Tom: Notiere einen Befund, deine Vermutung und eine offene Frage.",
          "AHR": "Auf dem Laufzettel bei Tom: Prüfe die Behauptung mit zwei Befunden und zwei Grenzen. Skizziere die nächste Studie."
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
              "Lies den letzten Absatz des Artikels noch einmal. Was würdest du testen?",
              "Ob ein Mittel gut vertragen wird, ist eine Frage. Ob es eine Schwangerschaft verhindert, ist eine andere."
            ],
            "ESA": [
              "Lies den dritten Absatz im Artikel. Welche Fragen müssen Tests klären?",
              "Es kann einige Zeit dauern, bis klar ist, ob ein Mittel gut schützt und vertragen wird."
            ],
            "MSA": [
              "Lies im Artikel den Absatz zur Spermienzahl. Was sagt der Messwert über Schwangerschaften aus?",
              "Ein Ergebnis belegt nur das, was mit der beschriebenen Methode untersucht wurde."
            ],
            "AHR": [
              "Lies die Kästen zu Studie A und B. Welche Messgröße wurde jeweils erhoben?",
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
      "Enthält keine Hormone. Das Kondom fängt Sperma auf. Bei intaktem Kondom gelangen so keine Spermien in die Scheide.",
      "Bei einem Jahr Anwendung im Alltag werden etwa 60 bis 130 von 1.000 Frauen schwanger. Der Schutz hängt davon ab, ob das Kondom bei jedem Sex von Anfang an richtig benutzt wird.",
      "Das Kondom wird vor dem Sex über den steifen Penis gerollt. Jedes Mal ein neues benutzen.",
      "Kann reißen oder abrutschen. Fehler bei der Anwendung mindern den Schutz.",
      "Verändert die Periode nicht.",
      "Senkt das Risiko vieler sexuell übertragbarer Infektionen. Vollständigen Schutz bietet es nicht."
    ],
    "P": [
      "Kombinationspille",
      "Enthält zwei Hormone. Sie verhindern vor allem den Eisprung.",
      "Bei einem Jahr Anwendung im Alltag werden etwa 24 bis 70 von 1.000 Frauen schwanger. Vergessene Tabletten können den Schutz verringern.",
      "Die Pille wird regelmäßig nach Einnahmeplan genommen.",
      "Übelkeit ist möglich. Selten können gefährliche Blutgerinnsel entstehen. Die Eignung ärztlich klären.",
      "Blutungen können schwächer und weniger schmerzhaft werden.",
      "Schützt nicht vor sexuell übertragbaren Infektionen."
    ],
    "Cu": [
      "Kupferspirale",
      "Kupfer hemmt die Beweglichkeit und die Befruchtungsfähigkeit von Spermien. Enthält keine Hormone.",
      "Bei einem Jahr Anwendung werden etwa 1 bis 10 von 1.000 Frauen schwanger. Die Spirale schützt nach der Einlage sehr zuverlässig und braucht keine tägliche Anwendung. Das Modell spielt eine Rolle.",
      "Wird in einer Praxis in die Gebärmutter eingesetzt. Wirkt lange und sehr zuverlässig. Keine tägliche Einnahme.",
      "Das Einsetzen kann wehtun. Die Spirale kann verrutschen oder ausgestoßen werden.",
      "Die Periode kann stärker und schmerzhafter werden.",
      "Schützt nicht vor sexuell übertragbaren Infektionen."
    ],
    "H": [
      "Hormonspirale",
      "Gibt ein Hormon ab. Der Schleim am Gebärmutterhals wird für Spermien schwer durchlässig.",
      "Bei einem Jahr Anwendung werden etwa 1 bis 3 von 1.000 Frauen schwanger. Die Spirale schützt nach der Einlage sehr zuverlässig und braucht keine tägliche Anwendung. Das Modell spielt eine Rolle.",
      "Wird in einer Praxis in die Gebärmutter eingesetzt. Wirkt lange und sehr zuverlässig. Keine tägliche Einnahme.",
      "Das Einsetzen kann wehtun. Unregelmäßige Blutungen sind vor allem am Anfang möglich.",
      "Blutungen und Schmerzen können nachlassen. Wie es einer Person damit geht, ist offen.",
      "Schützt nicht vor sexuell übertragbaren Infektionen."
    ]
  }
};
