package com.gmative.mitopulse
import java.util.Base64
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
object Crypto {
  fun hmacSha256(secret: ByteArray, msg: ByteArray): String {
    val mac = Mac.getInstance("HmacSHA256")
    mac.init(SecretKeySpec(secret, "HmacSHA256"))
    val raw = mac.doFinal(msg)
    return Base64.getUrlEncoder().withoutPadding().encodeToString(raw)
  }
}
