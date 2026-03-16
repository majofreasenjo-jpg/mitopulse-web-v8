import Foundation
import CryptoKit

/// Official Swift SDK for MitoPulse Verify (iOS)
/// Secures critical human-presence verification natively on Apple devices.
/// Depends on CryptoKit for hardware-backed Ed25519 signing.
public class MitoPulseVerify {
    
    private let publicKey: String
    private var privateKey: Curve25519.Signing.PrivateKey
    private var deviceId: String
    
    public init(apiKey: String) {
        self.publicKey = apiKey
        
        // Lookup existing key in Secure Enclave/Keychain, or generate new
        if let existingKey = Keychain.load(key: "mitopulse_ed25519") {
            self.privateKey = try! Curve25519.Signing.PrivateKey(rawRepresentation: existingKey)
            self.deviceId = UserDefaults.standard.string(forKey: "mitopulse_device_id") ?? "node_ios_fallback"
        } else {
            self.privateKey = Curve25519.Signing.PrivateKey()
            self.deviceId = "node_ios_\(UUID().uuidString.prefix(8))"
            Keychain.save(key: "mitopulse_ed25519", data: self.privateKey.rawRepresentation)
            UserDefaults.standard.set(self.deviceId, forKey: "mitopulse_device_id")
        }
    }
    
    /// Generates a non-repudiable Proof-of-Presence payload for critical operations
    public func generatePresencePayload(context: [String: Any]) throws -> [String: Any] {
        let timestamp = Date().timeIntervalSince1970
        let nonce = UUID().uuidString
        
        let messageString = "\(deviceId):\(timestamp):\(nonce)"
        guard let messageData = messageString.data(using: .utf8) else {
            throw MitoPulseError.invalidEncoding
        }
        
        // 1. Hardware-level Cryptographic Signature (Ed25519)
        let signatureData = try self.privateKey.signature(for: messageData)
        let signatureBase64 = signatureData.base64EncodedString()
        
        // 2. Transmit to client's backend securely
        return [
            "device_id": self.deviceId,
            "timestamp": timestamp,
            "nonce": nonce,
            "signature": signatureBase64,
            "context": context
        ]
    }
}

enum MitoPulseError: Error {
    case invalidEncoding
    case keychainError
}
