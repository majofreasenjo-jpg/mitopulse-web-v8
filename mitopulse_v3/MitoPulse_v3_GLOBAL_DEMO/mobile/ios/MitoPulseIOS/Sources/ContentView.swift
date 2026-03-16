import SwiftUI

struct ContentView: View {
  @State private var status: String = "idle"
  @State private var history: [Double] = []
  private let secret = KeychainSecret.getOrCreate()

  var body: some View {
    VStack(alignment: .leading, spacing: 12) {
      Text("MitoPulse iOS Prototype").font(.title2).bold()
      Text("Status: \(status)").font(.callout)

      Button("Send DEMO Event (Local-First)") { Task { await sendDemo() } }
        .buttonStyle(.borderedProminent)

      Button("Verify (on-demand)") { Task { await verify() } }
        .buttonStyle(.bordered)

      Spacer()
    }.padding()
  }

  func sendDemo() async {
    let ts = Int(Date().timeIntervalSince1970)
    let s = Sample(ts: ts, hr: 88, hrvRmssd: 42, spo2: 97, sleepScore: 80, accelLoad: 4.5, altitudeM: 520, tempC: 23, humidity: 55)
    let res = Engine.compute(history: &history, s: s, secret: secret)
    let evt = IdentityEvent(user_id: Config.userId, device_id: Config.deviceId, ts: ts, request_id: UUID().uuidString,
                            dynamic_id: res.dynamicId, index_value: res.indexValue, slope: res.slope, tier: res.tier,
                            risk: res.risk, coercion: res.coercion, meta: ["source":"ios_demo"])
    do {
      let (code, txt) = try await Api.postJSON(path: "v1/identity-events", body: evt)
      status = "POST -> \(code) \(txt) tier=\(res.tier) risk=\(res.risk)"
    } catch { status = "error: \(error)" }
  }

  func verify() async {
    let ts = Int(Date().timeIntervalSince1970)
    let mean = history.reduce(0,+) / Double(max(1, history.count))
    let last = history.last ?? 0.5
    let slope = history.count>=2 ? (history[history.count-1]-history[history.count-2]) : 0.0
    let vec:[String:Double] = ["mean":mean,"last":last,"slope":slope]
    let vecData = try! JSONSerialization.data(withJSONObject: vec, options: [.sortedKeys])
    let dyn = Engine.hmac(secret: secret, msg: vecData)
    let req = VerifyReq(user_id: Config.userId, device_id: Config.deviceId, ts: ts, request_id: UUID().uuidString, dynamic_id: dyn)
    do {
      let (code, txt) = try await Api.postJSON(path: "v1/verify", body: req)
      status = "VERIFY -> \(code) \(txt)"
    } catch { status = "error: \(error)" }
  }
}
