import json
import requests
import ipywidgets as widgets
from IPython.display import display

def show_flashcards(url):
    # JSON mit den Karten laden
    response = requests.get(url)
    response.raise_for_status()
    cards = json.loads(response.text)

    if not cards:
        print("Keine Karten gefunden.")
        return

    has_multiple = len(cards) > 1

    # Zustand: aktuelle Karte + ob Rückseite schon gezeigt wurde
    state = {
        "index": 0,
        "back_shown": False
    }

    # Widgets
    front_label = widgets.HTML()
    back_label = widgets.HTML()
    show_button = widgets.Button(description="Hinweis anzeigen")

    prev_button = None
    next_button = None
    if has_multiple:
        prev_button = widgets.Button(description="Previous")
        next_button = widgets.Button(description="Next", disabled=True)

    # Karte (Front/Back) aktualisieren
    def update_card():
        i = state["index"]
        front = cards[i].get("front", "")
        back = cards[i].get("back", "")

        front_label.value = f"<b>{front}</b>"
        if state["back_shown"]:
            back_label.value = back
        else:
            back_label.value = ""

    # Navigations-Buttons (sichtbar/aktiv) aktualisieren
    def update_nav_buttons():
        if not has_multiple:
            return

        # Previous nur anzeigen, wenn wir NICHT auf der ersten Karte sind
        if state["index"] == 0:
            prev_button.layout.display = "none"
        else:
            prev_button.layout.display = ""

        # Next: auf letzter Karte komplett ausblenden,
        # sonst anzeigen und ggf. aktivieren/deaktivieren
        if state["index"] < len(cards) - 1:
            next_button.layout.display = ""
            next_button.disabled = not state["back_shown"]
        else:
            next_button.layout.display = "none"

    # Klick auf "Hinweis anzeigen"
    def on_show_clicked(b):
        if not state["back_shown"]:
            state["back_shown"] = True
            update_card()
            update_nav_buttons()

    show_button.on_click(on_show_clicked)

    # Klick auf "Next"
    if has_multiple:
        def on_next_clicked(b):
            if state["index"] < len(cards) - 1:
                state["index"] += 1
                state["back_shown"] = False
                update_card()
                update_nav_buttons()

        next_button.on_click(on_next_clicked)

        # Klick auf "Previous"
        def on_prev_clicked(b):
            if state["index"] > 0:
                state["index"] -= 1
                state["back_shown"] = False
                update_card()
                update_nav_buttons()

        prev_button.on_click(on_prev_clicked)

    # Startzustand
    update_card()
    update_nav_buttons()

    # Layout zusammenbauen
    children = [front_label, show_button, back_label]
    if has_multiple:
        children.append(widgets.HBox([prev_button, next_button]))

    box = widgets.VBox(children)
    display(box)
