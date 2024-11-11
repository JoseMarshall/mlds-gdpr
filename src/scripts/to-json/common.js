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

module.exports = {
  uuidV4Generator: idAsyncGenerator(),
  subPointTransformer,
};
