const fs = require('fs');
const path = require('path');

const gdprClasses = {
  CHAPTER: 'CHAPTER',
  SECTION: 'SECTION',
  ARTICLE: 'ARTICLE',
  POINT: 'POINT',
  SUBPOINT: 'SUBPOINT',
};

/**
 * Navigate through the gdprEu1 object and create a new object with the same structure but with the values from the gdprEu2 object.
 */
function syncGDPRs(gdprEu1, gdprEu2) {
  const result = {};

  const keysEu1 = Object.keys(gdprEu1);
  let index = 0;

  for (const key of keysEu1) {
    if (isObJectAndNotArray(gdprEu1[key])) {
      const r = syncGDPRs(gdprEu1[key], getValue(gdprEu2, key, index));
      if (Object.keys(r).length) {
        result[key] = r;
      } else {
        index--;
      }
    } else {
      result[key] = getLiteralValue(gdprEu2[key]);
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

function makeHumanReadableIds(gdprEu, gdprEuCopy, parentKey = '') {
  const result = {};

  const keys = Object.keys(gdprEu);
  let index = 0;
  for (const key of keys) {
    if (isObJectAndNotArray(gdprEu[key])) {
      const builtKey = buildId(gdprEu[key], index);
      const newKey = builtKey ? `${parentKey ? `${parentKey}.${builtKey}` : builtKey}` : key;

      result[newKey] = makeHumanReadableIds(
        gdprEu[key],
        getValue(gdprEuCopy, key, index),
        builtKey ? newKey : parentKey
      );
    } else {
      result[key] = getLiteralValue(gdprEuCopy[key]);
    }
    index++;
  }

  return result;
}

function main() {
  const gdprWithReadableId = makeHumanReadableIds(
    require('../../datasets/gdpr-eu-pt.json'),
    require('../../datasets/gdpr-eu-pt.json')
  );
  fs.writeFileSync(
    path.resolve(__dirname, `../../datasets/gdpr-eu-pt.json`),
    JSON.stringify(gdprWithReadableId, null, 2)
  );

  ['it', 'de', 'en'].forEach((locale) => {
    const synced = syncGDPRs(gdprWithReadableId, require(`../../datasets/gdpr-eu-${locale}.json`));
    fs.writeFileSync(
      path.resolve(__dirname, `../../datasets/gdpr-eu-${locale}.json`),
      JSON.stringify(synced, null, 2)
    );
  });

  return 'gdpr-eu ids Synced Successfully ✅';
}

main();

module.exports = main;
