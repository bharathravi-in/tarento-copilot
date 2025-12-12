// Logger utility for consistent logging across app
export type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

const LogLevelMap: Record<LogLevel, number> = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
};

class Logger {
  private logLevel: LogLevel;

  constructor(level: LogLevel = 'INFO') {
    this.logLevel = level;
  }

  setLogLevel(level: LogLevel) {
    this.logLevel = level;
  }

  private log(level: LogLevel, message: string, data?: unknown) {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level}]`;

    const levels = LogLevelMap;
    if (levels[level] >= levels[this.logLevel]) {
      if (data) {
        console.log(`${prefix}`, message, data);
      } else {
        console.log(`${prefix}`, message);
      }
    }
  }

  debug(message: string, data?: unknown) {
    this.log('DEBUG', message, data);
  }

  info(message: string, data?: unknown) {
    this.log('INFO', message, data);
  }

  warn(message: string, data?: unknown) {
    this.log('WARN', message, data);
  }

  error(message: string, data?: unknown) {
    this.log('ERROR', message, data);
  }
}

export const logger = new Logger();
