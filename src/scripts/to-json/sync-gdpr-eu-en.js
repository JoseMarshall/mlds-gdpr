const gdprEuPt = require('../../datasets/gdpr-eu-pt.json');
const gdprEuEn = require('../../datasets/gdpr-eu-en.json');
const fs = require('fs');
const path = require('path');

/**
 * Navigate through the gdprEuPt object and create a new object with the same structure but with the values from the gdprEuEn object.
 */
function syncGdprEuEn(gdprEuPt, gdprEuEn) {
  const result = {};

  const ptKeys = Object.keys(gdprEuPt);
  let index = 0;
  for (const key of ptKeys) {
    if (isObJectAndNotArray(gdprEuPt[key])) {
      result[key] = syncGdprEuEn(gdprEuPt[key], getValue(gdprEuEn, key, index));
    } else {
      result[key] = getLiteralValue(gdprEuEn[key]);
    }
    index++;
  }

  return result;
}

function getValue(gdprEuEnPartial, key, keyIndex) {
  const values = Object.values(gdprEuEnPartial);
  const value = ['content', 'classType'].includes(key)
    ? (gdprEuEnPartial[key] ?? values[keyIndex])
    : values[keyIndex];
  return isObJectAndNotArray(value) ? value : gdprEuEnPartial;
}

function isObJectAndNotArray(value) {
  return typeof value === 'object' && !Array.isArray(value);
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

const gdprEuEnSync = syncGdprEuEn(gdprEuPt, gdprEuEn);

fs.writeFileSync(
  path.resolve(__dirname, '../../datasets/gdpr-eu-en-sync.json'),
  JSON.stringify(gdprEuEnSync, null, 2)
);
