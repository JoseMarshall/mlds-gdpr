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

const gdprClassesRegex = {
  CHAPTER: /^CAPÍTULO ([IVX]+)$/,
  SECTION: /^SECÇÃO ([IVX]+)$/,
  ARTICLE: /^Artigo \d+\.º$/,
  POINT: /^\d+ \- .+/,
  SUBPOINT: /^\w{1}\) .+/,

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

const classTransformerHandlers = {
  [gdprClasses.SUBPOINT]: (obj) => {
    if (typeof obj !== 'object' || Array.isArray(obj)) {
      return obj;
    }
    const newObj = flatObjectWithSingleChild(obj);
    const values = Object.values(newObj.content);

    if (
      values.length === 2 &&
      typeof values[0].content === 'string' &&
      typeof values[1].content === 'string'
    ) {
      return {
        classType: newObj.classType,
        content: values.map((x) => x.content).sort((a, b) => (a.length >= b.length ? 1 : -1)),
      };
    }
    return newObj;
  },
};

function getGdprClass(className, node) {
  let foundClassType = Object.entries(gdprClassesRegex).find(([_, regex]) =>
    regex.test(node?.textContent?.trim())
  );

  if (foundClassType) {
    if (gdprClassesRegex.TITLE.test(className)) {
      return gdprClasses.TITLE;
    } else if (gdprClassesRegex.TITLE_ID.test(className)) {
      return gdprClasses.TITLE_ID;
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

function flatObjectWithSingleChild(obj, result = {}) {
  if (typeof obj === 'object') {
    // Check if the current value is a string
    const contentKeys = 'content' in obj ? Object.keys(obj.content) : [];
    if (contentKeys.length > 1 && !Object.keys(obj.content).includes('content')) {
      result.content = obj.content;
      result.classType = obj.classType;
    } else {
      const keys = Object.keys(obj).filter((key) => key !== 'classType');
      flatObjectWithSingleChild(obj.content ?? obj[keys[0]], result);
    }
  }

  return result;
}

function elementTransformer(obj) {
  if (typeof obj.content === 'string') {
    return obj;
  }
  return obj; // classTransformerHandlers[obj.classType]?.(obj) ?? obj;
}

// Recursive function to parse each element
async function parseElement(element) {
  const children = element.children;
  let result = {
    classType: getGdprClass(element.className, element),
    content: {},
  };

  if (!children || children.length === 0 || element.className === 'paragraph-normal-text') {
    result.content = element.textContent.trim();
  }

  for (const child of Array.from(children)) {
    const isLeaf =
      ['SPAN', 'TD'].includes(child.tagName) ||
      (['P'].includes(child.tagName) && child.children.length === 0);

    const id = await (await uuidV4Generator.next()).value;
    if (isLeaf) {
      const childClassType = getGdprClass(child.className, child);
      result.content[id] = {
        classType: childClassType,
        content:
          childClassType === gdprClasses.TITLE_ID && result.classType === gdprClasses.ARTICLE
            ? element.textContent.trim()
            : child.textContent.trim(),
      };
    } else {
      result.content[id] = {
        classType: getGdprClass(child.className, child),
        content: await parseElement(child),
      };
    }
  }

  return result;
}

async function transverseNode(node) {
  const classType = getGdprClass(node.className, node);

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

async function main() {
  const gdprHtml = fs.readFileSync(path.resolve(__dirname, '../../raw-data/gdpr-pt.html'), 'utf8');
  const dom = new JSDOM('<!DOCTYPE html>' + gdprHtml);

  const htmlNodes = Array.from(dom.window.document.body.children);

  for (const node of htmlNodes) {
    await transverseNode(node);
  }
  // output the JSON to a file
  fs.writeFileSync(
    path.resolve(__dirname, '../../datasets/gdpr-pt.json'),
    JSON.stringify(jsonOutput, null, 2)
  );
}

main().then(() => {
  console.log('JSON file generated successfully ✅');
});
