package com.mitopulse.core

import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sqrt

data class Env(
    val altitudeM: Double = 0.0,
    val tempC: Double = 22.0,
    val humidity: Double = 50.0,
    val pressureHpa: Double = 1013.25
)

data class Signals(
    val hr: Double? = null,
    val hrvRmssd: Double? = null,
    val spo2: Double? = null,
    val sleepScore: Double? = null,
    val accelLoad: Double? = null
)

object Engine {
    private fun clamp(x: Double, lo: Double, hi: Double) = max(lo, min(hi, x))
    private fun normalize(x: Double, lo: Double, hi: Double): Double {
        if (hi <= lo) return 0.5
        return clamp((x - lo) / (hi - lo), 0.0, 1.0)
    }

    fun pickTier(s: Signals): String = if (s.hrvRmssd != null) "tier2" else "tier1"

    fun cEnv(env: Env): Double {
        val alt = env.altitudeM / 1000.0
        val t = abs(env.tempC - 22.0)
        val h = abs(env.humidity - 50.0) / 50.0
        val p = abs(env.pressureHpa - 1013.25) / 100.0
        val raw = 1.0 / (1.0 + 0.012 * alt + 0.008 * t + 0.005 * h + 0.003 * p)
        return clamp(raw, 0.85, 1.15)
    }

    fun fusedIndex(s: Signals, env: Env): Double {
        val bHr = 1.0 - normalize(s.hr ?: 75.0, 45.0, 140.0)
        val bHrv = normalize(s.hrvRmssd ?: 25.0, 5.0, 120.0)
        val bSpo2 = normalize(s.spo2 ?: 96.0, 85.0, 100.0)
        val bSleep = normalize(s.sleepScore ?: 70.0, 0.0, 100.0)
        val bLoad = 1.0 - normalize(s.accelLoad ?: 0.3, 0.0, 1.5)

        val tier = pickTier(s)
        val f = if (tier == "tier1") {
            0.35 * bHr + 0.25 * bSpo2 + 0.20 * bSleep + 0.20 * bLoad
        } else {
            0.25 * bHr + 0.30 * bHrv + 0.20 * bSpo2 + 0.15 * bSleep + 0.10 * bLoad
        }
        return clamp(f * cEnv(env), 0.0, 1.0)
    }

    fun slope(values: List<Double>): Double {
        val n = values.size
        if (n < 2) return 0.0
        val xs = (0 until n).map { it.toDouble() }
        val xbar = xs.sum() / n
        val ybar = values.sum() / n
        val num = (0 until n).sumOf { (xs[it] - xbar) * (values[it] - ybar) }
        val den = (0 until n).sumOf { (xs[it] - xbar) * (xs[it] - xbar) }.takeIf { it != 0.0 } ?: 1.0
        return num / den
    }

    fun risk(idx: Double, slope: Double): Pair<Int, Boolean> {
        var r = 0
        if (idx < 0.35) r += 35
        if (idx < 0.20) r += 35
        if (slope < -0.05) r += 20
        if (slope < -0.10) r += 20
        r = clamp(r.toDouble(), 0.0, 100.0).toInt()
        val coercion = r >= 80 || idx < 0.12
        return Pair(r, coercion)
    }
}
