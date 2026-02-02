/**
 * Terra Scout Mineflayer Bot
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
    this.episodeRunning = false;
    this.stepCount = 0;
    this.totalReward = 0;
    this.startPosition = null;
    this.visitedBlocks = new Set();
  }

  async connect() {
    logger.info(
      `Connecting to ${config.minecraft.host}:${config.minecraft.port}...`,
    );

    this.bot = mineflayer.createBot({
      host: config.minecraft.host,
      port: config.minecraft.port,
      username: config.minecraft.username,
      version: config.minecraft.version,
      hideErrors: false,
    });

    // Load plugins
    this.bot.loadPlugin(pathfinder);
    this.bot.loadPlugin(collectBlock);
    this.bot.loadPlugin(autoEat);

    // Setup event handlers
    this.setupEventHandlers();

    // Wait for spawn
    return new Promise((resolve, reject) => {
      this.bot.once("spawn", () => {
        logger.success("Bot spawned successfully!");
        this.isConnected = true;
        this.setupPathfinder();
        resolve();
      });

      this.bot.once("error", (err) => {
        logger.error("Connection error:", err.message);
        reject(err);
      });

      this.bot.once("kicked", (reason) => {
        logger.error("Kicked:", reason);
        reject(new Error(reason));
      });
    });
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

    this.bot.on("end", () => {
      logger.warn("Disconnected from server");
      this.isConnected = false;
    });
  }

  setupPathfinder() {
    const movements = new Movements(this.bot);
    movements.canDig = true;
    movements.allow1by1towers = true;
    movements.scafoldingBlocks = [];
    this.bot.pathfinder.setMovements(movements);
  }

  /**
   * Get current observation
   */
  getObservation() {
    if (!this.bot || !this.isConnected) {
      return null;
    }

    const pos = this.bot.entity.position;

    return {
      position: {
        x: pos.x,
        y: pos.y,
        z: pos.z,
      },
      health: this.bot.health,
      food: this.bot.food,
      yaw: this.bot.entity.yaw,
      pitch: this.bot.entity.pitch,
      onGround: this.bot.entity.onGround,
      inventory: this.getInventoryState(),
      nearbyBlocks: this.getNearbyBlocks(),
      nearbyEntities: this.getNearbyEntities(),
      isRaining: this.bot.isRaining,
      time: this.bot.time.day,
      stepCount: this.stepCount,
      visitedCount: this.visitedBlocks.size,
    };
  }

  getInventoryState() {
    const items = {};
    this.bot.inventory.items().forEach((item) => {
      items[item.name] = (items[item.name] || 0) + item.count;
    });
    return items;
  }

  getNearbyBlocks() {
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
              position: { x: pos.x + x, y: pos.y + y, z: pos.z + z },
              hardness: block.hardness,
            });
          }
        }
      }
    }
    return blocks;
  }

  getNearbyEntities() {
    const entities = [];
    const radius = config.observation.nearbyEntityRadius;

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
    return entities;
  }

  /**
   * Execute an action
   */
  async executeAction(action) {
    if (!this.bot || !this.isConnected) {
      return { success: false, error: "Not connected" };
    }

    this.stepCount++;
    const pos = this.bot.entity.position;
    const blockKey = `${Math.floor(pos.x)},${Math.floor(pos.y)},${Math.floor(pos.z)}`;
    this.visitedBlocks.add(blockKey);

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
        case "noop":
          await this.sleep(50);
          break;
        default:
          return { success: false, error: `Unknown action: ${action.type}` };
      }
      return { success: true };
    } catch (err) {
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
    if (position) {
      const block = this.bot.blockAt(position);
      if (block && block.name !== "air") {
        await this.bot.dig(block);
      }
    } else {
      // Dig block in front
      const target = this.bot.blockAtCursor(4);
      if (target && target.name !== "air") {
        await this.bot.dig(target);
      }
    }
  }

  async actionAttack() {
    const entity = this.bot.nearestEntity();
    if (entity && entity.position.distanceTo(this.bot.entity.position) < 4) {
      this.bot.attack(entity);
    }
  }

  async actionForwardJump() {
    this.bot.setControlState("forward", true);
    this.bot.setControlState("jump", true);
    await this.sleep(200);
    this.bot.setControlState("forward", false);
    this.bot.setControlState("jump", false);
  }

  /**
   * Calculate reward
   */
  calculateReward() {
    let reward = -0.001; // Small step penalty

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
      reward += (0.01 * (16 - y)) / 80; // Reward for being in diamond zone
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
      if (block.name === "diamond_ore") reward += 10;
      else if (block.name === "iron_ore") reward += 0.5;
      else if (block.name === "gold_ore") reward += 1;
      else if (block.name === "redstone_ore") reward += 2;
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
      this.startPosition = this.bot.entity.position.clone();

      // Respawn if dead
      if (this.bot.health <= 0) {
        this.bot.chat("/respawn");
        await this.sleep(1000);
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
    const done = !this.episodeRunning || this.bot.health <= 0;

    return {
      observation,
      reward,
      done,
      info: {
        stepCount: this.stepCount,
        totalReward: this.totalReward,
        success: result.success,
      },
    };
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  disconnect() {
    if (this.bot) {
      this.bot.quit();
      this.isConnected = false;
    }
  }
}

module.exports = TerraScoutBot;
