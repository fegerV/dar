import i18n from "i18next"
import { initReactI18next } from "react-i18next"
import LanguageDetector from "i18next-browser-languagedetector"

const resources = {
  ru: {
    translation: {
      home: "Главная",
      profile: "Профиль",
      onboarding: {
        title: "Создавайте поздравления с AI",
        subtitle: "Выберите получателя, сценарий и модель — мы сделаем всё остальное.",
        get_started: "Начать",
        skip: "Пропустить",
        step1: "Загрузите фото",
        step2: "Выберите сценарий",
        step3: "Получите видео",
      },
      dashboard: {
        title: "Мои проекты",
        active: "Активные",
        completed: "Завершённые",
        archived: "Архив",
        purchases: "Покупки",
        favorites: "Избранные получатели",
        quick_actions: "Быстрые действия",
        new_greeting: "Создать поздравление",
      },
      editor: {
        title: "Редактор сценария",
        prompt: "Описание сцены",
        negative: "Negative prompt",
        model: "Модель",
        save: "Сохранить",
        regenerate: "Перегенерировать",
        history: "История версий",
        version: "Версия",
      },
      notification: {
        title: "Уведомление",
        message: "Ваше видео готово!",
      },
    },
  },
  en: {
    translation: {
      home: "Home",
      profile: "Profile",
      onboarding: {
        title: "Create AI greetings",
        subtitle: "Choose recipient, scenario and model — we will do the rest.",
        get_started: "Get Started",
        skip: "Skip",
        step1: "Upload photo",
        step2: "Choose scenario",
        step3: "Get video",
      },
      dashboard: {
        title: "My Projects",
        active: "Active",
        completed: "Completed",
        archived: "Archived",
        purchases: "Purchases",
        favorites: "Favorite Recipients",
        quick_actions: "Quick Actions",
        new_greeting: "Create Greeting",
      },
      editor: {
        title: "Scenario Editor",
        prompt: "Scene description",
        negative: "Negative prompt",
        model: "Model",
        save: "Save",
        regenerate: "Regenerate",
        history: "Version history",
        version: "Version",
      },
      notification: {
        title: "Notification",
        message: "Your video is ready!",
      },
    },
  },
}

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "ru",
    interpolation: { escapeValue: false },
    detection: { order: ["querystring", "cookie", "localStorage", "navigator"] },
  })

export default i18n
