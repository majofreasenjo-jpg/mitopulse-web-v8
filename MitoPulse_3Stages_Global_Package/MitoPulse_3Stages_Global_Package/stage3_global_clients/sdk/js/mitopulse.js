export class MitoPulseClient {
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.apiKey = apiKey;
  }
  async verifyPresence(payload) {
    const r = await fetch(`${this.baseUrl}/v1/verify/presence`, {
      method:"POST",
      headers:{"Content-Type":"application/json","X-API-Key":this.apiKey},
      body:JSON.stringify(payload)
    });
    return await r.json();
  }
}
