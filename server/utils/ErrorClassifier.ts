import { ParsedPipelineError } from '../../src/types/index.js';

export class ErrorClassifier {
  /**
   * Classifies raw stderr or error messages from pipeline scripts into an enterprise-grade
   * structured ParsedPipelineError object.
   */
  public static classify(
    rawError: string,
    scriptPath?: string,
    stageName?: string,
    configuredModel?: string
  ): ParsedPipelineError {
    const rawStr = typeof rawError === 'string' ? rawError : String(rawError || '');
    const timestamp = new Date().toISOString();

    // Try extracting line number / function from traceback
    let lineInfo = '';
    const lineMatch = rawStr.match(/File "([^"]+)", line (\d+)(?:, in (\w+))?/);
    if (lineMatch) {
      const lineNum = lineMatch[2];
      const funcName = lineMatch[3] ? ` in ${lineMatch[3]}` : '';
      lineInfo = `line ${lineNum}${funcName}`;
    }

    // 1. Ollama Model Not Found
    // Matches e.g. "ResponseError: model 'llama3.2:3bawda' not found" or "model "..." not found"
    const modelNotFoundMatch = rawStr.match(/model ['"]([^'"]+)['"] not found/i) ||
      rawStr.match(/ResponseError:.*model ['"]?([^'"]+?)['"]? not found/i);

    if (modelNotFoundMatch || rawStr.includes('ResponseError') && rawStr.includes('not found')) {
      const missingModel = modelNotFoundMatch ? modelNotFoundMatch[1] : (configuredModel || 'specified');
      return {
        code: 'OLLAMA_MODEL_NOT_FOUND',
        title: `Ollama Model '${missingModel}' Not Found`,
        category: 'AI Model Configuration',
        userMessage: `The configured Ollama model '${missingModel}' is not installed or available on your Ollama server instance.`,
        recoverySteps: [
          `Open Settings (Gear Icon) to verify or update your OLLAMA_MODEL name (e.g. 'llama3.2:3b').`,
          `Run 'ollama pull ${missingModel}' in your local terminal to download the missing model weights.`,
          `Verify your local Ollama server is active and responding.`
        ],
        script: scriptPath,
        stage: stageName,
        lineInfo,
        technicalDetails: `Ollama ResponseError: model '${missingModel}' not found on endpoint http://localhost:11434`,
        rawStderr: rawStr,
        timestamp
      };
    }

    // 2. Ollama Connection Refused / Server Offline
    if (
      rawStr.includes('ConnectionRefusedError') ||
      rawStr.includes('ECONNREFUSED') ||
      rawStr.includes('Failed to connect') ||
      rawStr.includes('httpx.ConnectError') ||
      rawStr.includes('Connection refused') ||
      rawStr.includes('Failed to establish a new connection')
    ) {
      return {
        code: 'OLLAMA_CONNECTION_REFUSED',
        title: 'Ollama Service Connection Refused',
        category: 'Service Connection Failure',
        userMessage: 'Unable to reach the local Ollama service at http://localhost:11434. The Ollama background process appears to be offline.',
        recoverySteps: [
          'Ensure the Ollama application is launched on your desktop or machine.',
          'Start the service manually by executing "ollama serve" in your terminal.',
          'Confirm no local firewall, security software, or proxy is blocking port 11434.'
        ],
        script: scriptPath,
        stage: stageName,
        lineInfo,
        technicalDetails: 'HTTP Connection Refused to http://localhost:11434',
        rawStderr: rawStr,
        timestamp
      };
    }

    // 3. Empty Corpus / No Raw Data Uploaded
    if (
      rawStr.toLowerCase().includes('no raw files found') ||
      rawStr.toLowerCase().includes('no valid text extracted') ||
      rawStr.toLowerCase().includes('no corpus files') ||
      rawStr.toLowerCase().includes('corpus is empty') ||
      rawStr.toLowerCase().includes('data/raw is empty')
    ) {
      return {
        code: 'EMPTY_CORPUS_DATA',
        title: 'No Writing Samples Available',
        category: 'Input Data Required',
        userMessage: 'The pipeline could not find any text corpus in data/raw to analyze your writing stylometry.',
        recoverySteps: [
          'Upload .txt, .docx, or .pdf handwriting or essay samples using the upload dropzone.',
          'Alternatively, paste a text sample directly in the "Paste Text Sample" box.',
          'Ensure uploaded documents contain extractable plain text.'
        ],
        script: scriptPath,
        stage: stageName,
        lineInfo,
        technicalDetails: 'Data directory data/raw contains no valid source documents.',
        rawStderr: rawStr,
        timestamp
      };
    }

    // 4. Missing Python Module / Dependency / spaCy Model
    if (
      rawStr.includes('ModuleNotFoundError') ||
      rawStr.includes('ImportError') ||
      rawStr.includes('No module named') ||
      rawStr.includes('en_core_web_md')
    ) {
      const moduleMatch = rawStr.match(/No module named ['"]([^'"]+)['"]/i) || rawStr.match(/ModuleNotFoundError: (.*)/i);
      const missingName = moduleMatch ? moduleMatch[1] : 'required dependency';
      return {
        code: 'PYTHON_ENV_DEPENDENCY_MISSING',
        title: `Python Dependency Missing (${missingName})`,
        category: 'Python Environment',
        userMessage: `A required Python package or NLP model (${missingName}) was not found in the python runtime environment.`,
        recoverySteps: [
          'Run "python3.11 backend/setup_orchestrator.py" to initialize the dedicated virtual environment.',
          'Or run "pip install -r backend/requirements.txt" and "python -m spacy download en_core_web_md".',
          'Check that Python 3.11 is properly installed on your machine.'
        ],
        script: scriptPath,
        stage: stageName,
        lineInfo,
        technicalDetails: `Python Module/Model Missing: ${missingName}`,
        rawStderr: rawStr,
        timestamp
      };
    }

    // 5. File Not Found / Path Errors
    if (rawStr.includes('FileNotFoundError') || rawStr.includes('No such file or directory')) {
      return {
        code: 'FILE_NOT_FOUND',
        title: 'Required Workspace File Missing',
        category: 'File System Error',
        userMessage: 'A required pipeline intermediate file or directory was missing during execution.',
        recoverySteps: [
          'Re-run the pipeline from Step 1 (Environment & Ingestion).',
          'Ensure workspace folders data/raw, data/clean, data/profiles, data/output have write permissions.',
          'Use the "Reset Memory" option in the header if state files are corrupted.'
        ],
        script: scriptPath,
        stage: stageName,
        lineInfo,
        technicalDetails: 'FileNotFoundError raised during python execution.',
        rawStderr: rawStr,
        timestamp
      };
    }

    // 6. Generic Python Script Execution Error
    const scriptNameOnly = scriptPath ? scriptPath.split('/').pop() : 'Pipeline Script';
    return {
      code: 'SCRIPT_EXECUTION_FAILURE',
      title: `${scriptNameOnly} Execution Error`,
      category: 'Pipeline Processing Error',
      userMessage: `An unexpected error occurred while executing ${scriptNameOnly}${lineInfo ? ` (${lineInfo})` : ''}.`,
      recoverySteps: [
        'Inspect the expandable "Developer Stack Trace" below for precise line numbers and traceback details.',
        'Review settings in the Settings panel to confirm valid generation parameters.',
        'Check backend console logs for additional environment diagnostics.'
      ],
      script: scriptPath,
      stage: stageName,
      lineInfo,
      technicalDetails: rawStr.slice(0, 300) + (rawStr.length > 300 ? '...' : ''),
      rawStderr: rawStr,
      timestamp
    };
  }
}
