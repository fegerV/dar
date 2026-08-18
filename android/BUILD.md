# Android Build Setup

## GitHub Actions

The Android build runs automatically on:
- Every push to `main`
- Every pull request to `main`

### Artifacts

- **Debug APK** — uploaded on every build, retained for 14 days
- **Release AAB** — uploaded only on push to `main`, retained for 30 days
- **Test results** — uploaded if tests fail, retained for 7 days

### Signing (optional)

To enable signed release builds, add these secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

| Secret | Description |
|--------|-------------|
| `DARAGENT_SIGNING_KEY` | Base64-encoded keystore file (`.jks`) |
| `DARAGENT_SIGNING_STORE_PASSWORD` | Keystore password |
| `DARAGENT_SIGNING_KEY_ALIAS` | Key alias |
| `DARAGENT_SIGNING_KEY_PASSWORD` | Key password |

#### Generate base64 keystore

```bash
base64 -i daragent-release.jks | tr -d '\n'
```

Copy the output and paste it as `DARAGENT_SIGNING_KEY`.

## Local Build

```bash
cd android
./gradlew assembleDebug
```

Output: `android/app/build/outputs/apk/debug/app-debug.apk`

```bash
cd android
./gradlew bundleRelease
```

Output: `android/app/build/outputs/bundle/release/app-release.aab`
