/**
 * Альтернативный Следопыт (Kasoda) — проверка зависимости Laaru.
 * При входе в мир, если модуль Laaru•Compendium•DnD14 не активен, показывает
 * ГМу предупреждение: ссылки на заклинания и боевые стили не разрешатся без него.
 */
const MODULE_ID = "sledopyt-kasoda";
const LAARU_ID = "laaru-dnd5-hw";

Hooks.once("ready", () => {
  const laaru = game.modules.get(LAARU_ID);
  if (laaru?.active) return; // всё в порядке — Laaru включён

  const msg =
    "Альтернативный Следопыт: для разрешения ссылок на заклинания и боевые стили " +
    "подклассов включите модуль «Laaru•Compendium•DnD14» (laaru-dnd5-hw). " +
    "Без него класс работает, но эти ссылки будут пустыми.";

  console.warn(`${MODULE_ID} |`, msg);

  // Баннер показываем только ГМу, чтобы не спамить игрокам.
  if (game.user?.isGM) {
    ui.notifications.warn(msg, { permanent: true });
  }
});
