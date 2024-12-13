const fs = require('fs');
const path = require('path');

function isObJectAndNotArray(value) {
  return typeof value === 'object' && !Array.isArray(value);
}

function getValue(gdprPartial, key, keyIndex) {
  const values = Object.values(gdprPartial);
  const value = ['content', 'classType'].includes(key)
    ? (gdprPartial[key] ?? values[keyIndex])
    : values[keyIndex];
  return isObJectAndNotArray(value) ? value : gdprPartial;
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
const alphabet = '_abcdefghijklmnopqrstuvwxyz';

function charToNumber(char) {
  return Number.isInteger(Number(char)) ? char : alphabet.indexOf(char);
}

function makeHumanReadableIds(gdpr, gdprCopy, parentCounter = 1) {
  const result = {};

  const keys = Object.keys(gdpr);

  let index = 0;

  let counter =
    keys
      .map((x) => Number(x.match(/_(\d+)$/)?.[1]))
      .filter((x) => x)
      .sort((a, b) => (a > b ? -1 : 1))[0] ?? 0;

  counter = charToNumber(counter);
  parentCounter = String(parentCounter).match(/\w/) ? charToNumber(parentCounter) : parentCounter;

  for (const key of keys) {
    if (key === 'cpt_1.art_4.pt_72234c19-a210-466d-b416-8796f2c4a58e') {
      console.log();
    }
    if (isObJectAndNotArray(gdpr[key])) {
      const parts = key.split('.');
      let newKey =
        parts.length > 1 &&
        parts[parts.length - 1].includes('-') &&
        ['POINT', 'SUBPOINT', 'SUBSUBPOINT'].includes(gdpr[key].classType)
          ? key.replace(
              parts[parts.length - 1],
              parts[parts.length - 1].split('_')[0] +
                '_' +
                (keys.filter((k) => k.match(/_([a-z]+)$/i)?.[1]).length
                  ? alphabet[++counter]
                  : ++counter)
            )
          : key;

      const partsNewKey = newKey.split('.');
      newKey =
        partsNewKey.length > 1 &&
        partsNewKey[partsNewKey.length - 2].includes('-') &&
        ['POINT', 'SUBPOINT', 'SUBSUBPOINT'].includes(gdpr[key].classType)
          ? newKey.replace(
              partsNewKey[partsNewKey.length - 2],
              partsNewKey[partsNewKey.length - 2].split('_')[0] +
                '_' +
                (partsNewKey[partsNewKey.length - 2].startsWith('pt_')
                  ? parentCounter
                  : alphabet[parentCounter])
            )
          : newKey;

      result[newKey] = makeHumanReadableIds(
        gdpr[key],
        getValue(gdprCopy, key, index),
        counter <= 0 ? parentCounter : counter
      );
    } else {
      result[key] = getLiteralValue(gdprCopy[key]);
    }
    index++;
  }

  return result;
}

function main() {
  const gdprName = 'gdpr-pt-en.json';
  const gdprWithReadableId = makeHumanReadableIds(
    require(`../../datasets/${gdprName}`),
    require(`../../datasets/${gdprName}`)
  );

  fs.writeFileSync(
    path.resolve(__dirname, `../../datasets/${gdprName}`),
    JSON.stringify(gdprWithReadableId, null, 2)
  );

  return 'gdpr-eu ids transformed Successfully ✅';
}

console.log(main());
