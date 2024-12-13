const { areArticlesRelated } = require('./find-similarity');

const gdprEuPt = require('../datasets/gdpr-eu-pt.json');
const gdprPt = require('../datasets/gdpr-pt.json');

const fs = require('fs');

function getPointContent(point) {
  return typeof point.content === 'string'
    ? [point.content]
    : Object.values(point.content).flatMap((x) =>
        typeof x.content === 'string' ? x.content : x.content[1]
      );
}

/**
 * Retrieve a value from an object using a dot notation path.
 * @param {Object} obj - The object to traverse.
 * @param {string} path - The dot notation path.
 * @returns {*} - The value at the given path or undefined if not found.
 */
function getObjectByPath(obj, path) {
  if (!obj || typeof path !== 'string') return undefined;

  const paths = path.split('.');
  let p = '';
  let result = null;
  for (const iterator of paths) {
    const index = p ? p + '.' + iterator : iterator;
    result = (obj.content ?? obj)[index];
    obj = result;
    p = index;
  }
  return result;
}

// Helper function to extract all articles from JSON
function extractArticles(jsonObj) {
  const articles = [];

  function traverse(node, path = '') {
    if (node.classType === 'ARTICLE') {
      const values = Object.values(node.content || {});
      const p = path.split('content.');
      articles.push({
        path: p[p.length - 1],
        title: values.find((v) => v.classType === 'TITLE')?.content,
        points: values.filter((item) => item.classType === 'POINT').flatMap(getPointContent),
      });
    }

    if (typeof node === 'object' && node !== null) {
      for (const [key, value] of Object.entries(node)) {
        traverse(value, path ? `${path}.${key}` : key);
      }
    }
  }

  traverse(jsonObj);
  return articles.filter((a) => a.title);
}

// Extract articles from both JSONs
const ptArticles = extractArticles(gdprPt);
const euArticles = extractArticles(gdprEuPt);

// Add relatedArticles to gdpr-pt.json
for (const ptArticle of ptArticles) {
  try {
    getObjectByPath(gdprPt, ptArticle.path).relatedArticles = euArticles
      .filter((euArticle) => areArticlesRelated({ article1: ptArticle, article2: euArticle }))
      .map((euArticle) => euArticle.path.match(/art_(\d+)/)[1])
      .slice(0, 4);
  } catch (error) {
    console.log(error);
  }
}

// Write updated JSON back to file

fs.writeFileSync(
  path.resolve(__dirname, '../datasets/gdpr-pt.json'),
  JSON.stringify(gdprPt, null, 2)
);

console.log('Updated gdpr-pt.json with relatedArticles key.');
