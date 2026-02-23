export default function PremiumPage() {
  return (
    <main className="card grid">
      <h1>Premium</h1>
      <p>Для MVP оплата заглушка, но экран готов под подключение провайдера.</p>
      <div className="card grid">
        <h3>Free</h3>
        <p>Лимит писем: 5/день</p>
        <p>Базовый поиск</p>
      </div>
      <div className="card grid">
        <h3>Premium</h3>
        <p>Безлимит лайков</p>
        <p>Больше писем в день</p>
        <p>Приоритет в выдаче</p>
      </div>
      <button className="button primary">Подключить (soon)</button>
    </main>
  );
}
