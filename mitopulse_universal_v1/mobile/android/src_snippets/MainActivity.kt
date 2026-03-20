package com.mitopulse.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.mitopulse.core.*

import java.util.UUID
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class MainActivity: ComponentActivity() {

    // Demo secret in-memory (en producción: Keystore/EncryptedSharedPreferences)
    private val secret: ByteArray = Crypto.randomSecret()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { AppUI() }
    }

    @Composable
    fun AppUI() {
        var userId by remember { mutableStateOf("manuel") }
        var deviceId by remember { mutableStateOf("note9") }
        var log by remember { mutableStateOf("") }
        var lastDyn by remember { mutableStateOf("") }

        val scope = rememberCoroutineScope()

        fun canonicalVectorJson(windowN:Int, mean:Double, last:Double, std:Double, slope7:Double, tier:String): String {
            val o = JSONObject()
            o.put("last", last)
            o.put("mean", mean)
            o.put("slope7", slope7)
            o.put("std", std)
            o.put("tier", tier)
            o.put("window_n", windowN)
            // canonical-ish: stable keys order not guaranteed in JSONObject,
            // pero para demo funciona. Para producción usa serializer determinista.
            return o.toString()
        }

        suspend fun httpPost(path:String, body:String): Pair<Int,String> {
            val url = URL("${Config.BASE_URL}${path}")
            val conn = (url.openConnection() as HttpURLConnection)
            conn.requestMethod = "POST"
            conn.setRequestProperty("Content-Type","application/json")
            conn.doOutput = true
            conn.outputStream.use { it.write(body.toByteArray()) }
            val code = conn.responseCode
            val text = try {
                conn.inputStream.bufferedReader().readText()
            } catch(e: Exception) {
                conn.errorStream?.bufferedReader()?.readText() ?: ""
            }
            conn.disconnect()
            return Pair(code,text)
        }

        Column(Modifier.padding(16.dp)) {
            Text("MitoPulse Android Demo", style = MaterialTheme.typography.titleLarge)
            Spacer(Modifier.height(10.dp))

            OutlinedTextField(value=userId, onValueChange={userId=it}, label={Text("user_id")})
            OutlinedTextField(value=deviceId, onValueChange={deviceId=it}, label={Text("device_id")})
            Spacer(Modifier.height(10.dp))

            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Button(onClick={
                    scope.launch(Dispatchers.IO){
                        val ts = (System.currentTimeMillis()/1000).toInt()
                        val signals = Signals(hr=72.0, hrvRmssd=38.0, spo2=97.0, sleepScore=78.0, accelLoad=0.35)
                        val env = Env(altitudeM=520.0, tempC=22.0, humidity=50.0, pressureHpa=1013.0)
                        val tier = Engine.pickTier(signals)
                        val idx = Engine.fusedIndex(signals, env)
                        val s = 0.0
                        val (risk, coercion) = Engine.risk(idx, s)
                        val vecJson = canonicalVectorJson(1, idx, idx, 0.0, s, tier)
                        val dyn = Crypto.dynamicId(secret, vecJson)
                        val requestId = UUID.randomUUID().toString()

                        val payload = JSONObject()
                        payload.put("ts", ts)
                        payload.put("user_id", userId)
                        payload.put("device_id", deviceId)
                        payload.put("request_id", requestId)
                        payload.put("tier_used", tier)
                        payload.put("index_value", idx)
                        payload.put("slope", s)
                        payload.put("dynamic_id", dyn)
                        payload.put("risk", risk)
                        payload.put("coercion", coercion)
                        payload.put("signature", JSONObject.NULL)

                        val (code, text) = httpPost("/v1/identity-events", payload.toString())
                        lastDyn = dyn
                        log = "POST $code $text\n$log"
                    }
                }){ Text("Send DEMO Event") }

                Button(enabled = lastDyn.isNotBlank(), onClick={
                    scope.launch(Dispatchers.IO){
                        val requestId = UUID.randomUUID().toString()
                        val payload = JSONObject()
                        payload.put("user_id", userId)
                        payload.put("device_id", deviceId)
                        payload.put("request_id", requestId)
                        payload.put("dynamic_id", lastDyn)
                        val (code,text) = httpPost("/v1/verify", payload.toString())
                        log = "VERIFY $code $text\n$log"
                    }
                }){ Text("Verify") }
            }

            Spacer(Modifier.height(10.dp))
            Text("Último dynamic_id: ${if(lastDyn.isBlank()) "(none)" else lastDyn.take(18)+"…"}")
            Spacer(Modifier.height(10.dp))
            Text("Log:", style = MaterialTheme.typography.titleMedium)
            Text(log)
        }
    }
}
