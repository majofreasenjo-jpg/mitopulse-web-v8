
class MitoPulseClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async evaluate(entity, signal) {
        const res = await fetch(this.baseUrl + "/evaluate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({entity, signal})
        });
        return res.json();
    }
}

export default MitoPulseClient;
