# iOS Setup (Xcode)

Este paquete incluye código SwiftUI en `Sources/`.

1) Xcode → New Project → iOS → App (SwiftUI)
2) Nombre: MitoPulseIOS
3) Copia todos los archivos de `Sources/` dentro del proyecto
4) Copia `Config.swift` dentro del proyecto
5) Cambia `backendBaseURL` a tu IP local.

Por defecto es modo DEMO (sin HealthKit).
Si quieres HealthKit real:
- Signing & Capabilities → + HealthKit
- Agrega permisos y queries (queda como siguiente paso).
