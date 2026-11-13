"""Question generation for both game difficulty levels."""

import random


def _options(answer, count):
    values = {answer}
    while len(values) < count:
        offset = random.randint(1, max(4, min(12, abs(answer) // 3 + 2)))
        candidate = answer + random.choice((-offset, offset))
        if candidate >= 0:
            values.add(candidate)
    options = [{"value": value, "correct": value == answer} for value in values]
    random.shuffle(options)
    return options


def _arithmetic_question(level):
    if level == "Alpha":
        first = random.randint(1, 15)
        second = random.randint(1, 15)
        operation = random.choice(("+", "-"))
        if operation == "-" and second > first:
            first, second = second, first
        answer = first + second if operation == "+" else first - second
        prompt = f"{first} {operation} {second} = ?"
        count = 2
        time_limit = 0
    else:
        if random.choice((True, False)):
            first, second = random.randint(2, 11), random.randint(2, 11)
            operation = "×"
            answer = first * second
        else:
            divisor = random.randint(2, 10)
            answer = random.randint(2, 11)
            first, second, operation = answer * divisor, divisor, "÷"
        prompt = f"{first} {operation} {second} = ?"
        count = 3
        time_limit = 15
    return {
        "prompt": prompt,
        "category": "Cálculo mental",
        "time_limit": time_limit,
        "options": _options(answer, count),
    }


def _challenge_question(level):
    count = 2 if level == "Alpha" else 3
    examples = [
        (
            "Geometría",
            "📐",
            lambda: (
                lambda base, height: (
                    f"Un rectángulo mide {base} cm de base y {height} cm de altura. "
                    "¿Cuál es su área?",
                    base * height,
                )
            )(random.randint(4, 15), random.randint(3, 12)),
        ),
        (
            "Fracciones",
            "🍕",
            lambda: (
                lambda pieces: (
                    f"Una pizza tiene {pieces} rebanadas. Si se comieron la mitad, "
                    "¿cuántas rebanadas se comieron?",
                    pieces // 2,
                )
            )(random.randint(2, 10) * 2),
        ),
        (
            "Aritmética",
            "🧮",
            lambda: (
                lambda rows, seats: (
                    f"Hay {rows} filas con {seats} sillas cada una. "
                    "¿Cuántas sillas hay en total?",
                    rows * seats,
                )
            )(random.randint(4, 12), random.randint(3, 10)),
        ),
    ]
    if level == "Beta":
        examples.extend(
            [
                (
                    "Geometría",
                    "📦",
                    lambda: (
                        lambda length, width, height: (
                            f"Una caja mide {length} × {width} × {height} cm. "
                            "¿Cuál es su volumen?",
                            length * width * height,
                        )
                    )(
                        random.randint(2, 8),
                        random.randint(2, 7),
                        random.randint(2, 6),
                    ),
                ),
                (
                    "Porcentajes",
                    "💯",
                    lambda: (
                        lambda divisor, multiplier: (
                            f"¿Cuánto es el 25% de {divisor * multiplier}?",
                            (divisor * multiplier) // 4,
                        )
                    )(4, random.randint(4, 40)),
                ),
            ]
        )
    category, icon, make_prompt = random.choice(examples)
    prompt, answer = make_prompt()
    return {
        "prompt": f"{icon} {prompt}",
        "category": category,
        "time_limit": 60,
        "options": _options(answer, count),
    }


def generate_question(level):
    """Return one randomized arithmetic or word-problem question."""
    if level not in {"Alpha", "Beta"}:
        raise ValueError(f"Nivel no reconocido: {level}")
    generator = _challenge_question if random.random() > 0.5 else _arithmetic_question
    return generator(level)
