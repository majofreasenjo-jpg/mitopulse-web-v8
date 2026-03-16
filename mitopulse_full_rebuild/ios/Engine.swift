
import Foundation
import CryptoKit

func dynamicId(vector:String, secret:String)->String{
    let key = SymmetricKey(data: secret.data(using:.utf8)!)
    let sig = HMAC<SHA256>.authenticationCode(for: vector.data(using:.utf8)!, using:key)
    return Data(sig).base64EncodedString()
}
