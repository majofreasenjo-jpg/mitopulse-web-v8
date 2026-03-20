import Foundation

struct Env {
    var altitudeM: Double = 0
    var tempC: Double = 22
    var humidity: Double = 50
    var pressureHpa: Double = 1013.25
}

struct Signals {
    var hr: Double? = nil
    var hrvRmssd: Double? = nil
    var spo2: Double? = nil
    var sleepScore: Double? = nil
    var accelLoad: Double? = nil
}

enum Engine {
    static func clamp(_ x: Double, _ lo: Double, _ hi: Double) -> Double { max(lo, min(hi, x)) }
    static func normalize(_ x: Double, _ lo: Double, _ hi: Double) -> Double {
        if hi <= lo { return 0.5 }
        return clamp((x - lo) / (hi - lo), 0, 1)
    }
    static func pickTier(_ s: Signals) -> String { s.hrvRmssd != nil ? "tier2" : "tier1" }

    static func cEnv(_ env: Env) -> Double {
        let alt = env.altitudeM / 1000.0
        let t = abs(env.tempC - 22.0)
        let h = abs(env.humidity - 50.0) / 50.0
        let p = abs(env.pressureHpa - 1013.25) / 100.0
        let raw = 1.0 / (1.0 + 0.012*alt + 0.008*t + 0.005*h + 0.003*p)
        return clamp(raw, 0.85, 1.15)
    }

    static func fusedIndex(_ s: Signals, _ env: Env) -> Double {
        let bHr = 1.0 - normalize(s.hr ?? 75.0, 45, 140)
        let bHrv = normalize(s.hrvRmssd ?? 25.0, 5, 120)
        let bSpo2 = normalize(s.spo2 ?? 96.0, 85, 100)
        let bSleep = normalize(s.sleepScore ?? 70.0, 0, 100)
        let bLoad = 1.0 - normalize(s.accelLoad ?? 0.3, 0, 1.5)

        let tier = pickTier(s)
        let f: Double = (tier == "tier1")
            ? (0.35*bHr + 0.25*bSpo2 + 0.20*bSleep + 0.20*bLoad)
            : (0.25*bHr + 0.30*bHrv + 0.20*bSpo2 + 0.15*bSleep + 0.10*bLoad)

        return clamp(f * cEnv(env), 0, 1)
    }

    static func risk(idx: Double, slope: Double) -> (Int, Bool) {
        var r = 0
        if idx < 0.35 { r += 35 }
        if idx < 0.20 { r += 35 }
        if slope < -0.05 { r += 20 }
        if slope < -0.10 { r += 20 }
        r = Int(clamp(Double(r), 0, 100))
        let coercion = r >= 80 || idx < 0.12
        return (r, coercion)
    }
}
