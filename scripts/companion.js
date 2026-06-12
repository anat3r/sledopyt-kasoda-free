// Beast Companion Manager — Альтернативный Следопыт (Kasoda)
// Управление Зверем-спутником Повелителя зверей.

const MODULE_ID = "sledopyt-kasoda-free";
const FLAG_IMPRINTS = "imprints";       // [{uuid, name, cr}]
const FLAG_ACTIVE   = "activeImprint";  // index in imprints array
const FIGURINE_UUID_FLAG = "figurineItemId"; // actor flag → figurine item id

// ── Helpers ──────────────────────────────────────────────────────────────────

function _pb(actor) {
  return actor?.system?.attributes?.prof ?? 2;
}

function _rangerLevel(actor) {
  return actor?.classes?.sledopyt?.system?.levels ?? 1;
}

function _maxHp(baseHp, rangerLevel) {
  return Math.max(baseHp, 5 * rangerLevel);
}

function _getFigurineItem(actor) {
  return actor?.items?.find(i => i.flags?.[MODULE_ID]?.isFigurine === true) ?? null;
}

// ── Dialog helpers ────────────────────────────────────────────────────────────

async function _showBeastPicker(rangerActor, currentImprints, maxSlots) {
  const maxCr = Math.floor(_rangerLevel(rangerActor) / 2) || 1;

  // Collect world actors: NPC type, user has OWNER permission
  const worldBeasts = game.actors.filter(a =>
    a.type === "npc" &&
    a.testUserPermission(game.user, "OWNER") &&
    a.id !== rangerActor.id
  ).sort((a, b) => (a.system?.details?.cr ?? 0) - (b.system?.details?.cr ?? 0));

  const isFull = currentImprints.length >= maxSlots;
  const replaceWarning = isFull
    ? `<p class="notification warning">Статуэтка заполнена (${maxSlots}/${maxSlots}). При добавлении нового зверя один из существующих отпечатков будет удалён.</p>`
    : "";

  const worldOptions = worldBeasts.map(a => {
    const cr = a.system?.details?.cr ?? "?";
    return `<option value="world:${a.id}">🐾 ${a.name} (ПО ${cr}) — актёр мира</option>`;
  }).join("");

  const content = `
    <style>
      .beast-picker label { font-weight: bold; display: block; margin-top: 8px; }
      .beast-picker select { width: 100%; margin-bottom: 4px; }
      .beast-picker .hint { font-size: 0.85em; color: #666; margin-bottom: 6px; }
      .beast-picker .section-title { font-size: 1em; font-weight: bold; margin-top: 12px; border-bottom: 1px solid #ccc; padding-bottom: 2px; }
    </style>
    <div class="beast-picker">
      ${replaceWarning}
      <p>Выберите зверя, чей отпечаток вы хотите сохранить в статуэтке.</p>

      <div class="section-title">Актёры мира (переданные мастером)</div>
      <p class="hint">NPC-актёры, на которых у вас есть право владения. Мастер передаёт право через настройки актёра → Разрешения.</p>
      ${worldBeasts.length > 0
        ? `<select id="beast-world"><option value="">— выберите актёра —</option>${worldOptions}</select>`
        : `<p class="hint" style="color:#999"><em>Нет доступных актёров мира. Мастер может передать право владения.</em></p>`
      }

      <div class="section-title">Компендиум</div>
      <p class="hint">
        Откройте Обозреватель компендиумов (кнопка 📚 в боковой панели), найдите нужного зверя (ПО ≤ ${maxCr}),
        создайте его в мире (правая кнопка → «Импортировать»), а затем найдите его выше в списке «Актёры мира».
      </p>
      <p class="hint" style="color:#888"><em>Если зверя уже нет в мире — сначала импортируйте его из компендиума, мастер передаст вам право владения.</em></p>

      <hr>
      <p class="hint">Максимальный ПО зверя: <strong>${maxCr}</strong> (половина уровня Следопыта). Доступно слотов: <strong>${Math.max(0, maxSlots - currentImprints.length)}</strong> из <strong>${maxSlots}</strong>.</p>
    </div>
  `;

  return new Promise(resolve => {
    new Dialog({
      title: "Привязать зверя к статуэтке",
      content,
      buttons: {
        ok: {
          icon: '<i class="fas fa-paw"></i>',
          label: "Привязать",
          callback: html => {
            const worldVal = html.find("#beast-world").val();
            if (worldVal && worldVal !== "") {
              const id = worldVal.replace("world:", "");
              resolve({ source: "world", actor: game.actors.get(id) });
            } else {
              ui.notifications.warn("Выберите зверя из списка.");
              resolve(null);
            }
          }
        },
        cancel: { label: "Отмена", callback: () => resolve(null) }
      },
      default: "ok"
    }).render(true);
  });
}

async function _showReplaceDialog(imprints) {
  const options = imprints.map((imp, i) =>
    `<option value="${i}">${imp.name} (ПО ${imp.cr ?? "?"})</option>`
  ).join("");

  return new Promise(resolve => {
    new Dialog({
      title: "Статуэтка заполнена",
      content: `
        <p>Все слоты заняты. Выберите отпечаток, который будет заменён:</p>
        <select id="replace-idx" style="width:100%">${options}</select>
      `,
      buttons: {
        ok: {
          label: "Заменить",
          callback: html => resolve(parseInt(html.find("#replace-idx").val()))
        },
        cancel: { label: "Отмена", callback: () => resolve(null) }
      },
      default: "ok"
    }).render(true);
  });
}

async function _showSummonDialog(imprints) {
  if (imprints.length === 1) return imprints[0];
  const options = imprints.map((imp, i) =>
    `<option value="${i}">${imp.name} (ПО ${imp.cr ?? "?"})</option>`
  ).join("");

  return new Promise(resolve => {
    new Dialog({
      title: "Призвать зверя из статуэтки",
      content: `
        <p>Выберите зверя для призыва:</p>
        <select id="summon-idx" style="width:100%">${options}</select>
      `,
      buttons: {
        ok: {
          icon: '<i class="fas fa-dragon"></i>',
          label: "Призвать",
          callback: html => resolve(imprints[parseInt(html.find("#summon-idx").val())])
        },
        cancel: { label: "Отмена", callback: () => resolve(null) }
      },
      default: "ok"
    }).render(true);
  });
}

// ── Core API ──────────────────────────────────────────────────────────────────

/**
 * Привязать зверя к статуэтке.
 * Открывает диалог выбора, создаёт копию актёра с бонусами класса,
 * сохраняет UUID в флагах статуэтки.
 */
async function bindBeast(figurineItem) {
  const actor = figurineItem.actor;
  if (!actor) return ui.notifications.error("Статуэтка не находится на листе персонажа.");

  const maxSlots = _pb(actor);
  const imprints = figurineItem.getFlag(MODULE_ID, FLAG_IMPRINTS) ?? [];

  const chosen = await _showBeastPicker(actor, imprints, maxSlots);
  if (!chosen) return;

  const sourceActor = chosen.actor;
  if (!sourceActor) return ui.notifications.error("Актёр не найден.");

  const maxCr = Math.floor(_rangerLevel(actor) / 2) || 1;
  const cr = sourceActor.system?.details?.cr ?? 0;
  if (cr > maxCr) {
    return ui.notifications.error(`ПО зверя (${cr}) превышает допустимое (${maxCr}). Выберите другого.`);
  }

  // Create companion actor
  const newActor = await _createCompanionActor(actor, sourceActor);
  if (!newActor) return;

  // Build new imprints list
  const newImprints = [...imprints];
  let replaceIdx = null;
  if (newImprints.length >= maxSlots) {
    replaceIdx = await _showReplaceDialog(newImprints);
    if (replaceIdx === null) { await newActor.delete(); return; }
    // Delete old companion actor if it exists
    const old = await fromUuid(newImprints[replaceIdx].uuid).catch(() => null);
    if (old) await old.delete().catch(() => {});
    newImprints[replaceIdx] = { uuid: newActor.uuid, name: newActor.name, cr };
  } else {
    newImprints.push({ uuid: newActor.uuid, name: newActor.name, cr });
  }

  await figurineItem.setFlag(MODULE_ID, FLAG_IMPRINTS, newImprints);
  // Set newly bound beast as active
  const activeIdx = replaceIdx ?? newImprints.length - 1;
  await figurineItem.setFlag(MODULE_ID, FLAG_ACTIVE, activeIdx);
  // Consume one use slot (imprint slot)
  const spent = Math.min((figurineItem.system.uses.spent ?? 0) + 1, maxSlots);
  await figurineItem.update({ "system.uses.spent": spent });

  ChatMessage.create({
    content: `<p><strong>${actor.name}</strong> привязал зверя <strong>${newActor.name}</strong> к статуэтке. Слотов занято: ${newImprints.length}/${maxSlots}.</p>`,
    speaker: ChatMessage.getSpeaker({ actor })
  });
}

/**
 * Создать актёра-компаньона из исходного актёра с бонусами класса.
 * HP = max(базовые HP, 5 × уровень). Имя = «Зверь (Персонаж)».
 */
async function _createCompanionActor(rangerActor, sourceActor) {
  const level = _rangerLevel(rangerActor);
  const pb = _pb(rangerActor);
  const baseHp = sourceActor.system?.attributes?.hp?.max ?? 10;
  const newHp = _maxHp(baseHp, level);

  const data = sourceActor.toObject();
  data.name = `${sourceActor.name} (${rangerActor.name})`;
  data._id = undefined;
  data.folder = null;
  data.ownership = { default: 0, [game.user.id]: 3 };
  data.system.attributes.hp.max = newHp;
  data.system.attributes.hp.value = newHp;

  // Store metadata for future HP updates
  foundry.utils.setProperty(data, `flags.${MODULE_ID}.isCompanion`, true);
  foundry.utils.setProperty(data, `flags.${MODULE_ID}.rangerActorId`, rangerActor.id);
  foundry.utils.setProperty(data, `flags.${MODULE_ID}.sourceActorUuid`, sourceActor.uuid);
  foundry.utils.setProperty(data, `flags.${MODULE_ID}.baseHp`, baseHp);

  return Actor.create(data);
}

/**
 * Призвать зверя из статуэтки на текущую сцену.
 * Показывает список сохранённых отпечатков.
 */
async function summonBeast(figurineItem) {
  const actor = figurineItem.actor;
  const imprints = figurineItem.getFlag(MODULE_ID, FLAG_IMPRINTS) ?? [];

  if (!imprints.length) {
    return ui.notifications.warn("В статуэтке нет сохранённых зверей. Сначала привяжите зверя.");
  }

  const chosen = await _showSummonDialog(imprints);
  if (!chosen) return;

  const sourceActor = await fromUuid(chosen.uuid).catch(() => null);
  if (!sourceActor) {
    return ui.notifications.error(`Актёр «${chosen.name}» не найден в мире. Возможно, он был удалён.`);
  }

  // Place token on active scene
  if (!canvas?.scene) return ui.notifications.error("Нет активной сцены для призыва.");

  const td = await sourceActor.getTokenDocument({
    x: canvas.stage.pivot.x,
    y: canvas.stage.pivot.y,
    hidden: false
  });
  const [token] = await canvas.scene.createEmbeddedDocuments("Token", [td.toObject()]);

  ChatMessage.create({
    content: `<p><strong>${actor?.name ?? "Следопыт"}</strong> призывает <strong>${sourceActor.name}</strong>.</p>`,
    speaker: ChatMessage.getSpeaker({ actor })
  });

  // Auto-apply beast traits from ranger's sheet
  if (token && actor) {
    await _applyTraitsToToken(token, actor);
  }
}

/**
 * Применить AE активных черт зверя к токену.
 * Находит черты с флагом beastTrait на листе Следопыта.
 */
async function _applyTraitsToToken(tokenDoc, rangerActor) {
  const traitItems = rangerActor.items.filter(i =>
    i.flags?.[MODULE_ID]?.beastTrait === true && i.effects?.size > 0
  );
  if (!traitItems.length) return;

  const effectsToCreate = [];
  for (const traitItem of traitItems) {
    for (const effect of traitItem.effects) {
      const ed = effect.toObject();
      ed._id = foundry.utils.randomID();
      ed.origin = traitItem.uuid;
      ed.disabled = false;
      ed.transfer = false;
      effectsToCreate.push(ed);
    }
  }

  if (effectsToCreate.length) {
    await tokenDoc.actor?.createEmbeddedDocuments("ActiveEffect", effectsToCreate);
    const names = [...new Set(traitItems.map(i => i.name))].join(", ");
    ChatMessage.create({
      content: `<p>Черты зверя применены к <strong>${tokenDoc.actor?.name}</strong>: ${names}.</p>
        <p><em>Эффекты можно отключить в панели эффектов токена.</em></p>`,
      speaker: ChatMessage.getSpeaker({ actor: rangerActor })
    });
  }
}

/**
 * Обновить HP всех сохранённых компаньонов при повышении уровня Следопыта.
 * Вызывается через хук dnd5e.levelUp.
 */
async function updateCompanionHp(rangerActor) {
  const figurine = _getFigurineItem(rangerActor);
  if (!figurine) return;
  const imprints = figurine.getFlag(MODULE_ID, FLAG_IMPRINTS) ?? [];
  if (!imprints.length) return;

  const level = _rangerLevel(rangerActor);
  let updated = 0;

  for (const imp of imprints) {
    const a = await fromUuid(imp.uuid).catch(() => null);
    if (!a) continue;
    const baseHp = a.getFlag(MODULE_ID, "baseHp") ?? a.system.attributes.hp.max;
    const newHp = _maxHp(baseHp, level);
    if (a.system.attributes.hp.max !== newHp) {
      await a.update({
        "system.attributes.hp.max": newHp,
        "system.attributes.hp.value": Math.min(a.system.attributes.hp.value, newHp)
      });
      updated++;
    }
  }

  if (updated > 0) {
    ChatMessage.create({
      content: `<p>Максимальные хиты ${updated} ${updated === 1 ? "зверя" : "зверей"}-спутника обновлены (уровень ${level}, формула: max(базовые HP, ${5 * level})).</p>`,
      speaker: ChatMessage.getSpeaker({ actor: rangerActor })
    });
  }
}

/**
 * Создать статуэтку в инвентаре персонажа.
 * Проверяет, что статуэтка ещё не создана (по флагу isFigurine).
 */
async function createFigurine(actor) {
  if (_getFigurineItem(actor)) {
    return ui.notifications.warn("Статуэтка уже есть в вашем инвентаре.");
  }
  const pack = game.packs.get(`${MODULE_ID}.features`);
  if (!pack) return ui.notifications.error("Пак features модуля не найден.");
  const index = await pack.getIndex();
  const entry = index.find(e => e.flags?.[MODULE_ID]?.isFigurine === true);
  if (!entry) return ui.notifications.error("Статуэтка не найдена в паке модуля.");
  const figurineDoc = await pack.getDocument(entry._id);
  if (!figurineDoc) return ui.notifications.error("Не удалось загрузить статуэтку.");
  const [created] = await actor.createEmbeddedDocuments("Item", [figurineDoc.toObject()]);
  ui.notifications.info(`Статуэтка «${created.name}» добавлена в инвентарь.`);
}

// ── Hooks ─────────────────────────────────────────────────────────────────────

Hooks.once("ready", () => {
  game[MODULE_ID] = game[MODULE_ID] ?? {};
  game[MODULE_ID].companion = {
    bindBeast,
    summonBeast,
    createFigurine,
    updateCompanionHp,
    applyTraitsToToken: _applyTraitsToToken
  };
  console.log(`[${MODULE_ID}] Beast Companion Manager ready.`);
});

// Auto-update HP on ranger level-up
Hooks.on("dnd5e.levelUp", (actor, updates) => {
  if (!actor?.classes?.sledopyt) return;
  updateCompanionHp(actor);
});

// Intercept figurine / companion-feat activity usage — run our dialogs instead of
// dnd5e's default usage flow (which would just post a plain empty chat card).
Hooks.on("dnd5e.preUseActivity", (activity, _usageConfig, _messageConfig, _dialogConfig) => {
  const item = activity.item;
  switch (activity.id ?? activity._id) {
    case "0RViZMYv0UB3gtBI": // Создать статуэтку (Спутник следопыта)
      createFigurine(item?.actor);
      return false;
    case "gxmZmRlXKNKfwLA7": // Привязать существо (Статуэтка)
      bindBeast(item);
      return false;
    case "j8GuHvtcBOjhL15E": // Призвать Зверя (Статуэтка)
      summonBeast(item);
      return false;
  }
});

// Auto-apply traits when a companion token is placed on scene by our summon
Hooks.on("createToken", async (tokenDoc) => {
  const actor = tokenDoc?.actor;
  if (!actor?.flags?.[MODULE_ID]?.isCompanion) return;
  const rangerActorId = actor.getFlag(MODULE_ID, "rangerActorId");
  if (!rangerActorId) return;
  const rangerActor = game.actors.get(rangerActorId);
  if (!rangerActor) return;
  // Small delay to ensure token is fully placed
  await new Promise(r => setTimeout(r, 300));
  await _applyTraitsToToken(tokenDoc, rangerActor);
});
