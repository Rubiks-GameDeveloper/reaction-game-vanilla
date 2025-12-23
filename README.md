# Игра на реакцию (Vue.js)

Игра на реакцию, переписанная на Vue.js 3 с использованием Vite.

## Установка

1. Установите зависимости:
```bash
npm install
```

2. Скопируйте звуковые файлы в `public/sounds/`:
```powershell
# Windows PowerShell
.\copy-sounds.ps1

# Или вручную скопируйте файлы из папки sounds/ в public/sounds/
```

## Запуск в режиме разработки

```bash
npm run dev
```

Откройте браузер по адресу, который покажет Vite (обычно http://localhost:5173)

## Сборка для продакшена

```bash
npm run build
```

Собранные файлы будут в папке `dist/`

## Предпросмотр продакшен сборки

```bash
npm run preview
```

## Структура проекта

```
├── public/
│   └── sounds/          # Звуковые файлы (скопируйте из sounds/)
├── src/
│   ├── components/      # Vue компоненты
│   │   ├── GameHeader.vue
│   │   ├── DifficultySelection.vue
│   │   ├── GameArea.vue
│   │   ├── GameInfo.vue
│   │   ├── HighScores.vue
│   │   ├── KeyboardControls.vue
│   │   └── Settings.vue
│   ├── composables/    # Композиционные функции
│   │   ├── useGame.js
│   │   └── useSoundManager.js
│   ├── App.vue         # Главный компонент
│   ├── main.js         # Точка входа
│   └── styles.css       # Стили
├── index.html
├── package.json
├── vite.config.js
└── copy-sounds.ps1      # Скрипт для копирования звуков
```

## Исправленные баги

1. ✅ Исправлен баг с музыкой при переключении звука - теперь музыка корректно возобновляется
2. ✅ Исправлено позиционирование частиц при скролле - частицы используют fixed позиционирование
3. ✅ Исправлено форматирование - добавлена адаптивная верстка для всех размеров экранов

## Технологии

- Vue.js 3 (Composition API)
- Vite
- GSAP (для анимаций)
- LocalStorage (для сохранения рекордов и настроек)

