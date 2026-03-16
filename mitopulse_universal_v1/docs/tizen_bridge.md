# Samsung Galaxy Watch SM-R800 (Tizen) — Bridge realista

SM-R800 usa **Tizen**, no Wear OS.

Ruta universal recomendada para demo:
1) El reloj sincroniza HR/steps/sleep con **Samsung Health** en el teléfono Android.
2) La app Android de MitoPulse ingesta esos datos desde:
   - Health Connect (si Samsung Health exporta), o
   - exportación de Samsung Health (CSV/JSON), o
   - Samsung Health SDK (si habilitado y aprobado).

Para una demo rápida:
- usa exportación y/o Health Connect si lo tienes disponible.
- el core engine no cambia: solo cambian los adaptadores de ingesta.

Esto te permite “mostrar MitoPulse corriendo con reloj” sin desarrollar un binario Tizen.
