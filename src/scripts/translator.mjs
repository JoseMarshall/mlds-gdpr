import 'dotenv/config';

import * as deepl from 'deepl-node';

const translator = new deepl.Translator(process.env.DEEPL_API_KEY);

// Function to translate text
export async function translateText({ text, targetLanguage, sourceLanguage }) {
  try {
    const result = await translator.translateText(text, sourceLanguage, targetLanguage);
    return result.text;
  } catch (error) {
    console.error('Error translating text:', error.message ?? error);
  }
}

export async function translateObject(obj, targetLanguage, sourceLanguage) {
  if (typeof obj !== 'object' || Array.isArray(obj)) {
    return obj;
  }

  const result = {};
  for (const key in obj) {
    const value = obj[key];
    if (typeof value === 'object' && !Array.isArray(value)) {
      result[key] = await translateObject(value, targetLanguage, sourceLanguage);
    } else if (key === 'content' && value && typeof value === 'string') {
      result[key] = await translateText({ text: value, targetLanguage, sourceLanguage });
    } else {
      result[key] = value;
    }
  }

  return result;
}
