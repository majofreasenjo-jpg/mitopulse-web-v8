class DeviceTelemetry:
    """
    V92 Physical Device Connector
    Analyzes Gyroscope/Accelerometer and Battery state to detect Emulators and Bots.
    """
    def evaluate(self, telemetry: dict) -> dict:
        risk = 0.0
        flags = []
        
        # Emulators typically have 0 movement (perfectly still gyroscope)
        # and battery strictly locked at 100%.
        gyro_x = telemetry.get("gyro_x", 0.0)
        gyro_y = telemetry.get("gyro_y", 0.0)
        battery = telemetry.get("battery", 100.0)
        
        # Dead silence on sensors indicates a Bot Farm Emulator
        if abs(gyro_x) < 0.0001 and abs(gyro_y) < 0.0001 and battery == 100.0:
            risk += 85.0
            flags.append("synthetic_emulator_bot")
        
        return {"device_risk": min(risk, 100.0), "flags": flags}
