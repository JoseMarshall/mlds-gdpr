const gdprPt = require('./gdpr-eu-pt.json');
const gdprComparing = require('./gdpr-eu-en.json');

function deepCompare(obj1, obj2, path = '') {
  const differences = [];

  for (const key in obj1) {
    const fullPath = path ? `${path}.${key}` : key;

    if (!(key in obj2)) {
      // Key is present in obj1 but missing in obj2
      differences.push(`${fullPath} is missing in obj2`);
    } else if (
      typeof obj1[key] === 'object' &&
      typeof obj2[key] === 'object' &&
      obj1[key] !== null &&
      obj2[key] !== null
    ) {
      // Recursively compare nested objects
      differences.push(...deepCompare(obj1[key], obj2[key], fullPath));
    }
  }

  // Check for keys in obj2 that are missing in obj1
  for (const key in obj2) {
    const fullPath = path ? `${path}.${key}` : key;
    if (!(key in obj1)) {
      differences.push(`${fullPath} is missing in obj1`);
    }
  }

  return differences;
}

const differences = deepCompare(gdprPt, gdprComparing);
console.log(differences);
