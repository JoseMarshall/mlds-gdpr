const makeGdprEuPtJson = require('./gdpr-eu-pt');
const makeGdprEuItJson = require('./gdpr-eu-it');
const makeGdprEuDeJson = require('./gdpr-eu-de');
const makeGdprEuEnJson = require('./gdpr-eu-en');
const syncGdprEuIds = require('./sync-gdpr-eu-ids');

async function main() {
  const result = await Promise.all([
    makeGdprEuPtJson(),
    makeGdprEuItJson(),
    makeGdprEuDeJson(),
    // makeGdprEuEnJson(),
  ]);

  // Sync the Ids
  syncGdprEuIds();

  return result;
}

main().then(console.log).catch(console.error);
