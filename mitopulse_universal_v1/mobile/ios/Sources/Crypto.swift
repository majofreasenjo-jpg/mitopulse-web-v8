import Foundation
import CryptoKit

enum Crypto {
    static func b64url(_ data: Data) -> String {
        let s = data.base64EncodedString()
        return s.replacingOccurrences(of: "+", with: "-")
            .replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: "=", with: "")
    }

    static func hmacSHA256(secret: Data, msg: Data) -> Data {
        let key = SymmetricKey(data: secret)
        let mac = HMAC<SHA256>.authenticationCode(for: msg, using: key)
        return Data(mac)
    }

    static func dynamicId(secret: Data, canonicalJson: String) -> String {
        let mac = hmacSHA256(secret: secret, msg: Data(canonicalJson.utf8))
        return b64url(mac)
    }
}
