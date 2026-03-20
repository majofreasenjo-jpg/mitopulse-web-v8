
package com.mitopulse

import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import java.util.Base64

object Engine {

    fun dynamicId(vector:String, secret:String):String{
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(secret.toByteArray(),"HmacSHA256"))
        return Base64.getEncoder().encodeToString(mac.doFinal(vector.toByteArray()))
    }

}
