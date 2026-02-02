/**
 * Terra Scout API Server
 * HTTP and WebSocket API for Python agent communication
 */

const express = require("express");
const { WebSocketServer } = require("ws");
const http = require("http");
const logger = require("./utils/logger");
const config = require("./utils/config");
const TerraScoutBot = require("./bot");

class TerraScoutServer {
  constructor() {
    this.bot = new TerraScoutBot();
    this.app = express();
    this.app.use(express.json());
    this.server = http.createServer(this.app);
    this.wss = new WebSocketServer({ server: this.server });
    this.clients = new Set();

    this.setupRoutes();
    this.setupWebSocket();
  }

  setupRoutes() {
    // Health check
    this.app.get("/health", (req, res) => {
      res.json({ status: "ok", connected: this.bot.isConnected });
    });

    // Get current observation
    this.app.get("/observation", (req, res) => {
      const obs = this.bot.getObservation();
      if (obs) {
        res.json(obs);
      } else {
        res.status(503).json({ error: "Bot not connected" });
      }
    });

    // Execute action
    this.app.post("/action", async (req, res) => {
      try {
        const result = await this.bot.step(req.body);
        res.json(result);
        this.broadcast("step", result);
      } catch (err) {
        res.status(500).json({ error: err.message });
      }
    });

    // Reset episode
    this.app.post("/reset", async (req, res) => {
      try {
        const obs = await this.bot.reset();
        res.json({ observation: obs });
        this.broadcast("reset", { observation: obs });
      } catch (err) {
        res.status(500).json({ error: err.message });
      }
    });

    // Get bot status
    this.app.get("/status", (req, res) => {
      res.json({
        connected: this.bot.isConnected,
        episodeRunning: this.bot.episodeRunning,
        stepCount: this.bot.stepCount,
        totalReward: this.bot.totalReward,
        visitedBlocks: this.bot.visitedBlocks.size,
      });
    });

    // Connect to Minecraft server
    this.app.post("/connect", async (req, res) => {
      try {
        await this.bot.connect();
        res.json({ success: true, message: "Connected to Minecraft" });
      } catch (err) {
        res.status(500).json({ success: false, error: err.message });
      }
    });

    // Disconnect
    this.app.post("/disconnect", (req, res) => {
      this.bot.disconnect();
      res.json({ success: true, message: "Disconnected" });
    });
  }

  setupWebSocket() {
    this.wss.on("connection", (ws) => {
      logger.info("WebSocket client connected");
      this.clients.add(ws);

      ws.on("message", async (message) => {
        try {
          const data = JSON.parse(message);

          switch (data.type) {
            case "action":
              const result = await this.bot.step(data.action);
              ws.send(JSON.stringify({ type: "step", data: result }));
              break;
            case "reset":
              const obs = await this.bot.reset();
              ws.send(
                JSON.stringify({ type: "reset", data: { observation: obs } }),
              );
              break;
            case "observation":
              const observation = this.bot.getObservation();
              ws.send(
                JSON.stringify({ type: "observation", data: observation }),
              );
              break;
          }
        } catch (err) {
          ws.send(JSON.stringify({ type: "error", error: err.message }));
        }
      });

      ws.on("close", () => {
        logger.info("WebSocket client disconnected");
        this.clients.delete(ws);
      });
    });
  }

  broadcast(type, data) {
    const message = JSON.stringify({ type, data });
    this.clients.forEach((client) => {
      if (client.readyState === 1) {
        client.send(message);
      }
    });
  }

  async start() {
    // Connect to Minecraft
    try {
      await this.bot.connect();
    } catch (err) {
      logger.error("Failed to connect to Minecraft:", err.message);
      logger.warn("Server will start without Minecraft connection");
      logger.info("Use POST /connect to connect later");
    }

    // Start HTTP server
    this.server.listen(config.api.port, () => {
      logger.success(
        `API Server running on http://localhost:${config.api.port}`,
      );
      logger.success(`WebSocket running on ws://localhost:${config.api.port}`);
    });
  }
}

module.exports = TerraScoutServer;
