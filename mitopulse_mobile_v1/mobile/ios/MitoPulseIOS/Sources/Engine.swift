import Foundation
import CryptoKit

struct Sample {
  let ts: Int
  let hr: Double
  let hrvRmssd: Double?
  let spo2: Double?
  let sleepScore: Double?
  let accelLoad: Double?
  let altitudeM: Double?
  let tempC: Double?
  let humidity: Double?
}

struct ComputeResult {
  let indexValue: Double
  let slope: Double
  let tier: String
  let risk: Int
  let coercion: Bool
  let dynamicId: String
  let vectorJson: String
}

enum Engine {
  static func clamp(_ x: Double,_ lo: Double,_ hi: Double)->Double { max(lo, min(hi, x)) }
  static func tier(_ s: Sample)->String {
    let hasBasic = (s.spo2 != nil || s.sleepScore != nil || s.accelLoad != nil)
    return (hasBasic && s.hrvRmssd != nil) ? "tier2" : "tier1"
  }
  static func cEnv(_ s: Sample)->Double {
    if s.altitudeM==nil && s.tempC==nil && s.humidity==nil { return 1.0 }
    let alt=(s.altitudeM ?? 0.0)/1000.0
    let t=s.tempC ?? 22.0
    let h=s.humidity ?? 50.0
    let v=1.0/(1.0 + 0.012*alt + 0.008*abs(t-22.0) + 0.005*abs(h-50.0)/50.0)
    return clamp(v, 0.85, 1.15)
  }
  static func norm(_ s: Sample)->[String:Double] {
    var out:[String:Double]=[:]
    out["hr"]=clamp(1.0-(s.hr-50.0)/80.0,0.0,1.0)
    if let h=s.hrvRmssd { out["hrv"]=clamp((h-10.0)/90.0,0.0,1.0) }
    if let o=s.spo2 { out["spo2"]=clamp((o-90.0)/10.0,0.0,1.0) }
    if let sl=s.sleepScore { out["sleep"]=clamp(sl/100.0,0.0,1.0) }
    if let ld=s.accelLoad { out["load"]=clamp(1.0-ld/10.0,0.0,1.0) }
    return out
  }
  static func hmac(secret: Data, msg: Data)->String {
    let key = SymmetricKey(data: secret)
    let mac = HMAC<SHA256>.authenticationCode(for: msg, using: key)
    return Data(mac).base64EncodedString().replacingOccurrences(of: "+", with: "-").replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: "=", with: "")
  }
  static func compute(history: inout [Double], s: Sample, secret: Data)->ComputeResult {
    let t = tier(s)
    let b = norm(s)
    let w:[String:Double] = (t=="tier2") ? ["hr":0.30,"hrv":0.30,"spo2":0.20,"sleep":0.10,"load":0.10] : ["hr":0.40,"spo2":0.25,"sleep":0.20,"load":0.15]
    var acc=0.0; var tw=0.0
    for (k,wk) in w { if let v=b[k] { acc += wk*v; tw += wk } }
    let base = (tw<=0) ? 0.5 : acc/tw
    let idx = clamp(base*cEnv(s),0.0,1.0)
    history.append(idx)
    let mean = history.reduce(0,+)/Double(history.count)
    let last = history.last ?? idx
    let slope = (history.count>=2) ? (history[history.count-1]-history[history.count-2]) : 0.0
    let vec:[String:Double] = ["mean":mean,"last":last,"slope":slope]
    let vecData = try! JSONSerialization.data(withJSONObject: vec, options: [.sortedKeys])
    let dyn = hmac(secret: secret, msg: vecData)
    var risk=0
    if idx<0.25 { risk += 50 }
    if slope < -0.05 { risk += 20 }
    if let h=s.hrvRmssd, h<20 { risk += 20 }
    if s.hr>110 { risk += 20 }
    risk = Int(clamp(Double(risk),0,100))
    let coercion = risk >= 75
    let vecJson = String(data: vecData, encoding: .utf8) ?? "{}"
    return ComputeResult(indexValue: idx, slope: slope, tier: t, risk: risk, coercion: coercion, dynamicId: dyn, vectorJson: vecJson)
  }
}
