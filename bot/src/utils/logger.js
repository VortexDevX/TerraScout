/**
 * Terra Scout Bot Logger
 */

const LOG_LEVELS = {
  debug: 0,
  info: 1,
  warn: 2,
  error: 3,
};

const currentLevel = LOG_LEVELS[process.env.LOG_LEVEL || "info"];

const colors = {
  reset: "\x1b[0m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
  gray: "\x1b[90m",
};

function timestamp() {
  return new Date().toISOString().substr(11, 8);
}

const logger = {
  debug: (msg, ...args) => {
    if (currentLevel <= LOG_LEVELS.debug) {
      console.log(
        `${colors.gray}[${timestamp()}] [DEBUG]${colors.reset}`,
        msg,
        ...args,
      );
    }
  },

  info: (msg, ...args) => {
    if (currentLevel <= LOG_LEVELS.info) {
      console.log(
        `${colors.cyan}[${timestamp()}] [INFO]${colors.reset}`,
        msg,
        ...args,
      );
    }
  },

  warn: (msg, ...args) => {
    if (currentLevel <= LOG_LEVELS.warn) {
      console.log(
        `${colors.yellow}[${timestamp()}] [WARN]${colors.reset}`,
        msg,
        ...args,
      );
    }
  },

  error: (msg, ...args) => {
    if (currentLevel <= LOG_LEVELS.error) {
      console.log(
        `${colors.red}[${timestamp()}] [ERROR]${colors.reset}`,
        msg,
        ...args,
      );
    }
  },

  success: (msg, ...args) => {
    console.log(
      `${colors.green}[${timestamp()}] [OK]${colors.reset}`,
      msg,
      ...args,
    );
  },

  bot: (msg, ...args) => {
    console.log(
      `${colors.magenta}[${timestamp()}] [BOT]${colors.reset}`,
      msg,
      ...args,
    );
  },
};

module.exports = logger;
