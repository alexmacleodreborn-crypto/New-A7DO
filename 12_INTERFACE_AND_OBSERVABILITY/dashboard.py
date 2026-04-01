class Dashboard:
    """
    Lightweight text dashboard for CLI and tests.
    Reads from an IntrospectionSnapshot-compatible object.
    """

    def __init__(self, snapshot):
        self.snapshot = snapshot

    def render_text(self) -> str:
        view = self.snapshot.capture()
        world = view.get("world", {})
        memory = view.get("memory", [])
        attention = view.get("attention", [])
        prediction = view.get("prediction", {})
        council = view.get("council", {})
        civilisation = world.get("civilisation") or {}

        lines = [
            "WORLD",
            f"energy={world.get('energy')}, strain={world.get('strain')}, time={world.get('time')}",
            f"place={world.get('current_place')}, action={world.get('last_action')}",
            "MEMORY",
            f"recent={memory}",
            "ATTENTION",
            f"focus={attention}",
            "PREDICTION",
            f"forecast={prediction}",
            "COUNCIL",
            f"opinions={council}",
        ]

        if civilisation:
            lines.extend(
                [
                    "CIVILISATION",
                    (
                        f"population={civilisation.get('population')}, "
                        f"season={civilisation.get('season')}, "
                        f"choice={civilisation.get('dominant_choice')}"
                    ),
                    f"story={civilisation.get('story')}",
                ]
            )

        return "\n".join(lines)
