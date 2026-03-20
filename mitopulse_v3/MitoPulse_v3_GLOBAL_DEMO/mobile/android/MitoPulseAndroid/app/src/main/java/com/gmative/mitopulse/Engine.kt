package com.gmative.mitopulse
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

data class Sample(
  val ts: Long,
  val hr: Double,
  val hrvRmssd: Double?=null,
  val spo2: Double?=null,
  val sleepScore: Double?=null,
  val accelLoad: Double?=null,
  val altitudeM: Double?=null,
  val tempC: Double?=null,
  val humidity: Double?=null,
)

data class ComputeResult(
  val indexValue: Double,
  val slope: Double,
  val tier: String,
  val risk: Int,
  val coercion: Boolean,
  val dynamicId: String,
  val vectorJson: String
)

object Engine {
  private fun clamp(x: Double, lo: Double, hi: Double)=max(lo, min(hi, x))
  private fun tier(s: Sample): String {
    val hasBasic = (s.spo2!=null || s.sleepScore!=null || s.accelLoad!=null)
    return if (hasBasic && s.hrvRmssd!=null) "tier2" else "tier1"
  }
  private fun cEnv(s: Sample): Double {
    if (s.altitudeM==null && s.tempC==null && s.humidity==null) return 1.0
    val alt=(s.altitudeM?:0.0)/1000.0
    val t=s.tempC?:22.0
    val h=s.humidity?:50.0
    val v=1.0/(1.0 + 0.012*alt + 0.008*abs(t-22.0) + 0.005*abs(h-50.0)/50.0)
    return clamp(v, 0.85, 1.15)
  }
  private fun norm(s: Sample): Map<String, Double> {
    val out=mutableMapOf<String,Double>()
    out["hr"]=clamp(1.0-(s.hr-50.0)/80.0,0.0,1.0)
    s.hrvRmssd?.let { out["hrv"]=clamp((it-10.0)/90.0,0.0,1.0) }
    s.spo2?.let { out["spo2"]=clamp((it-90.0)/10.0,0.0,1.0) }
    s.sleepScore?.let { out["sleep"]=clamp(it/100.0,0.0,1.0) }
    s.accelLoad?.let { out["load"]=clamp(1.0-it/10.0,0.0,1.0) }
    return out
  }
  fun compute(history: MutableList<Double>, s: Sample, secret: ByteArray): ComputeResult {
    val tierUsed=tier(s)
    val b=norm(s)
    val w = if (tierUsed=="tier2") mapOf("hr" to 0.30,"hrv" to 0.30,"spo2" to 0.20,"sleep" to 0.10,"load" to 0.10)
            else mapOf("hr" to 0.40,"spo2" to 0.25,"sleep" to 0.20,"load" to 0.15)
    var acc=0.0; var tw=0.0
    for ((k,wk) in w) {
      val v=b[k] ?: continue
      acc += wk*v; tw += wk
    }
    val base = if (tw<=0.0) 0.5 else acc/tw
    val idx = clamp(base*cEnv(s), 0.0, 1.0)
    history.add(idx)
    val mean=history.sum()/history.size
    val last=history.last()
    val slope= if (history.size>=2) history[history.size-1]-history[history.size-2] else 0.0
    val vecJson = "{"mean":$mean,"last":$last,"slope":$slope}"
    val dyn = Crypto.hmacSha256(secret, vecJson.toByteArray(Charsets.UTF_8))
    var risk=0
    if (idx<0.25) risk+=50
    if (slope<-0.05) risk+=20
    if (s.hrvRmssd!=null && s.hrvRmssd<20) risk+=20
    if (s.hr>110) risk+=20
    risk=clamp(risk.toDouble(),0.0,100.0).toInt()
    val coercion=risk>=75
    return ComputeResult(idx,slope,tierUsed,risk,coercion,dyn,vecJson)
  }
}
