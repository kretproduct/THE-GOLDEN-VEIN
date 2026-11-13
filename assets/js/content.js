/*
  THE GOLDEN VEIN — контент сайта.
  Пруфы и кейсы добавляются здесь, верстку трогать не нужно.
  Картинки кладутся в assets/img/proofs/ и assets/img/cases/.
*/
window.TGV = {
  // Куда ведут кнопки «Связаться» (Telegram, WhatsApp, почта и т.д.)
  contact: { label: "Связаться", url: "#" },

  // Пруфы. Пример: { src: "assets/img/proofs/1.jpg", title: "Заголовок", note: "Короткая подпись" }
  // Пока src пустой — на сайте показывается аккуратная заглушка.
  proofs: [
    { src: "", title: "", note: "" },
    { src: "", title: "", note: "" },
    { src: "", title: "", note: "" },
    { src: "", title: "", note: "" },
    { src: "", title: "", note: "" },
    { src: "", title: "", note: "" }
  ],

  // Кейсы учеников.
  // name — имя, role — кто это, before/after — точка А и точка Б, period — срок,
  // quote — короткая цитата, story — полный текст кейса (можно с переносами строк),
  // photo — аватар (необязательно), shots — скриншоты к кейсу (необязательно).
  cases: [
    { name: "", role: "", before: "", after: "", period: "", quote: "", story: "", photo: "", shots: [] },
    { name: "", role: "", before: "", after: "", period: "", quote: "", story: "", photo: "", shots: [] },
    { name: "", role: "", before: "", after: "", period: "", quote: "", story: "", photo: "", shots: [] }
  ]
};
