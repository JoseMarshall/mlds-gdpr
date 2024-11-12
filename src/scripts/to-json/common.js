const ids = require('./ids.json');

async function* idAsyncGenerator() {
  for (const id of ids) {
    yield id;
  }
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

function subPointTransformer(obj) {
  if (typeof obj !== 'object' || Array.isArray(obj)) {
    return obj;
  }
  const newObj = flatObjectWithSingleChild(obj);
  const values =
    typeof newObj.content === 'string' ? ['', newObj.content] : Object.values(newObj.content);

  if (
    values.length === 2 &&
    (values[0] === '' ||
      (typeof values[0].content === 'string' && typeof values[1].content === 'string'))
  ) {
    return {
      classType: newObj.classType,
      content: values.map((x) => x.content ?? x).sort((a, b) => (a.length >= b.length ? 1 : -1)),
    };
  }
  return newObj;
}

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
    } else if (obj1[key] !== obj2[key]) {
      // Key is present in both, but values differ
      differences.push(`${fullPath}: '${obj1[key]}' (obj1) !== '${obj2[key]}' (obj2)`);
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

module.exports = {
  uuidV4Generator: idAsyncGenerator(),
  subPointTransformer,
  deepCompare,
};
