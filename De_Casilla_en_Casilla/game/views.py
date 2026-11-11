import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods

from .logic import generate_question

TEAM_COLORS = ["#3B82F6", "#F97316", "#10B981", "#8B5CF6"]
TEAM_CLASSES = ["team-blue", "team-orange", "team-green", "team-purple"]
AVATARS = ["🦁", "🦊", "🐼", "🐨", "🐸", "🐙", "🦖", "🦄"]
DEFAULT_TEAMS = [
    {"name": "Equipo León", "avatar": "🦁", "members": ["León 1"]},
    {"name": "Equipo Zorro", "avatar": "🦊", "members": ["Zorro 1"]},
    {"name": "Equipo Panda", "avatar": "🐼", "members": ["Panda 1"]},
    {"name": "Equipo Koala", "avatar": "🐨", "members": ["Koala 1"]},
]


def home(request):
    return render(request, "home.html")


@require_http_methods(["GET", "POST"])
def setup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.POST.get("configuration", ""))
            configuration = _validate_configuration(data)
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            return _setup_page(
                request,
                error_message=str(error),
                submitted_configuration=request.POST.get("configuration", ""),
            )

        request.session["game_configuration"] = configuration
        request.session.modified = True
        return redirect(reverse("play", kwargs={"level": configuration["level"].lower()}))

    level = request.GET.get("level", "Alpha")
    if level not in {"Alpha", "Beta"}:
        level = "Alpha"
    return _setup_page(request, level=level)


def _setup_page(
    request, *, error_message="", submitted_configuration="", level="Alpha"
):
    teams = [
        {
            **team,
            "id": index + 1,
            "color": TEAM_COLORS[index],
            "color_class": TEAM_CLASSES[index],
            "avatars": AVATARS,
        }
        for index, team in enumerate(DEFAULT_TEAMS)
    ]
    return render(
        request,
        "setup.html",
        {
            "teams": teams,
            "selected_level": level,
            "error_message": error_message,
            "submitted_configuration": submitted_configuration,
        },
    )


def _validate_configuration(data):
    if not isinstance(data, dict):
        raise ValueError("No se recibió una configuración válida.")

    level = data.get("level")
    if level not in {"Alpha", "Beta"}:
        raise ValueError("Selecciona un nivel de juego válido.")

    try:
        quantity = int(data.get("qty"))
        board_tiles = int(data.get("boardTiles"))
    except (TypeError, ValueError) as error:
        raise ValueError("La cantidad de equipos o casillas no es válida.") from error
    if quantity not in {2, 3, 4}:
        raise ValueError("Elige entre 2 y 4 equipos.")
    if not 10 <= board_tiles <= 200:
        raise ValueError("El tablero debe tener entre 10 y 200 casillas.")

    submitted_teams = data.get("teams")
    if not isinstance(submitted_teams, list) or len(submitted_teams) < quantity:
        raise ValueError("Faltan los datos de uno o más equipos.")

    teams = []
    names = set()
    for index, team in enumerate(submitted_teams[:quantity]):
        if not isinstance(team, dict):
            raise ValueError("Los datos de un equipo no son válidos.")
        name = str(team.get("name", "")).strip()[:20]
        avatar = team.get("avatar")
        members = team.get("members")
        if not name:
            raise ValueError("El nombre de cada equipo es obligatorio.")
        if name.casefold() in names:
            raise ValueError("Cada equipo debe tener un nombre único.")
        names.add(name.casefold())
        if avatar not in AVATARS:
            raise ValueError("Selecciona una mascota válida para cada equipo.")
        if not isinstance(members, list) or not 1 <= len(members) <= 6:
            raise ValueError("Cada equipo debe tener entre 1 y 6 integrantes.")
        clean_members = [str(member).strip()[:30] for member in members]
        if any(not member for member in clean_members):
            raise ValueError("Los nombres de integrantes no pueden estar vacíos.")
        teams.append(
            {
                "id": index + 1,
                "name": name,
                "avatar": avatar,
                "members": clean_members,
                "colorClass": TEAM_CLASSES[index],
                "hexColor": TEAM_COLORS[index],
                "correctAnswers": 0,
                "incorrectAnswers": 0,
            }
        )

    return {
        "level": level,
        "qty": quantity,
        "boardTiles": board_tiles,
        "teams": teams,
    }


@require_GET
def play(request, level):
    configuration = request.session.get("game_configuration")
    requested_level = level.capitalize()
    if requested_level not in {"Alpha", "Beta"}:
        return redirect("setup")
    if not configuration or configuration.get("level") != requested_level:
        return redirect(f"{reverse('setup')}?level={requested_level}")
    return render(
        request,
        "play.html",
        {
            "configuration": configuration,
            "level_name": "Alfa" if requested_level == "Alpha" else "Beta",
            "level_icon": "🍎" if requested_level == "Alpha" else "🚀",
            "level_description": (
                "Sumas y restas" if requested_level == "Alpha" else "Multiplicación y división"
            ),
        },
    )


@require_GET
def question(request):
    configuration = request.session.get("game_configuration")
    if not configuration:
        return JsonResponse(
            {"error": "Configura una partida antes de solicitar preguntas."},
            status=400,
        )
    return JsonResponse(generate_question(configuration["level"]))
