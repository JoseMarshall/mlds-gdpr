const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');
const { v4: uuid } = require('uuid');

const gdprClasses = {
  CHAPTER: 'CHAPTER',
  SECTION: 'SECTION',
  ARTICLE: 'ARTICLE',
  POINT: 'POINT',
  SUBPOINT: 'SUBPOINT',
  PARAGRAPH: 'PARAGRAPH',

  // For Id annotation
  TITLE: 'TITLE',
  TITLE_ID: 'TITLE_ID',
};

const gdprClassesRegex = {
  CHAPTER: /^ti-section-1$/,
  SECTION: /^ti-section-1$/,
  ARTICLE: /^ti-art$/,
  POINT: /^normal$/,

  // For Id annotation
  TITLE: /^(ti-section-2|sti-art)$/,
  TITLE_ID: /^[a-z0-9]+\-[0-9]+\-[0-9]$/,
};

const readingStack = [];

let jsonOutput = {};
const gdprClassesPrecedence = {
  [gdprClasses.CHAPTER]: 0,
  [gdprClasses.SECTION]: 1,
  [gdprClasses.ARTICLE]: 2,
  [gdprClasses.POINT]: 3,
  [gdprClasses.SUBPOINT]: 4,
  [gdprClasses.PARAGRAPH]: 5,
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
  let foundClassType = Object.entries(gdprClassesRegex).find(([_, regex]) => regex.test(className));

  if (foundClassType) {
    if (
      foundClassType[0] === gdprClasses.CHAPTER &&
      node?.textContent?.trim().match(/^Abschnitt \d+$/)
    ) {
      return gdprClasses.SECTION;
    }
    return foundClassType[0];
  }

  /**
   * Particular cases
   */
  const lastElement = readingStack[readingStack.length - 1];
  if ([gdprClasses.POINT, gdprClasses.SUBPOINT].includes(lastElement?.classType) && !className) {
    return gdprClasses.SUBPOINT;
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
  return classTransformerHandlers[obj.classType]?.(obj) ?? obj;
}

// Recursive function to parse each element
function parseElement(element) {
  const children = element.children;
  let result = {
    classType: getGdprClass(element.className, element),
    content: {},
  };
  const ignoreTags = ['COLGROUP', 'COL'];

  if (!children || children.length === 0 || element.className === 'normal') {
    result.content = element.textContent.trim();
  }

  Array.from(children).forEach((child) => {
    if (ignoreTags.includes(child.tagName)) {
      return;
    }
    const isLeaf =
      ['SPAN', 'TD'].includes(child.tagName) ||
      (['P'].includes(child.tagName) && child.children.length === 0);

    const id = uuid();
    if (isLeaf) {
      const childClassType =
        getGdprClass(element.id, element) ?? getGdprClass(element.className, element);
      result.content[id] = {
        classType: childClassType,
        content:
          childClassType === gdprClasses.TITLE_ID && result.classType === gdprClasses.ARTICLE
            ? element.textContent.trim()
            : child.textContent.trim(),
      };
    } else {
      result.content[id] = {
        classType: getGdprClass(child.id, child) ?? getGdprClass(child.className, child),
        content: parseElement(child),
      };
    }
  });

  return result;
}

function transverseNode(node) {
  const classType = getGdprClass(node.className, node);

  while (shouldPopFromStack(classType)) {
    readingStack.pop();
  }

  const lastElement = readingStack[readingStack.length - 1];
  const parsedElement = elementTransformer(parseElement(node));

  const id = uuid();
  if (classType in gdprClassesPrecedence) {
    readingStack.push({ id, classType, parsedElement });
  }

  if (lastElement?.id) {
    if (typeof lastElement.parsedElement.content === 'object') {
      lastElement.parsedElement.content[id] = parsedElement;
    } else {
      lastElement.parsedElement.content = {
        [uuid()]: { ...lastElement.parsedElement },
        [id]: parsedElement,
      };
    }
    // jsonOutput[lastElement.id] ??= lastElement.parsedElement;
  } else {
    jsonOutput[id] ??= parsedElement;
  }
}

function main() {
  const gdprHtml = fs.readFileSync(path.resolve(__dirname, '../raw-data/gdpr-eu-de.html'), 'utf8');
  const dom = new JSDOM('<!DOCTYPE html>' + gdprHtml);

  const htmlNodes = Array.from(dom.window.document.body.children);
  htmlNodes.forEach(transverseNode);
  // output the JSON to a file
  fs.writeFileSync(
    path.resolve(__dirname, '../datasets/gdpr-eu-de.json'),
    JSON.stringify(jsonOutput, null, 2)
  );

  console.log('JSON file generated successfully ✅');
}

main();
