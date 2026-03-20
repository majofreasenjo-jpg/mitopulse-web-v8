package com.mitopulse.core

import android.util.Base64
import java.security.SecureRandom
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

object Crypto {
    fun hmacSha256(secret: ByteArray, msg: ByteArray): ByteArray {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(secret, "HmacSHA256"))
        return mac.doFinal(msg)
    }

    fun b64url(bytes: ByteArray): String =
        Base64.encodeToString(bytes, Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING)

    fun dynamicId(secret: ByteArray, canonicalJson: String): String =
        b64url(hmacSha256(secret, canonicalJson.toByteArray(Charsets.UTF_8)))

    fun randomSecret(n: Int = 32): ByteArray {
        val b = ByteArray(n)
        SecureRandom().nextBytes(b)
        return b
    }
}
