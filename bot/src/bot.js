/**
 * Terra Scout Mineflayer Bot
 * Phase 5: Mining Patterns & Cave Exploration
 */

const mineflayer = require("mineflayer");
const { pathfinder, Movements, goals } = require("mineflayer-pathfinder");
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
    this.diamondsThisEpisode = 0;

    // Mining pattern state
    this.miningDirection = 0; // 0=north, 1=east, 2=south, 3=west
    this.stripMineLength = 0;
    this.branchCount = 0;
    this.currentStrategy = "descend"; // descend, strip_mine, explore_cave

    // Cave detection
    this.inCave = false;
    this.caveEntrancePos = null;

    // Dangerous blocks
    this.dangerousBlocks = new Set([
      "lava",
      "flowing_lava",
      "fire",
      "cactus",
      "magma_block",
      "sweet_berry_bush",
      "powder_snow",
    ]);

    // Valuable ores (priority order)
    this.oreValues = {
      diamond_ore: 100,
      deepslate_diamond_ore: 100,
      emerald_ore: 50,
      deepslate_emerald_ore: 50,
      gold_ore: 20,
      deepslate_gold_ore: 20,
      lapis_ore: 15,
      deepslate_lapis_ore: 15,
      redstone_ore: 10,
      deepslate_redstone_ore: 10,
      iron_ore: 5,
      deepslate_iron_ore: 5,
      copper_ore: 3,
      deepslate_copper_ore: 3,
      coal_ore: 1,
      deepslate_coal_ore: 1,
    };

    this.valuableOres = new Set(Object.keys(this.oreValues));
  }

  async connect() {
    if (this.isConnecting) return;

    this.isConnecting = true;
    logger.info(
      `Connecting to ${config.minecraft.host}:${config.minecraft.port}...`,
    );

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

        const timeout = setTimeout(() => {
          this.isConnecting = false;
          reject(new Error("Connection timeout"));
        }, 30000);

        this.bot.once("spawn", () => {
          clearTimeout(timeout);
          logger.success("Bot spawned!");
          this.isConnected = true;
          this.isConnecting = false;
          this.spawnPosition = this.bot.entity.position.clone();
          this.loadPlugins();
          this.setupEventHandlers();
          resolve();
        });

        this.bot.once("error", (err) => {
          clearTimeout(timeout);
          this.isConnecting = false;
          reject(err);
        });

        this.bot.once("kicked", (reason) => {
          clearTimeout(timeout);
          this.isConnecting = false;
          reject(new Error(`Kicked: ${reason}`));
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
      const movements = new Movements(this.bot);
      movements.canDig = true;
      movements.allow1by1towers = false;
      this.bot.pathfinder.setMovements(movements);
      logger.info("Pathfinder loaded");
    } catch (err) {}
  }

  setupEventHandlers() {
    this.bot.on("health", () => {
      if (this.bot.health <= 0) {
        this.episodeRunning = false;
      }
    });

    this.bot.on("death", () => {
      logger.warn("Bot died!");
      this.episodeRunning = false;
    });

    this.bot.on("end", () => {
      this.isConnected = false;
    });
  }

  // ===== BLOCK UTILITIES =====

  isBlockExposed(blockPos) {
    const dirs = [
      [1, 0, 0],
      [-1, 0, 0],
      [0, 1, 0],
      [0, -1, 0],
      [0, 0, 1],
      [0, 0, -1],
    ];
    for (const [dx, dy, dz] of dirs) {
      const adj = this.bot.blockAt(blockPos.offset(dx, dy, dz));
      if (!adj || adj.name === "air" || adj.name === "cave_air") {
        return true;
      }
    }
    return false;
  }

  wouldReleaseLava(blockPos) {
    const dirs = [
      [1, 0, 0],
      [-1, 0, 0],
      [0, 1, 0],
      [0, -1, 0],
      [0, 0, 1],
      [0, 0, -1],
    ];
    for (const [dx, dy, dz] of dirs) {
      const adj = this.bot.blockAt(blockPos.offset(dx, dy, dz));
      if (adj && (adj.name === "lava" || adj.name === "flowing_lava")) {
        return true;
      }
    }
    return false;
  }

  /**
   * Scan for danger in a radius around the bot
   * Returns: { dangerNearby, lavaDistance, fallRisk, dangerType }
   */
  scanForDanger(radius = 3) {
    try {
      const pos = this.bot.entity.position;
      let closestLava = 100;
      let dangerType = null;

      for (let x = -radius; x <= radius; x++) {
        for (let y = -radius; y <= radius; y++) {
          for (let z = -radius; z <= radius; z++) {
            const block = this.bot.blockAt(pos.offset(x, y, z));
            if (block && this.dangerousBlocks.has(block.name)) {
              const dist = Math.sqrt(x * x + y * y + z * z);
              if (dist < closestLava) {
                closestLava = dist;
                dangerType = block.name;
              }
            }
          }
        }
      }

      const fallRisk = this.checkForFall();

      return {
        dangerNearby: closestLava < 4 || fallRisk,
        lavaDistance: closestLava,
        fallRisk: fallRisk,
        dangerType: dangerType,
      };
    } catch (err) {
      return {
        dangerNearby: false,
        lavaDistance: 100,
        fallRisk: false,
        dangerType: null,
      };
    }
  }

  /**
   * Check if there's a dangerous fall below the bot
   */
  checkForFall() {
    try {
      const pos = this.bot.entity.position;
      let airBelow = 0;

      // Check blocks directly below
      for (let y = 1; y <= 5; y++) {
        const block = this.bot.blockAt(pos.offset(0, -y, 0));
        if (!block || block.name === "air" || block.name === "cave_air") {
          airBelow++;
        } else if (block.name === "lava" || block.name === "flowing_lava") {
          return true; // Lava below is very dangerous
        } else {
          break; // Found solid ground
        }
      }

      return airBelow >= 4; // 4+ block fall is dangerous
    } catch (err) {
      return false;
    }
  }

  isInCave() {
    try {
      const pos = this.bot.entity.position;
      let airCount = 0;
      let stoneCount = 0;

      // Check surrounding blocks
      for (let x = -3; x <= 3; x++) {
        for (let y = -2; y <= 3; y++) {
          for (let z = -3; z <= 3; z++) {
            const block = this.bot.blockAt(pos.offset(x, y, z));
            if (!block || block.name === "air" || block.name === "cave_air") {
              airCount++;
            } else if (
              block.name.includes("stone") ||
              block.name.includes("deepslate")
            ) {
              stoneCount++;
            }
          }
        }
      }

      // In a cave if lots of air space surrounded by stone
      return airCount > 50 && stoneCount > 30;
    } catch (err) {
      return false;
    }
  }

  findCaveEntrance(maxDist = 10) {
    try {
      const pos = this.bot.entity.position;

      // Look for large air pockets (caves)
      for (let x = -maxDist; x <= maxDist; x++) {
        for (let y = -maxDist; y <= 2; y++) {
          // Prefer downward caves
          for (let z = -maxDist; z <= maxDist; z++) {
            const block = this.bot.blockAt(pos.offset(x, y, z));
            if (block && (block.name === "air" || block.name === "cave_air")) {
              // Check if this is a cave (has stone around it)
              let stoneNearby = 0;
              for (const [dx, dy, dz] of [
                [1, 0, 0],
                [-1, 0, 0],
                [0, 1, 0],
                [0, -1, 0],
                [0, 0, 1],
                [0, 0, -1],
              ]) {
                const adj = this.bot.blockAt(
                  pos.offset(x + dx, y + dy, z + dz),
                );
                if (
                  adj &&
                  (adj.name.includes("stone") || adj.name.includes("deepslate"))
                ) {
                  stoneNearby++;
                }
              }
              if (stoneNearby >= 3) {
                return pos.offset(x, y, z);
              }
            }
          }
        }
      }
      return null;
    } catch (err) {
      return null;
    }
  }

  findNearestVisibleOre(maxDistance = 6) {
    try {
      const pos = this.bot.entity.position;
      let bestOre = null;
      let bestScore = -1;

      for (let x = -maxDistance; x <= maxDistance; x++) {
        for (let y = -maxDistance; y <= maxDistance; y++) {
          for (let z = -maxDistance; z <= maxDistance; z++) {
            const blockPos = pos.offset(x, y, z);
            const block = this.bot.blockAt(blockPos);

            if (block && this.valuableOres.has(block.name)) {
              if (this.isBlockExposed(blockPos)) {
                const dist = Math.sqrt(x * x + y * y + z * z);
                const value = this.oreValues[block.name] || 1;
                const score = value / (dist + 1); // Prioritize close, high-value ores

                if (score > bestScore) {
                  bestScore = score;
                  bestOre = block;
                }
              }
            }
          }
        }
      }
      return bestOre;
    } catch (err) {
      return null;
    }
  }

  getVisibleOres() {
    try {
      const ores = [];
      const pos = this.bot.entity.position;
      const radius = 6;

      for (let x = -radius; x <= radius; x++) {
        for (let y = -radius; y <= radius; y++) {
          for (let z = -radius; z <= radius; z++) {
            const blockPos = pos.offset(x, y, z);
            const block = this.bot.blockAt(blockPos);

            if (
              block &&
              this.valuableOres.has(block.name) &&
              this.isBlockExposed(blockPos)
            ) {
              ores.push({
                name: block.name,
                position: blockPos,
                distance: Math.sqrt(x * x + y * y + z * z),
                value: this.oreValues[block.name] || 1,
              });
            }
          }
        }
      }

      ores.sort((a, b) => b.value - a.value);
      return ores;
    } catch (err) {
      return [];
    }
  }

  // ===== OBSERVATIONS =====

  getObservation() {
    if (!this.bot || !this.isConnected) return null;

    try {
      const pos = this.bot.entity.position;
      const visibleOres = this.getVisibleOres();
      const inCave = this.isInCave();
      const dangerInfo = this.scanForDanger(4); // Use enhanced danger scanning

      return {
        position: { x: pos.x, y: pos.y, z: pos.z },
        health: this.bot.health || 20,
        food: this.bot.food || 20,
        yaw: this.bot.entity.yaw || 0,
        pitch: this.bot.entity.pitch || 0,
        onGround: this.bot.entity.onGround,
        inventory: this.getInventoryState(),
        visibleOres: visibleOres,
        nearbyBlocks: this.getNearbyBlocks(),
        stepCount: this.stepCount,
        visitedCount: this.visitedBlocks.size,
        diamondsThisEpisode: this.diamondsThisEpisode,
        minedOresCount: this.minedOres.size,
        isStuck: this.stuckCounter > 10,

        // Cave and mining info
        inCave: inCave,
        currentStrategy: this.currentStrategy,
        miningDirection: this.miningDirection,
        stripMineLength: this.stripMineLength,

        // Enhanced danger detection
        dangerNearby: dangerInfo.dangerNearby,
        lavaDistance: dangerInfo.lavaDistance,
        fallRisk: dangerInfo.fallRisk,
        dangerType: dangerInfo.dangerType,
        diamondNearby: visibleOres.some((o) => o.name.includes("diamond")),

        // Y-level info
        atDiamondLevel: pos.y >= -64 && pos.y <= -50,
        atOptimalY: pos.y >= -59 && pos.y <= -54,
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
      const pos = this.bot.entity.position;
      const radius = 4;

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

  // ===== ACTIONS =====

  async executeAction(action) {
    if (!this.bot || !this.isConnected) {
      return { success: false, error: "Not connected" };
    }

    this.stepCount++;

    // Track position
    try {
      const pos = this.bot.entity.position;
      const key = `${Math.floor(pos.x)},${Math.floor(pos.y)},${Math.floor(pos.z)}`;
      this.visitedBlocks.add(key);

      if (this.lastPosition) {
        const dist = pos.distanceTo(this.lastPosition);
        this.stuckCounter = dist < 0.1 ? this.stuckCounter + 1 : 0;
      }
      this.lastPosition = pos.clone();
    } catch (err) {}

    try {
      switch (action.type) {
        // Basic movement
        case "forward":
          await this.actionMove("forward", 2);
          break;
        case "back":
          await this.actionMove("back", 2);
          break;
        case "left":
          await this.actionMove("left", 2);
          break;
        case "right":
          await this.actionMove("right", 2);
          break;
        case "jump":
          await this.actionJump();
          break;
        case "forward_jump":
          await this.actionForwardJump();
          break;
        case "sprint_forward":
          await this.actionSprintForward();
          break;

        // Looking
        case "look_down":
          await this.actionLook(0, 0.4);
          break;
        case "look_up":
          await this.actionLook(0, -0.4);
          break;
        case "look_left":
          await this.actionLook(-0.5, 0);
          break;
        case "look_right":
          await this.actionLook(0.5, 0);
          break;

        // Basic mining
        case "dig_forward":
          await this.actionDigForward();
          break;
        case "dig_down":
          await this.actionDigDown();
          break;
        case "safe_dig_down":
          await this.actionSafeDigDown();
          break;

        // Advanced mining patterns
        case "tunnel_forward":
          await this.actionTunnelForward();
          break;
        case "strip_mine":
          await this.actionStripMine();
          break;
        case "branch_mine":
          await this.actionBranchMine();
          break;
        case "mine_ore":
          await this.actionMineNearestOre();
          break;
        case "mine_diamond":
          await this.actionMineDiamond();
          break;

        // Exploration
        case "explore_cave":
          await this.actionExploreCave();
          break;
        case "descend":
          await this.actionDescend();
          break;
        case "find_cave":
          await this.actionFindCave();
          break;

        // Strategy
        case "switch_direction":
          await this.actionSwitchDirection();
          break;

        case "noop":
          await this.sleep(50);
          break;
        default:
          return { success: false, error: `Unknown: ${action.type}` };
      }
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  // Basic actions
  async actionMove(dir, duration) {
    this.bot.setControlState(dir, true);
    await this.sleep(duration * 100);
    this.bot.setControlState(dir, false);
  }

  async actionJump() {
    this.bot.setControlState("jump", true);
    await this.sleep(150);
    this.bot.setControlState("jump", false);
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

  async actionLook(yaw, pitch) {
    await this.bot.look(
      this.bot.entity.yaw + yaw,
      this.bot.entity.pitch + pitch,
      false,
    );
  }

  // Mining actions
  async actionDigForward() {
    try {
      const pos = this.bot.entity.position;
      const yaw = this.bot.entity.yaw;
      const dx = -Math.sin(yaw);
      const dz = Math.cos(yaw);

      const block = this.bot.blockAt(pos.offset(dx, 0, dz));
      if (block && block.name !== "air" && block.name !== "bedrock") {
        if (this.wouldReleaseLava(block.position)) {
          logger.warn("Lava ahead!");
          return;
        }
        await this.bot.dig(block);
        await this.checkMinedOre(block);
      }
    } catch (err) {}
  }

  async actionDigDown() {
    try {
      const pos = this.bot.entity.position;
      const block = this.bot.blockAt(pos.offset(0, -1, 0));
      if (block && block.name !== "air" && block.name !== "bedrock") {
        await this.bot.dig(block);
        await this.checkMinedOre(block);
      }
    } catch (err) {}
  }

  async actionSafeDigDown() {
    try {
      const pos = this.bot.entity.position;
      const block = this.bot.blockAt(pos.offset(0, -1, 0));

      if (!block || block.name === "air" || block.name === "bedrock") return;
      if (this.wouldReleaseLava(block.position)) {
        logger.warn("Lava detected! Not digging down.");
        return;
      }

      await this.bot.dig(block);
      await this.checkMinedOre(block);
    } catch (err) {}
  }

  /**
   * Tunnel forward - dig 2-high passage with lava check
   */
  async actionTunnelForward() {
    try {
      const pos = this.bot.entity.position;
      const yaw = this.bot.entity.yaw;
      const dx = -Math.sin(yaw);
      const dz = Math.cos(yaw);

      const block1 = this.bot.blockAt(pos.offset(dx, 0, dz));
      const block2 = this.bot.blockAt(pos.offset(dx, 1, dz));

      // Check for lava
      if (
        (block1 && this.wouldReleaseLava(block1.position)) ||
        (block2 && this.wouldReleaseLava(block2.position))
      ) {
        logger.warn("Danger ahead! Stopping.");
        return;
      }

      // Dig lower
      if (block1 && block1.name !== "air" && block1.name !== "bedrock") {
        await this.bot.dig(block1);
        await this.checkMinedOre(block1);
      }

      // Dig upper
      if (block2 && block2.name !== "air" && block2.name !== "bedrock") {
        await this.bot.dig(block2);
        await this.checkMinedOre(block2);
      }

      // Move forward
      this.bot.setControlState("forward", true);
      await this.sleep(200);
      this.bot.setControlState("forward", false);

      this.stripMineLength++;
    } catch (err) {}
  }

  /**
   * Strip Mining Pattern - single step with ore priority
   * Best at Y=-59 for diamonds
   */
  async actionStripMine() {
    try {
      this.currentStrategy = "strip_mine";

      // Single tunnel step
      await this.actionTunnelForward();
      this.stripMineLength++;

      // Check for diamond ore first
      const visibleOres = this.getVisibleOres();
      if (visibleOres.length > 0) {
        const bestOre = visibleOres[0];
        if (bestOre.name.includes("diamond")) {
          await this.actionMineDiamond();
        } else if (bestOre.value >= 10) {
          await this.actionMineNearestOre();
        }
      }
    } catch (err) {}
  }

  /**
   * Branch Mining Pattern - simplified to one step per call
   * Optimal: branches every 3 blocks
   */
  async actionBranchMine() {
    try {
      this.currentStrategy = "strip_mine";

      // Single tunnel step
      await this.actionTunnelForward();
      this.branchCount++;

      // Every 6 steps, look for side ores (don't dig full branches - too slow)
      if (this.branchCount % 6 === 0) {
        const originalYaw = this.bot.entity.yaw;

        // Quick look left for ores
        await this.bot.look(originalYaw - Math.PI / 2, 0, false);
        await this.sleep(50);
        const leftOre = this.findNearestVisibleOre(3);
        if (leftOre && leftOre.name.includes("diamond")) {
          await this.actionMineDiamond();
        }

        // Quick look right for ores
        await this.bot.look(originalYaw + Math.PI / 2, 0, false);
        await this.sleep(50);
        const rightOre = this.findNearestVisibleOre(3);
        if (rightOre && rightOre.name.includes("diamond")) {
          await this.actionMineDiamond();
        }

        // Return to forward
        await this.bot.look(originalYaw, 0, false);
      }
    } catch (err) {}
  }

  async actionMineNearestOre() {
    try {
      const ore = this.findNearestVisibleOre(5);
      if (ore) {
        const dist = ore.position.distanceTo(this.bot.entity.position);
        logger.info(`Found visible ${ore.name} at ${dist.toFixed(1)}`);

        if (dist <= 4.5) {
          if (this.wouldReleaseLava(ore.position)) {
            logger.warn("Lava near ore!");
            return;
          }
          await this.bot.lookAt(ore.position);
          await this.sleep(100);
          await this.bot.dig(ore);
          await this.checkMinedOre(ore);
        } else {
          await this.bot.lookAt(ore.position);
          this.bot.setControlState("forward", true);
          await this.sleep(300);
          this.bot.setControlState("forward", false);
        }
      }
    } catch (err) {}
  }

  /**
   * Mine diamond ore specifically - ignores other ores
   */
  async actionMineDiamond() {
    try {
      const pos = this.bot.entity.position;
      let closestDiamond = null;
      let closestDist = 100;

      // Find closest diamond ore
      for (let x = -6; x <= 6; x++) {
        for (let y = -6; y <= 6; y++) {
          for (let z = -6; z <= 6; z++) {
            const blockPos = pos.offset(x, y, z);
            const block = this.bot.blockAt(blockPos);

            if (
              block &&
              (block.name === "diamond_ore" ||
                block.name === "deepslate_diamond_ore")
            ) {
              if (this.isBlockExposed(blockPos)) {
                const dist = Math.sqrt(x * x + y * y + z * z);
                if (dist < closestDist) {
                  closestDist = dist;
                  closestDiamond = block;
                }
              }
            }
          }
        }
      }

      if (closestDiamond) {
        logger.success(`💎 DIAMOND ORE at distance ${closestDist.toFixed(1)}!`);

        if (closestDist <= 4.5) {
          if (this.wouldReleaseLava(closestDiamond.position)) {
            logger.warn("Lava near diamond! Mining anyway...");
          }
          await this.bot.lookAt(closestDiamond.position);
          await this.sleep(100);
          await this.bot.dig(closestDiamond);
          await this.checkMinedOre(closestDiamond);
          this.diamondsThisEpisode++;
          logger.success("💎 DIAMOND MINED!");
        } else {
          // Move toward diamond
          await this.bot.lookAt(closestDiamond.position);
          this.bot.setControlState("forward", true);
          await this.sleep(400);
          this.bot.setControlState("forward", false);
        }
      }
    } catch (err) {}
  }

  /**
   * Descend to diamond level safely - optimized for speed
   */
  async actionDescend() {
    try {
      const pos = this.bot.entity.position;
      this.currentStrategy = "descend";

      // If at diamond level (-50 or below), switch to strip mining
      if (pos.y <= -50) {
        this.currentStrategy = "strip_mine";
        await this.actionStripMine();
        return;
      }

      // If close to diamond level, start horizontal mining
      if (pos.y <= -40) {
        await this.actionTunnelForward();
        return;
      }

      // Staircase pattern down
      const yaw = this.bot.entity.yaw;
      const dx = -Math.sin(yaw);
      const dz = Math.cos(yaw);

      // Dig step down
      const blockAhead = this.bot.blockAt(pos.offset(dx, 0, dz));
      const blockBelow = this.bot.blockAt(pos.offset(dx, -1, dz));

      if (blockBelow && this.wouldReleaseLava(blockBelow.position)) {
        // Turn and try different direction
        await this.actionSwitchDirection();
        return;
      }

      if (blockAhead && blockAhead.name !== "air") {
        await this.bot.dig(blockAhead);
      }
      if (
        blockBelow &&
        blockBelow.name !== "air" &&
        blockBelow.name !== "bedrock"
      ) {
        await this.bot.dig(blockBelow);
      }

      // Move forward and down
      this.bot.setControlState("forward", true);
      await this.sleep(300);
      this.bot.setControlState("forward", false);
    } catch (err) {}
  }

  /**
   * Find and enter a cave
   */
  async actionFindCave() {
    try {
      const cave = this.findCaveEntrance(12);
      if (cave) {
        logger.info(
          `Found cave entrance at ${cave.x.toFixed(0)}, ${cave.y.toFixed(0)}, ${cave.z.toFixed(0)}`,
        );
        this.caveEntrancePos = cave;
        await this.bot.lookAt(cave);
        this.bot.setControlState("forward", true);
        await this.sleep(500);
        this.bot.setControlState("forward", false);
      } else {
        // No cave, keep descending
        await this.actionDescend();
      }
    } catch (err) {}
  }

  /**
   * Explore cave system
   */
  async actionExploreCave() {
    try {
      this.currentStrategy = "explore_cave";
      this.inCave = this.isInCave();

      if (!this.inCave) {
        // Not in cave, try to find one
        await this.actionFindCave();
        return;
      }

      // In cave - look for ores first
      const ores = this.getVisibleOres();
      if (ores.length > 0) {
        await this.actionMineNearestOre();
        return;
      }

      // Explore cave - move towards air spaces while checking for ores
      const pos = this.bot.entity.position;

      // Prefer going deeper
      const downBlock = this.bot.blockAt(pos.offset(0, -1, 0));
      if (
        !downBlock ||
        downBlock.name === "air" ||
        downBlock.name === "cave_air"
      ) {
        // Can go down
        await this.actionMove("forward", 1);
      } else {
        // Follow the cave
        await this.actionMove("forward", 2);
      }

      // Look around for ores
      await this.actionLook(0.3, 0);
    } catch (err) {}
  }

  async actionSwitchDirection() {
    this.miningDirection = (this.miningDirection + 1) % 4;
    const angles = [0, Math.PI / 2, Math.PI, -Math.PI / 2];
    await this.bot.look(angles[this.miningDirection], 0, false);
    this.stripMineLength = 0;
  }

  async checkMinedOre(block) {
    if (this.valuableOres.has(block.name)) {
      const key = `${block.position.x},${block.position.y},${block.position.z}`;
      if (!this.minedOres.has(key)) {
        this.minedOres.add(key);
        logger.success(`Mined ${block.name}!`);

        if (block.name.includes("diamond")) {
          this.diamondsThisEpisode++;
          logger.success("💎 DIAMOND ORE MINED! 💎");
        }
      }
    }
  }

  // ===== REWARDS =====

  calculateReward() {
    if (!this.bot || !this.isConnected) return 0;

    let reward = -0.001;

    try {
      // Diamond mined this episode!
      if (this.diamondsThisEpisode > 0) {
        reward += 1000;
        this.episodeRunning = false;
        logger.success("💎 SUCCESS! Diamond obtained! 💎");
        return reward;
      }

      const pos = this.bot.entity.position;
      const y = pos.y;

      // Y-level rewards
      if (y <= -50 && y >= -64) {
        reward += 0.05; // At diamond level
        if (y >= -59 && y <= -54) {
          reward += 0.1; // Optimal Y
        }
      } else if (y < 16) {
        reward += (0.01 * (16 - y)) / 80;
      }

      // Cave exploration bonus
      if (this.isInCave() && y <= 0) {
        reward += 0.02;
      }

      // Visible ore rewards
      const ores = this.getVisibleOres();
      for (const ore of ores) {
        if (ore.name.includes("diamond")) {
          reward += 10;
        } else if (ore.value >= 10) {
          reward += 1;
        }
      }

      // Exploration
      const key = `${Math.floor(pos.x)},${Math.floor(pos.y)},${Math.floor(pos.z)}`;
      if (!this.visitedBlocks.has(key)) {
        reward += 0.02;
      }

      // Strip mining at correct level
      if (this.currentStrategy === "strip_mine" && y >= -60 && y <= -50) {
        reward += 0.01;
      }

      // Penalties
      if (this.stuckCounter > 20) reward -= 0.2;
      if (this.bot.health <= 0) {
        reward -= 100;
        this.episodeRunning = false;
      }
      if (this.bot.health < 20) {
        reward -= (20 - this.bot.health) * 0.05;
      }
    } catch (err) {}

    this.totalReward += reward;
    return reward;
  }

  // ===== EPISODE =====

  async reset() {
    logger.info("Resetting episode...");

    this.stepCount = 0;
    this.totalReward = 0;
    this.visitedBlocks.clear();
    this.minedOres.clear();
    this.stuckCounter = 0;
    this.lastPosition = null;
    this.episodeRunning = true;
    this.diamondsThisEpisode = 0;
    this.miningDirection = Math.floor(Math.random() * 4);
    this.stripMineLength = 0;
    this.branchCount = 0;
    this.currentStrategy = "descend";
    this.inCave = false;

    if (this.bot && this.isConnected) {
      try {
        // Stop movement
        ["forward", "back", "left", "right", "jump", "sprint"].forEach((s) =>
          this.bot.setControlState(s, false),
        );

        // Reset player
        this.bot.chat("/clear");
        await this.sleep(100);
        this.bot.chat("/give @s iron_pickaxe");
        await this.sleep(100);

        if (this.spawnPosition) {
          const sp = this.spawnPosition;
          this.bot.chat(
            `/tp @s ${Math.floor(sp.x)} ${Math.floor(sp.y)} ${Math.floor(sp.z)}`,
          );
          await this.sleep(200);
        }

        this.bot.chat("/effect give @s instant_health 1 10");
        this.bot.chat("/effect give @s saturation 1 10");
        await this.sleep(100);
      } catch (err) {}
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
        minedOres: this.minedOres.size,
        diamondsThisEpisode: this.diamondsThisEpisode,
        strategy: this.currentStrategy,
        inCave: this.inCave,
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
