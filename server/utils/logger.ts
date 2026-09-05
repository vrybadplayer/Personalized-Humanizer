import { ParsedPipelineError } from '../../src/types/index.js';

export class Logger {
  public static info(msg: string) {
    const timestamp = new Date().toISOString();
    console.log(`\x1b[36m[INFO]\x1b[0m \x1b[90m${timestamp}\x1b[0m ${msg}`);
  }

  public static warn(msg: string) {
    const timestamp = new Date().toISOString();
    console.warn(`\x1b[33m[WARN]\x1b[0m \x1b[90m${timestamp}\x1b[0m ${msg}`);
  }

  public static error(msg: string, err?: any) {
    const timestamp = new Date().toISOString();
    console.error(`\x1b[31m[ERROR]\x1b[0m \x1b[90m${timestamp}\x1b[0m ${msg}`, err ? err : '');
  }

  public static logPipelineStart(model: string, stage: string) {
    console.log(`\n\x1b[36m====================== [PIPELINE STARTED] ======================\x1b[0m`);
    console.log(`\x1b[90mTimestamp:\x1b[0m ${new Date().toISOString()}`);
    console.log(`\x1b[90mModel    :\x1b[0m \x1b[1m${model}\x1b[0m`);
    console.log(`\x1b[90mStage    :\x1b[0m ${stage}`);
    console.log(`\x1b[36m================================================================\x1b[0m\n`);
  }

  public static logPipelineStage(step: number, total: number, stage: string, details: string) {
    console.log(`\x1b[32m[STAGE ${step}/${total}]\x1b[0m \x1b[1m${stage}\x1b[0m - \x1b[90m${details}\x1b[0m`);
  }

  public static logPipelineError(parsedError: ParsedPipelineError) {
    console.error(`\n\x1b[41m\x1b[37m ====================== [PIPELINE ERROR LOG] ====================== \x1b[0m`);
    console.error(`\x1b[1m\x1b[31mTitle    :\x1b[0m \x1b[1m${parsedError.title}\x1b[0m (\x1b[33m${parsedError.code}\x1b[0m)`);
    console.error(`\x1b[90mTimestamp:\x1b[0m ${parsedError.timestamp}`);
    console.error(`\x1b[90mCategory :\x1b[0m ${parsedError.category}`);
    if (parsedError.script) {
      console.error(`\x1b[90mScript   :\x1b[0m ${parsedError.script}`);
    }
    if (parsedError.stage) {
      console.error(`\x1b[90mStage    :\x1b[0m ${parsedError.stage}`);
    }
    if (parsedError.lineInfo) {
      console.error(`\x1b[90mLocation :\x1b[0m ${parsedError.lineInfo}`);
    }
    console.error(`\x1b[90mUser Msg :\x1b[0m \x1b[36m${parsedError.userMessage}\x1b[0m`);

    if (parsedError.recoverySteps && parsedError.recoverySteps.length > 0) {
      console.error(`\x1b[90mActionable Troubleshooting Steps:\x1b[0m`);
      parsedError.recoverySteps.forEach((step, idx) => {
        console.error(`  \x1b[32m${idx + 1}.\x1b[0m ${step}`);
      });
    }

    if (parsedError.rawStderr) {
      console.error(`\x1b[90m------------------- RAW DEVELOPER TRACEBACK -------------------\x1b[0m`);
      console.error(`\x1b[31m${parsedError.rawStderr.trim()}\x1b[0m`);
      console.error(`\x1b[90m---------------------------------------------------------------\x1b[0m`);
    }
    console.error(`\x1b[41m\x1b[37m ================================================================== \x1b[0m\n`);
  }
}
