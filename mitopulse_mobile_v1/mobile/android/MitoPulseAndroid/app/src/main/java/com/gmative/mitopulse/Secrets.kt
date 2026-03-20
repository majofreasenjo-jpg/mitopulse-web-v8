package com.gmative.mitopulse
import android.content.Context
import java.security.SecureRandom
object Secrets {
  private const val PREF="mitopulse_secret"
  private const val KEY="hmac_secret_b64"
  fun getOrCreateSecret(ctx: Context): ByteArray {
    val sp=ctx.getSharedPreferences(PREF, Context.MODE_PRIVATE)
    val ex=sp.getString(KEY, null)
    if (ex!=null) return android.util.Base64.decode(ex, android.util.Base64.NO_WRAP)
    val buf=ByteArray(32); SecureRandom().nextBytes(buf)
    sp.edit().putString(KEY, android.util.Base64.encodeToString(buf, android.util.Base64.NO_WRAP)).apply()
    return buf
  }
}
