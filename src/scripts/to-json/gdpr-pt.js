const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');
const { uuidV4Generator } = require('./common');

const gdprClasses = {
  CHAPTER: 'CHAPTER',
  SECTION: 'SECTION',
  ARTICLE: 'ARTICLE',
  POINT: 'POINT',
  SUBPOINT: 'SUBPOINT',

  // For Id annotation
  TITLE: 'TITLE',
  TITLE_ID: 'TITLE_ID',
};

const gdprClassesRegexText = {
  CHAPTER: /^CAPÍTULO\s*([IVX]+)$/,
  SECTION: /^SECÇÃO\s*([IVX]+)$/,
  ARTICLE: /^Artigo\s*\d+\.º$/,
  POINT: /^(\d+)/,
};

const gdprClassesRegexClass = {
  SUBPOINT: /paragraph-normal-text/,

  // For Id annotation
  TITLE: /^paragraph-bold-center-14px$/,
  TITLE_ID: /^paragraph-center$/,
};

const readingStack = [];

let jsonOutput = {};
const gdprClassesPrecedence = {
  [gdprClasses.CHAPTER]: 0,
  [gdprClasses.SECTION]: 1,
  [gdprClasses.ARTICLE]: 2,
  [gdprClasses.POINT]: 3,
  [gdprClasses.SUBPOINT]: 4,
};

function subPointTransformer(obj) {
  if (typeof obj !== 'object' || Array.isArray(obj)) {
    return obj;
  }

  const [number, ...description] = obj.content.split(' ');

  return {
    classType: obj.classType,
    content: [number, description.join(' ')],
  };
}

const classTransformerHandlers = {
  [gdprClasses.SUBPOINT]: subPointTransformer,
};

function getGdprClass(className, node) {
  if (node.classType) {
    return node.classType;
  }

  let foundClassType = Object.entries(gdprClassesRegexText).find(([_, regex]) =>
    regex.test(node?.textContent?.trim())
  );

  foundClassType ??= Object.entries(gdprClassesRegexClass).find(([_, regex]) =>
    regex.test(className)
  );

  const lastElement = readingStack[readingStack.length - 1];

  if (foundClassType) {
    if (
      foundClassType[0] === gdprClasses.SUBPOINT &&
      lastElement?.classType === gdprClasses.ARTICLE
    ) {
      return gdprClasses.POINT;
    }
    return foundClassType[0];
  }
  return null;
}

function shouldPopFromStack(classType) {
  if (readingStack.length === 0) {
    return false;
  }
  const lastElement = readingStack[readingStack.length - 1];
  return gdprClassesPrecedence[classType] <= gdprClassesPrecedence[lastElement.classType];
}

function elementTransformer(obj) {
  if (!obj?.content) {
    return obj;
  }
  return classTransformerHandlers[obj.classType]?.(obj) ?? obj;
}

// Recursive function to parse each element
async function parseElement(element) {
  return {
    classType: getGdprClass(element.className, element),
    content: element.textContent.trim(),
  };
}

async function transverseNode(node) {
  const classType = getGdprClass(node.className, node);
  node.classType = classType;
  while (shouldPopFromStack(classType)) {
    readingStack.pop();
  }

  const lastElement = readingStack[readingStack.length - 1];
  const id = await (await uuidV4Generator.next()).value;
  const parsedElement = elementTransformer(await parseElement(node));

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

function makeHumanReadableIds(gdpr, gdprCopy, parentKey = '') {
  const result = {};

  const keys = Object.keys(gdpr);
  let index = 0;
  for (const key of keys) {
    if (isObJectAndNotArray(gdpr[key])) {
      const builtKey = buildId(gdpr[key], index);
      const newKey = builtKey ? `${parentKey ? `${parentKey}.${builtKey}` : builtKey}` : key;

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

function buildId(obj) {
  if (!obj) {
    return null;
  }
  const classType = obj.classType;

  const prefix = {
    [gdprClasses.CHAPTER]: 'cpt_',
    [gdprClasses.SECTION]: 'sct_',
    [gdprClasses.ARTICLE]: 'art_',
    [gdprClasses.POINT]: 'pt_',
    [gdprClasses.SUBPOINT]: 'spt_',
  };
  const numberExtractors = {
    [gdprClasses.CHAPTER]: (content) => {
      const match = content.match(/ ([IVXLCDM]+)$/);
      return match ? roman2Arabic(match[1].trim()) : null;
    },
    [gdprClasses.SECTION]: (content) => {
      const match = content.match(/ (\d+)$/);
      return match ? match[1].trim() : null;
    },
    [gdprClasses.ARTICLE]: (content) => {
      const match = content.match(/ (\d+)\./);
      return match ? match[1].trim() : null;
    },
    [gdprClasses.POINT]: (content) => {
      const match = content.slice(0, 5).match(/(\d+)/);
      return match ? match[1].trim() : null;
    },
    [gdprClasses.SUBPOINT]: (content) => {
      const match = content.match(/([\d\w]+)/);
      return match ? match[1].trim() : null;
    },
  };

  function roman2Arabic(roman) {
    // Define a mapping of Roman numerals to their Arabic values
    const romanToArabic = {
      I: 1,
      V: 5,
      X: 10,
      L: 50,
      C: 100,
      D: 500,
      M: 1000,
    };

    // Initialize the result to zero
    let result = 0;

    // Traverse the Roman numeral string
    for (let i = 0; i < roman.length; i++) {
      const current = romanToArabic[roman[i]];
      const next = romanToArabic[roman[i + 1]];

      // Check if the current numeral is less than the next numeral
      if (next && current < next) {
        // Subtract if the current numeral is less than the next
        result -= current;
      } else {
        // Otherwise, add the current numeral
        result += current;
      }
    }

    return result;
  }

  function build(content) {
    const extractedNumber = numberExtractors[classType](content);
    return extractedNumber ? prefix[classType] + extractedNumber : null;
  }

  if ([gdprClasses.CHAPTER, gdprClasses.SECTION, gdprClasses.ARTICLE].includes(classType)) {
    // Try to get the number from the content
    for (const iterator of Object.values(obj.content).filter(
      (value) => value.classType === 'TITLE_ID' || value.classType === classType
    )) {
      return build(iterator.content);
    }
  } else if (gdprClasses.POINT === classType) {
    if (typeof obj.content === 'string') {
      return build(obj.content);
    } else {
      const points = Object.values(obj.content).filter(
        (value) => value.classType === gdprClasses.POINT
      );
      return build(points[0].content);
    }
  } else if (gdprClasses.SUBPOINT === classType) {
    return build(obj.content[0]);
  }
  return null;
}

async function main() {
  const gdprHtml = fs.readFileSync(path.resolve(__dirname, '../../raw-data/gdpr-pt.html'), 'utf8');
  const dom = new JSDOM('<!DOCTYPE html>' + gdprHtml);

  const htmlNodes = Array.from(dom.window.document.body.children);

  for (const node of htmlNodes) {
    await transverseNode(node);
  }

  const gdprWithReadableId = makeHumanReadableIds(jsonOutput, Object.assign({}, jsonOutput));

  // output the JSON to a file
  fs.writeFileSync(
    path.resolve(__dirname, '../../datasets/gdpr-pt.json'),
    JSON.stringify(gdprWithReadableId, null, 2)
  );
}

main().then(() => {
  console.log('JSON file generated successfully ✅');
});
