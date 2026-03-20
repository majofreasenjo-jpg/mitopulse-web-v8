import Foundation

struct IdentityEvent: Codable {
  let user_id: String
  let device_id: String
  let ts: Int
  let request_id: String
  let dynamic_id: String
  let index_value: Double
  let slope: Double
  let tier: String
  let risk: Int
  let coercion: Bool
  let meta: [String:String]
}
struct VerifyReq: Codable {
  let user_id: String
  let device_id: String
  let ts: Int
  let request_id: String
  let dynamic_id: String
}
enum Api {
  static func postJSON<T: Encodable>(path: String, body: T) async throws -> (Int,String) {
    var req = URLRequest(url: Config.backendBaseURL.appendingPathComponent(path))
    req.httpMethod="POST"
    req.addValue("application/json", forHTTPHeaderField: "Content-Type")
    req.httpBody = try JSONEncoder().encode(body)
    let (data, resp) = try await URLSession.shared.data(for: req)
    let code = (resp as? HTTPURLResponse)?.statusCode ?? -1
    return (code, String(data: data, encoding: .utf8) ?? "")
  }
}
