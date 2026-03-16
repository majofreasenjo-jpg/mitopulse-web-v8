package com.gmative.mitopulse
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.UUID

class MainActivity : AppCompatActivity() {
  private val history: MutableList<Double> = mutableListOf()
  private val client = OkHttpClient()
  private val JSON = "application/json".toMediaType()

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)
    val status=findViewById<TextView>(R.id.status)
    val btnSend=findViewById<Button>(R.id.btnSendDemo)
    val btnVerify=findViewById<Button>(R.id.btnVerify)
    val secret=Secrets.getOrCreateSecret(this)

    btnSend.setOnClickListener {
      val s=Sample(
        ts=System.currentTimeMillis()/1000,
        hr=92.0, hrvRmssd=38.0, spo2=96.0, sleepScore=74.0, accelLoad=5.5,
        altitudeM=520.0, tempC=23.0, humidity=55.0
      )
      val res=Engine.compute(history, s, secret)
      val body = """{
        "user_id":"${Config.USER_ID}",
        "device_id":"${Config.DEVICE_ID}",
        "ts":${s.ts},
        "request_id":"${UUID.randomUUID()}",
        "dynamic_id":"${res.dynamicId}",
        "index_value":${res.indexValue},
        "slope":${res.slope},
        "tier":"${res.tier}",
        "risk":${res.risk},
        "coercion":${res.coercion},
        "meta":{"source":"android_demo"}
      }""".trimIndent()
      Thread {
        val req = Request.Builder()
          .url(Config.BACKEND_BASE_URL + "/v1/identity-events")
          .post(body.toRequestBody(JSON))
          .build()
        client.newCall(req).execute().use { resp ->
          val txt = resp.body?.string() ?: ""
          runOnUiThread { status.text = "POST -> ${resp.code} $txt (tier=${res.tier}, risk=${res.risk})" }
        }
      }.start()
    }

    btnVerify.setOnClickListener {
      val dyn = if (history.isNotEmpty()) {
        val mean=history.sum()/history.size
        val last=history.last()
        val slope= if (history.size>=2) history[history.size-1]-history[history.size-2] else 0.0
        val vecJson = "{\"mean\":$mean,\"last\":$last,\"slope\":$slope}"
        Crypto.hmacSha256(secret, vecJson.toByteArray(Charsets.UTF_8))
      } else "none"
      val body = """{
        "user_id":"${Config.USER_ID}",
        "device_id":"${Config.DEVICE_ID}",
        "ts":${System.currentTimeMillis()/1000},
        "request_id":"${UUID.randomUUID()}",
        "dynamic_id":"$dyn"
      }""".trimIndent()
      Thread {
        val req = Request.Builder()
          .url(Config.BACKEND_BASE_URL + "/v1/verify")
          .post(body.toRequestBody(JSON))
          .build()
        client.newCall(req).execute().use { resp ->
          val txt = resp.body?.string() ?: ""
          runOnUiThread { status.text = "VERIFY -> ${resp.code} $txt" }
        }
      }.start()
    }
  }
}
