# Powering BirdNET-Pi with Power Bank and Solar Panel

This guide explains how to power a Raspberry Pi running **BirdNET-Pi** using portable solutions like power banks and solar panels—ideal for field or off-grid deployments.

---

## 🧩 Powering Raspberry Pi with a Power Bank

**Recommended Requirements:**

- **Output:** 5V
- **Current:** Minimum 2.4A (Pi 3), 3.0A (Pi 4), 5.1V 5A (Pi 5)
- **Capacity:** 10000mAh or higher

**Steps:**

1. Power off the Raspberry Pi.
2. Connect the USB cable from the power bank to the Pi’s power port.
3. Turn on the power bank. The Pi will auto-boot.

🔗 **Suggested Products:**

- [Anker PowerCore 20000mAh](https://amzn.in/d/je3jWQD)
- [Reliance Digital Link](https://www.reliancedigital.in/product/anker-powercore-20000-mah-power-bank-a1363h11?)

---

## ☀️ Powering Raspberry Pi with a Solar Panel

Solar panels can be used via a solar-compatible power bank for regulated output.

**Recommended Setup:**

- **Panel:** 5V, 6W+ with USB output
- **Power Bank:** 5V/2.4A+ output + solar charging support

**Steps:**

1. Connect solar panel to the power bank input.
2. Expose panel to sunlight.
3. Power the Pi using the power bank as above.

🔗 [Example Solar Panel](https://amzn.in/d/5gy8jrk)

---

## ✅ Best Practices

- Use short, quality USB cables to minimize voltage drop.
- Monitor power draw using inline USB power meters.
- Do not power the Pi directly from unregulated solar panels.
- Use active/passive cooling, especially for Pi 4/5 in closed boxes.

---

## ⚡ BirdNET-Pi Power Consumption

| Pi Model      | Idle (W) | BirdNET Active (W) | Peak (USB Mic + WiFi) |
|---------------|----------|---------------------|------------------------|
| Pi Zero 2 W   | 0.6–1.0  | 1.3–1.8              | 2.0                    |
| Pi 3B+        | 1.5      | 3.0–3.5              | 4.0                    |
| Pi 4 (2GB/4GB)| 2.5–3.0  | 4.5–6.0              | 6.5                    |
| Pi 5          | 3.5–4.0  | 6.5–8.0              | 9.5–10                 |

---

## 🔋 Battery Runtime Estimates (with BirdNET active)

| Power Bank (mAh / Wh) | Raspberry Pi | Runtime (approx.) |
|------------------------|--------------|--------------------|
| 10000 mAh / 37 Wh      | Pi 3B+       | 10–11 hours        |
| 10000 mAh / 37 Wh      | Pi 4         | 6–7 hours          |
| 20000 mAh / 74 Wh      | Pi 4         | 11–12 hours        |
| 20000 mAh / 74 Wh      | Pi 5         | 8–9 hours          |

---

## 🧠 Setting Up BirdNET-Pi

Follow detailed installation instructions from the official GitHub repository:

🔗 [BirdNET-Pi GitHub Repository](https://github.com/chimarkhi/BirdNET-Pi-Edge)

---

## 📶 Updating WiFi Credentials on Raspberry Pi

Follow this step-by-step blog:

🔗 [Update WiFi on RPi](https://akashrajpurohit.com/blog/update-wifi-password-on-raspberry-pi)

---

## 🌐 Remote Access to Raspberry Pi

Use **Raspberry Pi Connect** or **Connect Lite**:

🔗 [Raspberry Pi Remote Access Guide](https://dronebotworkshop.com/pi-remote-access)

---

## 🔧 Component Reference & Links

| Component         | Link                                                                 |
|-------------------|----------------------------------------------------------------------|
| Compute Hardware  | [Raspberry Pi](https://amzn.in/d/ft53d1g)                            |
| Enclosure         | [Acrylic Case](https://amzn.in/d/3gQTtFw)                            |
| Microphone        | [USB Mic](https://amzn.in/d/c5NPG8B)                                 |
| Power Supply      | [RPI Power Supply](https://amzn.in/d/gZlT1gC)                        |
| Storage (SD Card) | [32GB SD Card](https://amzn.in/d/8gZ3upU)                            |
| UPS (optional)    | [Power Bank/UPS](https://amzn.in/d/fUTVqPE)                          |

**Other Tips:**

- Use foam windscreen for mics to reduce wind noise.
- Consider placing the Pi in a **weatherproof enclosure** with a breathable mic shield.