# Android Architecture

## Stack
- Kotlin + Jetpack Compose
- MVVM / Clean Architecture
- Retrofit/Ktor client
- Coroutines + Flow
- Firebase Crashlytics / alternative

## Modules
- app: UI, navigation, Compose screens
- data: API clients, repositories, local storage
- domain: use cases, models
- common: ui-kit, utils, extensions

## Key Screens
- Splash / Welcome
- Auth (Google, VK, Yandex, Phone)
- Home / Today Pack
- People / Recipients
- Create Greeting flow
- Recommendations
- Template details
- Generation progress
- Preview / Result
- Payment
- Profile / Wallet
- Calendar

## State
- Remote: FastAPI backend
- Local: Room / DataStore for offline cache

## Project Structure
```
android/
├── app/
│   ├── src/main/java/com/daragent/
│   │   ├── data/
│   │   │   ├── network/
│   │   │   │   ├── api/
│   │   │   │   │   ├── ApiModule.kt
│   │   │   │   │   ├── AuthApi.kt
│   │   │   │   │   ├── PeopleApi.kt
│   │   │   │   │   ├── TemplatesApi.kt
│   │   │   │   │   ├── GenerationsApi.kt
│   │   │   │   │   └── PaymentsApi.kt
│   │   │   │   └── NetworkModule.kt
│   │   │   └── repository/
│   │   │       └── RepositoryImpl.kt
│   │   ├── domain/
│   │   │   ├── model/
│   │   │   │   └── Models.kt
│   │   │   └── repository/
│   │   │       └── Repositories.kt
│   │   ├── presentation/
│   │   │   └── home/
│   │   │       ├── HomeScreen.kt
│   │   │       └── HomeViewModel.kt
│   │   ├── navigation/
│   │   │   └── DarAgentNavGraph.kt
│   │   ├── di/
│   │   │   └── ServiceLocator.kt
│   │   ├── MainActivity.kt
│   │   └── DarAgentApp.kt
│   └── build.gradle
├── build.gradle
├── settings.gradle
└── gradle.properties
```

## Next Steps
- Add Room entities for offline cache
- Add more screens (CreateGreeting, TemplateDetails, Generation, Payment)
- Integrate camera/gallery for photo upload
- Add push notifications
- Add share sheet integration
