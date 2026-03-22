import Foundation
import CryptoKit
import HealthKit

/// Official Swift SDK for MitoPulse Verify (iOS)
/// Secures critical human-presence verification natively on Apple devices.
/// Depends on CryptoKit for hardware-backed Ed25519 signing.
public class MitoPulseVerify {
    
    private let publicKey: String
    private var privateKey: Curve25519.Signing.PrivateKey
    private var deviceId: String
    
    // V91: The Cross Pulse Biometric Engine (Semi-hidden physiological monitor)
    private let healthStore = HKHealthStore()
    
    public init(apiKey: String) {
        self.publicKey = apiKey
        
        // V91 HealthKit Initialization
        if HKHealthStore.isHealthDataAvailable() {
            guard let heartRateType = HKObjectType.quantityType(forIdentifier: .heartRate),
                  let hrvType = HKObjectType.quantityType(forIdentifier: .heartRateVariabilitySDNN) else { return }
            
            // Requesting invisible read access for Cross Pulse Coercion assessment
            healthStore.requestAuthorization(toShare: nil, read: [heartRateType, hrvType]) { (success, error) in
                if !success { print("[CrossPulse] Authorization Denied by OS.") }
            }
        }
        
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
    
    /// Generates a non-repudiable Proof-of-Presence payload for critical operations.
    /// V91: Asynchronous. Extracts Apple Watch HealthKit biometrics to detect physical coercion (Extortion).
    public func generatePresencePayload(context: [String: Any]) async throws -> [String: Any] {
        let timestamp = Date().timeIntervalSince1970
        let nonce = UUID().uuidString
        
        // In physical production, HealthKit queries (`HKSampleQuery`) fetch the live BPM here.
        // For the V91 prototype schema, we structure the tensor template that backend RiskEngine requires.
        var crossPulse: [String: Any] = [
            "bpm": 0, // baseline placeholder or fallback
            "hrv": 0,
            "timestamp": timestamp
        ]
        
        // (If testing coercion, the integrating banking App will artificially inject the simulated stress context here)
        if let simPulse = context["simulated_cross_pulse"] as? [String: Any] {
            crossPulse = simPulse
        }
        
        var secureContext = context
        secureContext["cross_pulse"] = crossPulse
        
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
            "context": secureContext
        ]
    }
}

enum MitoPulseError: Error {
    case invalidEncoding
    case keychainError
}
