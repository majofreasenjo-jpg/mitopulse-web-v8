import Foundation

struct VerifyResponse: Codable { let verified: Bool; let reason: String }

enum Api {
    static func postJSON(path: String, body: Data) async throws -> (Int, Data) {
        var req = URLRequest(url: Config.baseURL.appendingPathComponent(path))
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = body
        let (data, resp) = try await URLSession.shared.data(for: req)
        let code = (resp as? HTTPURLResponse)?.statusCode ?? 0
        return (code, data)
    }
}
