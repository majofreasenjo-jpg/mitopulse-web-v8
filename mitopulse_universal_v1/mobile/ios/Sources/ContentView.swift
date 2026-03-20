import SwiftUI

struct ContentView: View {
    @State private var userId = "manuel"
    @State private var deviceId = "iphone"
    @State private var lastDyn = ""
    @State private var log = ""

    private let secret = Data("demo_secret_change_me".utf8) // TODO: Keychain in production

    func canonicalVectorJson(windowN:Int, mean:Double, last:Double, std:Double, slope7:Double, tier:String) -> String {
        // deterministic enough for demo
        return "{\"last\":\(last),\"mean\":\(mean),\"slope7\":\(slope7),\"std\":\(std),\"tier\":\"\(tier)\",\"window_n\":\(windowN)}"
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("MitoPulse iOS Demo").font(.title2).bold()

            TextField("user_id", text: $userId).textFieldStyle(.roundedBorder)
            TextField("device_id", text: $deviceId).textFieldStyle(.roundedBorder)

            Button("Send DEMO Event") {
                Task {
                    let ts = Int(Date().timeIntervalSince1970)
                    let signals = Signals(hr: 72, hrvRmssd: 38, spo2: 97, sleepScore: 78, accelLoad: 0.35)
                    let env = Env(altitudeM: 520, tempC: 22, humidity: 50, pressureHpa: 1013)
                    let tier = Engine.pickTier(signals)
                    let idx = Engine.fusedIndex(signals, env)
                    let slope = 0.0
                    let (risk, coercion) = Engine.risk(idx: idx, slope: slope)
                    let vecJson = canonicalVectorJson(windowN: 1, mean: idx, last: idx, std: 0, slope7: slope, tier: tier)
                    let dyn = Crypto.dynamicId(secret: secret, canonicalJson: vecJson)
                    lastDyn = dyn

                    let payload: [String: Any] = [
                        "ts": ts,
                        "user_id": userId,
                        "device_id": deviceId,
                        "request_id": UUID().uuidString,
                        "tier_used": tier,
                        "index_value": idx,
                        "slope": slope,
                        "dynamic_id": dyn,
                        "risk": risk,
                        "coercion": coercion,
                        "signature": NSNull()
                    ]
                    let data = try JSONSerialization.data(withJSONObject: payload)
                    let (code, resp) = try await Api.postJSON(path: "/v1/identity-events", body: data)
                    log = "POST \(code) \(String(data: resp, encoding: .utf8) ?? "")\n" + log
                }
            }

            Button("Verify") {
                Task {
                    let payload: [String: Any] = [
                        "user_id": userId,
                        "device_id": deviceId,
                        "request_id": UUID().uuidString,
                        "dynamic_id": lastDyn
                    ]
                    let data = try JSONSerialization.data(withJSONObject: payload)
                    let (code, resp) = try await Api.postJSON(path: "/v1/verify", body: data)
                    log = "VERIFY \(code) \(String(data: resp, encoding: .utf8) ?? "")\n" + log
                }
            }.disabled(lastDyn.isEmpty)

            Text("dynamic_id: \(lastDyn.isEmpty ? "(none)" : String(lastDyn.prefix(18)) + "…")").font(.footnote)
            ScrollView { Text(log).font(.system(.footnote, design: .monospaced)) }
        }
        .padding()
    }
}
