const ids = require('./ids.json');

async function* idAsyncGenerator() {
  for (const id of ids) {
    yield id;
  }
}

module.exports = {
  uuidV4Generator: idAsyncGenerator(),
};
