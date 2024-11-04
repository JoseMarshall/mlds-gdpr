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

const gdprClassesIdRegex = {
  CHAPTER: /^cpt_([IVX]+)$/,
  SECTION: /^cpt_([IVX]+).sct_[0-9]+$/,
  ARTICLE: /^art_([0-9]+)$/,
  POINT: /^[0-9]{1,3}.[0-9]{1,3}$/,

  // For Id annotation
  TITLE: /^.+\.tit_[0-9]+$/,
  TITLE_ID: /^[a-z0-9]+\-[0-9]+\-[0-9]$/,
};

const classTransformerHandlers = {
  [gdprClasses.POINT]: (content) => {
    if (typeof content !== 'object') {
      return content;
    }
    const values = Object.values(content);

    if (
      values.length === 2 &&
      typeof values[0].content === 'string' &&
      typeof values[1].content === 'string'
    ) {
      return values.map((x) => x.content).sort((a, b) => (a.length >= b.length ? 1 : -1));
    }
    return content;
  },

  [gdprClasses.SUBPOINT]: (content) =>
    typeof content === 'object' && !Array.isArray(content)
      ? Object.values(content)
          .map((x) => x.content ?? x)
          .sort((a, b) => (a.length >= b.length ? 1 : -1))
      : content,
};

function getGdprClass(id, content, parent) {
  let foundClassType = Object.entries(gdprClassesIdRegex).find(([_, regex]) => regex.test(id));

  if (foundClassType) {
    return foundClassType[0];
  }

  /* Particular Cases */
  if (gdprClassesIdRegex.POINT.test(parent.id)) {
    return typeof content === 'object' && Object.keys(content).length === 2
      ? gdprClasses.SUBPOINT
      : typeof content === 'string'
        ? gdprClasses.POINT
        : null;
  } else if (gdprClassesIdRegex.ARTICLE.test(parent.id)) {
    if (typeof content === 'object' && Object.keys(content).length === 2) {
      return gdprClasses.POINT;
    }
    return gdprClasses.PARAGRAPH;
  } else if (
    typeof content === 'object' &&
    Object.keys(content).length === 2 &&
    Object.values(content).some(({ content }) => /^\(\d+\)$/.test(content))
  ) {
    return gdprClasses.POINT;
  } else if (
    typeof content === 'object' &&
    Object.keys(content).length === 2 &&
    Object.values(content).some(({ content }) => /^\(\w+\)$/.test(content))
  ) {
    return gdprClasses.SUBPOINT;
  }
  return null;
}

function contentTransformer({ content, classType }) {
  if (typeof content === 'string') {
    return content;
  }
  return classTransformerHandlers[classType]?.(content) ?? content;
}

function flatObjectWithSingleChild(obj) {
  if (typeof obj === 'string') {
    return obj
      .split('\n')
      .map((x) => x.trim())
      .join(' ');
  }
  const keys = Object.keys(obj);
  if (keys.length === 1) {
    const key = keys[0];
    return flatObjectWithSingleChild(obj[key].content);
  }
  return { ...obj };
}

// Recursive function to parse each element
function parseElement(element) {
  const children = element.children;
  let result = { content: {} };
  const ignoreTags = ['COLGROUP', 'COL'];

  Array.from(children).forEach((child) => {
    if (ignoreTags.includes(child.tagName)) {
      return;
    }
    const isLeaf = ['P', 'SPAN'].includes(child.tagName) && child.children.length === 0;

    const id = child.id || uuid();
    if (isLeaf) {
      result.content[id] = { content: child.textContent.trim() };
    } else {
      result.content[id] = { content: parseElement(child) };
    }
    result.content[id].classType = getGdprClass(id, result.content[id].content, element);
    result.content[id].content = contentTransformer(result.content[id]);
  });

  return flatObjectWithSingleChild(result.content);
}

function parseHtmlToJson(document) {
  // Root object to hold JSON structure for all top-level divs
  const result = {};

  // Select all top-level divs in the document
  const chapterDivs = Array.from(document.querySelectorAll("div[id^='cpt_']")).filter((div) =>
    gdprClassesIdRegex.CHAPTER.test(div.id)
  );

  chapterDivs.forEach((chapterDiv) => {
    const id = chapterDiv.id;
    result[id] = {
      classType: gdprClasses.CHAPTER,
      content: parseElement(chapterDiv),
    };
  });

  return result;
}

function main() {
  const gdprHtml = fs.readFileSync(
    path.resolve(__dirname, '../../raw-data/gdpr-eu-en.html'),
    'utf8'
  );
  const dom = new JSDOM('<!DOCTYPE html>' + gdprHtml);
  // Usage example
  const jsonOutput = parseHtmlToJson(dom.window.document);
  // output the JSON to a file
  fs.writeFileSync(
    path.resolve(__dirname, '../../datasets/gdpr-eu-en.json'),
    JSON.stringify(jsonOutput, null, 2)
  );

  console.log('JSON file generated successfully ✅');
}

main();
