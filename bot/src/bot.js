/**
 * Terra Scout Mineflayer Bot
 * Fixed: Inventory reset, ore visibility, lava safety
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
    this.spawnPosition = null;
    this.visitedBlocks = new Set();
    this.minedOres = new Set();
    this.lastPosition = null;
    this.stuckCounter = 0;
    this.diamondsThisEpisode = 0; // Track diamonds found THIS episode only

    // Dangerous blocks to avoid
    this.dangerousBlocks = new Set([
      "lava",
      "flowing_lava",
      "fire",
      "cactus",
      "magma_block",
      "sweet_berry_bush",
      "powder_snow",
    ]);

    // Valuable ores to mine
    this.valuableOres = new Set([
      "diamond_ore",
      "deepslate_diamond_ore",
      "iron_ore",
      "deepslate_iron_ore",
      "gold_ore",
      "deepslate_gold_ore",
      "redstone_ore",
      "deepslate_redstone_ore",
      "lapis_ore",
      "deepslate_lapis_ore",
      "emerald_ore",
      "deepslate_emerald_ore",
      "coal_ore",
      "deepslate_coal_ore",
      "copper_ore",
      "deepslate_copper_ore",
    ]);
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

        const connectionTimeout = setTimeout(() => {
          this.isConnecting = false;
          reject(new Error("Connection timeout after 30 seconds"));
        }, 30000);

        this.bot.once("spawn", () => {
          clearTimeout(connectionTimeout);
          logger.success("Bot spawned successfully!");
          this.isConnected = true;
          this.isConnecting = false;
          this.spawnPosition = this.bot.entity.position.clone();
          this.loadPlugins();
          this.setupEventHandlers();
          resolve();
        });

        this.bot.once("error", (err) => {
          clearTimeout(connectionTimeout);
          this.isConnecting = false;
          logger.error("Connection error:", err.message);
          reject(err);
        });

        this.bot.once("kicked", (reason) => {
          clearTimeout(connectionTimeout);
          this.isConnecting = false;
          const reasonStr =
            typeof reason === "object" ? JSON.stringify(reason) : reason;
          reject(new Error(`Kicked: ${reasonStr}`));
        });

        this.bot.once("end", () => {
          this.isConnected = false;
          this.isConnecting = false;
        });
      } catch (err) {
        this.isConnecting = false;
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
    } catch (err) {}

    try {
      this.bot.loadPlugin(autoEat);
      this.bot.autoEat.options = { priority: "foodPoints", startAt: 14 };
    } catch (err) {}

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
      logger.warn("Bot died! Episode ending.");
      this.episodeRunning = false;
    });

    this.bot.on("error", (err) => {
      logger.error("Bot error:", err.message);
    });

    this.bot.on("end", () => {
      this.isConnected = false;
    });
  }

  setupPathfinder() {
    if (this.bot.pathfinder) {
      try {
        const movements = new Movements(this.bot);
        movements.canDig = true;
        movements.allow1by1towers = false;
        this.bot.pathfinder.setMovements(movements);
      } catch (err) {}
    }
  }

  /**
   * Check if a block is exposed to air (visible/mineable)
   */
  isBlockExposed(blockPos) {
    const directions = [
      { x: 1, y: 0, z: 0 },
      { x: -1, y: 0, z: 0 },
      { x: 0, y: 1, z: 0 },
      { x: 0, y: -1, z: 0 },
      { x: 0, y: 0, z: 1 },
      { x: 0, y: 0, z: -1 },
    ];

    for (const dir of directions) {
      const adjacentBlock = this.bot.blockAt(
        blockPos.offset(dir.x, dir.y, dir.z),
      );
      if (
        !adjacentBlock ||
        adjacentBlock.name === "air" ||
        adjacentBlock.name === "cave_air"
      ) {
        return true;
      }
    }
    return false;
  }

  /**
   * Check if digging a block would release lava
   */
  wouldReleaseLava(blockPos) {
    const directions = [
      { x: 1, y: 0, z: 0 },
      { x: -1, y: 0, z: 0 },
      { x: 0, y: 1, z: 0 },
      { x: 0, y: -1, z: 0 },
      { x: 0, y: 0, z: 1 },
      { x: 0, y: 0, z: -1 },
    ];

    for (const dir of directions) {
      const adjacentBlock = this.bot.blockAt(
        blockPos.offset(dir.x, dir.y, dir.z),
      );
      if (
        adjacentBlock &&
        (adjacentBlock.name === "lava" || adjacentBlock.name === "flowing_lava")
      ) {
        return true;
      }
    }
    return false;
  }

  /**
   * Find nearest VISIBLE ore block (exposed to air)
   */
  findNearestVisibleOre(maxDistance = 6) {
    try {
      const pos = this.bot.entity.position;
      let nearestOre = null;
      let nearestDist = maxDistance;

      for (let x = -maxDistance; x <= maxDistance; x++) {
        for (let y = -maxDistance; y <= maxDistance; y++) {
          for (let z = -maxDistance; z <= maxDistance; z++) {
            const blockPos = pos.offset(x, y, z);
            const block = this.bot.blockAt(blockPos);

            if (block && this.valuableOres.has(block.name)) {
              // Only count if exposed to air
              if (this.isBlockExposed(blockPos)) {
                const dist = Math.sqrt(x * x + y * y + z * z);
                if (dist < nearestDist) {
                  nearestDist = dist;
                  nearestOre = block;
                }
              }
            }
          }
        }
      }
      return nearestOre;
    } catch (err) {
      return null;
    }
  }

  getObservation() {
    if (!this.bot || !this.isConnected) return null;

    try {
      const pos = this.bot.entity.position;
      const nearbyBlocks = this.getNearbyBlocks();
      const visibleOres = this.getVisibleOres();

      const dangerNearby = nearbyBlocks.some((b) =>
        this.dangerousBlocks.has(b.name),
      );
      const diamondNearby = visibleOres.some((b) => b.name.includes("diamond"));

      return {
        position: { x: pos.x, y: pos.y, z: pos.z },
        health: this.bot.health || 20,
        food: this.bot.food || 20,
        yaw: this.bot.entity.yaw || 0,
        pitch: this.bot.entity.pitch || 0,
        onGround: this.bot.entity.onGround,
        inventory: this.getInventoryState(),
        nearbyBlocks: nearbyBlocks,
        visibleOres: visibleOres, // Only exposed ores
        nearbyEntities: [],
        stepCount: this.stepCount,
        visitedCount: this.visitedBlocks.size,
        dangerNearby: dangerNearby,
        diamondNearby: diamondNearby,
        oresNearby: visibleOres.length,
        minedOresCount: this.minedOres.size,
        isStuck: this.stuckCounter > 10,
        diamondsThisEpisode: this.diamondsThisEpisode,
      };
    } catch (err) {
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
      const radius = 4;
      const pos = this.bot.entity.position;

      for (let x = -radius; x <= radius; x++) {
        for (let y = -radius; y <= radius; y++) {
          for (let z = -radius; z <= radius; z++) {
            const block = this.bot.blockAt(pos.offset(x, y, z));
            if (block && block.name !== "air" && block.name !== "cave_air") {
              blocks.push({
                name: block.name,
                position: {
                  x: Math.floor(pos.x) + x,
                  y: Math.floor(pos.y) + y,
                  z: Math.floor(pos.z) + z,
                },
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

  /**
   * Get only VISIBLE ores (exposed to air)
   */
  getVisibleOres() {
    try {
      const ores = [];
      const radius = 6;
      const pos = this.bot.entity.position;

      for (let x = -radius; x <= radius; x++) {
        for (let y = -radius; y <= radius; y++) {
          for (let z = -radius; z <= radius; z++) {
            const blockPos = pos.offset(x, y, z);
            const block = this.bot.blockAt(blockPos);

            if (block && this.valuableOres.has(block.name)) {
              if (this.isBlockExposed(blockPos)) {
                ores.push({
                  name: block.name,
                  position: {
                    x: Math.floor(pos.x) + x,
                    y: Math.floor(pos.y) + y,
                    z: Math.floor(pos.z) + z,
                  },
                  distance: Math.sqrt(x * x + y * y + z * z),
                });
              }
            }
          }
        }
      }

      // Sort by distance
      ores.sort((a, b) => a.distance - b.distance);
      return ores;
    } catch (err) {
      return [];
    }
  }

  async executeAction(action) {
    if (!this.bot || !this.isConnected) {
      return { success: false, error: "Not connected" };
    }

    this.stepCount++;

    // Track position
    try {
      const pos = this.bot.entity.position;
      const blockKey = `${Math.floor(pos.x)},${Math.floor(pos.y)},${Math.floor(pos.z)}`;
      this.visitedBlocks.add(blockKey);

      if (this.lastPosition) {
        const dist = pos.distanceTo(this.lastPosition);
        this.stuckCounter = dist < 0.1 ? this.stuckCounter + 1 : 0;
      }
      this.lastPosition = pos.clone();
    } catch (err) {}

    try {
      switch (action.type) {
        case "move":
          await this.actionMove(action.direction, action.duration || 2);
          break;
        case "jump":
          await this.actionJump();
          break;
        case "look":
          await this.actionLook(action.yaw, action.pitch);
          break;
        case "dig":
          await this.actionDig();
          break;
        case "dig_down":
          await this.actionDigDown();
          break;
        case "dig_forward":
          await this.actionDigForward();
          break;
        case "forward_jump":
          await this.actionForwardJump();
          break;
        case "sprint_forward":
          await this.actionSprintForward();
          break;
        case "mine_ore":
          await this.actionMineNearestOre();
          break;
        case "tunnel_forward":
          await this.actionTunnelForward();
          break;
        case "safe_dig_down":
          await this.actionSafeDigDown();
          break;
        case "strip_mine":
          await this.actionStripMine();
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
    await this.sleep(150);
    this.bot.setControlState("jump", false);
  }

  async actionLook(yaw, pitch) {
    await this.bot.look(
      this.bot.entity.yaw + (yaw || 0),
      this.bot.entity.pitch + (pitch || 0),
      false,
    );
  }

  async actionDig() {
    try {
      const target = this.bot.blockAtCursor(4);
      if (target && target.name !== "air" && target.name !== "bedrock") {
        // Check for lava behind
        if (this.wouldReleaseLava(target.position)) {
          logger.warn("Lava behind block! Not digging.");
          return;
        }
        await this.bot.dig(target);
        await this.checkMinedOre(target);
      }
    } catch (err) {}
  }

  async actionDigDown() {
    try {
      const pos = this.bot.entity.position;
      const blockBelow = this.bot.blockAt(pos.offset(0, -1, 0));

      if (
        !blockBelow ||
        blockBelow.name === "air" ||
        blockBelow.name === "bedrock"
      ) {
        return;
      }

      // Check for lava around the block below
      if (this.wouldReleaseLava(blockBelow.position)) {
        logger.warn("Lava near block below! Not digging.");
        return;
      }

      await this.bot.dig(blockBelow);
      await this.checkMinedOre(blockBelow);
    } catch (err) {}
  }

  async actionSafeDigDown() {
    try {
      const pos = this.bot.entity.position;
      const block1 = this.bot.blockAt(pos.offset(0, -1, 0));

      if (!block1 || block1.name === "air" || block1.name === "bedrock") {
        return;
      }

      // Check for lava in ANY adjacent block
      if (this.wouldReleaseLava(block1.position)) {
        logger.warn("Lava detected! Safe dig aborted.");
        return;
      }

      await this.bot.dig(block1);
      await this.checkMinedOre(block1);
    } catch (err) {}
  }

  async actionDigForward() {
    try {
      const pos = this.bot.entity.position;
      const yaw = this.bot.entity.yaw;
      const dx = -Math.sin(yaw);
      const dz = Math.cos(yaw);

      const blockInFront = this.bot.blockAt(pos.offset(dx, 0, dz));
      if (
        !blockInFront ||
        blockInFront.name === "air" ||
        blockInFront.name === "bedrock"
      ) {
        return;
      }

      if (this.wouldReleaseLava(blockInFront.position)) {
        logger.warn("Lava ahead! Not digging.");
        return;
      }

      await this.bot.dig(blockInFront);
      await this.checkMinedOre(blockInFront);
    } catch (err) {}
  }

  async actionTunnelForward() {
    try {
      const pos = this.bot.entity.position;
      const yaw = this.bot.entity.yaw;
      const dx = -Math.sin(yaw);
      const dz = Math.cos(yaw);

      // Check both blocks ahead for lava
      const block1 = this.bot.blockAt(pos.offset(dx, 0, dz));
      const block2 = this.bot.blockAt(pos.offset(dx, 1, dz));

      if (block1 && this.wouldReleaseLava(block1.position)) {
        logger.warn("Danger ahead! Stopping tunnel.");
        return;
      }
      if (block2 && this.wouldReleaseLava(block2.position)) {
        logger.warn("Danger ahead! Stopping tunnel.");
        return;
      }

      // Dig lower block
      if (block1 && block1.name !== "air" && block1.name !== "bedrock") {
        await this.bot.dig(block1);
        await this.checkMinedOre(block1);
      }

      // Dig upper block
      if (block2 && block2.name !== "air" && block2.name !== "bedrock") {
        await this.bot.dig(block2);
        await this.checkMinedOre(block2);
      }

      // Move forward
      this.bot.setControlState("forward", true);
      await this.sleep(200);
      this.bot.setControlState("forward", false);
    } catch (err) {}
  }

  async actionStripMine() {
    // Classic strip mining pattern at current Y level
    try {
      // Dig 3 blocks forward in a 2-high tunnel
      for (let i = 0; i < 3; i++) {
        await this.actionTunnelForward();
        await this.sleep(100);
      }
    } catch (err) {}
  }

  async actionMineNearestOre() {
    try {
      const ore = this.findNearestVisibleOre(5);
      if (ore) {
        const dist = ore.position.distanceTo(this.bot.entity.position);
        logger.info(`Found visible ${ore.name} at distance ${dist.toFixed(1)}`);

        if (dist <= 4) {
          // Check for lava
          if (this.wouldReleaseLava(ore.position)) {
            logger.warn("Lava near ore! Not mining.");
            return;
          }

          await this.bot.dig(ore);
          await this.checkMinedOre(ore);
        } else {
          // Look at and move towards ore
          await this.bot.lookAt(ore.position);
          this.bot.setControlState("forward", true);
          await this.sleep(300);
          this.bot.setControlState("forward", false);
        }
      }
    } catch (err) {}
  }

  async actionForwardJump() {
    this.bot.setControlState("forward", true);
    this.bot.setControlState("jump", true);
    await this.sleep(250);
    this.bot.setControlState("forward", false);
    this.bot.setControlState("jump", false);
  }

  async actionSprintForward() {
    this.bot.setControlState("sprint", true);
    this.bot.setControlState("forward", true);
    await this.sleep(400);
    this.bot.setControlState("forward", false);
    this.bot.setControlState("sprint", false);
  }

  async checkMinedOre(block) {
    if (this.valuableOres.has(block.name)) {
      const key = `${block.position.x},${block.position.y},${block.position.z}`;
      if (!this.minedOres.has(key)) {
        this.minedOres.add(key);
        logger.success(`Mined ${block.name}!`);

        // Track diamonds specifically
        if (block.name.includes("diamond")) {
          this.diamondsThisEpisode++;
          logger.success("💎 DIAMOND ORE MINED! 💎");
        }
      }
    }
  }

  calculateReward() {
    if (!this.bot || !this.isConnected) return 0;

    let reward = -0.001; // Step penalty

    try {
      // Check for DIAMONDS MINED THIS EPISODE (not in inventory from before)
      if (this.diamondsThisEpisode > 0) {
        reward += 1000;
        this.episodeRunning = false;
        logger.success("💎 EPISODE SUCCESS: Diamond obtained! 💎");
      }

      const y = this.bot.entity.position.y;

      // Y-level rewards
      if (y < 16) {
        reward += (0.01 * (16 - y)) / 80;
      }

      // Exploration
      const pos = this.bot.entity.position;
      const blockKey = `${Math.floor(pos.x)},${Math.floor(pos.y)},${Math.floor(pos.z)}`;
      if (!this.visitedBlocks.has(blockKey)) {
        reward += 0.01;
      }

      // Visible ore rewards
      const visibleOres = this.getVisibleOres();
      for (const ore of visibleOres) {
        if (ore.name.includes("diamond")) reward += 5; // Diamond visible
      }

      // Stuck penalty
      if (this.stuckCounter > 20) reward -= 0.1;

      // Death
      if (this.bot.health <= 0) {
        reward -= 100;
        this.episodeRunning = false;
      }

      // Damage penalty
      if (this.bot.health < 20) {
        reward -= (20 - this.bot.health) * 0.1;
      }
    } catch (err) {}

    this.totalReward += reward;
    return reward;
  }

  /**
   * Reset episode - PROPERLY clears state
   */
  async reset() {
    logger.info("Resetting episode...");

    // Reset all tracking
    this.stepCount = 0;
    this.totalReward = 0;
    this.visitedBlocks.clear();
    this.minedOres.clear();
    this.stuckCounter = 0;
    this.lastPosition = null;
    this.episodeRunning = true;
    this.diamondsThisEpisode = 0; // CRITICAL: Reset diamonds count

    if (this.bot && this.isConnected) {
      try {
        // Stop all movements
        this.bot.setControlState("forward", false);
        this.bot.setControlState("back", false);
        this.bot.setControlState("left", false);
        this.bot.setControlState("right", false);
        this.bot.setControlState("jump", false);
        this.bot.setControlState("sprint", false);

        // Clear inventory
        this.bot.chat("/clear");
        await this.sleep(200);

        // Give iron pickaxe for mining
        this.bot.chat("/give @s iron_pickaxe");
        await this.sleep(100);

        // Teleport to spawn/surface to start fresh
        if (this.spawnPosition) {
          this.bot.chat(
            `/tp @s ${Math.floor(this.spawnPosition.x)} ${Math.floor(this.spawnPosition.y)} ${Math.floor(this.spawnPosition.z)}`,
          );
          await this.sleep(200);
        }

        // Heal the bot
        this.bot.chat("/effect give @s minecraft:instant_health 1 10");
        await this.sleep(100);
        this.bot.chat("/effect give @s minecraft:saturation 1 10");
        await this.sleep(100);

        this.startPosition = this.bot.entity.position.clone();
      } catch (err) {
        logger.warn("Reset warning:", err.message);
      }
    }

    return this.getObservation();
  }

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
        minedOres: this.minedOres.size,
        diamondsThisEpisode: this.diamondsThisEpisode,
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
      } catch (err) {}
      this.isConnected = false;
      this.bot = null;
    }
  }
}

module.exports = TerraScoutBot;
