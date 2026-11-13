(() => {
  const app = document.getElementById("game-app");
  if (!app) return;

  const configuration = JSON.parse(document.getElementById("game-configuration").textContent);
  const questionUrl = app.dataset.questionUrl;
  const setupUrl = app.dataset.setupUrl;
  const soundPrefix = app.dataset.soundPrefix;
  const positionKey = "serpientes_escaleras_posiciones";
  const sounds = new Map();
  let muted = false;
  let timer = null;
  let remaining = 0;
  let currentQuestion = null;
  let answering = false;
  let gameStarted = false;
  let wheelRotation = 0;
  let currentTeam = 0;
  let round = 1;
  let memberIndexes = configuration.teams.map(() => 0);
  let positions = {};

  try {
    const savedPositions = JSON.parse(localStorage.getItem(positionKey) || "{}");
    if (savedPositions && typeof savedPositions === "object" && !Array.isArray(savedPositions)) {
      positions = savedPositions;
    }
  } catch (error) {
    console.error("No se pudieron leer las posiciones guardadas.", error);
  }
  configuration.teams.forEach((team) => {
    if (!Number.isInteger(positions[team.name])) positions[team.name] = 0;
    team.correctAnswers = Number(team.correctAnswers) || 0;
    team.incorrectAnswers = Number(team.incorrectAnswers) || 0;
  });

  function playSound(file, loop = false) {
    if (muted) return;
    let audio = sounds.get(file);
    if (!audio) {
      audio = new Audio(`${soundPrefix}${file}`);
      sounds.set(file, audio);
    }
    audio.pause();
    audio.currentTime = 0;
    audio.loop = loop;
    audio.play().catch((error) => console.warn(`No se pudo reproducir ${file}.`, error));
  }

  function saveState() {
    localStorage.setItem(positionKey, JSON.stringify(positions));
    localStorage.setItem("serpientes_escaleras_setup", JSON.stringify(configuration));
  }

  function activeTeam() {
    return configuration.teams[currentTeam];
  }

  function renderTurn() {
    const team = activeTeam();
    document.getElementById("turn-avatar").textContent = team.avatar;
    const teamName = document.getElementById("turn-team");
    teamName.textContent = team.name;
    teamName.style.color = team.hexColor;
    document.getElementById("turn-member").textContent =
      team.members[memberIndexes[currentTeam] % team.members.length];
    document.getElementById("round-indicator").textContent = `Ronda ${round}`;
    document.getElementById("turn-indicator").style.borderColor = team.hexColor;
  }

  function drawBoard() {
    const board = document.getElementById("camino-tablero");
    board.replaceChildren();
    for (let tile = 0; tile <= configuration.boardTiles; tile += 1) {
      const cell = document.createElement("div");
      cell.id = `casilla-${tile}`;
      cell.className = "casilla-nodo";
      if (tile === 0) {
        cell.classList.add("inicio");
        cell.textContent = "🚀 Inicio";
      } else if (tile === configuration.boardTiles) {
        cell.classList.add("meta");
        cell.textContent = `🏁 ${tile}`;
      } else {
        cell.textContent = String(tile);
      }
      board.append(cell);
    }
    renderPositions();
  }

  function renderPositions() {
    document.querySelectorAll(".contenedor-fichas-casilla").forEach((container) => container.remove());
    document.querySelectorAll(".casilla-nodo.ocupada").forEach((cell) => cell.classList.remove("ocupada"));
    configuration.teams.forEach((team) => {
      const position = Math.max(0, Math.min(configuration.boardTiles, positions[team.name] || 0));
      const cell = document.getElementById(`casilla-${position}`);
      if (!cell) return;
      cell.classList.add("ocupada");
      let tokens = cell.querySelector(".contenedor-fichas-casilla");
      if (!tokens) {
        tokens = document.createElement("div");
        tokens.className = "contenedor-fichas-casilla";
        cell.append(tokens);
      }
      const token = document.createElement("span");
      token.className = "ficha-jugador";
      token.textContent = team.avatar;
      token.title = team.name;
      tokens.append(token);
    });
    renderLeaderboard();
  }

  function renderLeaderboard() {
    const list = document.getElementById("leaderboard-list");
    list.replaceChildren();
    [...configuration.teams]
      .sort((a, b) => positions[b.name] - positions[a.name])
      .forEach((team, index) => {
        const item = document.createElement("div");
        item.className = "leaderboard-item";
        item.style.borderLeftColor = team.hexColor;
        const info = document.createElement("div");
        info.className = "leaderboard-team-info";
        const rank = document.createElement("span");
        rank.className = "badge-casilla";
        rank.textContent = ["🥇", "🥈", "🥉", "🎖️"][index] || `${index + 1}º`;
        const avatar = document.createElement("span");
        avatar.className = "leaderboard-avatar";
        avatar.textContent = team.avatar;
        const name = document.createElement("span");
        name.className = "leaderboard-team-name";
        name.style.color = team.hexColor;
        name.textContent = team.name;
        info.append(rank, avatar, name);

        const stats = document.createElement("div");
        stats.className = "leaderboard-stats";
        const position = document.createElement("span");
        position.className = "badge-casilla";
        position.textContent = positions[team.name] ? `Casilla ${positions[team.name]} / ${configuration.boardTiles}` : "Inicio";
        stats.append(position);
        [-1, 1].forEach((change) => {
          const button = document.createElement("button");
          button.className = "btn-adj";
          button.type = "button";
          button.textContent = change > 0 ? "+" : "−";
          button.setAttribute("aria-label", `${change > 0 ? "Avanzar" : "Retroceder"} ${team.name} una casilla`);
          button.addEventListener("click", () => moveTeam(team, change));
          stats.append(button);
        });
        item.append(info, stats);
        list.append(item);
      });
  }

  function moveTeam(team, steps) {
    positions[team.name] = Math.max(0, Math.min(configuration.boardTiles, (positions[team.name] || 0) + steps));
    saveState();
    renderPositions();
    document.getElementById(`casilla-${positions[team.name]}`)?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    if (positions[team.name] >= configuration.boardTiles) showVictory(team);
  }

  function stopTimer() {
    if (timer !== null) window.clearInterval(timer);
    timer = null;
    document.getElementById("timer-box").hidden = true;
    sounds.forEach((audio) => {
      if (audio.loop) { audio.pause(); audio.currentTime = 0; }
    });
  }

  function startTimer(seconds) {
    stopTimer();
    if (!seconds) return;
    remaining = seconds;
    const box = document.getElementById("timer-box");
    box.hidden = false;
    box.classList.remove("timer-warning");
    document.getElementById("time-left").textContent = String(remaining);
    if (gameStarted) {
      timer = window.setInterval(() => {
        remaining -= 1;
        document.getElementById("time-left").textContent = String(remaining);
        if (remaining <= 10) box.classList.add("timer-warning");
        if (remaining <= 0) {
          stopTimer();
          finishAnswer(false, true);
        }
      }, 1000);
    }
  }

  async function loadQuestion() {
    answering = false;
    document.getElementById("btn-next-question").classList.add("hidden");
    document.getElementById("feedback-message").textContent = "";
    document.getElementById("feedback-message").className = "feedback";
    document.getElementById("options-container").replaceChildren();
    document.getElementById("math-question").textContent = "Cargando pregunta…";
    let response;
    try {
      response = await fetch(questionUrl, { headers: { Accept: "application/json" }, cache: "no-store" });
    } catch (error) {
      document.getElementById("math-question").textContent = "No se pudo conectar con el servidor.";
      console.error("Falló la conexión al solicitar una pregunta.", error);
      return;
    }
    if (!response.ok) {
      const detail = await response.json();
      document.getElementById("math-question").textContent = detail.error || "No se pudo cargar la pregunta.";
      return;
    }
    currentQuestion = await response.json();
    document.getElementById("question-category").textContent = currentQuestion.category;
    document.getElementById("math-question").textContent = currentQuestion.prompt;
    currentQuestion.options.forEach((option, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "fruit-btn";
      button.textContent = `Opción ${String.fromCharCode(65 + index)}: ${option.value}`;
      button.addEventListener("click", () => finishAnswer(option.correct, false));
      document.getElementById("options-container").append(button);
    });
    startTimer(currentQuestion.time_limit);
  }

  function finishAnswer(correct, timedOut) {
    if (answering) return;
    answering = true;
    stopTimer();
    document.querySelectorAll(".fruit-btn").forEach((button) => { button.disabled = true; });
    const team = activeTeam();
    if (correct) {
      team.correctAnswers += 1;
      document.getElementById("feedback-message").textContent = "✔ ¡Respuesta correcta! Gira la ruleta para avanzar.";
      document.getElementById("feedback-message").classList.add("correct");
      playSound("Ganar.mp3");
      openWheel(1);
    } else {
      team.incorrectAnswers += 1;
      document.getElementById("feedback-message").textContent = timedOut
        ? "⏰ ¡Se acabó el tiempo! Gira para saber cuánto retrocedes."
        : "✖ ¡Respuesta incorrecta! Gira la ruleta del destino.";
      document.getElementById("feedback-message").classList.add("incorrect");
      playSound(timedOut ? "fin-tiempo.mp3" : "perder.mp3");
      openWheel(-1);
    }
    saveState();
  }

  function openWheel(direction) {
    const modal = document.getElementById("wheel-modal");
    modal.dataset.direction = String(direction);
    document.getElementById("wheel-title").textContent = direction > 0 ? "¡Gira para avanzar!" : "¡Gira la ruleta del destino!";
    document.getElementById("wheel-result").textContent = "";
    document.getElementById("spin-wheel").disabled = false;
    modal.classList.remove("hidden");
  }

  document.getElementById("spin-wheel").addEventListener("click", () => {
    const button = document.getElementById("spin-wheel");
    const modal = document.getElementById("wheel-modal");
    const direction = Number(modal.dataset.direction);
    const steps = Math.floor(Math.random() * 3) + 1;
    button.disabled = true;
    playSound("ruleta.mp3");
    wheelRotation += 1800 + Math.floor(Math.random() * 360);
    document.getElementById("wheel").style.transform = `rotate(${wheelRotation}deg)`;
    window.setTimeout(() => {
      const team = activeTeam();
      const movement = steps * direction;
      document.getElementById("wheel-result").textContent =
        direction > 0 ? `¡Avanzas ${steps} casillas!` : `¡Retrocedes ${steps} casillas!`;
      moveTeam(team, movement);
      window.setTimeout(() => {
        modal.classList.add("hidden");
        if (!document.getElementById("victory-modal").classList.contains("hidden")) return;
        document.getElementById("btn-next-question").classList.remove("hidden");
      }, 1100);
    }, 1900);
  });

  function showVictory(team) {
    stopTimer();
    const modal = document.getElementById("victory-modal");
    document.getElementById("winner-avatar").textContent = team.avatar;
    const winnerName = document.getElementById("winner-name");
    winnerName.textContent = team.name;
    winnerName.style.color = team.hexColor;
    const tbody = document.getElementById("victory-stats");
    tbody.replaceChildren();
    configuration.teams.forEach((entry) => {
      const row = document.createElement("tr");
      const values = [entry.name, `Casilla ${positions[entry.name] || 0}`, entry.correctAnswers, entry.incorrectAnswers];
      values.forEach((value) => {
        const cell = document.createElement("td");
        cell.textContent = String(value);
        row.append(cell);
      });
      tbody.append(row);
    });
    modal.classList.remove("hidden");
    playSound("victoria.mp3");
  }

  document.getElementById("btn-next-question").addEventListener("click", () => {
    stopTimer();
    memberIndexes[currentTeam] = (memberIndexes[currentTeam] + 1) % activeTeam().members.length;
    currentTeam = (currentTeam + 1) % configuration.teams.length;
    if (currentTeam === 0) round += 1;
    renderTurn();
    loadQuestion();
  });
  document.getElementById("btn-close-rules").addEventListener("click", () => {
    document.getElementById("rules-modal").classList.add("hidden");
    gameStarted = true;
    if (currentQuestion?.time_limit) startTimer(remaining || currentQuestion.time_limit);
    playSound("a-jugar.mp3");
  });
  document.getElementById("mute-button").addEventListener("click", (event) => {
    muted = !muted;
    event.currentTarget.setAttribute("aria-pressed", String(muted));
    event.currentTarget.textContent = muted ? "🔇 Silencio" : "🔊 Sonido";
    if (muted) sounds.forEach((audio) => { audio.pause(); audio.currentTime = 0; });
  });
  document.getElementById("btn-play-again").addEventListener("click", () => {
    localStorage.removeItem(positionKey);
    window.location.href = setupUrl;
  });

  drawBoard();
  renderTurn();
  loadQuestion();
})();
