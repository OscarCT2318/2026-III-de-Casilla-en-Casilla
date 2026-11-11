(() => {
  const form = document.getElementById("setup-form");
  if (!form) return;

  const teams = Array.from(document.querySelectorAll(".team-card")).map((card, index) => ({
    id: index + 1,
    name: card.querySelector(".team-name-input").value,
    avatar: card.querySelector(".avatar-preview-circle").textContent.trim(),
    members: [`${card.querySelector(".team-name-input").value.replace(/^Equipo /, "")} 1`],
  }));
  const state = { level: "Alpha", qty: 3, boardTiles: 100, teams };
  const queryLevel = new URLSearchParams(window.location.search).get("level");
  if (queryLevel === "Alpha" || queryLevel === "Beta") state.level = queryLevel;

  const submitted = document.getElementById("submitted-configuration")?.textContent;
  if (submitted) {
    try {
      let previous = JSON.parse(submitted);
      if (typeof previous === "string") previous = JSON.parse(previous);
      if (previous && typeof previous === "object" && previous.level) {
        state.level = previous.level;
        state.qty = previous.qty;
        state.boardTiles = previous.boardTiles;
        previous.teams?.forEach((team, index) => {
          if (state.teams[index] && team) Object.assign(state.teams[index], team);
        });
      }
    } catch (error) {
      console.error("No se pudo restaurar la configuración enviada.", error);
    }
  } else {
    try {
      const previous = JSON.parse(localStorage.getItem("serpientes_escaleras_setup") || "null");
      if (previous?.teams?.length) {
        state.level = previous.level === "Beta" ? "Beta" : state.level;
        state.qty = [2, 3, 4].includes(Number(previous.qty)) ? Number(previous.qty) : state.qty;
        state.boardTiles = Number(previous.boardTiles) || state.boardTiles;
        previous.teams.slice(0, 4).forEach((team, index) => {
          if (state.teams[index] && team) Object.assign(state.teams[index], team);
        });
      }
    } catch (error) {
      console.error("No se pudo leer la configuración guardada.", error);
    }
  }

  const cards = Array.from(document.querySelectorAll(".team-card"));
  const errorBox = document.getElementById("setup-error");
  const nameFromAvatar = new Map([
    ["🦁", "León"], ["🦊", "Zorro"], ["🐼", "Panda"], ["🐨", "Koala"],
    ["🐸", "Rana"], ["🐙", "Pulpo"], ["🦖", "Dino"], ["🦄", "Unicornio"],
  ]);

  function renderTeam(index) {
    const team = state.teams[index];
    const card = cards[index];
    const nameInput = card.querySelector(".team-name-input");
    const preview = card.querySelector(".avatar-preview-circle");
    const membersList = card.querySelector(".member-name-list");
    const count = card.querySelector(".counter-value");

    nameInput.value = team.name;
    preview.textContent = team.avatar;
    count.textContent = String(team.members.length);
    card.querySelector(".minus-btn").disabled = team.members.length <= 1;
    card.querySelector(".plus-btn").disabled = team.members.length >= 6;
    membersList.replaceChildren();
    team.members.forEach((member, memberIndex) => {
      const input = document.createElement("input");
      input.className = "member-name-input";
      input.type = "text";
      input.maxLength = 30;
      input.required = true;
      input.value = member;
      input.setAttribute("aria-label", `Integrante ${memberIndex + 1} del equipo ${index + 1}`);
      input.addEventListener("input", () => { team.members[memberIndex] = input.value; });
      membersList.append(input);
    });
    card.querySelectorAll(".avatar-opt-btn").forEach((button) => {
      const active = button.dataset.emoji === team.avatar;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
  }

  function renderSelection() {
    document.querySelectorAll(".level-btn").forEach((button) => {
      const active = button.dataset.level === state.level;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    document.querySelectorAll(".qty-btn").forEach((button) => {
      const active = Number(button.dataset.qty) === state.qty;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    cards.forEach((card, index) => {
      card.classList.toggle("hidden-card", index >= state.qty);
      renderTeam(index);
    });
    document.getElementById("input-board-tiles").value = String(state.boardTiles);
  }

  document.querySelectorAll(".level-btn").forEach((button) => {
    button.addEventListener("click", () => { state.level = button.dataset.level; renderSelection(); });
  });
  document.querySelectorAll(".qty-btn").forEach((button) => {
    button.addEventListener("click", () => { state.qty = Number(button.dataset.qty); renderSelection(); });
  });
  cards.forEach((card, index) => {
    const team = state.teams[index];
    card.querySelector(".team-name-input").addEventListener("input", (event) => {
      team.name = event.currentTarget.value;
    });
    card.querySelectorAll(".avatar-opt-btn").forEach((button) => {
      button.addEventListener("click", () => {
        team.avatar = button.dataset.emoji;
        const friendlyName = `Equipo ${nameFromAvatar.get(team.avatar)}`;
        team.name = friendlyName;
        team.members = team.members.map((_, memberIndex) => `${nameFromAvatar.get(team.avatar)} ${memberIndex + 1}`);
        renderTeam(index);
      });
    });
    card.querySelector(".minus-btn").addEventListener("click", () => {
      if (team.members.length > 1) team.members.pop();
      renderTeam(index);
    });
    card.querySelector(".plus-btn").addEventListener("click", () => {
      if (team.members.length >= 6) return;
      const base = team.name.replace(/^Equipo /, "");
      team.members.push(`${base} ${team.members.length + 1}`);
      renderTeam(index);
    });
  });
  document.getElementById("input-board-tiles").addEventListener("input", (event) => {
    state.boardTiles = Number(event.currentTarget.value);
  });

  form.addEventListener("submit", (event) => {
    state.boardTiles = Number(document.getElementById("input-board-tiles").value);
    const activeTeams = state.teams.slice(0, state.qty);
    const names = activeTeams.map((team) => team.name.trim().toLocaleLowerCase());
    const invalidMembers = activeTeams.some((team) =>
      !Array.isArray(team.members) || team.members.length < 1 || team.members.length > 6 ||
      team.members.some((member) => !member.trim()));
    const duplicateNames = new Set(names).size !== names.length;
    if (!activeTeams.every((team) => team.name.trim()) || duplicateNames || invalidMembers ||
        !Number.isInteger(state.boardTiles) || state.boardTiles < 10 || state.boardTiles > 200) {
      event.preventDefault();
      errorBox.textContent = duplicateNames ? "Cada equipo debe tener un nombre único." :
        "Revisa los nombres de equipos e integrantes y el tamaño del tablero (10-200).";
      errorBox.hidden = false;
      errorBox.focus();
      return;
    }
    const configuration = {
      level: state.level,
      qty: state.qty,
      boardTiles: state.boardTiles,
      teams: activeTeams,
    };
    document.getElementById("configuration-data").value = JSON.stringify(configuration);
    localStorage.setItem("serpientes_escaleras_setup", JSON.stringify(configuration));
    localStorage.removeItem("serpientes_escaleras_posiciones");
  });

  renderSelection();
})();
