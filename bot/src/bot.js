/**
 * Terra Scout Mineflayer Bot
 * With improved connection handling
 */

const mineflayer = require("mineflayer");
const { pathfinder, Movements, goals } = require("mineflayer-pathfinder");
const collectBlock = require("mineflayer-collectblock").plugin;
const autoEat = require("mineflayer-auto-eat").plugin;
const logger = require("./utils/logger");
const config = require("./utils/config");

class TerraScoutBot {
  constructor() {
    this.bot = null;
    this.isConnected = false;
    this.isConnecting = false;
    this.episodeRunning = false;
    this.stepCount = 0;
    this.totalReward = 0;
    this.startPosition = null;
    this.visitedBlocks = new Set();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  async connect() {
    if (this.isConnecting) {
      logger.warn("Already attempting to connect...");
      return;
    }

    this.isConnecting = true;
    logger.info(
      `Connecting to ${config.minecraft.host}:${config.minecraft.port}...`,
    );
    logger.info(`Using Minecraft version: ${config.minecraft.version}`);
    logger.info(`Username: ${config.minecraft.username}`);

    return new Promise((resolve, reject) => {
      try {
        this.bot = mineflayer.createBot({
          host: config.minecraft.host,
          port: config.minecraft.port,
          username: config.minecraft.username,
          version: config.minecraft.version,
          hideErrors: false,
          checkTimeoutInterval: 30000,
          auth: "offline",
        });

        // Connection timeout
        const connectionTimeout = setTimeout(() => {
          this.isConnecting = false;
          reject(new Error("Connection timeout after 30 seconds"));
        }, 30000);

        // Spawn event - successful connection
        this.bot.once("spawn", () => {
          clearTimeout(connectionTimeout);
          logger.success("Bot spawned successfully!");
          this.isConnected = true;
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.loadPlugins();
          this.setupEventHandlers();
          resolve();
        });

        // Login event
        this.bot.once("login", () => {
          logger.info("Logged in to server");
        });

        // Error handling
        this.bot.once("error", (err) => {
          clearTimeout(connectionTimeout);
          this.isConnecting = false;
          logger.error("Connection error:", err.message);

          if (err.message.includes("ECONNREFUSED")) {
            logger.error("Server is not running or not accepting connections");
            logger.info("Make sure Minecraft server is started on port 25565");
          } else if (err.message.includes("ECONNRESET")) {
            logger.error("Connection was reset by server");
            logger.info("Possible causes:");
            logger.info("  1. Server is still starting up - wait and retry");
            logger.info("  2. Version mismatch - check BOT_VERSION in .env");
            logger.info("  3. Server rejected connection - check server logs");
          }

          reject(err);
        });

        // Kicked event
        this.bot.once("kicked", (reason, loggedIn) => {
          clearTimeout(connectionTimeout);
          this.isConnecting = false;
          const reasonStr =
            typeof reason === "object" ? JSON.stringify(reason) : reason;
          logger.error("Kicked from server:", reasonStr);
          reject(new Error(`Kicked: ${reasonStr}`));
        });

        // End event
        this.bot.once("end", (reason) => {
          this.isConnected = false;
          this.isConnecting = false;
          logger.warn("Disconnected:", reason || "unknown reason");
        });
      } catch (err) {
        this.isConnecting = false;
        logger.error("Failed to create bot:", err.message);
        reject(err);
      }
    });
  }

  loadPlugins() {
    try {
      this.bot.loadPlugin(pathfinder);
      logger.info("Loaded pathfinder plugin");
    } catch (err) {
      logger.warn("Failed to load pathfinder:", err.message);
    }

    try {
      this.bot.loadPlugin(collectBlock);
      logger.info("Loaded collectBlock plugin");
    } catch (err) {
      logger.warn("Failed to load collectBlock:", err.message);
    }

    try {
      this.bot.loadPlugin(autoEat);
      logger.info("Loaded autoEat plugin");
    } catch (err) {
      logger.warn("Failed to load autoEat:", err.message);
    }

    this.setupPathfinder();
  }

  setupEventHandlers() {
    this.bot.on("health", () => {
      if (this.bot.health <= 0) {
        logger.warn("Bot died!");
        this.episodeRunning = false;
      }
    });

    this.bot.on("death", () => {
      logger.warn("Bot died! Respawning...");
      this.episodeRunning = false;
    });

    this.bot.on("error", (err) => {
      logger.error("Bot error:", err.message);
    });

    this.bot.on("end", (reason) => {
      logger.warn("Disconnected from server:", reason || "unknown");
      this.isConnected = false;
    });

    this.bot.on("kicked", (reason) => {
      const reasonStr =
        typeof reason === "object" ? JSON.stringify(reason) : reason;
      logger.warn("Kicked:", reasonStr);
      this.isConnected = false;
    });

    // Chat logging
    this.bot.on("chat", (username, message) => {
      if (username !== this.bot.username) {
        logger.info(`[Chat] ${username}: ${message}`);
      }
    });
  }

  setupPathfinder() {
    if (this.bot.pathfinder) {
      try {
        const movements = new Movements(this.bot);
        movements.canDig = true;
        movements.allow1by1towers = true;
        movements.scafoldingBlocks = [];
        this.bot.pathfinder.setMovements(movements);
        logger.info("Pathfinder configured");
      } catch (err) {
        logger.warn("Failed to setup pathfinder:", err.message);
      }
    }
  }

  /**
   * Get current observation
   */
  getObservation() {
    if (!this.bot || !this.isConnected) {
      return null;
    }

    try {
      const pos = this.bot.entity.position;

      return {
        position: {
          x: pos.x,
          y: pos.y,
          z: pos.z,
        },
        health: this.bot.health || 20,
        food: this.bot.food || 20,
        yaw: this.bot.entity.yaw || 0,
        pitch: this.bot.entity.pitch || 0,
        onGround: this.bot.entity.onGround,
        inventory: this.getInventoryState(),
        nearbyBlocks: this.getNearbyBlocks(),
        nearbyEntities: this.getNearbyEntities(),
        isRaining: this.bot.isRaining,
        time: this.bot.time ? this.bot.time.day : 0,
        stepCount: this.stepCount,
        visitedCount: this.visitedBlocks.size,
      };
    } catch (err) {
      logger.error("Error getting observation:", err.message);
      return null;
    }
  }

  getInventoryState() {
    try {
      const items = {};
      if (this.bot.inventory) {
        this.bot.inventory.items().forEach((item) => {
          items[item.name] = (items[item.name] || 0) + item.count;
        });
      }
      return items;
    } catch (err) {
      return {};
    }
  }

  getNearbyBlocks() {
    try {
      const blocks = [];
      const radius = config.observation.nearbyBlockRadius;
      const pos = this.bot.entity.position;

      for (let x = -radius; x <= radius; x++) {
        for (let y = -radius; y <= radius; y++) {
          for (let z = -radius; z <= radius; z++) {
            const block = this.bot.blockAt(pos.offset(x, y, z));
            if (block && block.name !== "air") {
              blocks.push({
                name: block.name,
                position: {
                  x: Math.floor(pos.x) + x,
                  y: Math.floor(pos.y) + y,
                  z: Math.floor(pos.z) + z,
                },
                hardness: block.hardness,
              });
            }
          }
        }
      }
      return blocks;
    } catch (err) {
      return [];
    }
  }

  getNearbyEntities() {
    try {
      const entities = [];
      const radius = config.observation.nearbyEntityRadius;

      if (this.bot.entities) {
        Object.values(this.bot.entities).forEach((entity) => {
          if (entity === this.bot.entity) return;

          const dist = entity.position.distanceTo(this.bot.entity.position);
          if (dist <= radius) {
            entities.push({
              type: entity.type,
              name: entity.name || entity.type,
              position: {
                x: entity.position.x,
                y: entity.position.y,
                z: entity.position.z,
              },
              distance: dist,
            });
          }
        });
      }
      return entities;
    } catch (err) {
      return [];
    }
  }

  /**
   * Execute an action
   */
  async executeAction(action) {
    if (!this.bot || !this.isConnected) {
      return { success: false, error: "Not connected" };
    }

    this.stepCount++;

    try {
      const pos = this.bot.entity.position;
      const blockKey = `${Math.floor(pos.x)},${Math.floor(pos.y)},${Math.floor(pos.z)}`;
      this.visitedBlocks.add(blockKey);
    } catch (err) {
      // Ignore position tracking errors
    }

    try {
      switch (action.type) {
        case "move":
          await this.actionMove(action.direction, action.duration || 1);
          break;
        case "jump":
          await this.actionJump();
          break;
        case "look":
          await this.actionLook(action.yaw, action.pitch);
          break;
        case "dig":
          await this.actionDig(action.position);
          break;
        case "attack":
          await this.actionAttack();
          break;
        case "forward_jump":
          await this.actionForwardJump();
          break;
        case "dig_down":
          await this.actionDigDown();
          break;
        case "sprint_forward":
          await this.actionSprintForward();
          break;
        case "noop":
          await this.sleep(50);
          break;
        default:
          return { success: false, error: `Unknown action: ${action.type}` };
      }
      return { success: true };
    } catch (err) {
      logger.error("Action error:", err.message);
      return { success: false, error: err.message };
    }
  }

  async actionMove(direction, duration) {
    this.bot.setControlState(direction, true);
    await this.sleep(duration * 100);
    this.bot.setControlState(direction, false);
  }

  async actionJump() {
    this.bot.setControlState("jump", true);
    await this.sleep(100);
    this.bot.setControlState("jump", false);
  }

  async actionLook(yaw, pitch) {
    await this.bot.look(
      this.bot.entity.yaw + (yaw || 0),
      this.bot.entity.pitch + (pitch || 0),
      false,
    );
  }

  async actionDig(position) {
    try {
      if (position) {
        const block = this.bot.blockAt(position);
        if (block && block.name !== "air" && block.name !== "bedrock") {
          await this.bot.dig(block);
        }
      } else {
        const target = this.bot.blockAtCursor(4);
        if (target && target.name !== "air" && target.name !== "bedrock") {
          await this.bot.dig(target);
        }
      }
    } catch (err) {
      // Digging might fail, that's ok
    }
  }

  async actionAttack() {
    try {
      const entity = this.bot.nearestEntity();
      if (entity && entity.position.distanceTo(this.bot.entity.position) < 4) {
        this.bot.attack(entity);
      }
    } catch (err) {
      // Attack might fail, that's ok
    }
  }

  async actionForwardJump() {
    this.bot.setControlState("forward", true);
    this.bot.setControlState("jump", true);
    await this.sleep(200);
    this.bot.setControlState("forward", false);
    this.bot.setControlState("jump", false);
  }

  async actionDigDown() {
    try {
      const pos = this.bot.entity.position;
      const blockBelow = this.bot.blockAt(pos.offset(0, -1, 0));
      if (
        blockBelow &&
        blockBelow.name !== "air" &&
        blockBelow.name !== "bedrock"
      ) {
        await this.bot.dig(blockBelow);
      }
    } catch (err) {
      // Digging might fail, that's ok
    }
  }

  async actionSprintForward() {
    this.bot.setControlState("sprint", true);
    this.bot.setControlState("forward", true);
    await this.sleep(300);
    this.bot.setControlState("forward", false);
    this.bot.setControlState("sprint", false);
  }

  /**
   * Calculate reward
   */
  calculateReward() {
    if (!this.bot || !this.isConnected) {
      return 0;
    }

    let reward = -0.001; // Small step penalty

    try {
      // Check for diamond in inventory
      const inventory = this.getInventoryState();
      if (inventory["diamond"]) {
        reward += 1000;
        this.episodeRunning = false;
        logger.success("Diamond found!");
      }

      // Y-level reward (going deeper)
      const y = this.bot.entity.position.y;
      if (y < 16) {
        reward += (0.01 * (16 - y)) / 80;
      }

      // Exploration reward
      const pos = this.bot.entity.position;
      const blockKey = `${Math.floor(pos.x)},${Math.floor(pos.y)},${Math.floor(pos.z)}`;
      if (!this.visitedBlocks.has(blockKey)) {
        reward += 0.01;
      }

      // Ore discovery rewards
      const nearbyBlocks = this.getNearbyBlocks();
      nearbyBlocks.forEach((block) => {
        if (
          block.name === "diamond_ore" ||
          block.name === "deepslate_diamond_ore"
        )
          reward += 10;
        else if (
          block.name === "iron_ore" ||
          block.name === "deepslate_iron_ore"
        )
          reward += 0.5;
        else if (
          block.name === "gold_ore" ||
          block.name === "deepslate_gold_ore"
        )
          reward += 1;
        else if (
          block.name === "redstone_ore" ||
          block.name === "deepslate_redstone_ore"
        )
          reward += 2;
      });

      // Death penalty
      if (this.bot.health <= 0) {
        reward -= 100;
        this.episodeRunning = false;
      }

      // Damage penalty
      if (this.bot.health < 20) {
        reward -= (20 - this.bot.health) * 0.1;
      }
    } catch (err) {
      // Ignore reward calculation errors
    }

    this.totalReward += reward;
    return reward;
  }

  /**
   * Reset episode
   */
  async reset() {
    logger.info("Resetting episode...");

    this.stepCount = 0;
    this.totalReward = 0;
    this.visitedBlocks.clear();
    this.episodeRunning = true;

    if (this.bot && this.isConnected) {
      try {
        this.startPosition = this.bot.entity.position.clone();

        // Respawn if dead
        if (this.bot.health <= 0) {
          this.bot.chat("/respawn");
          await this.sleep(1000);
        }
      } catch (err) {
        logger.warn("Reset warning:", err.message);
      }
    }

    return this.getObservation();
  }

  /**
   * Step the environment
   */
  async step(action) {
    const result = await this.executeAction(action);
    const observation = this.getObservation();
    const reward = this.calculateReward();
    const done = !this.episodeRunning || (this.bot && this.bot.health <= 0);

    return {
      observation,
      reward,
      done,
      info: {
        stepCount: this.stepCount,
        totalReward: this.totalReward,
        success: result.success,
        error: result.error,
      },
    };
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  disconnect() {
    if (this.bot) {
      try {
        this.bot.quit();
      } catch (err) {
        // Ignore disconnect errors
      }
      this.isConnected = false;
      this.bot = null;
    }
  }
}

module.exports = TerraScoutBot;
