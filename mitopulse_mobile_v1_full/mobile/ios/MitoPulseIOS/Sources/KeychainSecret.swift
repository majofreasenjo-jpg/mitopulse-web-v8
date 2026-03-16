import Foundation
import Security

enum KeychainSecret {
  static let service="com.gmative.mitopulse"
  static let account="hmac_secret"
  static func getOrCreate()->Data {
    if let d=read() { return d }
    var buf=Data(count:32)
    _=buf.withUnsafeMutableBytes{ SecRandomCopyBytes(kSecRandomDefault, 32, $0.baseAddress!) }
    save(buf); return buf
  }
  private static func read()->Data? {
    let q:[String:Any]=[
      kSecClass as String:kSecClassGenericPassword,
      kSecAttrService as String:service,
      kSecAttrAccount as String:account,
      kSecReturnData as String:true,
      kSecMatchLimit as String:kSecMatchLimitOne
    ]
    var item:CFTypeRef?
    let st=SecItemCopyMatching(q as CFDictionary, &item)
    guard st==errSecSuccess else { return nil }
    return item as? Data
  }
  private static func save(_ data:Data) {
    let q:[String:Any]=[
      kSecClass as String:kSecClassGenericPassword,
      kSecAttrService as String:service,
      kSecAttrAccount as String:account,
      kSecValueData as String:data
    ]
    SecItemDelete(q as CFDictionary)
    SecItemAdd(q as CFDictionary, nil)
  }
}
