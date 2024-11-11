const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');
const { uuidV4Generator, subPointTransformer } = require('./common');

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
};

const classTransformerHandlers = {
  [gdprClasses.SUBPOINT]: subPointTransformer,
};

function getGdprClass(className, node) {
  if (node.classType && [gdprClasses.SUBPOINT].includes(node.classType)) {
    return node.classType;
  }
  let foundClassType = Object.entries(gdprClassesRegex).find(([_, regex]) => regex.test(className));
  const lastElement = readingStack[readingStack.length - 1];

  if (foundClassType) {
    if (
      foundClassType[0] === gdprClasses.POINT &&
      lastElement?.classType === gdprClasses.SUBPOINT &&
      !node?.textContent
        ?.trim()
        .slice(0, 5)
        .match(/.*\d.*/)
    ) {
      return gdprClasses.SUBPOINT;
    } else if (
      foundClassType[0] === gdprClasses.CHAPTER &&
      node?.textContent?.trim().match(/^Sezione \d+$/)
    ) {
      return gdprClasses.SECTION;
    }
    return foundClassType[0];
  } else if (

  /**
   * Particular cases
   */
    [gdprClasses.POINT, gdprClasses.SUBPOINT].includes(lastElement?.classType) &&
    !className
  ) {
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

function elementTransformer(obj) {
  if (!obj?.content) {
    return obj;
  }

  return classTransformerHandlers[obj.classType]?.(obj) ?? obj;
}

// Recursive function to parse each element
async function parseElement(element) {
  const children = element.children;
  let result = {
    classType: getGdprClass(element.className, element),
    content: {},
  };
  const ignoreTags = ['COLGROUP', 'COL'];

  if (!children || children.length === 0 || element.className === 'normal') {
    result.content = element.textContent.trim();
  }

  for (const child of Array.from(children)) {
    if (ignoreTags.includes(child.tagName)) {
      continue;
    }
    const isLeaf =
      ['SPAN', 'TD'].includes(child.tagName) ||
      (['P'].includes(child.tagName) && child.children.length === 0);

    const id = await (await uuidV4Generator.next()).value;
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
        content: await parseElement(child),
      };
    }
  }

  return result;
}

async function transverseNode(node) {
  if (node.tagName === 'DIV') {
    for (const child of Array.from(node.children)) {
      await transverseNode(child);
    }
    return;
  }
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

async function main() {
  const gdprHtml = fs.readFileSync(
    path.resolve(__dirname, '../../raw-data/gdpr-eu-it.html'),
    'utf8'
  );
  const dom = new JSDOM('<!DOCTYPE html>' + gdprHtml);

  const htmlNodes = Array.from(dom.window.document.body.children);
  for (const node of htmlNodes) {
    await transverseNode(node);
  }
  // output the JSON to a file
  fs.writeFileSync(
    path.resolve(__dirname, '../../datasets/gdpr-eu-it.json'),
    JSON.stringify(jsonOutput, null, 2)
  );
}

main().then(() => {
  console.log('JSON file generated successfully ✅');
});
