import { readFileSync, writeFileSync } from 'fs';
import { JSDOM } from 'jsdom';
import { resolve } from 'path';

import { uuidV4Generator } from './common.js';
import gdprDeArticles from './gdpr-de-articles.json' with { type: 'json' };
import gdprWebScraping from './gdpr-de-web-scraping.mjs';

const gdprClasses = {
  PART: 'PART',
  CHAPTER: 'CHAPTER',
  SECTION: 'SECTION',
  ARTICLE: 'ARTICLE',
  POINT: 'POINT',
  SUBPOINT: 'SUBPOINT',
  SUBSUBPOINT: 'SUBSUBPOINT',

  // For Id annotation
  TITLE: 'TITLE',
  TITLE_ID: 'TITLE_ID',
};

const gdprClassesRegexText = {
  PART: /^Teil\s*(\d+)/,
};

const gdprClassesRegexClass = {
  [gdprClasses.CHAPTER]: /^kapitel/,
  [gdprClasses.SECTION]: /^abschnitt/,
  [gdprClasses.ARTICLE]: /^artikel$/,
  [gdprClasses.POINT]: /^jurAbsatz$/,
  [gdprClasses.TITLE]: /^titel$/,
  [gdprClasses.TITLE_ID]: /^nummer$/,
};

const readingStack = [];

let articles = {};
let jsonOutput = {};
const gdprClassesPrecedence = {
  [gdprClasses.PART]: -1,
  [gdprClasses.CHAPTER]: 0,
  [gdprClasses.SECTION]: 1,
  [gdprClasses.ARTICLE]: 2,
  [gdprClasses.POINT]: 3,
  [gdprClasses.SUBPOINT]: 4,
  [gdprClasses.SUBSUBPOINT]: 5,
};

function getGdprClass(className, node) {
  if (node.classType) {
    return node.classType;
  }
  let foundClassType = Object.entries(gdprClassesRegexClass).find(([_, regex]) =>
    regex.test(className)
  );

  foundClassType ??= Object.entries(gdprClassesRegexText).find(([_, regex]) =>
    regex.test(node?.textContent?.trim())
  );

  return foundClassType?.[0];
}

function shouldPopFromStack(classType) {
  if (readingStack.length === 0) {
    return false;
  }
  const lastElement = readingStack[readingStack.length - 1];
  return gdprClassesPrecedence[classType] <= gdprClassesPrecedence[lastElement.classType];
}

// Recursive function to parse each element
async function parseElement(element) {
  const children = element.children;
  let result = {
    classType: getGdprClass(element.className, element),
    content: {},
  };

  if (!children || children.length === 0) {
    result.content = element.textContent.trim();
  } else if (result.classType === gdprClasses.ARTICLE) {
    // get the article link from the child
    const articleLink = element.querySelector('a');
    return articles[articleLink];
  }

  for (const child of Array.from(children)) {
    result.content[await (await uuidV4Generator.next()).value] = {
      classType: getGdprClass(child.className, child),
      content: child.textContent.trim(),
    };
  }

  return result;
}

async function transverseNode(node) {
  const classType = getGdprClass(node.className, node);
  node.classType = classType;
  while (shouldPopFromStack(classType)) {
    readingStack.pop();
  }

  const lastElement = readingStack[readingStack.length - 1];
  const id = await (await uuidV4Generator.next()).value;
  const parsedElement = await parseElement(node);

  if (classType in gdprClassesPrecedence) {
    readingStack.push({ id, classType, parsedElement });
  }

  if (lastElement?.id) {
    if (typeof lastElement.parsedElement.content === 'object') {
      lastElement.parsedElement.content[id] = parsedElement;
    } else {
      lastElement.parsedElement.content = {
        [await (await uuidV4Generator.next()).value]: { ...lastElement.parsedElement },
        [id]: parsedElement,
      };
    }
  } else {
    jsonOutput[id] ??= parsedElement;
  }
}

function isObJectAndNotArray(value) {
  return typeof value === 'object' && !Array.isArray(value);
}

function getValue(gdprEnPartial, key, keyIndex) {
  const values = Object.values(gdprEnPartial);
  const value = ['content', 'classType'].includes(key)
    ? (gdprEnPartial[key] ?? values[keyIndex])
    : values[keyIndex];
  return isObJectAndNotArray(value) ? value : gdprEnPartial;
}

function getLiteralValue(obj) {
  let result = null;

  function findContent(node) {
    // If 'node' is an object, check for 'content' property and go deeper if it exists
    if (isObJectAndNotArray(node)) {
      if (node.hasOwnProperty('content')) {
        findContent(node.content); // Recurse into 'content'
      } else {
        // If no 'content' key, look through all properties for nested objects
        for (let key in node) {
          if (node.hasOwnProperty(key)) {
            findContent(node[key]);
          }
        }
      }
    } else {
      return (result = node);
    }
  }

  findContent(obj);
  return result;
}

function buildId(obj) {
  if (!obj) {
    return null;
  }
  const classType = obj.classType;

  const prefix = {
    [gdprClasses.PART]: 'p_',
    [gdprClasses.CHAPTER]: 'cpt_',
    [gdprClasses.SECTION]: 'sct_',
    [gdprClasses.ARTICLE]: 'art_',
    [gdprClasses.POINT]: 'pt_',
    [gdprClasses.SUBPOINT]: 'spt_',
    [gdprClasses.SUBSUBPOINT]: 'sspt_',
  };
  const numberExtractors = {
    [gdprClasses.PART]: (obj) => {
      const match = obj.content.match(/^Teil (\d+)/);
      return match ? match[1].trim() : null;
    },
    [gdprClasses.CHAPTER]: (obj) => {
      const match = obj.content.match(/ (\d+)$/);
      return match ? match[1].trim() : null;
    },
    [gdprClasses.SECTION]: (obj) => {
      const match = obj.content.match(/ (\d+)$/);
      return match ? match[1].trim() : null;
    },
    [gdprClasses.ARTICLE]: (obj) => {
      const match = obj.content.match(/ (\d+)$/);
      return match ? match[1].trim() : null;
    },
    [gdprClasses.POINT]: (obj) => {
      return obj.number;
    },
    [gdprClasses.SUBPOINT]: (obj) => {
      return obj.number;
    },
    [gdprClasses.SUBSUBPOINT]: (obj) => {
      return obj.number.match(/(\w+)/)[1];
    },
  };

  function build(obj) {
    const extractedNumber = numberExtractors[classType](obj);
    return extractedNumber ? prefix[classType] + extractedNumber : null;
  }

  if (gdprClasses.PART === classType) {
    const iterator = Object.values(obj.content).find((value) => value.classType === 'PART');
    // console.log(iterator);
    return build(iterator ?? obj);
  } else if ([gdprClasses.CHAPTER, gdprClasses.SECTION, gdprClasses.ARTICLE].includes(classType)) {
    // Try to get the number from the content
    const iterator = Object.values(obj.content).find((value) => value.classType === 'TITLE_ID');
    return build(iterator);
  } else if (gdprClasses.POINT === classType) {
    if (typeof obj.content === 'string') {
      return build(obj);
    } else {
      const points = Object.values(obj.content).filter(
        (value) => value.classType === gdprClasses.POINT
      );
      return build(points[0]);
    }
  } else if ([gdprClasses.SUBPOINT, gdprClasses.SUBSUBPOINT].includes(classType)) {
    return build(obj);
  }
  return null;
}

function makeHumanReadableIds(gdpr, gdprCopy, parentKey = '') {
  const result = {};

  const keys = Object.keys(gdpr);
  let index = 0;
  for (const key of keys) {
    if (isObJectAndNotArray(gdpr[key])) {
      const builtKey = buildId(gdpr[key], index);
      let newKey = builtKey ? `${parentKey ? `${parentKey}.${builtKey}` : builtKey}` : key;
      const [secondLast, last] = newKey.split('.').slice(-2);
      if (secondLast === last) {
        newKey = secondLast;
      }
      result[newKey] = makeHumanReadableIds(
        gdpr[key],
        getValue(gdprCopy, key, index),
        builtKey ? newKey : parentKey
      );
    } else {
      result[key] = getLiteralValue(gdprCopy[key]);
    }
    index++;
  }

  return result;
}

async function main() {
  const gdprHtml = readFileSync(resolve('src/raw-data/gdpr-de.html'), 'utf8');
  const dom = new JSDOM('<!DOCTYPE html>' + gdprHtml);

  const htmlNodes = Array.from(dom.window.document.body.children);

  // get the articles content
  const existArticles = !!Object.keys(gdprDeArticles ?? {}).length;
  articles = existArticles ? gdprDeArticles : await gdprWebScraping();
  if (!existArticles) {
    writeFileSync(
      resolve('src/scripts/to-json/gdpr-de-articles.json'),
      JSON.stringify(articles, null, 2)
    );
  }

  for (const node of htmlNodes) {
    await transverseNode(node);
  }
  const gdprWithReadableId = makeHumanReadableIds(jsonOutput, Object.assign({}, jsonOutput));

  // output the JSON to a file
  writeFileSync(resolve('src/datasets/gdpr-de.json'), JSON.stringify(gdprWithReadableId, null, 2));

  return 'gdpr-de.json Created Successfully ✅';
}
main().then(console.log).catch(console.error);
export default main;
